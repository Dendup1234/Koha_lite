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

