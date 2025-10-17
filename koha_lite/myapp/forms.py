from django import forms
from .models import *

#Adminstration Module
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
#Patron Management Module
class PatronForm(forms.ModelForm):
    class Meta:
        model = Patron
        fields = ["external_id", "first_name", "last_name", "email", "category", "expires_at", "is_active"]
        widgets = {
            "expires_at": forms.DateInput(attrs={"type": "date"})  # native calendar UI
        }

class PatronCSVUploadForm(forms.Form):
    file = forms.FileField(
        help_text="CSV columns: external_id,first_name,last_name,email,category_code,expires_at(YYYY-MM-DD),is_active(true/false)"
    )
    update_existing = forms.BooleanField(
        required=False, initial=True,
        help_text="Update rows if external_id already exists."
    )