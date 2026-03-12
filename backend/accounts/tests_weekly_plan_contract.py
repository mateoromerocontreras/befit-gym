from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import (
    Exercise,
    MuscleGroup,
    ExerciseDifficulty,
    Routine,
    RoutineExercise,
    Weekday,
    WeeklyPlan,
)

User = get_user_model()


class WeeklyPlanContractAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="weekly.contract@test.com",
            password="SecurePass123!",
        )
        self.other_user = User.objects.create_user(
            email="weekly.other@test.com",
            password="SecurePass123!",
        )

        self.exercise_1 = Exercise.objects.create(
            name="Bench Press",
            muscle_group=MuscleGroup.CHEST,
            difficulty=ExerciseDifficulty.INTERMEDIATE,
        )
        self.exercise_2 = Exercise.objects.create(
            name="Pull Up",
            muscle_group=MuscleGroup.BACK,
            difficulty=ExerciseDifficulty.BEGINNER,
        )

        self.routine_user_mon = Routine.objects.create(
            name="Monday - Chest",
            description="Chest focus",
            duration_minutes=55,
            level="INTERMEDIATE",
        )
        RoutineExercise.objects.create(
            routine=self.routine_user_mon,
            exercise=self.exercise_1,
            series=4,
            repetitions="8-10",
            rest_seconds=90,
            order=1,
            notes="Control tempo",
        )

        self.routine_user_wed = Routine.objects.create(
            name="Wednesday - Back",
            description="Back focus",
            duration_minutes=50,
            level="INTERMEDIATE",
        )
        RoutineExercise.objects.create(
            routine=self.routine_user_wed,
            exercise=self.exercise_2,
            series=3,
            repetitions="10-12",
            rest_seconds=60,
            order=1,
            notes="Full range",
        )

        self.routine_other = Routine.objects.create(
            name="Tuesday - Other",
            description="Other user routine",
            duration_minutes=45,
            level="BEGINNER",
        )
        RoutineExercise.objects.create(
            routine=self.routine_other,
            exercise=self.exercise_1,
            series=3,
            repetitions="12",
            rest_seconds=60,
            order=1,
        )

        WeeklyPlan.objects.create(
            user=self.user,
            routine=self.routine_user_mon,
            weekday=Weekday.MONDAY,
            active=True,
            notes="Main day",
        )
        WeeklyPlan.objects.create(
            user=self.user,
            routine=self.routine_user_wed,
            weekday=Weekday.WEDNESDAY,
            active=True,
            notes="Secondary day",
        )
        WeeklyPlan.objects.create(
            user=self.other_user,
            routine=self.routine_other,
            weekday=Weekday.TUESDAY,
            active=True,
        )

        self.url = reverse("weekly-plan-list")

    def _extract_results(self, response_data):
        if isinstance(response_data, dict) and "results" in response_data:
            return response_data["results"]
        return response_data

    def test_weekly_plan_list_contract_fields(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        items = self._extract_results(response.data)
        self.assertEqual(len(items), 2)

        first = items[0]
        self.assertIn("day", first)
        self.assertIn("day_name", first)
        self.assertIn("focus", first)
        self.assertIn("active", first)
        self.assertIn("notes", first)
        self.assertIn("exercises", first)

        self.assertTrue(first["day_name"].startswith("Monday"))
        self.assertEqual(first["focus"], "Monday - Chest")

        first_exercise = first["exercises"][0]
        self.assertIn("name", first_exercise)
        self.assertIn("series", first_exercise)
        self.assertIn("repetitions", first_exercise)
        self.assertIn("order", first_exercise)
        self.assertIn("notes", first_exercise)

        self.assertIn("muscle_group", first_exercise)
        self.assertIn("difficulty", first_exercise)
        self.assertEqual(first_exercise["name"], "Bench Press")

    def test_weekly_plan_list_is_user_scoped(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        items = self._extract_results(response.data)
        focus_names = [item["focus"] for item in items]

        self.assertIn("Monday - Chest", focus_names)
        self.assertIn("Wednesday - Back", focus_names)
        self.assertNotIn("Tuesday - Other", focus_names)

    def test_weekly_plan_list_ordered_by_day(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        items = self._extract_results(response.data)
        days = [item["day"] for item in items]

        self.assertEqual(days, sorted(days))
        self.assertEqual(days, [Weekday.MONDAY, Weekday.WEDNESDAY])

    def test_weekly_plan_list_empty_state(self):
        empty_user = User.objects.create_user(
            email="weekly.empty@test.com",
            password="SecurePass123!",
        )
        self.client.force_authenticate(user=empty_user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        items = self._extract_results(response.data)
        self.assertEqual(items, [])
        if isinstance(response.data, dict) and "count" in response.data:
            self.assertEqual(response.data["count"], 0)
