import csv
from datetime import datetime
from io import TextIOWrapper
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView,FormView,DetailView
from .models import *
from .forms import *
from django.db import models, transaction
from django.contrib import messages
from .services.circulation import checkout as svc_checkout, checkin as svc_checkin, renew as svc_renew
from django.db.models import Q
# --- Dashboard (Administrative module entry) ---
def admin_dashboard(request):
    return render(request, "library/admin_dashboard.html")


class ModelTitleContextMixin:
    """Provide safe, template-friendly model labels and an action label."""
    action_label = None  # override per view if you like ("Create", "Edit")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        meta = self.model._meta
        ctx["model_verbose"] = meta.verbose_name.title()
        ctx["model_verbose_plural"] = meta.verbose_name_plural.title()
        # Fallback action label based on view type
        if self.action_label:
            ctx["action_label"] = self.action_label
        else:
            ctx["action_label"] = "Create" if isinstance(self, CreateView) else "Edit"
        return ctx

# ---------- Branch ----------
class BranchList(ListView):
    model = Branch
    template_name = "library/branch_list.html"
    context_object_name = "rows"

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(code__icontains=q)
        return qs

class BranchCreate(CreateView):
    model = Branch
    form_class = BranchForm
    template_name = "library/form.html"
    success_url = reverse_lazy("branch_list")
    action_label = "Create"

class BranchUpdate(UpdateView):
    model = Branch
    pk_url_kwarg = "code"  # primary key is 'code'
    slug_field = "code"
    slug_url_kwarg = "code"
    form_class = BranchForm
    template_name = "library/form.html"
    success_url = reverse_lazy("branch_list")
    action_label = "Edit"

class BranchDelete(DeleteView):
    model = Branch
    pk_url_kwarg = "code"
    slug_field = "code"
    slug_url_kwarg = "code"
    template_name = "library/confirm_delete.html"
    success_url = reverse_lazy("branch_list")

# ---------- ItemType ----------
class ItemTypeList(ListView):
    model = ItemType
    template_name = "library/itemtype_list.html"
    context_object_name = "rows"

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(code__icontains=q)
        return qs

class ItemTypeCreate(CreateView):
    model = ItemType
    form_class = ItemTypeForm
    template_name = "library/form.html"
    success_url = reverse_lazy("itemtype_list")
    action_label = "Create"

class ItemTypeUpdate(UpdateView):
    model = ItemType
    pk_url_kwarg = "code"
    slug_field = "code"
    slug_url_kwarg = "code"
    form_class = ItemTypeForm
    template_name = "library/form.html"
    success_url = reverse_lazy("itemtype_list")
    action_label = "Edit"

class ItemTypeDelete(DeleteView):
    model = ItemType
    pk_url_kwarg = "code"
    slug_field = "code"
    slug_url_kwarg = "code"
    template_name = "library/confirm_delete.html"
    success_url = reverse_lazy("itemtype_list")

# ---------- Patron Categories ----------
class PatronCategoryList(ListView):
    model = Patron_Categories
    template_name = "library/patroncat_list.html"
    context_object_name = "rows"

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(code__icontains=q)
        return qs

class PatronCategoryCreate(CreateView):
    model = Patron_Categories
    form_class = PatronCategoryForm
    template_name = "library/form.html"
    success_url = reverse_lazy("patroncat_list")
    action_label = "Create"

class PatronCategoryUpdate(UpdateView):
    model = Patron_Categories
    pk_url_kwarg = "code"
    slug_field = "code"
    slug_url_kwarg = "code"
    form_class = PatronCategoryForm
    template_name = "library/form.html"
    success_url = reverse_lazy("patroncat_list")
    action_label = "Edit"

class PatronCategoryDelete(DeleteView):
    model = Patron_Categories
    pk_url_kwarg = "code"
    slug_field = "code"
    slug_url_kwarg = "code"
    template_name = "library/confirm_delete.html"
    success_url = reverse_lazy("patroncat_list")

# Small mixin to avoid using _meta in templates
class ModelTitleContextMixin:
    action_label = None
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        meta = self.model._meta
        ctx["model_verbose"] = meta.verbose_name.title()
        ctx["model_verbose_plural"] = meta.verbose_name_plural.title()
        ctx["action_label"] = self.action_label or ("Create" if isinstance(self, CreateView) else "Edit")
        return ctx

