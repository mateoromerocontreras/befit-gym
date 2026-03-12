from django.db import migrations


def backfill_user_training_weekdays(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    UserTrainingWeekday = apps.get_model("accounts", "UserTrainingWeekday")

    default_weekdays = [1, 3, 5]
    to_create = []

    for user in User.objects.all().iterator():
        existing_days = set(
            UserTrainingWeekday.objects.filter(user_id=user.id).values_list("weekday", flat=True)
        )
        for day in default_weekdays:
            if day not in existing_days:
                to_create.append(UserTrainingWeekday(user_id=user.id, weekday=day))

    if to_create:
        UserTrainingWeekday.objects.bulk_create(to_create)


def reverse_backfill_user_training_weekdays(apps, schema_editor):
    UserTrainingWeekday = apps.get_model("accounts", "UserTrainingWeekday")
    UserTrainingWeekday.objects.filter(weekday__in=[1, 3, 5]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0010_usertrainingweekday"),
    ]

    operations = [
        migrations.RunPython(
            backfill_user_training_weekdays,
            reverse_backfill_user_training_weekdays,
        ),
    ]
