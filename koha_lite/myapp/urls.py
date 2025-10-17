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

    #Patron Management
    # Patrons
    path("patrons/", views.PatronList.as_view(), name="patron_list"),
    path("patrons/new/", views.PatronCreate.as_view(), name="patron_create"),
    path("patrons/<int:pk>/edit/", views.PatronUpdate.as_view(), name="patron_update"),
    path("patrons/<int:pk>/delete/", views.PatronDelete.as_view(), name="patron_delete"),
    path("patrons/import/", views.PatronBulkImport.as_view(), name="patron_import"),
    path("patrons/template.csv", views.patron_csv_template, name="patron_csv_template"),
    
    #Cateloguing Module
    # Biblio
    path("biblios/", views.BiblioList.as_view(), name="biblio_list"),
    path("biblios/new/", views.BiblioCreate.as_view(), name="biblio_create"),
    path("biblios/<int:pk>/edit/", views.BiblioUpdate.as_view(), name="biblio_update"),
    path("biblios/<int:pk>/delete/", views.BiblioDelete.as_view(), name="biblio_delete"),
    path("biblios/import/", views.BiblioImportFormView.as_view(), name="biblio_import"),
    path("biblios/template.csv", views.biblio_csv_template, name="biblio_csv_template"),

    # Item
    path("items/", views.ItemList.as_view(), name="item_list"),
    path("items/new/", views.ItemCreate.as_view(), name="item_create"),
    path("items/<int:pk>/edit/", views.ItemUpdate.as_view(), name="item_update"),
    path("items/<int:pk>/delete/", views.ItemDelete.as_view(), name="item_delete"),
    path("items/import/", views.ItemImportFormView.as_view(), name="item_import"),
    path("items/template.csv", views.item_csv_template, name="item_csv_template"),
    path("items/<int:pk>/", views.ItemDetail.as_view(), name="item_detail"),

    #Circulation Module
    # Rules
    path("rules/", views.IssuingRuleList.as_view(), name="rule_list"),
    path("rules/new/", views.IssuingRuleCreate.as_view(), name="rule_create"),
    path("rules/<int:pk>/edit/", views.IssuingRuleUpdate.as_view(), name="rule_update"),
    path("rules/<int:pk>/delete/", views.IssuingRuleDelete.as_view(), name="rule_delete"),

    # Circulation actions
    path("circulation/", views.circulation_dashboard, name="circ_dashboard"),
    path("circulation/checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("circulation/checkin/", views.CheckinView.as_view(), name="checkin"),
    path("circulation/renew/", views.RenewView.as_view(), name="renew"),

]