# ---------- List with search ----------
class PatronList(ListView):
    model = Patron
    template_name = "library/patron_list.html"
    context_object_name = "rows"

    def get_queryset(self):
        qs = super().get_queryset().select_related("category")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(
                models.Q(external_id__icontains=q) |
                models.Q(first_name__icontains=q)  |
                models.Q(last_name__icontains=q)   |
                models.Q(email__icontains=q)       |
                models.Q(category__code__icontains=q)
            )
        return qs

# ---------- CRUD ----------
class PatronCreate(ModelTitleContextMixin, CreateView):
    model = Patron
    form_class = PatronForm
    template_name = "library/form.html"
    success_url = reverse_lazy("patron_list")
    action_label = "Create"

class PatronUpdate(ModelTitleContextMixin, UpdateView):
    model = Patron
    form_class = PatronForm
    template_name = "library/form.html"
    success_url = reverse_lazy("patron_list")
    pk_url_kwarg = "pk"
    action_label = "Edit"

class PatronDelete(DeleteView):
    model = Patron
    template_name = "library/confirm_delete.html"
    success_url = reverse_lazy("patron_list")
    pk_url_kwarg = "pk"

# ---------- CSV helpers ----------
def parse_date_flexible(s: str):
    s = (s or "").strip()
    if not s or s.lower() in {"none", "null"}:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Invalid date '{s}'. Use YYYY-MM-DD or DD/MM/YYYY or MM/DD/YYYY.")

# ---------- Bulk Import ----------
class PatronBulkImport(FormView):
    template_name = "library/patron_import.html"
    form_class = PatronCSVUploadForm
    success_url = reverse_lazy("patron_list")

    def form_valid(self, form):
        file = form.cleaned_data["file"]
        update_existing = form.cleaned_data["update_existing"]

        wrapped = TextIOWrapper(file, encoding="utf-8", newline="")
        reader = csv.DictReader(wrapped)

        required = {"external_id", "first_name", "last_name", "email", "category_code", "expires_at", "is_active"}
        missing = required - set([h.strip() for h in (reader.fieldnames or [])])
        results = {"created": 0, "updated": 0, "skipped": 0, "errors": []}

        if missing:
            results["errors"].append(f"Missing columns: {', '.join(sorted(missing))}")
            return render(self.request, self.template_name, {"form": form, "results": results})

        with transaction.atomic():
            for i, row in enumerate(reader, start=2):
                try:
                    ext_id = (row.get("external_id") or "").strip()
                    if not ext_id:
                        raise ValueError("external_id is required")

                    cat_code = (row.get("category_code") or "").strip()
                    try:
                        category = Patron_Categories.objects.get(code=cat_code)
                    except Patron_Categories.DoesNotExist:
                        raise ValueError(f"category_code '{cat_code}' not found")

                    def norm_bool(v):
                        return str(v).strip().lower() in {"1", "true", "yes", "y", "t"}

                    payload = {
                        "first_name": (row.get("first_name") or "").strip(),
                        "last_name":  (row.get("last_name") or "").strip(),
                        "email":      (row.get("email") or "").strip(),
                        "category":   category,
                        "expires_at": parse_date_flexible(row.get("expires_at")),
                        "is_active":  norm_bool(row.get("is_active", "true")),
                    }

                    if update_existing and Patron.objects.filter(external_id=ext_id).exists():
                        Patron.objects.filter(external_id=ext_id).update(**payload)
                        results["updated"] += 1
                    else:
                        Patron.objects.create(external_id=ext_id, **payload)
                        results["created"] += 1

                except Exception as e:
                    results["skipped"] += 1
                    results["errors"].append(f"Row {i}: {e}")

        # fresh form after import
        return render(self.request, self.template_name, {"form": self.form_class(), "results": results})

# ---------- Downloadable CSV template ----------
def patron_csv_template(_request):
    """
    Sends a small CSV with headers + sample rows to guide users.
    """
    rows = [
        ["external_id","first_name","last_name","email","category_code","expires_at","is_active"],
        ["S1001","Sake","Dorji","sake@example.com","STU","2026-12-31","true"],
        ["T2001","Sonam","Tobgay","sonam.t@example.com","STA","2026-12-31","true"]
    ]
    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = 'attachment; filename="patrons_template.csv"'
    w = csv.writer(resp)
    for r in rows:
        w.writerow(r)
    return resp

