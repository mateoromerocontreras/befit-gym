from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from .models import (
    Exercise,
    Routine,
    RoutineExercise,
    WeeklyPlan,
    Equipment,
    TrainingGoal,
    TrainingLevel,
    UserTrainingWeekday,
    Weekday,
)

User = get_user_model()


class EquipmentSerializer(serializers.ModelSerializer):
    """Serializer for Equipment with category label."""

    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )

    class Meta:
        model = Equipment
        fields = (
            "id",
            "name",
            "category",
            "category_display",
        )


class UserEquipmentSelectionSerializer(serializers.Serializer):
    """Serializer to save selected user equipment."""

    equipment_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=True,
        required=True,
    )

    def to_internal_value(self, data):
        normalized_data = dict(data)
        # Backward compatibility with legacy payload
        if (
            "equipment_ids" not in normalized_data
            and "equipamientos" in normalized_data
        ):
            normalized_data["equipment_ids"] = normalized_data["equipamientos"]
        return super().to_internal_value(normalized_data)

    def validate_equipment_ids(self, value):
        # Remove duplicates preserving order
        unique_ids = list(dict.fromkeys(value))
        existing_ids = set(
            Equipment.objects.filter(id__in=unique_ids).values_list("id", flat=True)
        )
        missing_ids = [
            equipment_id
            for equipment_id in unique_ids
            if equipment_id not in existing_ids
        ]

        if missing_ids:
            raise serializers.ValidationError(
                _("Invalid equipment IDs: %(ids)s") % {"ids": missing_ids}
            )

        return unique_ids


