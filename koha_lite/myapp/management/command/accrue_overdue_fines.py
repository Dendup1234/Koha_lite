from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from myapp.models import Loan
from myapp.services.fines import assess_or_update_overdue_fine

class Command(BaseCommand):
    help = "Accrue/update overdue fines for all active overdue loans."

    def handle(self, *args, **opts):
        now = timezone.now()
        qs = Loan.objects.filter(return_date__isnull=True, due_at__lt=now).select_related("patron", "item", "item__item_type", "patron__category")
        count = 0
        with transaction.atomic():
            for loan in qs:
                f = assess_or_update_overdue_fine(loan, final=False)
                if f:
                    count += 1
        self.stdout.write(self.style.SUCCESS(f"Updated {count} overdue fine(s)."))