# Cateloguing Module

# --- small mixin from before (safe headings) ---
class ModelTitleContextMixin:
    action_label = None
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        m = self.model._meta
        ctx["model_verbose"] = m.verbose_name.title()
        ctx["model_verbose_plural"] = m.verbose_name_plural.title()
        ctx["action_label"] = self.action_label or ("Create" if isinstance(self, CreateView) else "Edit")
        return ctx

# ---------------- Biblios ----------------

class BiblioList(ListView):
    model = Biblio
    template_name = "library/biblio_list.html"
    context_object_name = "rows"

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(
                models.Q(title__icontains=q) |
                models.Q(author__icontains=q) |
                models.Q(isbn__icontains=q) |
                models.Q(publisher__icontains=q)
            )
        return qs

class BiblioCreate(ModelTitleContextMixin, CreateView):
    model = Biblio
    form_class = BiblioForm
    template_name = "library/form.html"
    success_url = reverse_lazy("biblio_list")
    action_label = "Create"

class BiblioUpdate(ModelTitleContextMixin, UpdateView):
    model = Biblio
    form_class = BiblioForm
    template_name = "library/form.html"
    success_url = reverse_lazy("biblio_list")
    pk_url_kwarg = "pk"
    action_label = "Edit"

class BiblioDelete(DeleteView):
    model = Biblio
    template_name = "library/confirm_delete.html"
    success_url = reverse_lazy("biblio_list")
    pk_url_kwarg = "pk"

# ---- Biblios bulk import ----

class BiblioImportFormView(FormView):
    template_name = "library/biblio_import.html"
    success_url = reverse_lazy("biblio_list")

    class DummyForm(forms.Form):
        file = forms.FileField(help_text="CSV: title,author,isbn,publisher,publication_year,attributes_json")

    form_class = DummyForm

    def form_valid(self, form):
        wrapped = TextIOWrapper(form.cleaned_data["file"], encoding="utf-8", newline="")
        reader = csv.DictReader(wrapped)
        required = {"title","author","isbn","publisher","publication_year","attributes_json"}
        missing = required - set([h.strip() for h in (reader.fieldnames or [])])

        results = {"created":0, "updated":0, "skipped":0, "errors":[]}
        if missing:
            results["errors"].append(f"Missing columns: {', '.join(sorted(missing))}")
            return render(self.request, self.template_name, {"form": self.form_class(), "results": results})

        with transaction.atomic():
            for line, row in enumerate(reader, start=2):
                try:
                    title = (row.get("title") or "").strip()
                    if not title:
                        raise ValueError("title is required")

                    isbn = (row.get("isbn") or "").strip() or None
                    attrs_raw = (row.get("attributes_json") or "").strip()
                    attrs = {}
                    if attrs_raw:
                        import json
                        attrs = json.loads(attrs_raw)

                    payload = {
                        "title": title,
                        "author": (row.get("author") or "").strip(),
                        "isbn": isbn,
                        "publisher": (row.get("publisher") or "").strip(),
                        "publication_year": int(row.get("publication_year") or 0) or None,
                        "attributes": attrs,
                    }

                    if isbn and Biblio.objects.filter(isbn=isbn).exists():
                        Biblio.objects.filter(isbn=isbn).update(**payload)
                        results["updated"] += 1
                    else:
                        Biblio.objects.create(**payload)
                        results["created"] += 1

                except Exception as e:
                    results["skipped"] += 1
                    results["errors"].append(f"Row {line}: {e}")

        return render(self.request, self.template_name, {"form": self.form_class(), "results": results})

def biblio_csv_template(_request):
    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = 'attachment; filename="biblios_template.csv"'
    w = csv.writer(resp)
    w.writerow(["title","author","isbn","publisher","publication_year","attributes_json"])
    w.writerow(["Fundamentals of OS","Silberschatz","9780470128725","Wiley","2010",'{"pages": 950, "language": "en"}'])
    w.writerow(["Modern Bhutan","-","","RUB Press","2022",'{"language": "dz"}'])
    return resp

# ---------------- Items ----------------

class ItemList(ListView):
    model = Item
    template_name = "library/item_list.html"
    context_object_name = "rows"

    def get_queryset(self):
        qs = super().get_queryset().select_related("biblio","item_type","branch")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(
                models.Q(accession_number__icontains=q) |
                models.Q(barcode__icontains=q) |
                models.Q(biblio__title__icontains=q) |
                models.Q(item_type__code__icontains=q) |
                models.Q(branch__code__icontains=q)
            )
        return qs

