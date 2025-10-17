from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist

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

    rule = _get_rule_for(patron, item)
    issued_at = timezone.now()
    due_at = compute_due_date(issued_at, rule)

    # Create loan
    loan = Loan.objects.create(patron=patron, item=item, due_at=due_at)

    # Update item status
    item.status = Item.Status.ISSUED
    item.save(update_fields=["status"])

    return loan

@transaction.atomic
def checkin(loan: Loan):
    if not loan.is_active:
        return loan
    loan.return_date = timezone.now()
    loan.save(update_fields=["return_date"])

    # mark item available again
    item = loan.item
    item.status = Item.Status.AVAILABLE
    item.save(update_fields=["status"])

    return loan

@transaction.atomic
def renew(loan: Loan):
    if not loan.is_active:
        raise ValidationError("Loan is not active.")

    patron = loan.patron
    item = loan.item
    rule = _get_rule_for(patron, item)

    if not rule.renewal_allowed:
        raise ValidationError("Renewals are not allowed by policy.")
    if loan.renewal_count >= rule.max_renewals:
        raise ValidationError(f"Renewal limit reached ({rule.max_renewals}).")

    # extend from current due_at (common policy)
    new_due = loan.due_at + (loan.due_at - (loan.issued_at if loan.renewal_count == 0 else loan.due_at - (loan.due_at - loan.due_at)))
    # simpler: add loan_days again
    from datetime import timedelta
    new_due = loan.due_at + timedelta(days=rule.loan_days)

    loan.due_at = new_due
    loan.renewal_count += 1
    loan.save(update_fields=["due_at", "renewal_count"])
    return loan
