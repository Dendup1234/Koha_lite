from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path("", views.admin_dashboard, name="admin_dashboard"),

    # Branch
    path("branches/", views.BranchList.as_view(), name="branch_list"),
    path("branches/new/", views.BranchCreate.as_view(), name="branch_create"),
    path("branches/<str:code>/edit/", views.BranchUpdate.as_view(), name="branch_update"),
    path("branches/<str:code>/delete/", views.BranchDelete.as_view(), name="branch_delete"),

    # ItemType
    path("item-types/", views.ItemTypeList.as_view(), name="itemtype_list"),
    path("item-types/new/", views.ItemTypeCreate.as_view(), name="itemtype_create"),
    path("item-types/<str:code>/edit/", views.ItemTypeUpdate.as_view(), name="itemtype_update"),
    path("item-types/<str:code>/delete/", views.ItemTypeDelete.as_view(), name="itemtype_delete"),

    # Patron Categories
    path("patron-categories/", views.PatronCategoryList.as_view(), name="patroncat_list"),
    path("patron-categories/new/", views.PatronCategoryCreate.as_view(), name="patroncat_create"),
    path("patron-categories/<str:code>/edit/", views.PatronCategoryUpdate.as_view(), name="patroncat_update"),
    path("patron-categories/<str:code>/delete/", views.PatronCategoryDelete.as_view(), name="patroncat_delete"),

]