class ItemCreate(ModelTitleContextMixin, CreateView):
    model = Item
    form_class = ItemForm
    template_name = "library/form.html"
    success_url = reverse_lazy("item_list")
    action_label = "Create"

class ItemUpdate(ModelTitleContextMixin, UpdateView):
    model = Item
    form_class = ItemForm
    template_name = "library/form.html"
    success_url = reverse_lazy("item_list")
    pk_url_kwarg = "pk"
    action_label = "Edit"

class ItemDelete(DeleteView):
    model = Item
    template_name = "library/confirm_delete.html"
    success_url = reverse_lazy("item_list")
    pk_url_kwarg = "pk"

# ---- Items bulk import ----

class ItemImportFormView(FormView):
    template_name = "library/item_import.html"
    success_url = reverse_lazy("item_list")

    class DummyForm(forms.Form):
        file = forms.FileField(help_text="CSV: accession_number,barcode,isbn_or_biblio_id,item_type_code,branch_code,status")
        isbn_priority = forms.BooleanField(required=False, initial=True,
                 help_text="If true, try mapping by ISBN to biblio; else use biblio_id column.")
    form_class = DummyForm

    def form_valid(self, form):
        wrapped = TextIOWrapper(form.cleaned_data["file"], encoding="utf-8", newline="")
        reader = csv.DictReader(wrapped)

        required = {"accession_number","barcode","isbn_or_biblio_id","item_type_code","branch_code","status"}
        missing = required - set([h.strip() for h in (reader.fieldnames or [])])
        results = {"created":0, "updated":0, "skipped":0, "errors":[]}

        if missing:
            results["errors"].append(f"Missing columns: {', '.join(sorted(missing))}")
            return render(self.request, self.template_name, {"form": self.form_class(), "results": results})

        use_isbn = form.cleaned_data.get("isbn_priority", True)

        with transaction.atomic():
            for line, row in enumerate(reader, start=2):
                try:
                    acc = (row.get("accession_number") or "").strip()
                    if not acc:
                        raise ValueError("accession_number is required")

                    # resolve biblio
                    bib_ref = (row.get("isbn_or_biblio_id") or "").strip()
                    if use_isbn and bib_ref:
                        bib = Biblio.objects.filter(isbn=bib_ref or None).first()
                        if not bib:
                            raise ValueError(f"No Biblio with ISBN '{bib_ref}'")
                    else:
                        if not bib_ref:
                            raise ValueError("isbn_or_biblio_id is required")
                        bib = Biblio.objects.filter(pk=int(bib_ref)).first()
                        if not bib:
                            raise ValueError(f"No Biblio id={bib_ref}")

                    # resolve item_type & branch
                    it_code = (row.get("item_type_code") or "").strip()
                    br_code = (row.get("branch_code") or "").strip()
                    try:
                        it = ItemType.objects.get(code=it_code)
                    except ItemType.DoesNotExist:
                        raise ValueError(f"item_type_code '{it_code}' not found")
                    try:
                        br = Branch.objects.get(code=br_code)
                    except Branch.DoesNotExist:
                        raise ValueError(f"branch_code '{br_code}' not found")

                    status = (row.get("status") or "AVAILABLE").strip().upper()
                    if status not in dict(Item.Status.choices):
                        raise ValueError(f"invalid status '{status}'")

                    payload = dict(biblio=bib, barcode=(row.get("barcode") or "").strip(),
                                   item_type=it, branch=br, status=status)

                    if Item.objects.filter(accession_number=acc).exists():
                        Item.objects.filter(accession_number=acc).update(**payload)
                        results["updated"] += 1
                    else:
                        Item.objects.create(accession_number=acc, **payload)
                        results["created"] += 1

                except Exception as e:
                    results["skipped"] += 1
                    results["errors"].append(f"Row {line}: {e}")

        return render(self.request, self.template_name, {"form": self.form_class(), "results": results})

