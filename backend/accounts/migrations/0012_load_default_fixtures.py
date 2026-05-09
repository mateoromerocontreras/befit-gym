# Generated manually to load initial equipment and exercises
from django.db import migrations
from django.core.management import call_command

def load_fixtures(apps, schema_editor):
    # We use call_command to load the json fixtures
    # Equipment must be loaded first because exercises depend on them via ManyToMany
    call_command("loaddata", "equipamientos.json")
    call_command("loaddata", "ejercicios.json")

def unload_fixtures(apps, schema_editor):
    Equipment = apps.get_model("accounts", "Equipment")
    Exercise = apps.get_model("accounts", "Exercise")
    # Deleting all will clear out the defaults
    Exercise.objects.all().delete()
    Equipment.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0011_backfill_user_training_weekdays"),
    ]

    operations = [
        migrations.RunPython(load_fixtures, unload_fixtures),
    ]
