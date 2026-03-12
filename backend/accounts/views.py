from rest_framework import status, generics, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework.views import APIView
from rest_framework import serializers
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    ExerciseSerializer,
    RoutineSerializer,
    WeeklyPlanSerializer,
    WeeklyPlanCalendarSerializer,
    EquipmentSerializer,
    UserEquipmentSelectionSerializer,
    GenerateRoutineSerializer,
)
from .models import Exercise, Routine, WeeklyPlan, Equipment
from .services.routine_generator import RoutineGeneratorService


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "message": _("User registered successfully"),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    class LoginSerializer(serializers.Serializer):
        email = serializers.EmailField(required=True)
        password = serializers.CharField(write_only=True, required=True)

    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        user = authenticate(email=email, password=password)

        if user is None:
            return Response(
                {"error": _("Invalid credentials")}, status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {"error": _("User account is disabled")}, status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "message": _("Login successful"),
            },
            status=status.HTTP_200_OK,
        )


class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only ViewSet for available exercises."""

    queryset = Exercise.objects.prefetch_related("equipment").all()
    serializer_class = ExerciseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Exercise.objects.prefetch_related("equipment").all()
        muscle_group = self.request.query_params.get("muscle_group", None)
        legacy_muscle_group = self.request.query_params.get("grupo_muscular", None)
        selected_muscle_group = muscle_group or legacy_muscle_group
        legacy_muscle_group_map = {
            "PECHO": "CHEST",
            "ESPALDA": "BACK",
            "HOMBROS": "SHOULDERS",
            "PIERNAS": "LEGS",
            "GLUTEOS": "LEGS",
            "BICEPS": "ARMS",
            "TRICEPS": "ARMS",
            "ABDOMEN": "CORE",
            "CARDIO": "FULL_BODY",
        }
        if selected_muscle_group in legacy_muscle_group_map:
            selected_muscle_group = legacy_muscle_group_map[selected_muscle_group]
        if selected_muscle_group:
            queryset = queryset.filter(muscle_group=selected_muscle_group)
        return queryset


class RoutineViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only ViewSet for available routines."""

    queryset = Routine.objects.prefetch_related(
        "routine_exercises__exercise__equipment"
    ).all()
    serializer_class = RoutineSerializer
    permission_classes = [IsAuthenticated]


class WeeklyPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only ViewSet for authenticated user's weekly plan."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter plans for the authenticated user only."""
        return (
            WeeklyPlan.objects.filter(user=self.request.user)
            .select_related("routine")
            .prefetch_related("routine__routine_exercises__exercise")
            .order_by("weekday")
        )

    def get_serializer_class(self):
        """Use calendar serializer for list, full serializer for detail."""
        if self.action == "list":
            return WeeklyPlanCalendarSerializer
        return WeeklyPlanSerializer


class EquipmentViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only ViewSet for available equipment."""

    queryset = Equipment.objects.all().order_by("name")
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Equipment.objects.all().order_by("name")
        category = self.request.query_params.get("category", None)
        legacy_category = self.request.query_params.get("categoria", None)
        selected_category = category or legacy_category
        legacy_category_map = {
            "PESO_LIBRE": "WEIGHTS",
            "MAQUINA": "MACHINE",
            "ACCESORIO": "ACCESSORY",
            "CALISTENIA": "CALISTHENICS",
        }
        if selected_category in legacy_category_map:
            selected_category = legacy_category_map[selected_category]
        if selected_category:
            queryset = queryset.filter(category=selected_category)
        return queryset


class UserEquipmentSelectionView(APIView):
    """Manage authenticated user's equipment selection."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        selected_ids = list(
            request.user.preferred_equipment.values_list("id", flat=True).order_by(
                "name"
            )
        )
        return Response(
            {"equipment_ids": selected_ids, "equipamientos": selected_ids},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = UserEquipmentSelectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        selected_ids = serializer.validated_data["equipment_ids"]
        request.user.preferred_equipment.set(selected_ids)

        return Response(
            {
                "message": _("Equipment selection saved successfully"),
                "equipment_ids": selected_ids,
                "equipamientos": selected_ids,
            },
            status=status.HTTP_200_OK,
        )


class GenerateRoutineView(APIView):
    """Generate a personalized training routine using Gemini AI."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GenerateRoutineSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        training_days = serializer.validated_data.get("training_days", 3)
        routine_name = serializer.validated_data.get("routine_name", None)
        training_weekdays = serializer.validated_data.get("training_weekdays", None)

        try:
            generator = RoutineGeneratorService()
            result = generator.generate_routine_for_user(
                user_id=request.user.id,
                training_days=training_days,
                routine_name=routine_name,
                training_weekdays=training_weekdays,
            )

            if result["success"]:
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                error_text = str(result.get("error", ""))
                if "QUOTA_EXCEEDED" in error_text or "429" in error_text or "quota" in error_text.lower():
                    return Response(
                        {
                            "error": result.get("message") or result.get("error"),
                            "code": "QUOTA_EXCEEDED",
                        },
                        status=status.HTTP_429_TOO_MANY_REQUESTS,
                    )
                return Response(
                    {"error": result.get("error", _("Unknown error"))},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": _("Internal error: %(error)s") % {"error": str(e)}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GenerateRoutinePrecheckView(APIView):
    """Validate prerequisites before generating AI routine."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        training_days_param = request.query_params.get("training_days")
        weekdays_param = request.query_params.get("training_weekdays", "")

        training_days = int(training_days_param) if training_days_param else 3
        training_weekdays = None

        if weekdays_param:
            training_weekdays = [
                int(item.strip()) for item in weekdays_param.split(",") if item.strip().isdigit()
            ]

        try:
            generator = RoutineGeneratorService(raise_on_missing_key=False)
            result = generator.get_generation_precheck(
                user_id=request.user.id,
                training_days=training_days,
                training_weekdays=training_weekdays,
            )
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": _("Internal error: %(error)s") % {"error": str(e)}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserProfileView(APIView):
    """Get and update authenticated user profile."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


# Backward-compatibility aliases (Phase 1)
EjercicioViewSet = ExerciseViewSet
RutinaViewSet = RoutineViewSet
PlanSemanalViewSet = WeeklyPlanViewSet
EquipamientoViewSet = EquipmentViewSet
