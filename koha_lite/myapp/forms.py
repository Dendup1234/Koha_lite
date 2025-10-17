from django import forms
from .models import *

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ["code", "name"]

class ItemTypeForm(forms.ModelForm):
    class Meta:
        model = ItemType
        fields = ["code", "name"]

class PatronCategoryForm(forms.ModelForm):
    class Meta:
        model = Patron_Categories
        fields = ["code", "name"]
