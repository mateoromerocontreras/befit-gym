from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class ObjetivoEntrenamiento(models.TextChoices):
    PERDER_PESO = "PERDER_PESO", "Perder Peso"
    GANAR_MASA = "GANAR_MASA", "Ganar Masa Muscular"
    TONIFICAR = "TONIFICAR", "Tonificar"
    FUERZA = "FUERZA", "Aumentar Fuerza"
    RESISTENCIA = "RESISTENCIA", "Mejorar Resistencia"
    SALUD_GENERAL = "SALUD_GENERAL", "Salud General"


class NivelEntrenamiento(models.TextChoices):
    PRINCIPIANTE = "PRINCIPIANTE", "Principiante"
    INTERMEDIO = "INTERMEDIO", "Intermedio"
    AVANZADO = "AVANZADO", "Avanzado"


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    peso = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="Peso en kg"
    )
    altura = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Altura en metros",
    )
    edad = models.PositiveIntegerField(
        null=True, blank=True, help_text="Edad del usuario"
    )
    objetivo = models.CharField(
        max_length=20,
        choices=ObjetivoEntrenamiento.choices,
        default=ObjetivoEntrenamiento.SALUD_GENERAL,
        help_text="Objetivo principal de entrenamiento",
    )
    nivel = models.CharField(
        max_length=20,
        choices=NivelEntrenamiento.choices,
        default=NivelEntrenamiento.PRINCIPIANTE,
        help_text="Nivel de experiencia en entrenamiento",
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    suscripcion_activa = models.BooleanField(
        default=False, help_text="Indica si el socio tiene membresía activa"
    )
    equipamientos_preferidos = models.ManyToManyField(
        "Equipamiento",
        related_name="usuarios_con_preferencia",
        blank=True,
    )
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class GrupoMuscular(models.TextChoices):
    PECHO = "PECHO", "Pecho"
    ESPALDA = "ESPALDA", "Espalda"
    HOMBROS = "HOMBROS", "Hombros"
    BICEPS = "BICEPS", "Bíceps"
    TRICEPS = "TRICEPS", "Tríceps"
    PIERNAS = "PIERNAS", "Piernas"
    GLUTEOS = "GLUTEOS", "Glúteos"
    ABDOMEN = "ABDOMEN", "Abdomen"
    CARDIO = "CARDIO", "Cardio"
    FULL_BODY = "FULL_BODY", "Full Body"


class DificultadEjercicio(models.TextChoices):
    PRINCIPIANTE = "PRINCIPIANTE", "Principiante"
    INTERMEDIO = "INTERMEDIO", "Intermedio"
    AVANZADO = "AVANZADO", "Avanzado"


class CategoriaEquipamiento(models.TextChoices):
    PESO_LIBRE = "PESO_LIBRE", "Peso Libre"
    MAQUINA = "MAQUINA", "Máquina"
    CARDIO = "CARDIO", "Cardio"
    ACCESORIO = "ACCESORIO", "Accesorio"
    CALISTENIA = "CALISTENIA", "Calistenia"


class Equipamiento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    categoria = models.CharField(
        max_length=20,
        choices=CategoriaEquipamiento.choices,
        default=CategoriaEquipamiento.ACCESORIO,
    )

    class Meta:
        verbose_name = "Equipamiento"
        verbose_name_plural = "Equipamientos"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()})"


class Ejercicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    grupo_muscular = models.CharField(
        max_length=20, choices=GrupoMuscular.choices, default=GrupoMuscular.FULL_BODY
    )
    dificultad = models.CharField(
        max_length=20,
        choices=DificultadEjercicio.choices,
        default=DificultadEjercicio.INTERMEDIO,
    )
    imagen_url = models.URLField(blank=True, null=True)
    equipamientos = models.ManyToManyField(
        Equipamiento,
        related_name="ejercicios",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = "Ejercicio"
        verbose_name_plural = "Ejercicios"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.get_grupo_muscular_display()})"


class Rutina(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    ejercicios = models.ManyToManyField(
        Ejercicio, through="RutinaEjercicio", related_name="rutinas"
    )
    duracion_minutos = models.PositiveIntegerField(
        default=60, help_text="Duración estimada en minutos"
    )
    nivel = models.CharField(
        max_length=20,
        choices=[
            ("PRINCIPIANTE", "Principiante"),
            ("INTERMEDIO", "Intermedio"),
            ("AVANZADO", "Avanzado"),
        ],
        default="INTERMEDIO",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rutina"
        verbose_name_plural = "Rutinas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class RutinaEjercicio(models.Model):
    rutina = models.ForeignKey(
        Rutina, on_delete=models.CASCADE, related_name="rutina_ejercicios"
    )
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    series = models.PositiveIntegerField(default=3)
    repeticiones = models.CharField(
        max_length=20, default="12", help_text="Ej: 12, 10-12, hasta el fallo"
    )
    descanso_segundos = models.PositiveIntegerField(default=60)
    orden = models.PositiveIntegerField(default=0)
    notas = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Ejercicio en Rutina"
        verbose_name_plural = "Ejercicios en Rutina"
        ordering = ["orden"]
        unique_together = ["rutina", "ejercicio"]

    def __str__(self):
        return f"{self.ejercicio.nombre} - {self.series}x{self.repeticiones}"


class DiaSemana(models.IntegerChoices):
    LUNES = 1, "Lunes"
    MARTES = 2, "Martes"
    MIERCOLES = 3, "Miércoles"
    JUEVES = 4, "Jueves"
    VIERNES = 5, "Viernes"
    SABADO = 6, "Sábado"
    DOMINGO = 7, "Domingo"


class PlanSemanal(models.Model):
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="planes_semanales"
    )
    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE, related_name="planes")
    dia_semana = models.IntegerField(choices=DiaSemana.choices)
    activo = models.BooleanField(default=True)
    notas = models.TextField(blank=True, help_text="Notas adicionales para este día")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plan Semanal"
        verbose_name_plural = "Planes Semanales"
        ordering = ["dia_semana"]
        unique_together = ["usuario", "dia_semana"]

    def __str__(self):
        return f"{self.usuario.email} - {self.get_dia_semana_display()} - {self.rutina.nombre}"
