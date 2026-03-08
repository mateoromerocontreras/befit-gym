from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Ejercicio, Rutina, RutinaEjercicio, PlanSemanal, Equipamiento

User = get_user_model()


class EquipamientoSerializer(serializers.ModelSerializer):
    """Serializer para Equipamiento con etiqueta de categoría"""

    categoria_display = serializers.CharField(
        source="get_categoria_display", read_only=True
    )

    class Meta:
        model = Equipamiento
        fields = (
            "id",
            "nombre",
            "categoria",
            "categoria_display",
        )


class UserEquipmentSelectionSerializer(serializers.Serializer):
    """Serializer para guardar selección de equipamientos de un usuario."""

    equipment_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=True,
        required=True,
    )

    def to_internal_value(self, data):
        normalized_data = dict(data)
        # Compatibilidad hacia atrás con payload antiguo
        if (
            "equipment_ids" not in normalized_data
            and "equipamientos" in normalized_data
        ):
            normalized_data["equipment_ids"] = normalized_data["equipamientos"]
        return super().to_internal_value(normalized_data)

    def validate_equipment_ids(self, value):
        # Eliminar duplicados preservando orden
        unique_ids = list(dict.fromkeys(value))
        existing_ids = set(
            Equipamiento.objects.filter(id__in=unique_ids).values_list("id", flat=True)
        )
        missing_ids = [
            equipment_id
            for equipment_id in unique_ids
            if equipment_id not in existing_ids
        ]

        if missing_ids:
            raise serializers.ValidationError(
                f"IDs de equipamiento inválidos: {missing_ids}"
            )

        return unique_ids


class GenerateRoutineSerializer(serializers.Serializer):
    """Serializer para solicitud de generación de rutina con IA."""

    dias_semana = serializers.IntegerField(
        min_value=1, max_value=7, default=3, help_text="Número de días de entrenamiento"
    )
    nombre_rutina = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="Nombre personalizado",
    )


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("email", "password", "password2")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"], password=validated_data["password"]
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class UserSerializer(serializers.ModelSerializer):
    objetivo_display = serializers.CharField(
        source="get_objetivo_display", read_only=True
    )
    nivel_display = serializers.CharField(source="get_nivel_display", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "peso",
            "altura",
            "edad",
            "objetivo",
            "objetivo_display",
            "nivel",
            "nivel_display",
            "suscripcion_activa",
            "date_joined",
        )
        read_only_fields = ("id", "email", "date_joined")


# Serializers para el Plan de Entrenamiento


class EjercicioSerializer(serializers.ModelSerializer):
    grupo_muscular_display = serializers.CharField(
        source="get_grupo_muscular_display", read_only=True
    )
    dificultad_display = serializers.CharField(
        source="get_dificultad_display", read_only=True
    )
    equipamientos = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="nombre",
    )

    class Meta:
        model = Ejercicio
        fields = (
            "id",
            "nombre",
            "descripcion",
            "grupo_muscular",
            "grupo_muscular_display",
            "dificultad",
            "dificultad_display",
            "imagen_url",
            "equipamientos",
        )


class RutinaEjercicioSerializer(serializers.ModelSerializer):
    ejercicio = EjercicioSerializer(read_only=True)

    class Meta:
        model = RutinaEjercicio
        fields = (
            "id",
            "ejercicio",
            "series",
            "repeticiones",
            "descanso_segundos",
            "orden",
            "notas",
        )


class RutinaSerializer(serializers.ModelSerializer):
    ejercicios_detalle = RutinaEjercicioSerializer(
        source="rutina_ejercicios", many=True, read_only=True
    )
    nivel_display = serializers.CharField(source="get_nivel_display", read_only=True)
    total_ejercicios = serializers.SerializerMethodField()

    class Meta:
        model = Rutina
        fields = (
            "id",
            "nombre",
            "descripcion",
            "duracion_minutos",
            "nivel",
            "nivel_display",
            "total_ejercicios",
            "ejercicios_detalle",
        )

    def get_total_ejercicios(self, obj):
        return obj.ejercicios.count()


class PlanSemanalSerializer(serializers.ModelSerializer):
    rutina = RutinaSerializer(read_only=True)
    dia_semana_display = serializers.CharField(
        source="get_dia_semana_display", read_only=True
    )
    rutina_id = serializers.PrimaryKeyRelatedField(
        queryset=Rutina.objects.all(), source="rutina", write_only=True
    )

    class Meta:
        model = PlanSemanal
        fields = (
            "id",
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

    def create(self, validated_data):
        validated_data["usuario"] = self.context["request"].user
        return super().create(validated_data)


class PlanSemanalListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar todos los días de la semana"""

    rutina_nombre = serializers.CharField(source="rutina.nombre", read_only=True)
    rutina_duracion = serializers.IntegerField(
        source="rutina.duracion_minutos", read_only=True
    )
    dia_semana_display = serializers.CharField(
        source="get_dia_semana_display", read_only=True
    )
    total_ejercicios = serializers.SerializerMethodField()

    class Meta:
        model = PlanSemanal
        fields = (
            "id",
            "dia_semana",
            "dia_semana_display",
            "rutina_nombre",
            "rutina_duracion",
            "total_ejercicios",
            "activo",
            "notas",
        )

    def get_total_ejercicios(self, obj):
        return obj.rutina.ejercicios.count()
