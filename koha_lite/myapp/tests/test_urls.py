from django.test import SimpleTestCase
from django.urls import reverse, resolve
from myapp import views

class TestUrls(SimpleTestCase):

    # --- Dashboard ---
    def test_admin_url_is_resolved(self):
        url = reverse("admin_dashboard")
        self.assertEqual(resolve(url).func, views.admin_dashboard)

    # --- Branch ---
    def test_branch_list_url(self):
        url = reverse("branch_list")
        self.assertEqual(resolve(url).func.view_class, views.BranchList)

    def test_branch_create_url(self):
        url = reverse("branch_create")
        self.assertEqual(resolve(url).func.view_class, views.BranchCreate)

    def test_branch_update_url(self):
        url = reverse("branch_update", args=["B001"])
        self.assertEqual(resolve(url).func.view_class, views.BranchUpdate)

    def test_branch_delete_url(self):
        url = reverse("branch_delete", args=["B001"])
        self.assertEqual(resolve(url).func.view_class, views.BranchDelete)

    # --- ItemType ---
    def test_itemtype_list_url(self):
        url = reverse("itemtype_list")
        self.assertEqual(resolve(url).func.view_class, views.ItemTypeList)

    def test_itemtype_create_url(self):
        url = reverse("itemtype_create")
        self.assertEqual(resolve(url).func.view_class, views.ItemTypeCreate)

    def test_itemtype_update_url(self):
        url = reverse("itemtype_update", args=["BOOK"])
        self.assertEqual(resolve(url).func.view_class, views.ItemTypeUpdate)

    def test_itemtype_delete_url(self):
        url = reverse("itemtype_delete", args=["BOOK"])
        self.assertEqual(resolve(url).func.view_class, views.ItemTypeDelete)

    # --- Patron Categories ---
    def test_patroncat_list_url(self):
        url = reverse("patroncat_list")
        self.assertEqual(resolve(url).func.view_class, views.PatronCategoryList)

    def test_patroncat_create_url(self):
        url = reverse("patroncat_create")
        self.assertEqual(resolve(url).func.view_class, views.PatronCategoryCreate)

    def test_patroncat_update_url(self):
        url = reverse("patroncat_update", args=["STU"])
        self.assertEqual(resolve(url).func.view_class, views.PatronCategoryUpdate)

    def test_patroncat_delete_url(self):
        url = reverse("patroncat_delete", args=["STU"])
        self.assertEqual(resolve(url).func.view_class, views.PatronCategoryDelete)

    # --- Patrons ---
    def test_patron_list_url(self):
        url = reverse("patron_list")
        self.assertEqual(resolve(url).func.view_class, views.PatronList)

    def test_patron_create_url(self):
        url = reverse("patron_create")
        self.assertEqual(resolve(url).func.view_class, views.PatronCreate)

    def test_patron_update_url(self):
        url = reverse("patron_update", args=[1])
        self.assertEqual(resolve(url).func.view_class, views.PatronUpdate)

    def test_patron_delete_url(self):
        url = reverse("patron_delete", args=[1])
        self.assertEqual(resolve(url).func.view_class, views.PatronDelete)

    def test_patron_import_url(self):
        url = reverse("patron_import")
        self.assertEqual(resolve(url).func.view_class, views.PatronBulkImport)

    def test_patron_csv_template_url(self):
        url = reverse("patron_csv_template")
        self.assertEqual(resolve(url).func, views.patron_csv_template)

    # --- Biblios ---
    def test_biblio_list_url(self):
        url = reverse("biblio_list")
        self.assertEqual(resolve(url).func.view_class, views.BiblioList)

    def test_biblio_create_url(self):
        url = reverse("biblio_create")
        self.assertEqual(resolve(url).func.view_class, views.BiblioCreate)

    def test_biblio_update_url(self):
        url = reverse("biblio_update", args=[1])
        self.assertEqual(resolve(url).func.view_class, views.BiblioUpdate)

    def test_biblio_delete_url(self):
        url = reverse("biblio_delete", args=[1])
        self.assertEqual(resolve(url).func.view_class, views.BiblioDelete)

    def test_biblio_import_url(self):
        url = reverse("biblio_import")
        self.assertEqual(resolve(url).func.view_class, views.BiblioImportFormView)

    def test_biblio_csv_template_url(self):
        url = reverse("biblio_csv_template")
        self.assertEqual(resolve(url).func, views.biblio_csv_template)

    # --- Items ---
    def test_item_list_url(self):
        url = reverse("item_list")
        self.assertEqual(resolve(url).func.view_class, views.ItemList)

    def test_item_create_url(self):
        url = reverse("item_create")
        self.assertEqual(resolve(url).func.view_class, views.ItemCreate)

    def test_item_update_url(self):
        url = reverse("item_update", args=[1])
        self.assertEqual(resolve(url).func.view_class, views.ItemUpdate)

    def test_item_delete_url(self):
        url = reverse("item_delete", args=[1])
        self.assertEqual(resolve(url).func.view_class, views.ItemDelete)

    def test_item_import_url(self):
        url = reverse("item_import")
        self.assertEqual(resolve(url).func.view_class, views.ItemImportFormView)

    def test_item_csv_template_url(self):
        url = reverse("item_csv_template")
        self.assertEqual(resolve(url).func, views.item_csv_template)

    def test_item_detail_url(self):
        url = reverse("item_detail", args=[1])
        self.assertEqual(resolve(url).func.view_class, views.ItemDetail)

    # --- Issuing Rules ---
    def test_rule_list_url(self):
        url = reverse("rule_list")
        self.assertEqual(resolve(url).func.view_class, views.IssuingRuleList)

    def test_rule_create_url(self):
        url = reverse("rule_create")
        self.assertEqual(resolve(url).func.view_class, views.IssuingRuleCreate)

    def test_rule_update_url(self):
        url = reverse("rule_update", args=[1])
        self.assertEqual(resolve(url).func.view_class, views.IssuingRuleUpdate)

    def test_rule_delete_url(self):
        url = reverse("rule_delete", args=[1])
        self.assertEqual(resolve(url).func.view_class, views.IssuingRuleDelete)

    # --- Circulation ---
    def test_circ_dashboard_url(self):
        url = reverse("circ_dashboard")
        self.assertEqual(resolve(url).func, views.circulation_dashboard)

    def test_checkout_url(self):
        url = reverse("checkout")
        self.assertEqual(resolve(url).func.view_class, views.CheckoutView)

    def test_checkin_url(self):
        url = reverse("checkin")
        self.assertEqual(resolve(url).func.view_class, views.CheckinView)

    def test_renew_url(self):
        url = reverse("renew")
        self.assertEqual(resolve(url).func.view_class, views.RenewView)

    # --- Fines ---
    def test_fine_list_url(self):
        url = reverse("fine_list")
        self.assertEqual(resolve(url).func.view_class, views.FineList)

    def test_fine_detail_url(self):
        url = reverse("fine_detail", args=[1])
        self.assertEqual(resolve(url).func.view_class, views.FineDetail)

    def test_fine_pay_url(self):
        url = reverse("fine_pay", args=[1])
        self.assertEqual(resolve(url).func.view_class, views.FinePayView)
