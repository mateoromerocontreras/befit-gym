from accounts.models import User, Equipment, TrainingGoal, TrainingLevel
from accounts.services.routine_generator import RoutineGeneratorService
import json

TARGET_EMAIL = "estudiante@mail.com"

user = User.objects.filter(email=TARGET_EMAIL).first()
if not user:
    user = User.objects.first()

if not user:
    user = User.objects.create_user(
        email=TARGET_EMAIL,
        password="test1234",
        goal=TrainingGoal.GENERAL_HEALTH,
        level=TrainingLevel.BEGINNER,
    )
    print(f"ℹ️ Usuario de prueba creado: {user.email}")

equipment_qs = Equipment.objects.all()
if not equipment_qs.exists():
    raise SystemExit(
        "❌ No hay equipamiento cargado. Ejecuta seed_initial_data antes de esta prueba."
    )

if not user.preferred_equipment.exists():
    user.preferred_equipment.set(equipment_qs)
    print("ℹ️ Equipamiento asignado al usuario de prueba.")

service = RoutineGeneratorService()

print(f"--- Iniciando generación para {user.email} ---")
try:
    routine = service.generate_routine_for_user(user_id=user.id, training_days=3)
    print("✅ RUTINA GENERADA CON ÉXITO:")
    print(json.dumps(routine, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"❌ ERROR EN LA GENERACIÓN: {e}")