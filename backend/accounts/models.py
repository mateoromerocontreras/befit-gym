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


class TrainingGoal(models.TextChoices):
    LOSE_WEIGHT = "LOSE_WEIGHT", "Lose Weight"
    GAIN_MUSCLE = "GAIN_MUSCLE", "Gain Muscle"
    TONE = "TONE", "Tone"
    STRENGTH = "STRENGTH", "Increase Strength"
    ENDURANCE = "ENDURANCE", "Improve Endurance"
    GENERAL_HEALTH = "GENERAL_HEALTH", "General Health"


class TrainingLevel(models.TextChoices):
    BEGINNER = "BEGINNER", "Beginner"
    INTERMEDIATE = "INTERMEDIATE", "Intermediate"
    ADVANCED = "ADVANCED", "Advanced"


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="Weight in kg"
    )
    height = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Height in meters",
    )
    age = models.PositiveIntegerField(
        null=True, blank=True, help_text="User age"
    )
    goal = models.CharField(
        max_length=20,
        choices=TrainingGoal.choices,
        default=TrainingGoal.GENERAL_HEALTH,
        help_text="Primary training goal",
    )
    level = models.CharField(
        max_length=20,
        choices=TrainingLevel.choices,
        default=TrainingLevel.BEGINNER,
        help_text="Training experience level",
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    active_subscription = models.BooleanField(
        default=False, help_text="Indicates if the member has an active subscription"
    )
    preferred_equipment = models.ManyToManyField(
        "Equipment",
        related_name="users_with_preference",
        blank=True,
    )
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class MuscleGroup(models.TextChoices):
    CHEST = "CHEST", "Chest"
    BACK = "BACK", "Back"
    LEGS = "LEGS", "Legs"
    SHOULDERS = "SHOULDERS", "Shoulders"
    ARMS = "ARMS", "Arms"
    CORE = "CORE", "Core"
    FULL_BODY = "FULL_BODY", "Full Body"


class ExerciseDifficulty(models.TextChoices):
    BEGINNER = "BEGINNER", "Beginner"
    INTERMEDIATE = "INTERMEDIATE", "Intermediate"
    ADVANCED = "ADVANCED", "Advanced"


class EquipmentCategory(models.TextChoices):
    WEIGHTS = "WEIGHTS", "Weights"
    MACHINE = "MACHINE", "Machine"
    CARDIO = "CARDIO", "Cardio"
    ACCESSORY = "ACCESSORY", "Accessory"
    CALISTHENICS = "CALISTHENICS", "Calisthenics"


class Equipment(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=20,
        choices=EquipmentCategory.choices,
        default=EquipmentCategory.ACCESSORY,
    )

    class Meta:
        verbose_name = "Equipment"
        verbose_name_plural = "Equipment"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Exercise(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    muscle_group = models.CharField(
        max_length=20, choices=MuscleGroup.choices, default=MuscleGroup.FULL_BODY
    )
    difficulty = models.CharField(
        max_length=20,
        choices=ExerciseDifficulty.choices,
        default=ExerciseDifficulty.INTERMEDIATE,
    )
    image_url = models.URLField(blank=True, null=True)
    equipment = models.ManyToManyField(
        Equipment,
        related_name="exercises",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = "Exercise"
        verbose_name_plural = "Exercises"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_muscle_group_display()})"


class Routine(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    exercises = models.ManyToManyField(
        Exercise, through="RoutineExercise", related_name="routines"
    )
    duration_minutes = models.PositiveIntegerField(
        default=60, help_text="Estimated duration in minutes"
    )
    level = models.CharField(
        max_length=20,
        choices=[
            ("BEGINNER", "Beginner"),
            ("INTERMEDIATE", "Intermediate"),
            ("ADVANCED", "Advanced"),
        ],
        default="INTERMEDIATE",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Routine"
        verbose_name_plural = "Routines"
        ordering = ["name"]

    def __str__(self):
        return self.name


class RoutineExercise(models.Model):
    routine = models.ForeignKey(
        Routine, on_delete=models.CASCADE, related_name="routine_exercises"
    )
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    series = models.PositiveIntegerField(default=3)
    repetitions = models.CharField(
        max_length=20, default="12", help_text="Ex: 12, 10-12, to failure"
    )
    rest_seconds = models.PositiveIntegerField(default=60)
    order = models.PositiveIntegerField(default=0)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Exercise in Routine"
        verbose_name_plural = "Exercises in Routine"
        ordering = ["order"]
        unique_together = ["routine", "exercise"]

    def __str__(self):
        return f"{self.exercise.name} - {self.series}x{self.repetitions}"


class Weekday(models.IntegerChoices):
    MONDAY = 1, "Monday"
    TUESDAY = 2, "Tuesday"
    WEDNESDAY = 3, "Wednesday"
    THURSDAY = 4, "Thursday"
    FRIDAY = 5, "Friday"
    SATURDAY = 6, "Saturday"
    SUNDAY = 7, "Sunday"


class UserTrainingWeekday(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="training_weekdays"
    )
    weekday = models.IntegerField(choices=Weekday.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Training Weekday"
        verbose_name_plural = "User Training Weekdays"
        ordering = ["weekday"]
        unique_together = ["user", "weekday"]

    def __str__(self):
        return f"{self.user.email} - {Weekday(self.weekday).label}"


class WeeklyPlan(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="weekly_plans"
    )
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name="plans")
    weekday = models.IntegerField(choices=Weekday.choices)
    active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, help_text="Additional notes for this day")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Weekly Plan"
        verbose_name_plural = "Weekly Plans"
        ordering = ["weekday"]
        unique_together = ["user", "weekday"]

    def __str__(self):
        return f"{self.user.email} - {self.get_weekday_display()} - {self.routine.name}"


# Backward-compatibility aliases (Phase 1)
ObjetivoEntrenamiento = TrainingGoal
NivelEntrenamiento = TrainingLevel
GrupoMuscular = MuscleGroup
DificultadEjercicio = ExerciseDifficulty
CategoriaEquipamiento = EquipmentCategory
Equipamiento = Equipment
Ejercicio = Exercise
Rutina = Routine
RutinaEjercicio = RoutineExercise
DiaSemana = Weekday
PlanSemanal = WeeklyPlan
DiaEntrenamientoUsuario = UserTrainingWeekday
