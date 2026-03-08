from rest_framework import status, generics, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework import serializers
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    EjercicioSerializer,
    RutinaSerializer,
    PlanSemanalSerializer,
    PlanSemanalListSerializer,
    EquipamientoSerializer,
    UserEquipmentSelectionSerializer,
)
from .models import Ejercicio, Rutina, PlanSemanal, Equipamiento


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
                "message": "User registered successfully",
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
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {"error": "User account is disabled"}, status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "message": "Login successful",
            },
            status=status.HTTP_200_OK,
        )


class EjercicioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para listar ejercicios disponibles.
    Requiere autenticación.
    """

    queryset = Ejercicio.objects.prefetch_related("equipamientos").all()
    serializer_class = EjercicioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Ejercicio.objects.prefetch_related("equipamientos").all()
        grupo_muscular = self.request.query_params.get("grupo_muscular", None)
        if grupo_muscular:
            queryset = queryset.filter(grupo_muscular=grupo_muscular)
        return queryset


class RutinaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para listar rutinas disponibles.
    Requiere autenticación.
    """

    queryset = Rutina.objects.prefetch_related(
        "rutina_ejercicios__ejercicio__equipamientos"
    ).all()
    serializer_class = RutinaSerializer
    permission_classes = [IsAuthenticated]


class PlanSemanalViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para el plan semanal del usuario autenticado.
    Solo muestra los planes del usuario actual.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtra los planes solo para el usuario autenticado."""
        return (
            PlanSemanal.objects.filter(usuario=self.request.user)
            .select_related("rutina")
            .prefetch_related("rutina__rutina_ejercicios__ejercicio__equipamientos")
            .order_by("dia_semana")
        )

    def get_serializer_class(self):
        """Usa serializer simplificado para lista, completo para detalle."""
        if self.action == "list":
            return PlanSemanalListSerializer
        return PlanSemanalSerializer


class EquipamientoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para listar equipamientos disponibles.
    Requiere autenticación.
    """

    queryset = Equipamiento.objects.all().order_by("nombre")
    serializer_class = EquipamientoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Equipamiento.objects.all().order_by("nombre")
        categoria = self.request.query_params.get("categoria", None)
        if categoria:
            queryset = queryset.filter(categoria=categoria)
        return queryset


class UserEquipmentSelectionView(APIView):
    """Gestiona la selección de equipamientos del usuario autenticado."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        selected_ids = list(
            request.user.equipamientos_preferidos.values_list("id", flat=True).order_by(
                "nombre"
            )
        )
        return Response({"equipamientos": selected_ids}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserEquipmentSelectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        selected_ids = serializer.validated_data["equipamientos"]
        request.user.equipamientos_preferidos.set(selected_ids)

        return Response(
            {
                "message": "Selección de equipamientos guardada correctamente",
                "equipamientos": selected_ids,
            },
            status=status.HTTP_200_OK,
        )
