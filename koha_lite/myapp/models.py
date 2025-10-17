from django.db import models


# AAdministrative Module
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
    

