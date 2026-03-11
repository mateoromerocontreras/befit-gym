import json
from unittest.mock import patch

from django.test import TestCase

from accounts.models import (
    Equipment,
    EquipmentCategory,
    Exercise,
    ExerciseDifficulty,
    MuscleGroup,
    Routine,
    RoutineExercise,
    TrainingGoal,
    TrainingLevel,
    User,
    Weekday,
    WeeklyPlan,
)
from accounts.services.routine_generator import RoutineGeneratorService


class RoutineGeneratorPersistenceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="routine.mock@test.com",
            password="Secure123!",
            age=30,
            weight=80,
            height=1.8,
            goal=TrainingGoal.GAIN_MUSCLE,
            level=TrainingLevel.INTERMEDIATE,
        )

        self.equipment = [
            Equipment.objects.create(name="Barbell", category=EquipmentCategory.WEIGHTS),
            Equipment.objects.create(name="Bench", category=EquipmentCategory.MACHINE),
            Equipment.objects.create(name="Dumbbells", category=EquipmentCategory.WEIGHTS),
        ]
        self.user.preferred_equipment.set(self.equipment)

        self.exercises = []
        for index in range(1, 13):
            exercise = Exercise.objects.create(
                name=f"Exercise {index}",
                description=f"Test exercise {index}",
                muscle_group=MuscleGroup.CHEST if index % 2 else MuscleGroup.BACK,
                difficulty=ExerciseDifficulty.INTERMEDIATE,
            )
            exercise.equipment.set(self.equipment[:2])
            self.exercises.append(exercise)

    def _mock_weekly_json(self):
        weekly_plan = []
        exercise_index = 0
        for day in range(1, 4):
            day_exercises = []
            for order in range(1, 5):
                exercise = self.exercises[exercise_index]
                exercise_index += 1
                day_exercises.append(
                    {
                        "exercise_id": exercise.id,
                        "series": 4 if order <= 2 else 3,
                        "repetitions": "8-10" if order <= 2 else "12",
                        "rest_seconds": 90 if order <= 2 else 60,
                        "order": order,
                        "notes": f"Day {day} order {order}",
                    }
                )

            weekly_plan.append(
                {
                    "day": day,
                    "day_name": f"Day {day}",
                    "focus": "Upper/Lower Split",
                    "exercises": day_exercises,
                }
            )

        return json.dumps(
            {
                "weekly_plan": weekly_plan,
                "estimated_duration_minutes": 60,
                "recommended_level": "INTERMEDIATE",
                "observations": "Mock unit test plan",
            }
        )

    @patch.object(RoutineGeneratorService, "_call_gemini_api")
    def test_generate_routine_persists_full_structure(self, mock_call_gemini):
        mock_call_gemini.return_value = self._mock_weekly_json()

        service = RoutineGeneratorService()
        result = service.generate_routine_for_user(
            user_id=self.user.id,
            training_days=3,
            routine_name="Mock Plan",
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["exercises_count"], 12)

        root_routine = Routine.objects.get(id=result["routine_id"])
        self.assertEqual(root_routine.name, "Mock Plan")

        plans = WeeklyPlan.objects.filter(user=self.user).select_related("routine").order_by("weekday")
        self.assertEqual(plans.count(), 3)
        self.assertEqual(list(plans.values_list("weekday", flat=True)), [Weekday.MONDAY, Weekday.TUESDAY, Weekday.WEDNESDAY])
        self.assertEqual(sorted(result["plan_ids"]), sorted(plans.values_list("id", flat=True)))

        total_rows = 0
        for plan in plans:
            routine_exercises = RoutineExercise.objects.filter(routine=plan.routine).order_by("order")
            self.assertEqual(routine_exercises.count(), 4)

            orders = [row.order for row in routine_exercises]
            self.assertEqual(orders, [1, 2, 3, 4])

            for row in routine_exercises:
                self.assertGreater(row.series, 0)
                self.assertTrue(row.repetitions)
                self.assertGreater(row.rest_seconds, 0)

            total_rows += routine_exercises.count()

        self.assertEqual(total_rows, 12)