class GenerateRoutineSerializer(serializers.Serializer):
    """Serializer for AI routine generation request."""

    training_days = serializers.IntegerField(
        min_value=1,
        max_value=7,
        default=3,
        help_text=_("Number of training days"),
        required=False,
    )
    routine_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text=_("Custom routine name"),
    )
    training_weekdays = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=7),
        required=False,
        allow_empty=False,
        help_text=_("Preferred weekdays (1=Monday ... 7=Sunday)"),
    )

    def validate_training_weekdays(self, value):
        unique_days = list(dict.fromkeys(value))
        if len(unique_days) != len(value):
            raise serializers.ValidationError(_("Training weekdays cannot contain duplicates"))
        return sorted(unique_days)

    def to_internal_value(self, data):
        normalized_data = dict(data)
        if "training_days" not in normalized_data and "dias_semana" in normalized_data:
            normalized_data["training_days"] = normalized_data["dias_semana"]
        if "routine_name" not in normalized_data and "nombre_rutina" in normalized_data:
            normalized_data["routine_name"] = normalized_data["nombre_rutina"]
        if "training_weekdays" not in normalized_data and "dias_entrenamiento" in normalized_data:
            normalized_data["training_weekdays"] = normalized_data["dias_entrenamiento"]
        return super().to_internal_value(normalized_data)


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    age = serializers.IntegerField(required=False, min_value=1, max_value=120)
    goal = serializers.ChoiceField(
        choices=TrainingGoal.choices,
        required=False,
    )
    level = serializers.ChoiceField(
        choices=TrainingLevel.choices,
        required=False,
    )

    class Meta:
        model = User
        fields = ("email", "password", "password2", "age", "goal", "level")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": _("Password fields didn't match.")}
            )
        return attrs

    def create(self, validated_data):
        extra_fields = {}
        for field in ("age", "goal", "level"):
            if field in validated_data:
                extra_fields[field] = validated_data[field]

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            **extra_fields,
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class UserSerializer(serializers.ModelSerializer):
    goal_display = serializers.CharField(source="get_goal_display", read_only=True)
    level_display = serializers.CharField(source="get_level_display", read_only=True)

    # Legacy aliases (read-only)
    objetivo_display = serializers.CharField(source="get_goal_display", read_only=True)
    nivel_display = serializers.CharField(source="get_level_display", read_only=True)
    peso = serializers.DecimalField(source="weight", max_digits=5, decimal_places=2, read_only=True)
    altura = serializers.DecimalField(source="height", max_digits=4, decimal_places=2, read_only=True)
    edad = serializers.IntegerField(source="age", read_only=True)
    objetivo = serializers.CharField(source="goal", read_only=True)
    nivel = serializers.CharField(source="level", read_only=True)
    suscripcion_activa = serializers.BooleanField(source="active_subscription", read_only=True)
    training_weekdays = serializers.SerializerMethodField()
    training_weekdays_input = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=7),
        required=False,
        allow_empty=False,
        write_only=True,
    )
    dias_entrenamiento = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "weight",
            "height",
            "age",
            "goal",
            "goal_display",
            "level",
            "level_display",
            "active_subscription",
            "peso",
            "altura",
            "edad",
            "objetivo",
            "objetivo_display",
            "nivel",
            "nivel_display",
            "suscripcion_activa",
            "training_weekdays",
            "training_weekdays_input",
            "dias_entrenamiento",
            "date_joined",
        )
        read_only_fields = ("id", "email", "date_joined")

    def get_training_weekdays(self, instance):
        return list(
            instance.training_weekdays.values_list("weekday", flat=True).order_by("weekday")
        )

    def get_dias_entrenamiento(self, instance):
        return self.get_training_weekdays(instance)

    def validate_training_weekdays_input(self, value):
        unique_days = list(dict.fromkeys(value))
        if len(unique_days) != len(value):
            raise serializers.ValidationError(_("Training weekdays cannot contain duplicates"))
        invalid_days = [day for day in unique_days if day not in [choice.value for choice in Weekday]]
        if invalid_days:
            raise serializers.ValidationError(
                _("Invalid weekdays: %(days)s") % {"days": invalid_days}
            )
        return sorted(unique_days)

    def to_internal_value(self, data):
        normalized_data = dict(data)
        alias_map = {
            "peso": "weight",
            "altura": "height",
            "edad": "age",
            "objetivo": "goal",
            "nivel": "level",
            "dias_entrenamiento": "training_weekdays_input",
            "training_weekdays": "training_weekdays_input",
        }
        for old_key, new_key in alias_map.items():
            if new_key not in normalized_data and old_key in normalized_data:
                normalized_data[new_key] = normalized_data[old_key]

        goal_value_map = {
            "PERDER_PESO": "LOSE_WEIGHT",
            "GANAR_MASA": "GAIN_MUSCLE",
            "TONIFICAR": "TONE",
            "FUERZA": "STRENGTH",
            "RESISTENCIA": "ENDURANCE",
            "SALUD_GENERAL": "GENERAL_HEALTH",
        }
        level_value_map = {
            "PRINCIPIANTE": "BEGINNER",
            "INTERMEDIO": "INTERMEDIATE",
            "AVANZADO": "ADVANCED",
        }

        if "goal" in normalized_data:
            normalized_data["goal"] = goal_value_map.get(
                normalized_data["goal"], normalized_data["goal"]
            )

        if "level" in normalized_data:
            normalized_data["level"] = level_value_map.get(
                normalized_data["level"], normalized_data["level"]
            )
        return super().to_internal_value(normalized_data)

    def update(self, instance, validated_data):
        training_weekdays = validated_data.pop("training_weekdays_input", None)
        instance = super().update(instance, validated_data)

        if training_weekdays is not None:
            UserTrainingWeekday.objects.filter(user=instance).delete()
            UserTrainingWeekday.objects.bulk_create(
                [
                    UserTrainingWeekday(user=instance, weekday=weekday)
                    for weekday in training_weekdays
                ]
            )

        return instance


# Training Plan serializers


