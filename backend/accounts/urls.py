from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    ExerciseViewSet,
    RoutineViewSet,
    WeeklyPlanViewSet,
    EquipmentViewSet,
    UserEquipmentSelectionView,
    GenerateRoutineView,
    UserProfileView,
)

# Primary router with English endpoints
router = DefaultRouter()
router.register(r"equipment", EquipmentViewSet, basename="equipment")
router.register(r"exercises", ExerciseViewSet, basename="exercise")
router.register(r"routines", RoutineViewSet, basename="routine")
router.register(r"weekly-plan", WeeklyPlanViewSet, basename="weekly-plan")

urlpatterns = [
    # Auth endpoints
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path(
        "user-equipment/", UserEquipmentSelectionView.as_view(), name="user-equipment"
    ),
    path(
        "user-equipamiento/",
        UserEquipmentSelectionView.as_view(),
        name="user-equipamiento",
    ),
    path("generate-routine/", GenerateRoutineView.as_view(), name="generate-routine"),
    path("generar-rutina/", GenerateRoutineView.as_view(), name="generar-rutina"),
    # API endpoints (router) - English primary routes
    path("", include(router.urls)),
    # Legacy aliases (Spanish) - manually created to avoid converter conflicts
    re_path(r"^equipamientos/$", EquipmentViewSet.as_view({"get": "list"}), name="equipamiento-list"),
    re_path(r"^equipamientos/(?P<pk>\d+)/$", EquipmentViewSet.as_view({"get": "retrieve"}), name="equipamiento-detail"),
    re_path(r"^ejercicios/$", ExerciseViewSet.as_view({"get": "list"}), name="ejercicio-list"),
    re_path(r"^ejercicios/(?P<pk>\d+)/$", ExerciseViewSet.as_view({"get": "retrieve"}), name="ejercicio-detail"),
    re_path(r"^rutinas/$", RoutineViewSet.as_view({"get": "list"}), name="rutina-list"),
    re_path(r"^rutinas/(?P<pk>\d+)/$", RoutineViewSet.as_view({"get": "retrieve"}), name="rutina-detail"),
    re_path(r"^plan-semanal/$", WeeklyPlanViewSet.as_view({"get": "list"}), name="plan-semanal-list"),
    re_path(r"^plan-semanal/(?P<pk>\d+)/$", WeeklyPlanViewSet.as_view({"get": "retrieve"}), name="plan-semanal-detail"),
]
