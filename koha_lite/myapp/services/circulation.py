from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from .fines import assess_or_update_overdue_fine
from myapp.models import IssuingRule, Loan, Item, Patron

def _get_rule_for(patron: Patron, item: Item) -> IssuingRule:
    try:
        return IssuingRule.objects.get(
            patron_category=patron.category, item_type=item.item_type
        )
    except IssuingRule.DoesNotExist:
        raise ValidationError(
            f"No issuing rule for category '{patron.category.code}' and item type '{item.item_type.code}'."
        )

def compute_due_date(issued_at, rule: IssuingRule):
    return issued_at + timedelta(days=rule.loan_days)

@transaction.atomic
def checkout(patron: Patron, item: Item) -> Loan:
    if not patron.is_active:
        raise ValidationError("Patron is not active.")
    if item.status != Item.Status.AVAILABLE:
        raise ValidationError(f"Item {item.accession_number} is not available (status={item.status}).")

    rule = _get_rule_for(patron=patron, item=item)  # your helper from earlier
    issued_at = timezone.now()
    due_at = issued_at + timedelta(days=rule.loan_days)

    loan = Loan.objects.create(patron=patron, item=item, due_at=due_at)
    item.status = Item.Status.ISSUED
    item.save(update_fields=["status"])
    return loan

@transaction.atomic
def checkin(loan: Loan):
    if not loan.is_active:
        return loan
    loan.return_date = timezone.now()
    loan.save(update_fields=["return_date"])

    # finalize the overdue fine (if any) based on actual return time
    assess_or_update_overdue_fine(loan, final=True)

    item = loan.item
    item.status = Item.Status.AVAILABLE
    item.save(update_fields=["status"])
    return loan

@transaction.atomic
def renew(loan: Loan):
    if not loan.is_active:
        raise ValidationError("Loan is not active.")

    rule = _get_rule_for(loan.patron, loan.item)
    if not rule.renewal_allowed:
        raise ValidationError("Renewals are not allowed by policy.")
    if loan.renewal_count >= rule.max_renewals:
        raise ValidationError(f"Renewal limit reached ({rule.max_renewals}).")

    from datetime import timedelta
    loan.due_at = loan.due_at + timedelta(days=rule.loan_days)
    loan.renewal_count += 1
    loan.save(update_fields=["due_at", "renewal_count"])

    # If already overdue, renewing does NOT waive existing overdue — but the amount
    # for active loan should reflect the new due date going forward:
    assess_or_update_overdue_fine(loan, final=False)
    return loan