class ExerciseSerializer(serializers.ModelSerializer):
    muscle_group_display = serializers.CharField(
        source="get_muscle_group_display", read_only=True
    )
    difficulty_display = serializers.CharField(
        source="get_difficulty_display", read_only=True
    )
    equipment = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
    )

    # Legacy aliases
    grupo_muscular_display = serializers.CharField(source="get_muscle_group_display", read_only=True)
    dificultad_display = serializers.CharField(source="get_difficulty_display", read_only=True)
    equipamientos = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name", source="equipment")

    class Meta:
        model = Exercise
        fields = (
            "id",
            "name",
            "description",
            "muscle_group",
            "muscle_group_display",
            "difficulty",
            "difficulty_display",
            "image_url",
            "equipment",
            "nombre",
            "descripcion",
            "grupo_muscular",
            "grupo_muscular_display",
            "dificultad",
            "dificultad_display",
            "imagen_url",
            "equipamientos",
        )

    nombre = serializers.CharField(source="name", read_only=True)
    descripcion = serializers.CharField(source="description", read_only=True)
    grupo_muscular = serializers.CharField(source="muscle_group", read_only=True)
    dificultad = serializers.CharField(source="difficulty", read_only=True)
    imagen_url = serializers.CharField(source="image_url", read_only=True)


class RoutineExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)

    # Legacy alias
    ejercicio = ExerciseSerializer(read_only=True, source="exercise")

    class Meta:
        model = RoutineExercise
        fields = (
            "id",
            "exercise",
            "series",
            "repetitions",
            "rest_seconds",
            "order",
            "notes",
            "ejercicio",
            "repeticiones",
            "descanso_segundos",
            "orden",
            "notas",
        )

    repeticiones = serializers.CharField(source="repetitions", read_only=True)
    descanso_segundos = serializers.IntegerField(source="rest_seconds", read_only=True)
    orden = serializers.IntegerField(source="order", read_only=True)
    notas = serializers.CharField(source="notes", read_only=True)


class RoutineSerializer(serializers.ModelSerializer):
    exercise_details = RoutineExerciseSerializer(
        source="routine_exercises", many=True, read_only=True
    )
    level_display = serializers.CharField(source="get_level_display", read_only=True)
    total_exercises = serializers.SerializerMethodField()

    # Legacy aliases
    ejercicios_detalle = RoutineExerciseSerializer(source="routine_exercises", many=True, read_only=True)
    nivel_display = serializers.CharField(source="get_level_display", read_only=True)
    total_ejercicios = serializers.SerializerMethodField()
    nombre = serializers.CharField(source="name", read_only=True)
    descripcion = serializers.CharField(source="description", read_only=True)
    duracion_minutos = serializers.IntegerField(source="duration_minutes", read_only=True)
    nivel = serializers.CharField(source="level", read_only=True)

    class Meta:
        model = Routine
        fields = (
            "id",
            "name",
            "description",
            "duration_minutes",
            "level",
            "level_display",
            "total_exercises",
            "exercise_details",
            "nombre",
            "descripcion",
            "duracion_minutos",
            "nivel",
            "nivel_display",
            "total_ejercicios",
            "ejercicios_detalle",
        )

    def get_total_exercises(self, obj):
        return obj.exercises.count()

    def get_total_ejercicios(self, obj):
        return obj.exercises.count()


