from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from myapp.models import (
    Branch, ItemType, Patron_Categories, Patron, Biblio, Item,
    IssuingRule, Loan, Fine
)

class TestViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Core reference data
        cls.branch = Branch.objects.create(code="MAIN", name="Main Branch")
        cls.itemtype = ItemType.objects.create(code="BOOK", name="Book")
        cls.pcat = Patron_Categories.objects.create(code="STU", name="Student")
        cls.pcat_staff = Patron_Categories.objects.create(code="STA", name="Staff")

        # Patron + Biblio + Item
        cls.patron = Patron.objects.create(
            external_id="S0001", first_name="A", last_name="B",
            email="a@example.com", category=cls.pcat
        )
        cls.biblio = Biblio.objects.create(
            title="Test Book", author="Anon", isbn="9780470128725",
            publisher="Wiley", publication_year=2010
        )
        cls.item = Item.objects.create(
            biblio=cls.biblio, accession_number="ACC-0001",
            barcode="BC-0001", item_type=cls.itemtype, branch=cls.branch
        )

        # Issuing rule required by circulation services
        cls.rule = IssuingRule.objects.create(
            patron_category=cls.pcat, item_type=cls.itemtype,
            loan_days=7, daily_fine="1.50", max_fine="50.00",
            renewal_allowed=True, max_renewals=2
        )

        # A fine to exercise fine views
        cls.loan = Loan.objects.create(
            patron=cls.patron, item=cls.item,
            issued_at=timezone.now(),
            due_at=timezone.now() + timezone.timedelta(days=7)
        )
        cls.fine = Fine.objects.create(
            patron=cls.patron, loan=cls.loan, item=cls.item,
            fine_type=Fine.OVERDUE, amount="10.00", paid_amount="0.00"
        )

    def setUp(self):
        self.client = Client()

    # --- Dashboard ---
    def test_admin_dashboard_GET(self):
        resp = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "library/admin_dashboard.html")

    # --- Branch ---
    def test_branch_list_GET(self):
        resp = self.client.get(reverse("branch_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "library/branch_list.html")

    def test_branch_create_POST(self):
        resp = self.client.post(reverse("branch_create"), {"code": "CST", "name": "CST Library"})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Branch.objects.filter(code="CST").exists())

    def test_branch_update_POST(self):
        url = reverse("branch_update", args=[self.branch.code])
        resp = self.client.post(url, {"code": "MAIN", "name": "Main Branch Updated"})
        self.assertEqual(resp.status_code, 302)
        self.branch.refresh_from_db()
        self.assertEqual(self.branch.name, "Main Branch Updated")

    def test_branch_delete_POST(self):
        b = Branch.objects.create(code="TEMP", name="Temp")
        url = reverse("branch_delete", args=[b.code])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Branch.objects.filter(code="TEMP").exists())

    # --- ItemType ---
    def test_itemtype_list_GET(self):
        resp = self.client.get(reverse("itemtype_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "library/itemtype_list.html")

    def test_itemtype_create_POST(self):
        resp = self.client.post(reverse("itemtype_create"), {"code": "DVD", "name": "DVD"})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(ItemType.objects.filter(code="DVD").exists())

    def test_itemtype_update_POST(self):
        url = reverse("itemtype_update", args=[self.itemtype.code])
        resp = self.client.post(url, {"code": "BOOK", "name": "Book Updated"})
        self.assertEqual(resp.status_code, 302)
        self.itemtype.refresh_from_db()
        self.assertEqual(self.itemtype.name, "Book Updated")

    def test_itemtype_delete_POST(self):
        it = ItemType.objects.create(code="MAG", name="Magazine")
        url = reverse("itemtype_delete", args=[it.code])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(ItemType.objects.filter(code="MAG").exists())

    # --- Patron Categories ---
    def test_patroncat_list_GET(self):
        resp = self.client.get(reverse("patroncat_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "library/patroncat_list.html")

    def test_patroncat_create_POST(self):
        resp = self.client.post(reverse("patroncat_create"), {"code": "GUEST", "name": "Guest"})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Patron_Categories.objects.filter(code="GUEST").exists())

    def test_patroncat_update_POST(self):
        url = reverse("patroncat_update", args=[self.pcat.code])
        resp = self.client.post(url, {"code": "STU", "name": "Student Updated"})
        self.assertEqual(resp.status_code, 302)
        self.pcat.refresh_from_db()
        self.assertEqual(self.pcat.name, "Student Updated")

    def test_patroncat_delete_POST(self):
        pc = Patron_Categories.objects.create(code="TMP", name="Tmp")
        url = reverse("patroncat_delete", args=[pc.code])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Patron_Categories.objects.filter(code="TMP").exists())

    # --- Patron CRUD + List ---
    def test_patron_list_GET(self):
        resp = self.client.get(reverse("patron_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "library/patron_list.html")

    def test_patron_create_POST(self):
        data = {
            "external_id": "S0002",
            "first_name": "C",
            "last_name": "D",
            "email": "c@example.com",
            "category": self.pcat.pk,
            "expires_at": "",
            "is_active": True,
        }
        resp = self.client.post(reverse("patron_create"), data)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Patron.objects.filter(external_id="S0002").exists())

    def test_patron_update_POST(self):
        url = reverse("patron_update", args=[self.patron.pk])
        data = {
            "external_id": "S0001",
            "first_name": "AA",
            "last_name": "B",
            "email": "a@example.com",
            "category": self.pcat.pk,
            "expires_at": "",
            "is_active": True,
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 302)
        self.patron.refresh_from_db()
        self.assertEqual(self.patron.first_name, "AA")

    def test_patron_delete_POST(self):
        p = Patron.objects.create(
            external_id="S9999", first_name="X", last_name="Y",
            email="x@example.com", category=self.pcat
        )
        url = reverse("patron_delete", args=[p.pk])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Patron.objects.filter(external_id="S9999").exists())

    # --- Patron CSV Template + Import ---
    def test_patron_csv_template_GET(self):
        resp = self.client.get(reverse("patron_csv_template"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "text/csv")

    def test_patron_import_POST(self):
        csv_bytes = (
            b"external_id,first_name,last_name,email,category_code,expires_at,is_active\n"
            b"S2000,Sonam,Tobgay,sonam.t@example.com,STA,2026-12-31,true\n"
        )
        upload = SimpleUploadedFile("patrons.csv", csv_bytes, content_type="text/csv")
        resp = self.client.post(reverse("patron_import"), {"file": upload, "update_existing": "on"})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Patron.objects.filter(external_id="S2000").exists())

    # --- Biblio CRUD + List + Import + Template ---
    def test_biblio_list_GET(self):
        resp = self.client.get(reverse("biblio_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "library/biblio_list.html")

    def test_biblio_create_POST(self):
        data = {
            "title": "New Book",
            "author": "Auth",
            "isbn": "1112223334445",
            "publisher": "Pub",
            "publication_year": 2022,
            "attributes": "{}",
        }
        resp = self.client.post(reverse("biblio_create"), data)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Biblio.objects.filter(title="New Book").exists())

    def test_biblio_update_POST(self):
        url = reverse("biblio_update", args=[self.biblio.pk])
        data = {
            "title": "Test Book Updated",
            "author": "Anon",
            "isbn": "9780470128725",
            "publisher": "Wiley",
            "publication_year": 2010,
            "attributes": "{}",
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 302)
        self.biblio.refresh_from_db()
        self.assertEqual(self.biblio.title, "Test Book Updated")

    def test_biblio_delete_POST(self):
        b = Biblio.objects.create(title="Temp Biblio")
        url = reverse("biblio_delete", args=[b.pk])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Biblio.objects.filter(pk=b.pk).exists())

    def test_biblio_csv_template_GET(self):
        resp = self.client.get(reverse("biblio_csv_template"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "text/csv")

    def test_biblio_import_POST(self):
        csv_bytes = (
            b"title,author,isbn,publisher,publication_year,attributes_json\n"
            b"Fundamentals of OS,Silberschatz,9998887776665,Wiley,2010,{\"pages\":950}\n"
        )
        upload = SimpleUploadedFile("biblios.csv", csv_bytes, content_type="text/csv")
        resp = self.client.post(reverse("biblio_import"), {"file": upload})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Biblio.objects.filter(isbn="9998887776665").exists())

    # --- Item CRUD + List + Detail + Import + Template ---
    def test_item_list_GET(self):
        resp = self.client.get(reverse("item_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "library/item_list.html")

    def test_item_create_POST(self):
        data = {
            "biblio": self.biblio.pk,
            "accession_number": "ACC-0002",
            "barcode": "BC-0002",
            "item_type": self.itemtype.pk,
            "branch": self.branch.pk,
            "status": "AVAILABLE",
        }
        resp = self.client.post(reverse("item_create"), data)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Item.objects.filter(accession_number="ACC-0002").exists())

    def test_item_update_POST(self):
        url = reverse("item_update", args=[self.item.pk])
        data = {
            "biblio": self.biblio.pk,
            "accession_number": "ACC-0001",
            "barcode": "BC-0001X",
            "item_type": self.itemtype.pk,
            "branch": self.branch.pk,
            "status": "AVAILABLE",
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 302)
        self.item.refresh_from_db()
        self.assertEqual(self.item.barcode, "BC-0001X")

    def test_item_delete_POST(self):
        it = Item.objects.create(
            biblio=self.biblio, accession_number="ACC-9999",
            barcode="BC-9999", item_type=self.itemtype, branch=self.branch
        )
        url = reverse("item_delete", args=[it.pk])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Item.objects.filter(pk=it.pk).exists())

    def test_item_detail_GET(self):
        url = reverse("item_detail", args=[self.item.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "library/item_detail.html")

    def test_item_csv_template_GET(self):
        resp = self.client.get(reverse("item_csv_template"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "text/csv")

    def test_item_import_POST(self):
        # Import by ISBN mapping (isbn_priority on)
        csv_bytes = (
            b"accession_number,barcode,isbn_or_biblio_id,item_type_code,branch_code,status\n"
            b"ACC-0100,BC-0100,9780470128725,BOOK,MAIN,AVAILABLE\n"
        )
        upload = SimpleUploadedFile("items.csv", csv_bytes, content_type="text/csv")
        resp = self.client.post(reverse("item_import"), {"file": upload, "isbn_priority": "on"})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Item.objects.filter(accession_number="ACC-0100").exists())

    # --- Rules (IssuingRule) CRUD + List ---
    def test_rule_list_GET(self):
        resp = self.client.get(reverse("rule_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "library/rule_list.html")

    def test_rule_create_POST(self):
        resp = self.client.post(
            reverse("rule_create"),
            {
                "patron_category": self.pcat_staff.pk,
                "item_type": self.itemtype.pk,
                "loan_days": 14,
                "daily_fine": "2.00",
                "max_fine": "100.00",
                "renewal_allowed": True,
                "max_renewals": 3,
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(IssuingRule.objects.filter(patron_category=self.pcat_staff, item_type=self.itemtype).exists())

    def test_rule_update_POST(self):
        url = reverse("rule_update", args=[self.rule.pk])
        resp = self.client.post(
            url,
            {
                "patron_category": self.pcat.pk,
                "item_type": self.itemtype.pk,
                "loan_days": 10,
                "daily_fine": "1.50",
                "max_fine": "50.00",
                "renewal_allowed": True,
                "max_renewals": 2,
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.rule.refresh_from_db()
        self.assertEqual(self.rule.loan_days, 10)

    def test_rule_delete_POST(self):
        r = IssuingRule.objects.create(
            patron_category=self.pcat_staff, item_type=self.itemtype,
            loan_days=5, daily_fine="1.00", max_fine="20.00",
            renewal_allowed=False, max_renewals=0
        )
        url = reverse("rule_delete", args=[r.pk])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(IssuingRule.objects.filter(pk=r.pk).exists())

    # --- Circulation dashboard + actions ---
    def test_circ_dashboard_GET(self):
        resp = self.client.get(reverse("circ_dashboard"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "library/circulation_dashboard.html")

    def test_checkout_POST(self):
        # Ensure item is available
        self.item.refresh_from_db()
        url = reverse("checkout")
        resp = self.client.post(url, {"patron": self.patron.pk, "item": self.item.pk})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Loan.objects.filter(item=self.item, return_date__isnull=True).exists())

    def test_renew_POST(self):
        # Make sure a live loan exists (from setUpTestData)
        url = reverse("renew")
        resp = self.client.post(url, {"loan": self.loan.pk})
        self.assertEqual(resp.status_code, 302)
        self.loan.refresh_from_db()
        self.assertGreaterEqual(self.loan.renewal_count, 1)

    def test_checkin_POST(self):
        # Ensure a live loan exists; then check it in
        url = reverse("checkin")
        resp = self.client.post(url, {"loan": self.loan.pk})
        self.assertEqual(resp.status_code, 302)
        self.loan.refresh_from_db()
        self.assertIsNotNone(self.loan.return_date)

    # --- Fines list/detail/pay ---
    def test_fine_list_GET(self):
        resp = self.client.get(reverse("fine_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "library/fine_list.html")

    def test_fine_detail_GET(self):
        url = reverse("fine_detail", args=[self.fine.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "library/fine_detail.html")

    def test_fine_pay_POST(self):
        url = reverse("fine_pay", args=[self.fine.pk])
        resp = self.client.post(url, {"amount": "3.00"})
        self.assertEqual(resp.status_code, 302)
        self.fine.refresh_from_db()
        self.assertEqual(str(self.fine.paid_amount), "3.00")
