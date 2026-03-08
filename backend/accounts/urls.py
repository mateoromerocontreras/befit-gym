from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    EjercicioViewSet,
    RutinaViewSet,
    PlanSemanalViewSet,
    EquipamientoViewSet,
    UserEquipmentSelectionView,
)

# Router para los ViewSets
router = DefaultRouter()
router.register(r"equipamientos", EquipamientoViewSet, basename="equipamiento")
router.register(r"ejercicios", EjercicioViewSet, basename="ejercicio")
router.register(r"rutinas", RutinaViewSet, basename="rutina")
router.register(r"plan-semanal", PlanSemanalViewSet, basename="plan-semanal")

urlpatterns = [
    # Auth endpoints
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "user-equipment/", UserEquipmentSelectionView.as_view(), name="user-equipment"
    ),
    # API endpoints (router)
    path("", include(router.urls)),
]
