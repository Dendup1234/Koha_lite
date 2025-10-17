from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import *
from .forms import *

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
