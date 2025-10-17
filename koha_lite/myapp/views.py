import csv
from datetime import datetime
from io import TextIOWrapper
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView,FormView
from .models import *
from .forms import *
from django.db import models, transaction

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