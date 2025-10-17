from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

# Administrative Module
class Branch(models.Model):
    code = models.CharField(max_length=20, unique=True,primary_key=True)   # UNIQUE as per spec
    name = models.CharField(max_length=120,null=False)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.name}"


class ItemType(models.Model):
    # You wanted code as PRIMARY KEY
    code = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=80,null=False)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.name}"

class Patron_Categories(models.Model):
    code = models.CharField(max_length=20, unique=True,primary_key= True)
    name = models.CharField(max_length=120,null=False)
    
    class Meta:
        ordering = ["code"]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
# Patron Management Module    
class Patron(models.Model):
    external_id = models.CharField(max_length=40, unique=True)  # student/staff ID
    first_name  = models.CharField(max_length=80)
    last_name   = models.CharField(max_length=80)
    email       = models.EmailField(blank=True)

    # keep DB column name 'category_code' and FK to Patron_Categories(code)
    category = models.ForeignKey(
        "myapp.Patron_Categories",
        to_field="code",
        db_column="category_code",
        on_delete=models.PROTECT,
        related_name="patrons",
    )

    expires_at = models.DateField(null=True, blank=True)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name = "patron"
        verbose_name_plural = "patrons"

    def __str__(self):
        return f"{self.external_id} — {self.first_name} {self.last_name}"
    #Logic for the expiration date
    @property
    def is_expired(self):
        from django.utils import timezone
        return bool(self.expires_at and self.expires_at <= timezone.localdate())
    
#Cateloguing Module
class Biblio(models.Model):
    """
    Core bibliographic record. Keep it simple and add a flexible JSON field
    for item-type-specific metadata (e.g., { "duration_min": 90 } for DVDs).
    """
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    isbn = models.CharField(max_length=20, unique=True, null=True, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    publication_year = models.PositiveIntegerField(null=True, blank=True)

    # Optional flexible attributes per item type (server-agnostic)
    attributes = models.JSONField(blank=True, default=dict, help_text="Optional per-item-type metadata")

    class Meta:
        ordering = ["title"]
        verbose_name = "biblio"
        verbose_name_plural = "biblios"

    def __str__(self):
        return self.title


class Item(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        ISSUED    = "ISSUED", "Issued"
        OVERDUE   = "OVERDUE", "Overdue"
        LOST      = "LOST", "Lost"

    biblio = models.ForeignKey(Biblio, on_delete=models.PROTECT, related_name="items")
    accession_number = models.CharField(max_length=30, unique=True)
    barcode = models.CharField(max_length=50, blank=True)
    item_type = models.ForeignKey("myapp.ItemType", on_delete=models.PROTECT, related_name="items")
    branch = models.ForeignKey("myapp.Branch", on_delete=models.PROTECT, related_name="items")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.AVAILABLE)

    class Meta:
        ordering = ["accession_number"]
        indexes = [
            models.Index(fields=["item_type"]),
            models.Index(fields=["branch"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.accession_number} — {self.biblio}"
    
# Circulation Module
class IssuingRule(models.Model):
    """Policy for a PatronCategory + ItemType pair."""
    patron_category = models.ForeignKey(
        "myapp.Patron_Categories",
        to_field="code",
        db_column="patron_category",
        on_delete=models.CASCADE,
        related_name="issuing_rules",
    )
    item_type = models.ForeignKey(
        "myapp.ItemType",
        to_field="code",
        db_column="item_type",
        on_delete=models.CASCADE,
        related_name="issuing_rules",
    )
    loan_days = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text="How many days per loan.")
    daily_fine = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    max_fine = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    renewal_allowed = models.BooleanField(default=True)
    max_renewals = models.PositiveIntegerField(default=2)

    class Meta:
        unique_together = ("patron_category", "item_type")
        ordering = ["patron_category__code", "item_type__code"]
        verbose_name = "issuing rule"
        verbose_name_plural = "issuing rules"

    def __str__(self):
        return f"{self.patron_category_id} / {self.item_type_id} → {self.loan_days} days"


class Loan(models.Model):
    patron = models.ForeignKey("myapp.Patron", on_delete=models.PROTECT, related_name="loans")
    item = models.ForeignKey("myapp.Item", on_delete=models.PROTECT, related_name="loans")
    issued_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    renewal_count = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=["patron", "due_at"]),
            models.Index(fields=["item", "due_at"]),
        ]
        # prevent more than one ACTIVE loan for the same item
        constraints = [
            models.UniqueConstraint(
                fields=["item"],
                condition=models.Q(return_date__isnull=True),
                name="unique_active_loan_per_item",
            ),
        ]
        ordering = ["-issued_at"]

    @property
    def is_active(self):
        return self.return_date is None

    def __str__(self):
        return f"Loan #{self.pk} — {self.patron} → {self.item}"