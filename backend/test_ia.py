import json
import os
from unittest.mock import patch

from accounts.models import (
    Equipment,
    Exercise,
    Routine,
    RoutineExercise,
    TrainingGoal,
    TrainingLevel,
    User,
    WeeklyPlan,
)
from accounts.services.routine_generator import RoutineGeneratorService

TARGET_EMAIL = "mock.routine.user@mail.com"
TRAINING_DAYS = 3
EXERCISES_PER_DAY = 4
TEST_MODE = os.getenv("TEST_IA_MODE", "mock").strip().lower()


def build_mock_ai_response(exercises):
    if len(exercises) < TRAINING_DAYS * EXERCISES_PER_DAY:
        raise SystemExit(
            "❌ No hay suficientes ejercicios para construir la respuesta mock. "
            "Ejecuta seed_initial_data primero."
        )

    plan = []
    exercise_index = 0
    for day in range(1, TRAINING_DAYS + 1):
        day_exercises = []
        for order in range(1, EXERCISES_PER_DAY + 1):
            exercise = exercises[exercise_index]
            exercise_index += 1
            day_exercises.append(
                {
                    "exercise_id": exercise.id,
                    "series": 4 if order <= 2 else 3,
                    "repetitions": "8-10" if order <= 2 else "12",
                    "rest_seconds": 90 if order <= 2 else 60,
                    "order": order,
                    "notes": f"Mock note day {day} order {order}",
                }
            )

        plan.append(
            {
                "day": day,
                "day_name": f"Day {day}",
                "focus": "Strength",
                "exercises": day_exercises,
            }
        )

    return json.dumps(
        {
            "weekly_plan": plan,
            "estimated_duration_minutes": 60,
            "recommended_level": "INTERMEDIATE",
            "observations": "Mock generated plan",
        },
        ensure_ascii=False,
    )


def validate_db_persistence(user, result):
    routine = Routine.objects.filter(id=result["routine_id"]).first()
    if not routine:
        raise AssertionError("Routine principal no fue guardada en BD")

    plans = WeeklyPlan.objects.filter(user=user).select_related("routine").order_by("weekday")
    if plans.count() != TRAINING_DAYS:
        raise AssertionError(
            f"Se esperaban {TRAINING_DAYS} WeeklyPlan y se encontraron {plans.count()}"
        )

    plan_ids = list(plans.values_list("id", flat=True))
    if sorted(plan_ids) != sorted(result["plan_ids"]):
        raise AssertionError("Los plan_ids retornados no coinciden con la BD")

    total_exercises = 0
    expected_weekdays = list(range(1, TRAINING_DAYS + 1))
    current_weekdays = list(plans.values_list("weekday", flat=True))
    if current_weekdays != expected_weekdays:
        raise AssertionError(
            f"Weekdays inválidos. Esperado {expected_weekdays}, actual {current_weekdays}"
        )

    for plan in plans:
        routine_exercises = RoutineExercise.objects.filter(routine=plan.routine).order_by("order")
        if not routine_exercises.exists():
            raise AssertionError(f"La rutina diaria {plan.routine.id} no tiene ejercicios")

        orders = [item.order for item in routine_exercises]
        if orders != list(range(1, len(orders) + 1)):
            raise AssertionError(
                f"Orden inválido en rutina diaria {plan.routine.id}. Órdenes: {orders}"
            )

        if TEST_MODE == "mock" and routine_exercises.count() != EXERCISES_PER_DAY:
            raise AssertionError(
                f"Se esperaban {EXERCISES_PER_DAY} ejercicios en rutina {plan.routine.id} "
                f"y se encontraron {routine_exercises.count()}"
            )

        for item in routine_exercises:
            if item.series <= 0:
                raise AssertionError(f"Series inválidas en RoutineExercise {item.id}")
            if item.rest_seconds <= 0:
                raise AssertionError(f"Rest inválido en RoutineExercise {item.id}")
            if not item.repetitions:
                raise AssertionError(f"Repeticiones vacías en RoutineExercise {item.id}")

        total_exercises += routine_exercises.count()

    if total_exercises != result["exercises_count"]:
        raise AssertionError(
            f"exercises_count inconsistente. Resultado={result['exercises_count']} BD={total_exercises}"
        )

    print("✅ PERSISTENCIA EN BD VALIDADA:")
    print(
        json.dumps(
            {
                "routine_id": routine.id,
                "weekly_plans": plans.count(),
                "exercise_rows": total_exercises,
                "weekdays": current_weekdays,
                "mode": TEST_MODE,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


def create_clean_mock_user():
    User.objects.filter(email=TARGET_EMAIL).delete()
    user = User.objects.create_user(
        email=TARGET_EMAIL,
        password="test1234",
        age=29,
        weight=78.5,
        height=1.78,
        goal=TrainingGoal.GAIN_MUSCLE,
        level=TrainingLevel.INTERMEDIATE,
    )
    print(f"ℹ️ Usuario mock creado limpio: {user.email}")
    return user


equipment_qs = Equipment.objects.all().order_by("id")
if not equipment_qs.exists():
    raise SystemExit(
        "❌ No hay equipamiento cargado. Ejecuta seed_initial_data antes de esta prueba."
    )

exercise_qs = (
    Exercise.objects.filter(equipment__in=equipment_qs)
    .distinct()
    .order_by("id")
)
if exercise_qs.count() < TRAINING_DAYS * EXERCISES_PER_DAY:
    raise SystemExit(
        "❌ No hay suficientes ejercicios para la prueba. Ejecuta seed_initial_data."
    )

user = create_clean_mock_user()
user.preferred_equipment.set(equipment_qs[:10])
print(f"ℹ️ Equipamiento asignado: {user.preferred_equipment.count()} ítems")

service = RoutineGeneratorService()

print(f"--- Iniciando generación para {user.email} (mode={TEST_MODE}) ---")

try:
    if TEST_MODE == "mock":
        mock_response = build_mock_ai_response(list(exercise_qs[: TRAINING_DAYS * EXERCISES_PER_DAY]))
        with patch.object(RoutineGeneratorService, "_call_gemini_api", return_value=mock_response):
            routine = service.generate_routine_for_user(user_id=user.id, training_days=TRAINING_DAYS)
    else:
        routine = service.generate_routine_for_user(user_id=user.id, training_days=TRAINING_DAYS)

    if routine.get("success"):
        print("✅ RUTINA GENERADA CON ÉXITO:")
        print(json.dumps(routine, indent=2, ensure_ascii=False))
        validate_db_persistence(user, routine)
    else:
        print("❌ ERROR EN LA GENERACIÓN:")
        print(json.dumps(routine, indent=2, ensure_ascii=False))
        raise SystemExit(1)

except Exception as e:
    print(f"❌ ERROR EN LA GENERACIÓN: {e}")
    raise