class WeeklyPlanSerializer(serializers.ModelSerializer):
    routine = RoutineSerializer(read_only=True)
    weekday_display = serializers.CharField(
        source="get_weekday_display", read_only=True
    )
    routine_id = serializers.PrimaryKeyRelatedField(
        queryset=Routine.objects.all(), source="routine", write_only=True
    )

    # Legacy aliases
    rutina = RoutineSerializer(read_only=True, source="routine")
    dia_semana_display = serializers.CharField(source="get_weekday_display", read_only=True)
    rutina_id = serializers.PrimaryKeyRelatedField(queryset=Routine.objects.all(), source="routine", write_only=True)
    dia_semana = serializers.IntegerField(source="weekday", read_only=True)
    activo = serializers.BooleanField(source="active", read_only=True)
    notas = serializers.CharField(source="notes", read_only=True)

    class Meta:
        model = WeeklyPlan
        fields = (
            "id",
            "weekday",
            "weekday_display",
            "routine",
            "routine_id",
            "active",
            "notes",
            "dia_semana",
            "dia_semana_display",
            "rutina",
            "rutina_id",
            "activo",
            "notas",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def to_internal_value(self, data):
        normalized_data = dict(data)
        alias_map = {
            "dia_semana": "weekday",
            "rutina_id": "routine_id",
            "activo": "active",
            "notas": "notes",
        }
        for old_key, new_key in alias_map.items():
            if new_key not in normalized_data and old_key in normalized_data:
                normalized_data[new_key] = normalized_data[old_key]
        return super().to_internal_value(normalized_data)

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class WeeklyPlanListSerializer(serializers.ModelSerializer):
    """Simplified serializer to list all weekdays."""

    routine_name = serializers.CharField(source="routine.name", read_only=True)
    routine_duration = serializers.IntegerField(
        source="routine.duration_minutes", read_only=True
    )
    weekday_display = serializers.CharField(
        source="get_weekday_display", read_only=True
    )
    total_exercises = serializers.SerializerMethodField()

    # Legacy aliases
    rutina_nombre = serializers.CharField(source="routine.name", read_only=True)
    rutina_duracion = serializers.IntegerField(source="routine.duration_minutes", read_only=True)
    dia_semana_display = serializers.CharField(source="get_weekday_display", read_only=True)
    total_ejercicios = serializers.SerializerMethodField()
    dia_semana = serializers.IntegerField(source="weekday", read_only=True)
    activo = serializers.BooleanField(source="active", read_only=True)
    notas = serializers.CharField(source="notes", read_only=True)

    class Meta:
        model = WeeklyPlan
        fields = (
            "id",
            "weekday",
            "weekday_display",
            "routine_name",
            "routine_duration",
            "total_exercises",
            "active",
            "notes",
            "dia_semana",
            "dia_semana_display",
            "rutina_nombre",
            "rutina_duracion",
            "total_ejercicios",
            "activo",
            "notas",
        )

    def get_total_exercises(self, obj):
        return obj.routine.exercises.count()

    def get_total_ejercicios(self, obj):
        return obj.routine.exercises.count()


class WeeklyPlanExerciseCalendarSerializer(serializers.ModelSerializer):
    """Exercise payload optimized for weekly calendar UI."""

    name = serializers.CharField(source="exercise.name", read_only=True)
    muscle_group = serializers.CharField(source="exercise.muscle_group", read_only=True)
    difficulty = serializers.CharField(source="exercise.difficulty", read_only=True)

    class Meta:
        model = RoutineExercise
        fields = (
            "id",
            "name",
            "muscle_group",
            "difficulty",
            "series",
            "repetitions",
            "order",
            "notes",
        )


class WeeklyPlanCalendarSerializer(serializers.ModelSerializer):
    """Weekly plan serializer for calendar view on dashboard."""

    day = serializers.IntegerField(source="weekday", read_only=True)
    day_name = serializers.SerializerMethodField()
    focus = serializers.CharField(source="routine.name", read_only=True)
    exercises = WeeklyPlanExerciseCalendarSerializer(
        source="routine.routine_exercises", many=True, read_only=True
    )

    class Meta:
        model = WeeklyPlan
        fields = (
            "id",
            "day",
            "day_name",
            "focus",
            "active",
            "notes",
            "exercises",
        )

    def get_day_name(self, obj):
        routine_name = obj.routine.name if obj.routine else ""
        weekday_name = obj.get_weekday_display()
        return f"{weekday_name} - {routine_name}" if routine_name else weekday_name


# Backward-compatibility aliases (Phase 1)
EquipamientoSerializer = EquipmentSerializer
EjercicioSerializer = ExerciseSerializer
RutinaEjercicioSerializer = RoutineExerciseSerializer
RutinaSerializer = RoutineSerializer
PlanSemanalSerializer = WeeklyPlanSerializer
PlanSemanalListSerializer = WeeklyPlanListSerializer
