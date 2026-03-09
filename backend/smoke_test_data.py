from accounts.models import (
    Equipment,
    Exercise,
    EquipmentCategory,
    MuscleGroup,
    ExerciseDifficulty,
)


EXPECTED_EQUIPMENT_COUNT = 32
EXPECTED_EXERCISE_COUNT = 40


def print_result(title, ok, detail):
    icon = "✅" if ok else "❌"
    print(f"{icon} {title}: {detail}")


def validate_counts():
    equipment_count = Equipment.objects.count()
    exercise_count = Exercise.objects.count()

    equipment_ok = equipment_count == EXPECTED_EQUIPMENT_COUNT
    exercise_ok = exercise_count == EXPECTED_EXERCISE_COUNT

    print_result(
        "Conteo Equipment",
        equipment_ok,
        f"esperado={EXPECTED_EQUIPMENT_COUNT}, actual={equipment_count}",
    )
    print_result(
        "Conteo Exercise",
        exercise_ok,
        f"esperado={EXPECTED_EXERCISE_COUNT}, actual={exercise_count}",
    )

    return equipment_ok and exercise_ok


def validate_enums():
    allowed_categories = set(EquipmentCategory.values)
    allowed_muscle_groups = set(MuscleGroup.values)
    allowed_difficulties = set(ExerciseDifficulty.values)

    category_values = set(Equipment.objects.values_list("category", flat=True).distinct())
    muscle_values = set(Exercise.objects.values_list("muscle_group", flat=True).distinct())
    difficulty_values = set(Exercise.objects.values_list("difficulty", flat=True).distinct())

    invalid_categories = sorted(category_values - allowed_categories)
    invalid_muscles = sorted(muscle_values - allowed_muscle_groups)
    invalid_difficulties = sorted(difficulty_values - allowed_difficulties)

    known_spanish_values = {
        "PESO_LIBRE",
        "MAQUINA",
        "ACCESORIO",
        "CALISTENIA",
        "PECHO",
        "ESPALDA",
        "PIERNAS",
        "GLUTEOS",
        "HOMBROS",
        "BICEPS",
        "TRICEPS",
        "ABDOMEN",
        "PRINCIPIANTE",
        "INTERMEDIO",
        "AVANZADO",
    }

    spanish_hits = sorted(
        (category_values | muscle_values | difficulty_values) & known_spanish_values
    )

    categories_ok = len(invalid_categories) == 0
    muscles_ok = len(invalid_muscles) == 0
    difficulties_ok = len(invalid_difficulties) == 0
    spanish_ok = len(spanish_hits) == 0

    print_result(
        "Enums Equipment.category",
        categories_ok,
        f"valores inválidos={invalid_categories or 'ninguno'}",
    )
    print_result(
        "Enums Exercise.muscle_group",
        muscles_ok,
        f"valores inválidos={invalid_muscles or 'ninguno'}",
    )
    print_result(
        "Enums Exercise.difficulty",
        difficulties_ok,
        f"valores inválidos={invalid_difficulties or 'ninguno'}",
    )
    print_result(
        "Sin valores en español",
        spanish_ok,
        f"detectados={spanish_hits or 'ninguno'}",
    )

    return categories_ok and muscles_ok and difficulties_ok and spanish_ok


def validate_many_to_many():
    exercise = Exercise.objects.order_by("?").first()

    if exercise is None:
        print_result("Integridad Many-to-Many", False, "no hay ejercicios en la base")
        return False

    linked_equipment = list(exercise.equipment.values_list("name", flat=True))
    m2m_ok = len(linked_equipment) > 0

    print_result(
        "Integridad Many-to-Many",
        m2m_ok,
        f"ejercicio='{exercise.name}', equipos={linked_equipment or 'ninguno'}",
    )
    return m2m_ok


def validate_queryset():
    try:
        beginner_count = Exercise.objects.filter(
            difficulty=ExerciseDifficulty.BEGINNER
        ).count()
        queryset_ok = isinstance(beginner_count, int)
        print_result(
            "Prueba Queryset BEGINNER",
            queryset_ok,
            f"Exercise.objects.filter(difficulty='BEGINNER').count()={beginner_count}",
        )
        return queryset_ok
    except Exception as exc:
        print_result("Prueba Queryset BEGINNER", False, f"error={exc}")
        return False


def main():
    print("\n================ SMOKE TEST DATA REPORT ================")
    print("Validación post-refactor de fixtures y ORM\n")

    checks = [
        validate_counts(),
        validate_enums(),
        validate_many_to_many(),
        validate_queryset(),
    ]

    all_ok = all(checks)
    print("\n--------------------------------------------------------")
    print_result("Resultado general", all_ok, "OK" if all_ok else "FALLÓ")
    print("========================================================\n")

    if not all_ok:
        raise SystemExit(1)


main()