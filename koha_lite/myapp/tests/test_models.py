from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from django.db.utils import IntegrityError

from myapp.models import (
    Branch, ItemType, Patron_Categories, Patron,
    Biblio, Item, IssuingRule, Loan, Fine
)


class TestModels(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Admin data
        cls.branch = Branch.objects.create(code="MAIN", name="Main Branch")
        cls.itemtype = ItemType.objects.create(code="BOOK", name="Book")
        cls.pcat_stu = Patron_Categories.objects.create(code="STU", name="Student")
        cls.pcat_sta = Patron_Categories.objects.create(code="STA", name="Staff")

        # Patron + Biblio + Item
        cls.patron = Patron.objects.create(
            external_id="S0001",
            first_name="Sake",
            last_name="Dorji",
            email="sake@example.com",
            category=cls.pcat_stu,
            is_active=True,
        )
        cls.biblio = Biblio.objects.create(
            title="Operating Systems",
            author="Silberschatz",
            isbn="9780470128725",
            publisher="Wiley",
            publication_year=2010,
            attributes={"pages": 950, "language": "en"},
        )
        cls.item = Item.objects.create(
            biblio=cls.biblio,
            accession_number="ACC-0001",
            barcode="BC-0001",
            item_type=cls.itemtype,
            branch=cls.branch,
            status=Item.Status.AVAILABLE,
        )

        # Rule needed for circulation
        cls.rule = IssuingRule.objects.create(
            patron_category=cls.pcat_stu, item_type=cls.itemtype,
            loan_days=7, daily_fine=Decimal("1.50"), max_fine=Decimal("50.00"),
            renewal_allowed=True, max_renewals=2
        )

    # ---------- Simple creation & __str__ ----------
    def test_branch_create_and_str(self):
        b = Branch.objects.create(code="CST", name="CST Library")
        self.assertEqual(str(b), "CST — CST Library")

    def test_itemtype_create_and_str(self):
        it = ItemType.objects.create(code="DVD", name="DVD")
        self.assertEqual(str(it), "DVD — DVD")

    def test_patron_category_create_and_str(self):
        pc = Patron_Categories.objects.create(code="GUEST", name="Guest")
        self.assertEqual(str(pc), "GUEST - Guest")

    def test_patron_create_and_str(self):
        self.assertIn("S0001 — Sake Dorji", str(self.patron))

    def test_biblio_create_and_str(self):
        self.assertEqual(str(self.biblio), "Operating Systems")

    def test_item_create_and_str(self):
        s = str(self.item)
        self.assertIn("ACC-0001", s)
        self.assertIn("Operating Systems", s)

    def test_issuingrule_str(self):
        s = str(self.rule)
        self.assertIn("STU", s)
        self.assertIn("BOOK", s)
        self.assertIn("7 days", s)

    # ---------- Uniques & constraints ----------
    def test_branch_code_primary_key_unique(self):
        with self.assertRaises(IntegrityError):
            Branch.objects.create(code="MAIN", name="Dup Main")

    def test_itemtype_code_primary_key_unique(self):
        with self.assertRaises(IntegrityError):
            ItemType.objects.create(code="BOOK", name="Duplicate")

    def test_patron_external_id_unique(self):
        with self.assertRaises(IntegrityError):
            Patron.objects.create(
                external_id="S0001", first_name="X", last_name="Y",
                email="", category=self.pcat_stu
            )

    def test_biblio_isbn_unique_allows_null(self):
        # Same ISBN should fail
        with self.assertRaises(IntegrityError):
            Biblio.objects.create(title="Another", isbn="9780470128725")
        # Null/blank allowed and not conflicting
        b2 = Biblio.objects.create(title="No ISBN", isbn=None)
        self.assertIsNone(b2.isbn)

    def test_item_accession_number_unique(self):
        with self.assertRaises(IntegrityError):
            Item.objects.create(
                biblio=self.biblio, accession_number="ACC-0001",
                barcode="BC-dup", item_type=self.itemtype, branch=self.branch
            )

    def test_issuingrule_unique_pair(self):
        with self.assertRaises(IntegrityError):
            IssuingRule.objects.create(
                patron_category=self.pcat_stu, item_type=self.itemtype,
                loan_days=14, daily_fine=1, max_fine=10
            )

    def test_unique_active_loan_per_item_constraint(self):
        # Create one active loan
        l1 = Loan.objects.create(
            patron=self.patron, item=self.item,
            issued_at=timezone.now(),
            due_at=timezone.now() + timezone.timedelta(days=7),
            return_date=None,
        )
        self.assertTrue(l1.is_active)
        # Second active loan for same item should fail (constraint)
        with self.assertRaises(IntegrityError):
            Loan.objects.create(
                patron=self.patron, item=self.item,
                issued_at=timezone.now(),
                due_at=timezone.now() + timezone.timedelta(days=7),
                return_date=None,
            )
        # Once returned, new active loan is allowed
        l1.return_date = timezone.now()
        l1.save()
        l2 = Loan.objects.create(
            patron=self.patron, item=self.item,
            issued_at=timezone.now(),
            due_at=timezone.now() + timezone.timedelta(days=7),
            return_date=None,
        )
        self.assertTrue(l2.is_active)

    def test_fine_unique_overdue_per_loan(self):
        f1 = Fine.objects.create(
            patron=self.patron, loan=self._make_active_loan(),
            item=self.item, fine_type=Fine.OVERDUE, amount=Decimal("5.00")
        )
        with self.assertRaises(IntegrityError):
            Fine.objects.create(
                patron=self.patron, loan=f1.loan,
                item=self.item, fine_type=Fine.OVERDUE, amount=Decimal("3.00")
            )

    # ---------- Properties / helpers ----------
    def test_patron_is_expired_property(self):
        today = timezone.localdate()
        p_today = Patron.objects.create(
            external_id="S0002", first_name="T", last_name="U",
            email="t@example.com", category=self.pcat_stu, expires_at=today
        )
        p_future = Patron.objects.create(
            external_id="S0003", first_name="V", last_name="W",
            email="v@example.com", category=self.pcat_stu,
            expires_at=today + timezone.timedelta(days=1)
        )
        p_none = Patron.objects.create(
            external_id="S0004", first_name="X", last_name="Y",
            email="x@example.com", category=self.pcat_stu, expires_at=None
        )
        self.assertTrue(p_today.is_expired)
        self.assertFalse(p_future.is_expired)
        self.assertFalse(p_none.is_expired)

    def test_loan_is_active_property(self):
        loan = Loan.objects.create(
            patron=self.patron, item=self.item,
            issued_at=timezone.now(),
            due_at=timezone.now() + timezone.timedelta(days=7),
            return_date=None
        )
        self.assertTrue(loan.is_active)
        loan.return_date = timezone.now()
        loan.save()
        self.assertFalse(loan.is_active)

    def test_fine_status_and_payments(self):
        loan = self._make_active_loan()
        fine = Fine.objects.create(
            patron=self.patron, loan=loan, item=self.item,
            fine_type=Fine.OVERDUE, amount=Decimal("10.00"), paid_amount=Decimal("0.00")
        )
        self.assertEqual(fine.status, "UNPAID")
        # Partial payment
        fine.add_payment(Decimal("3.00"))
        fine.refresh_from_db()
        self.assertEqual(fine.paid_amount, Decimal("3.00"))
        self.assertEqual(fine.status, "UNPAID")
        # Overpay should cap at amount
        fine.add_payment(Decimal("20.00"))
        fine.refresh_from_db()
        self.assertEqual(fine.paid_amount, Decimal("10.00"))
        self.assertEqual(fine.status, "PAID")
        # Negative should raise
        with self.assertRaises(ValueError):
            fine.add_payment(Decimal("-1.00"))

    def test_biblio_attributes_json_preserved(self):
        self.assertEqual(self.biblio.attributes.get("pages"), 950)
        self.assertEqual(self.biblio.attributes.get("language"), "en")

    # ---------- ForeignKey to_field + db_column wiring ----------
    def test_patron_fk_to_category_code(self):
        # the FK stores code in db_column 'category_code'
        self.assertEqual(self.patron.category.code, "STU")
        # Swapping category works and persists
        self.patron.category = self.pcat_sta
        self.patron.save()
        self.patron.refresh_from_db()
        self.assertEqual(self.patron.category.code, "STA")

    # ---------- Helpers ----------
    def _make_active_loan(self):
        # Ensure item is not already locked by active loan for this helper
        # Return any active loan so we can reuse the item
        Loan.objects.filter(item=self.item, return_date__isnull=True).update(
            return_date=timezone.now()
        )
        return Loan.objects.create(
            patron=self.patron,
            item=self.item,
            issued_at=timezone.now(),
            due_at=timezone.now() + timezone.timedelta(days=7),
            return_date=None,
        )
