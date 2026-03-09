from django.db import migrations


def migrate_enum_values_to_english(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    Equipment = apps.get_model("accounts", "Equipment")
    Exercise = apps.get_model("accounts", "Exercise")
    Routine = apps.get_model("accounts", "Routine")

    user_goal_map = {
        "PERDER_PESO": "LOSE_WEIGHT",
        "GANAR_MASA": "GAIN_MUSCLE",
        "TONIFICAR": "TONE",
        "FUERZA": "STRENGTH",
        "RESISTENCIA": "ENDURANCE",
        "SALUD_GENERAL": "GENERAL_HEALTH",
    }
    for old_value, new_value in user_goal_map.items():
        User.objects.filter(goal=old_value).update(goal=new_value)

    user_level_map = {
        "PRINCIPIANTE": "BEGINNER",
        "INTERMEDIO": "INTERMEDIATE",
        "AVANZADO": "ADVANCED",
    }
    for old_value, new_value in user_level_map.items():
        User.objects.filter(level=old_value).update(level=new_value)

    equipment_category_map = {
        "PESO_LIBRE": "FREE_WEIGHTS",
        "MAQUINA": "MACHINE",
        "ACCESORIO": "ACCESSORY",
    }
    for old_value, new_value in equipment_category_map.items():
        Equipment.objects.filter(category=old_value).update(category=new_value)

    exercise_muscle_group_map = {
        "PECHO": "CHEST",
        "ESPALDA": "BACK",
        "HOMBROS": "SHOULDERS",
        "PIERNAS": "LEGS",
        "GLUTEOS": "GLUTES",
    }
    for old_value, new_value in exercise_muscle_group_map.items():
        Exercise.objects.filter(muscle_group=old_value).update(muscle_group=new_value)

    exercise_difficulty_map = {
        "PRINCIPIANTE": "BEGINNER",
        "INTERMEDIO": "INTERMEDIATE",
        "AVANZADO": "ADVANCED",
    }
    for old_value, new_value in exercise_difficulty_map.items():
        Exercise.objects.filter(difficulty=old_value).update(difficulty=new_value)

    routine_level_map = {
        "PRINCIPIANTE": "BEGINNER",
        "INTERMEDIO": "INTERMEDIATE",
        "AVANZADO": "ADVANCED",
    }
    for old_value, new_value in routine_level_map.items():
        Routine.objects.filter(level=old_value).update(level=new_value)


def reverse_migrate_enum_values_to_spanish(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    Equipment = apps.get_model("accounts", "Equipment")
    Exercise = apps.get_model("accounts", "Exercise")
    Routine = apps.get_model("accounts", "Routine")

    user_goal_map = {
        "LOSE_WEIGHT": "PERDER_PESO",
        "GAIN_MUSCLE": "GANAR_MASA",
        "TONE": "TONIFICAR",
        "STRENGTH": "FUERZA",
        "ENDURANCE": "RESISTENCIA",
        "GENERAL_HEALTH": "SALUD_GENERAL",
    }
    for old_value, new_value in user_goal_map.items():
        User.objects.filter(goal=old_value).update(goal=new_value)

    user_level_map = {
        "BEGINNER": "PRINCIPIANTE",
        "INTERMEDIATE": "INTERMEDIO",
        "ADVANCED": "AVANZADO",
    }
    for old_value, new_value in user_level_map.items():
        User.objects.filter(level=old_value).update(level=new_value)

    equipment_category_map = {
        "FREE_WEIGHTS": "PESO_LIBRE",
        "MACHINE": "MAQUINA",
        "ACCESSORY": "ACCESORIO",
    }
    for old_value, new_value in equipment_category_map.items():
        Equipment.objects.filter(category=old_value).update(category=new_value)

    exercise_muscle_group_map = {
        "CHEST": "PECHO",
        "BACK": "ESPALDA",
        "SHOULDERS": "HOMBROS",
        "LEGS": "PIERNAS",
        "GLUTES": "GLUTEOS",
    }
    for old_value, new_value in exercise_muscle_group_map.items():
        Exercise.objects.filter(muscle_group=old_value).update(muscle_group=new_value)

    exercise_difficulty_map = {
        "BEGINNER": "PRINCIPIANTE",
        "INTERMEDIATE": "INTERMEDIO",
        "ADVANCED": "AVANZADO",
    }
    for old_value, new_value in exercise_difficulty_map.items():
        Exercise.objects.filter(difficulty=old_value).update(difficulty=new_value)

    routine_level_map = {
        "BEGINNER": "PRINCIPIANTE",
        "INTERMEDIATE": "INTERMEDIO",
        "ADVANCED": "AVANZADO",
    }
    for old_value, new_value in routine_level_map.items():
        Routine.objects.filter(level=old_value).update(level=new_value)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0007_user_edad_user_nivel_user_objetivo"),
    ]

    operations = [
        migrations.RenameModel(old_name="Equipamiento", new_name="Equipment"),
        migrations.RenameModel(old_name="Ejercicio", new_name="Exercise"),
        migrations.RenameModel(old_name="Rutina", new_name="Routine"),
        migrations.RenameModel(old_name="RutinaEjercicio", new_name="RoutineExercise"),
        migrations.RenameModel(old_name="PlanSemanal", new_name="WeeklyPlan"),
        migrations.RenameField(model_name="user", old_name="peso", new_name="weight"),
        migrations.RenameField(model_name="user", old_name="altura", new_name="height"),
        migrations.RenameField(model_name="user", old_name="edad", new_name="age"),
        migrations.RenameField(model_name="user", old_name="objetivo", new_name="goal"),
        migrations.RenameField(model_name="user", old_name="nivel", new_name="level"),
        migrations.RenameField(
            model_name="user",
            old_name="suscripcion_activa",
            new_name="active_subscription",
        ),
        migrations.RenameField(
            model_name="user",
            old_name="equipamientos_preferidos",
            new_name="preferred_equipment",
        ),
        migrations.RenameField(
            model_name="equipment", old_name="nombre", new_name="name"
        ),
        migrations.RenameField(
            model_name="equipment", old_name="categoria", new_name="category"
        ),
        migrations.RenameField(
            model_name="exercise", old_name="nombre", new_name="name"
        ),
        migrations.RenameField(
            model_name="exercise", old_name="descripcion", new_name="description"
        ),
        migrations.RenameField(
            model_name="exercise", old_name="grupo_muscular", new_name="muscle_group"
        ),
        migrations.RenameField(
            model_name="exercise", old_name="dificultad", new_name="difficulty"
        ),
        migrations.RenameField(
            model_name="exercise", old_name="imagen_url", new_name="image_url"
        ),
        migrations.RenameField(
            model_name="exercise", old_name="equipamientos", new_name="equipment"
        ),
        migrations.RenameField(
            model_name="routine", old_name="nombre", new_name="name"
        ),
        migrations.RenameField(
            model_name="routine", old_name="descripcion", new_name="description"
        ),
        migrations.RenameField(
            model_name="routine", old_name="ejercicios", new_name="exercises"
        ),
        migrations.RenameField(
            model_name="routine", old_name="duracion_minutos", new_name="duration_minutes"
        ),
        migrations.RenameField(
            model_name="routine", old_name="nivel", new_name="level"
        ),
        migrations.RenameField(
            model_name="routineexercise", old_name="rutina", new_name="routine"
        ),
        migrations.RenameField(
            model_name="routineexercise", old_name="ejercicio", new_name="exercise"
        ),
        migrations.RenameField(
            model_name="routineexercise", old_name="repeticiones", new_name="repetitions"
        ),
        migrations.RenameField(
            model_name="routineexercise", old_name="descanso_segundos", new_name="rest_seconds"
        ),
        migrations.RenameField(
            model_name="routineexercise", old_name="orden", new_name="order"
        ),
        migrations.RenameField(
            model_name="routineexercise", old_name="notas", new_name="notes"
        ),
        migrations.RenameField(
            model_name="weeklyplan", old_name="usuario", new_name="user"
        ),
        migrations.RenameField(
            model_name="weeklyplan", old_name="rutina", new_name="routine"
        ),
        migrations.RenameField(
            model_name="weeklyplan", old_name="dia_semana", new_name="weekday"
        ),
        migrations.RenameField(
            model_name="weeklyplan", old_name="activo", new_name="active"
        ),
        migrations.RenameField(
            model_name="weeklyplan", old_name="notas", new_name="notes"
        ),
        migrations.RunPython(
            migrate_enum_values_to_english,
            reverse_migrate_enum_values_to_spanish,
        ),
    ]
