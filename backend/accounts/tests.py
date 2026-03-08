from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import (
    CategoriaEquipamiento,
    DiaSemana,
    Ejercicio,
    Equipamiento,
    GrupoMuscular,
    PlanSemanal,
    Rutina,
    RutinaEjercicio,
)

User = get_user_model()


class UserModelTest(TestCase):
    """Tests para el modelo User personalizado"""

    def setUp(self):
        self.user_data = {"email": "test@example.com", "password": "TestPassword123!"}

    def test_create_user(self):
        """Test para crear un usuario básico"""
        user = User.objects.create_user(
            email=self.user_data["email"], password=self.user_data["password"]
        )
        self.assertEqual(user.email, self.user_data["email"])
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_without_email(self):
        """Test para verificar que se requiere email"""
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="test123")

    def test_create_superuser(self):
        """Test para crear un superusuario"""
        admin_user = User.objects.create_superuser(
            email="admin@example.com", password="AdminPass123!"
        )
        self.assertEqual(admin_user.email, "admin@example.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_user_str_representation(self):
        """Test para verificar la representación string del usuario"""
        user = User.objects.create_user(email="test@example.com", password="test123")
        self.assertEqual(str(user), "test@example.com")

    def test_email_normalization(self):
        """Test para verificar la normalización del email"""
        email = "test@EXAMPLE.COM"
        user = User.objects.create_user(email=email, password="test123")
        self.assertEqual(user.email, "test@example.com")


class UserRegistrationAPITest(APITestCase):
    """Tests para el endpoint de registro de usuarios"""

    def setUp(self):
        self.register_url = reverse("register")
        self.valid_user_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "password2": "SecurePass123!",
        }

    def test_user_registration_success(self):
        """Test para registro exitoso de usuario"""
        response = self.client.post(
            self.register_url, self.valid_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], self.valid_user_data["email"])

        # Verificar que el usuario fue creado en la base de datos
        self.assertTrue(
            User.objects.filter(email=self.valid_user_data["email"]).exists()
        )

    def test_user_registration_password_mismatch(self):
        """Test para verificar error cuando las contraseñas no coinciden"""
        invalid_data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
            "password2": "DifferentPass123!",
        }
        response = self.client.post(self.register_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_user_registration_duplicate_email(self):
        """Test para verificar error al registrar email duplicado"""
        # Crear usuario primero
        User.objects.create_user(
            email=self.valid_user_data["email"], password="test123"
        )

        # Intentar registrar con el mismo email
        response = self.client.post(
            self.register_url, self.valid_user_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_invalid_email(self):
        """Test para verificar error con email inválido"""
        invalid_data = {
            "email": "not-an-email",
            "password": "SecurePass123!",
            "password2": "SecurePass123!",
        }
        response = self.client.post(self.register_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_weak_password(self):
        """Test para verificar error con contraseña débil"""
        weak_password_data = {
            "email": "test@example.com",
            "password": "123",  # Contraseña muy corta
            "password2": "123",
        }
        response = self.client.post(
            self.register_url, weak_password_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_missing_fields(self):
        """Test para verificar error cuando faltan campos requeridos"""
        incomplete_data = {"email": "test@example.com"}
        response = self.client.post(self.register_url, incomplete_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginAPITest(APITestCase):
    """Tests para el endpoint de login de usuarios"""

    def setUp(self):
        self.login_url = reverse("login")
        self.user_data = {"email": "testuser@example.com", "password": "TestPass123!"}
        # Crear usuario para las pruebas de login
        self.user = User.objects.create_user(
            email=self.user_data["email"], password=self.user_data["password"]
        )

    def test_user_login_success(self):
        """Test para login exitoso"""
        response = self.client.post(self.login_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["message"], "Login successful")

    def test_user_login_invalid_credentials(self):
        """Test para login con credenciales incorrectas"""
        invalid_data = {
            "email": self.user_data["email"],
            "password": "WrongPassword123!",
        }
        response = self.client.post(self.login_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data)

    def test_user_login_nonexistent_user(self):
        """Test para login con usuario que no existe"""
        nonexistent_data = {
            "email": "nonexistent@example.com",
            "password": "SomePass123!",
        }
        response = self.client.post(self.login_url, nonexistent_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_login_inactive_user(self):
        """Test para login con usuario inactivo"""
        self.user.is_active = False
        self.user.save()

        response = self.client.post(self.login_url, self.user_data, format="json")
        # El método authenticate() de Django devuelve None para usuarios inactivos
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data)


class EquipamientoAPITest(APITestCase):
    """Tests para el endpoint de equipamientos"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="equip@example.com", password="SecurePass123!"
        )
        self.list_url = reverse("equipamiento-list")

        Equipamiento.objects.create(
            nombre="Barra Olímpica", categoria=CategoriaEquipamiento.PESO_LIBRE
        )
        Equipamiento.objects.create(
            nombre="Bicicleta Fija", categoria=CategoriaEquipamiento.CARDIO
        )
        Equipamiento.objects.create(
            nombre="Banco Plano", categoria=CategoriaEquipamiento.MAQUINA
        )

    def test_equipamiento_list_requires_authentication(self):
        """Debe rechazar acceso sin JWT"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_equipamiento_list_returns_paginated_response(self):
        """Debe retornar estructura paginada global DRF"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(len(response.data["results"]), 3)

        first_item = response.data["results"][0]
        self.assertIn("categoria_display", first_item)

    def test_equipamiento_filter_by_categoria(self):
        """Debe filtrar equipamientos por categoría"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            self.list_url, {"categoria": CategoriaEquipamiento.CARDIO}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["nombre"], "Bicicleta Fija")


class EjercicioAPITest(APITestCase):
    """Tests para endpoint de ejercicios y filtros"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="exercise@example.com", password="SecurePass123!"
        )
        self.list_url = reverse("ejercicio-list")

        self.mancuernas = Equipamiento.objects.create(
            nombre="Mancuernas", categoria=CategoriaEquipamiento.PESO_LIBRE
        )
        self.maquina = Equipamiento.objects.create(
            nombre="Prensa de Piernas", categoria=CategoriaEquipamiento.MAQUINA
        )

        self.ejercicio_pecho = Ejercicio.objects.create(
            nombre="Press de Banca",
            descripcion="Ejercicio de pecho",
            grupo_muscular=GrupoMuscular.PECHO,
            dificultad="INTERMEDIO",
        )
        self.ejercicio_pecho.equipamientos.add(self.mancuernas)

        self.ejercicio_piernas = Ejercicio.objects.create(
            nombre="Prensa 45",
            descripcion="Ejercicio de piernas",
            grupo_muscular=GrupoMuscular.PIERNAS,
            dificultad="PRINCIPIANTE",
        )
        self.ejercicio_piernas.equipamientos.add(self.maquina)

    def test_ejercicio_list_returns_paginated_with_new_fields(self):
        """Debe incluir paginación y campos nuevos en serializer"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 2)

        item = response.data["results"][0]
        self.assertIn("dificultad", item)
        self.assertIn("dificultad_display", item)
        self.assertIn("equipamientos", item)

    def test_ejercicio_filter_by_grupo_muscular(self):
        """Debe filtrar ejercicios por grupo muscular"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url, {"grupo_muscular": "PIERNAS"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["nombre"], "Prensa 45")


class RutinaPlanSemanalAPITest(APITestCase):
    """Tests para rutinas y aislamiento de plan semanal por usuario"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="owner@example.com", password="SecurePass123!"
        )
        self.other_user = User.objects.create_user(
            email="other@example.com", password="SecurePass123!"
        )

        equip = Equipamiento.objects.create(
            nombre="Bandas de Resistencia", categoria=CategoriaEquipamiento.ACCESORIO
        )
        ejercicio = Ejercicio.objects.create(
            nombre="Remo con Banda",
            descripcion="Trabajo de espalda",
            grupo_muscular=GrupoMuscular.ESPALDA,
            dificultad="PRINCIPIANTE",
        )
        ejercicio.equipamientos.add(equip)

        self.rutina = Rutina.objects.create(
            nombre="Espalda Inicial",
            descripcion="Rutina de prueba",
            duracion_minutos=40,
            nivel="PRINCIPIANTE",
        )
        RutinaEjercicio.objects.create(
            rutina=self.rutina,
            ejercicio=ejercicio,
            series=3,
            repeticiones="12",
            descanso_segundos=60,
            orden=1,
        )

        self.plan_user = PlanSemanal.objects.create(
            usuario=self.user,
            rutina=self.rutina,
            dia_semana=DiaSemana.LUNES,
            activo=True,
        )
        PlanSemanal.objects.create(
            usuario=self.other_user,
            rutina=self.rutina,
            dia_semana=DiaSemana.MARTES,
            activo=True,
        )

        self.rutina_url = reverse("rutina-list")
        self.plan_list_url = reverse("plan-semanal-list")

    def test_rutina_list_includes_total_ejercicios(self):
        """Debe incluir conteo total de ejercicios por rutina"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.rutina_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["total_ejercicios"], 1)

    def test_plan_semanal_list_returns_only_authenticated_user(self):
        """Debe listar solo los planes del usuario autenticado"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.plan_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["dia_semana"], DiaSemana.LUNES)
        self.assertIn("rutina_nombre", response.data["results"][0])

    def test_plan_semanal_detail_uses_detail_serializer(self):
        """Detalle debe incluir objeto rutina completo"""
        self.client.force_authenticate(user=self.user)
        detail_url = reverse("plan-semanal-detail", args=[self.plan_user.id])
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("rutina", response.data)
        self.assertEqual(response.data["rutina"]["nombre"], "Espalda Inicial")


class UserEquipmentSelectionAPITest(APITestCase):
    """Tests para guardar y obtener selección de equipamiento del usuario."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="selection@example.com", password="SecurePass123!"
        )
        self.url = reverse("user-equipment")

        self.equip_1 = Equipamiento.objects.create(
            nombre="Mancuernas Ajustables", categoria=CategoriaEquipamiento.PESO_LIBRE
        )
        self.equip_2 = Equipamiento.objects.create(
            nombre="Elíptica Home", categoria=CategoriaEquipamiento.CARDIO
        )

    def test_get_user_equipment_selection_initially_empty(self):
        """Debe retornar lista vacía al iniciar."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["equipamientos"], [])

    def test_save_and_get_user_equipment_selection(self):
        """Debe persistir selección y poder recuperarla."""
        self.client.force_authenticate(user=self.user)
        payload = {"equipamientos": [self.equip_1.id, self.equip_2.id]}

        save_response = self.client.post(self.url, payload, format="json")
        self.assertEqual(save_response.status_code, status.HTTP_200_OK)
        self.assertEqual(save_response.data["equipamientos"], payload["equipamientos"])

        get_response = self.client.get(self.url)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            sorted(get_response.data["equipamientos"]),
            sorted(payload["equipamientos"]),
        )

    def test_save_user_equipment_selection_invalid_id(self):
        """Debe retornar 400 si se envía un ID inexistente."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.url,
            {"equipamientos": [self.equip_1.id, 999999]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("equipamientos", response.data)
