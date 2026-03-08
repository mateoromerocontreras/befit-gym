from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

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
