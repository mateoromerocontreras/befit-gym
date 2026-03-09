"""
Test Script for Routine Generator Service
==========================================

Este script prueba manualmente el servicio de generación de rutinas.
"""

import os
import sys
import django

# Setup Django
sys.path.append("/code")
os.environ.setdefault("DJANGO_PROJECT_SETTINGS_MODULE", "django_project.settings")
django.setup()

from accounts.models import User, Equipment
from accounts.services.routine_generator import generate_routine


def setup_test_user():
    """Configura un usuario de prueba con datos completos."""
    try:
        user = User.objects.get(email="test@example.com")
    except User.DoesNotExist:
        print("❌ Usuario test@example.com no existe.")
        print("   Crea el usuario primero o usa otro email.")
        return None

    # Actualizar perfil
    user.age = 28
    user.goal = "GAIN_MUSCLE"
    user.level = "INTERMEDIATE"
    user.weight = 75.0
    user.height = 1.75
    user.save()

    # Asignar equipamiento
    equipos = Equipment.objects.filter(category__in=["WEIGHTS", "MACHINE"])[:10]
    user.preferred_equipment.set(equipos)

    print(f"✅ Usuario configurado: {user.email}")
    print(f"   - Objetivo: {user.get_goal_display()}")
    print(f"   - Nivel: {user.get_level_display()}")
    print(f"   - Equipamiento: {user.preferred_equipment.count()} items")

    return user


def test_routine_generation():
    """Prueba la generación de rutina."""
    print("\n🚀 Iniciando test de generación de rutina...")
    print("=" * 60)

    # Setup usuario
    user = setup_test_user()
    if not user:
        return

    # Verificar API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n⚠️  GEMINI_API_KEY no configurada")
        print("   Define la variable de entorno antes de ejecutar:")
        print("   export GEMINI_API_KEY='tu_clave_aqui'")
        return

    print(f"\n✅ API Key configurada (primeros 10 chars): {api_key[:10]}...")

    # Generar rutina
    print("\n📝 Generando rutina para 3 días...")
    resultado = generate_routine(
        user_id=user.id, dias_semana=3, nombre_rutina="Plan Test IA"
    )

    # Mostrar resultado
    print("\n" + "=" * 60)
    if resultado["success"]:
        print("✅ RUTINA GENERADA EXITOSAMENTE")
        print(f"   - Rutina ID: {resultado['rutina_id']}")
        print(f"   - Planes creados: {len(resultado['plan_ids'])}")
        print(f"   - Total ejercicios: {resultado['ejercicios_count']}")
        print(f"   - Mensaje: {resultado['mensaje']}")
    else:
        print("❌ ERROR AL GENERAR RUTINA")
        print(f"   - Error: {resultado.get('error', 'Desconocido')}")
        print(f"   - Mensaje: {resultado.get('mensaje', '')}")

    print("=" * 60)


if __name__ == "__main__":
    test_routine_generation()
