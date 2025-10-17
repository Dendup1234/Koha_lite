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
    

