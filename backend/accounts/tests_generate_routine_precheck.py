from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Equipment, EquipmentCategory, Exercise, ExerciseDifficulty, MuscleGroup

User = get_user_model()


class GenerateRoutinePrecheckAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="precheck@test.com",
            password="SecurePass123!",
        )
        self.url = reverse("generate-routine-precheck")

    def test_precheck_reports_missing_equipment_and_exercises(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["ready"])
        self.assertIn("equipment", response.data["missing"])
        self.assertIn("compatible_exercises", response.data["missing"])
        self.assertEqual(response.data["checks"]["equipment_count"], 0)

    def test_precheck_reports_missing_compatible_exercises_when_equipment_selected(self):
        equip = Equipment.objects.create(name="Bands", category=EquipmentCategory.ACCESSORY)
        self.user.preferred_equipment.set([equip])

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["ready"])
        self.assertNotIn("equipment", response.data["missing"])
        self.assertIn("compatible_exercises", response.data["missing"])

    def test_precheck_ready_when_all_requirements_met(self):
        equip = Equipment.objects.create(name="Barbell", category=EquipmentCategory.WEIGHTS)
        exercise = Exercise.objects.create(
            name="Bench Press",
            muscle_group=MuscleGroup.CHEST,
            difficulty=ExerciseDifficulty.INTERMEDIATE,
        )
        exercise.equipment.set([equip])
        self.user.preferred_equipment.set([equip])

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["ready"])
        self.assertEqual(response.data["missing"], [])
        self.assertEqual(response.data["checks"]["compatible_exercises_count"], 1)

    @override_settings(GOOGLE_API_KEY="")
    def test_precheck_reports_missing_api_key(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["ready"])
        self.assertIn("api_key", response.data["missing"])
