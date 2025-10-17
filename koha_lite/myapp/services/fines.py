from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError

from myapp.models import IssuingRule, Fine, Loan, Item

def _get_rule_for(loan: Loan) -> IssuingRule:
    try:
        return IssuingRule.objects.get(
            patron_category=loan.patron.category,
            item_type=loan.item.item_type,
        )
    except IssuingRule.DoesNotExist:
        raise ValidationError(
            f"No issuing rule for category '{loan.patron.category.code}' and item type '{loan.item.item_type.code}'."
        )

def _overdue_days(as_of, loan: Loan) -> int:
    """as_of: datetime; returns full overdue days (>=0)."""
    if as_of <= loan.due_at:
        return 0
    delta = as_of.date() - loan.due_at.date()
    return max(0, delta.days)

def compute_overdue_amount(loan: Loan, as_of=None) -> Decimal:
    as_of = as_of or timezone.now()
    rule = _get_rule_for(loan)
    days = _overdue_days(as_of, loan)
    base = Decimal(rule.daily_fine) * Decimal(days)
    cap = Decimal(rule.max_fine or 0)
    return min(base, cap) if cap > 0 else base

@transaction.atomic
def assess_or_update_overdue_fine(loan: Loan, final=False) -> Fine | None:
    """
    Create or update the aggregated OVERDUE fine for a loan.
    If `final=True`, use return_date (if set) to freeze the amount at check-in.
    """
    # Determine 'as_of' time for calculation
    as_of = loan.return_date if (final and loan.return_date) else timezone.now()
    amt = compute_overdue_amount(loan, as_of=as_of)

    if amt <= 0:
        # No fine required; if a fine exists but amount is 0, keep it or delete per policy.
        return None

    fine, created = Fine.objects.get_or_create(
        loan=loan, fine_type=Fine.OVERDUE,
        defaults={"patron": loan.patron, "item": loan.item, "amount": amt, "paid_amount": 0},
    )
    if not created and fine.amount != amt:
        # Do not reduce historical fines if check-in already finalized;
        # but for active overdue loans, keep it in sync.
        fine.amount = amt
        fine.save(update_fields=["amount", "updated_at"])

    return fine
