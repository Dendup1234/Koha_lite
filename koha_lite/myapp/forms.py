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

# Cateloguing Module
class BiblioForm(forms.ModelForm):
    class Meta:
        model = Biblio
        fields = ["title", "author", "isbn", "publisher", "publication_year", "attributes"]
        widgets = {
            "attributes": forms.Textarea(attrs={"rows": 4, "placeholder": '{"pages": 200, "language": "dz"}'}),
        }

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["biblio", "accession_number", "barcode", "item_type", "branch", "status"]

#Circulation Module
class CheckoutForm(forms.Form):
    patron_query = forms.CharField(
        label="Patron", help_text="Enter external ID or name", max_length=64
    )
    item_query = forms.CharField(
        label="Item", help_text="Enter accession number or barcode", max_length=64
    )

    def clean(self):
        cleaned = super().clean()
        pq = cleaned.get("patron_query", "").strip()
        iq = cleaned.get("item_query", "").strip()

        # Resolve patron
        patron = (Patron.objects
                  .filter(external_id__iexact=pq).first()
                  or Patron.objects.filter(first_name__icontains=pq).order_by("id").first()
                  or Patron.objects.filter(last_name__icontains=pq).order_by("id").first())
        if not patron:
            raise forms.ValidationError("Patron not found.")
        cleaned["patron"] = patron

        # Resolve item
        item = (Item.objects
                .filter(accession_number__iexact=iq).first()
                or Item.objects.filter(barcode__iexact=iq).first())
        if not item:
            raise forms.ValidationError("Item not found.")
        cleaned["item"] = item

        return cleaned


class CheckinForm(forms.Form):
    item_query = forms.CharField(
        label="Item", help_text="Enter accession number or barcode", max_length=64
    )

    def clean(self):
        cleaned = super().clean()
        q = cleaned.get("item_query", "").strip()
        from .models import Loan, Item

        item = (Item.objects.filter(accession_number__iexact=q).first()
                or Item.objects.filter(barcode__iexact=q).first())
        if not item:
            raise forms.ValidationError("Item not found.")

        loan = Loan.objects.filter(item=item, return_date__isnull=True).select_related("patron").first()
        if not loan:
            raise forms.ValidationError("No active loan found for this item.")

        cleaned["loan"] = loan
        return cleaned


class RenewForm(forms.Form):
    item_query = forms.CharField(
        label="Item", help_text="Enter accession number or barcode", max_length=64
    )

    def clean(self):
        cleaned = super().clean()
        q = cleaned.get("item_query", "").strip()
        from .models import Loan, Item

        item = (Item.objects.filter(accession_number__iexact=q).first()
                or Item.objects.filter(barcode__iexact=q).first())
        if not item:
            raise forms.ValidationError("Item not found.")

        loan = Loan.objects.filter(item=item, return_date__isnull=True).select_related("patron").first()
        if not loan:
            raise forms.ValidationError("No active loan to renew for this item.")

        cleaned["loan"] = loan
        return cleaned