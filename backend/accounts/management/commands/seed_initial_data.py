from django.core.management import call_command
from django.core.management.base import BaseCommand

from accounts.models import Equipment


class Command(BaseCommand):
    help = "Seed initial equipment data if table is empty"

    def handle(self, *args, **options):
        if Equipment.objects.exists():
            self.stdout.write(self.style.SUCCESS("Equipment already seeded. Skipping."))
            return

        call_command("loaddata", "accounts/fixtures/equipamientos.json")
        count = Equipment.objects.count()
        self.stdout.write(self.style.SUCCESS(f"Seeded {count} equipment items."))
