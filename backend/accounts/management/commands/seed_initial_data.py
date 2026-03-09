from django.core.management import call_command
from django.core.management.base import BaseCommand

from accounts.models import Equipment, Exercise


class Command(BaseCommand):
    help = "Seed initial equipment and exercise data if missing"

    def handle(self, *args, **options):
        if not Equipment.objects.exists():
            call_command("loaddata", "accounts/fixtures/equipamientos.json")
            equipment_count = Equipment.objects.count()
            self.stdout.write(
                self.style.SUCCESS(f"Seeded {equipment_count} equipment items.")
            )
        else:
            self.stdout.write(self.style.SUCCESS("Equipment already seeded. Skipping."))

        if not Exercise.objects.exists():
            call_command("loaddata", "accounts/fixtures/ejercicios.json")
            exercise_count = Exercise.objects.count()
            self.stdout.write(
                self.style.SUCCESS(f"Seeded {exercise_count} exercises.")
            )
        else:
            self.stdout.write(self.style.SUCCESS("Exercises already seeded. Skipping."))