def item_csv_template(_request):
    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = 'attachment; filename="items_template.csv"'
    w = csv.writer(resp)
    w.writerow(["accession_number","barcode","isbn_or_biblio_id","item_type_code","branch_code","status"])
    w.writerow(["ACC-0001","BC-001","9780470128725","BOOK","CST","AVAILABLE"])
    w.writerow(["ACC-0002","BC-002","9780470128725","BOOK","CST","AVAILABLE"])
    w.writerow(["ACC-0100","BC-0100","2","DVD","MAIN","LOST"])  # example by biblio_id
    return resp

class ItemDetail(DetailView):
    model = Item
    template_name = "library/item_detail.html"
    pk_url_kwarg = "pk"

    # JOIN related tables for one efficient query
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("biblio", "item_type", "branch")
        )

#Circulations Module
# ---- Rules CRUD (reuse your generic form.html / confirm_delete.html) ----

class IssuingRuleList(ListView):
    model = IssuingRule
    template_name = "library/rule_list.html"
    context_object_name = "rows"

    def get_queryset(self):
        qs = super().get_queryset().select_related("patron_category", "item_type")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(
                models.Q(patron_category__code__icontains=q) |
                models.Q(item_type__code__icontains=q)
            )
        return qs

class IssuingRuleCreate(CreateView):
    model = IssuingRule
    fields = ["patron_category", "item_type", "loan_days", "daily_fine", "max_fine", "renewal_allowed", "max_renewals"]
    template_name = "library/form.html"
    success_url = reverse_lazy("rule_list")

class IssuingRuleUpdate(UpdateView):
    model = IssuingRule
    fields = ["patron_category", "item_type", "loan_days", "daily_fine", "max_fine", "renewal_allowed", "max_renewals"]
    template_name = "library/form.html"
    success_url = reverse_lazy("rule_list")
    pk_url_kwarg = "pk"

class IssuingRuleDelete(DeleteView):
    model = IssuingRule
    template_name = "library/confirm_delete.html"
    success_url = reverse_lazy("rule_list")
    pk_url_kwarg = "pk"


# ---- Circulation dashboard (Checkout / Check-in / Renew) ----

def circulation_dashboard(request):
    q = request.GET.get("q", "").strip()
    filter_type = request.GET.get("filter", "all")

    loans = (
        Loan.objects
        .select_related("patron", "item", "item__biblio")
        .order_by("-issued_at")
    )

    if q:
        loans = loans.filter(
            Q(patron__external_id__icontains=q)
            | Q(patron__first_name__icontains=q)
            | Q(patron__last_name__icontains=q)
            | Q(item__accession_number__icontains=q)
            | Q(item__biblio__title__icontains=q)
        )

    if filter_type == "checkedout":
        loans = loans.filter(return_date__isnull=True)
    elif filter_type == "checkedin":
        loans = loans.filter(return_date__isnull=False)
    elif filter_type == "renewed":
        loans = loans.filter(renewal_count__gt=0)

    return render(request, "library/circulation_dashboard.html", {
        "loans": loans[:50],  # limit display
        "q": q,
        "filter": filter_type,
    })

class CheckoutView(FormView):
    template_name = "library/checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("checkout")

    def form_valid(self, form):
        patron = form.cleaned_data["patron"]
        item = form.cleaned_data["item"]
        try:
            loan = svc_checkout(patron, item)
            messages.success(self.request, f"Checked out {item.accession_number} to {patron.external_id}. Due: {loan.due_at:%Y-%m-%d %H:%M}.")
        except Exception as e:
            messages.error(self.request, f"Checkout failed: {e}")
        return redirect(self.success_url)

class CheckinView(FormView):
    template_name = "library/checkin.html"
    form_class = CheckinForm
    success_url = reverse_lazy("checkin")

    def form_valid(self, form):
        loan = form.cleaned_data["loan"]
        try:
            svc_checkin(loan)
            messages.success(self.request, f"Checked in {loan.item.accession_number} from {loan.patron.external_id}.")
        except Exception as e:
            messages.error(self.request, f"Check-in failed: {e}")
        return redirect(self.success_url)

class RenewView(FormView):
    template_name = "library/renew.html"
    form_class = RenewForm
    success_url = reverse_lazy("renew")

    def form_valid(self, form):
        loan = form.cleaned_data["loan"]
        try:
            svc_renew(loan)
            messages.success(self.request, f"Renewed. New due date: {loan.due_at:%Y-%m-%d %H:%M} (renewals: {loan.renewal_count}).")
        except Exception as e:
            messages.error(self.request, f"Renew failed: {e}")
        return redirect(self.success_url)
