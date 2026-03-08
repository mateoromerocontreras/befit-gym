"""
Servicio de Generación de Rutinas con IA
=========================================

Este servicio utiliza Gemini AI para generar planes de entrenamiento personalizados
basados en el perfil del usuario y el equipamiento disponible.

Autor: Sistema de Entrenamiento Gym App
"""

import json
import os
from typing import Dict, List, Optional
from django.conf import settings
from django.db import transaction
import google.generativeai as genai
from accounts.models import (
    User,
    Ejercicio,
    Rutina,
    RutinaEjercicio,
    PlanSemanal,
    DiaSemana,
)


class RoutineGeneratorService:
    """
    Servicio para generar rutinas de entrenamiento personalizadas usando Gemini AI.

    Funcionalidades:
    - Analiza el perfil del usuario (objetivo, nivel, edad)
    - Filtra ejercicios basados en equipamiento disponible
    - Genera prompt optimizado para Gemini
    - Procesa respuesta JSON de la IA
    - Crea automáticamente Rutina, RutinaEjercicio y PlanSemanal
    """

    def __init__(self):
        """Inicializa el servicio y configura Gemini AI."""
        api_key = os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY no configurada. "
                "Define la variable de entorno o agrégala en settings.py"
            )

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def generate_routine_for_user(
        self, user_id: int, dias_semana: int = 3, nombre_rutina: Optional[str] = None
    ) -> Dict:
        """
        Genera un plan de entrenamiento completo para un usuario.

        Args:
            user_id: ID del usuario
            dias_semana: Número de días de entrenamiento (1-7)
            nombre_rutina: Nombre personalizado para la rutina (opcional)

        Returns:
            Dict con información de la rutina generada:
            {
                'success': bool,
                'rutina_id': int,
                'plan_ids': List[int],
                'mensaje': str,
                'ejercicios_count': int
            }

        Raises:
            ValueError: Si el usuario no existe o no tiene equipamiento
            Exception: Si hay error al comunicarse con Gemini
        """
        try:
            # 1. Obtener usuario y validar
            user = self._get_user_profile(user_id)

            # 2. Obtener ejercicios disponibles según equipamiento
            ejercicios_disponibles = self._get_available_exercises(user)

            if not ejercicios_disponibles:
                raise ValueError(
                    f"Usuario {user.email} no tiene equipamiento configurado. "
                    "Debe seleccionar equipamiento disponible primero."
                )

            # 3. Generar prompt para Gemini
            prompt = self._build_prompt(
                user=user, ejercicios=ejercicios_disponibles, dias_semana=dias_semana
            )

            # 4. Llamar a Gemini AI
            ai_response = self._call_gemini_api(prompt)

            # 5. Parsear respuesta JSON
            plan_data = self._parse_ai_response(ai_response)

            # 6. Crear rutinas y plan semanal en DB
            result = self._create_routine_in_database(
                user=user,
                plan_data=plan_data,
                nombre_rutina=nombre_rutina
                or f"Plan IA - {user.get_objetivo_display()}",
            )

            return {
                "success": True,
                "rutina_id": result["rutina_id"],
                "plan_ids": result["plan_ids"],
                "mensaje": f"Rutina generada exitosamente para {dias_semana} días",
                "ejercicios_count": result["total_ejercicios"],
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "mensaje": f"Error al generar rutina: {str(e)}",
            }

    def _get_user_profile(self, user_id: int) -> User:
        """Obtiene el perfil completo del usuario."""
        try:
            user = User.objects.prefetch_related("equipamientos_preferidos").get(
                id=user_id
            )
            return user
        except User.DoesNotExist:
            raise ValueError(f"Usuario con ID {user_id} no existe")

    def _get_available_exercises(self, user: User) -> List[Dict]:
        """
        Filtra ejercicios según equipamiento disponible del usuario.

        Returns:
            Lista de diccionarios con información de ejercicios:
            [{'id': int, 'nombre': str, 'grupo_muscular': str, 'dificultad': str}, ...]
        """
        equipamiento_ids = user.equipamientos_preferidos.values_list("id", flat=True)

        if not equipamiento_ids:
            return []

        # Filtrar ejercicios que usan equipamiento disponible
        ejercicios = (
            Ejercicio.objects.filter(equipamientos__id__in=equipamiento_ids)
            .distinct()
            .values("id", "nombre", "grupo_muscular", "dificultad", "descripcion")
        )

        return list(ejercicios)

    def _build_prompt(
        self, user: User, ejercicios: List[Dict], dias_semana: int
    ) -> str:
        """
        Construye el prompt optimizado para Gemini AI.

        Incluye:
        - Contexto del rol (entrenador experto)
        - Perfil del usuario
        - Lista estricta de ejercicios disponibles
        - Formato JSON requerido
        - Restricciones y reglas
        """
        ejercicios_lista = "\n".join(
            [
                f"- ID: {ej['id']} | Nombre: {ej['nombre']} | "
                f"Grupo: {ej['grupo_muscular']} | Dificultad: {ej['dificultad']}"
                for ej in ejercicios
            ]
        )

        # Mapear objetivo a descripción detallada
        objetivo_map = {
            "PERDER_PESO": "perder peso y quemar grasa corporal",
            "GANAR_MASA": "ganar masa muscular y volumen",
            "TONIFICAR": "tonificar y definir músculos",
            "FUERZA": "aumentar fuerza máxima",
            "RESISTENCIA": "mejorar resistencia cardiovascular y muscular",
            "SALUD_GENERAL": "mantener salud general y fitness",
        }

        objetivo_desc = objetivo_map.get(user.objetivo, "mejorar condición física")

        prompt = f"""Eres un entrenador personal certificado y experto en programación de ejercicios.

**PERFIL DEL USUARIO:**
- Objetivo: {objetivo_desc}
- Nivel de experiencia: {user.get_nivel_display()}
- Edad: {user.edad or 'No especificada'}
- Peso: {user.peso or 'No especificado'} kg
- Altura: {user.altura or 'No especificada'} m

**EJERCICIOS DISPONIBLES (EQUIPAMIENTO DEL USUARIO):**
{ejercicios_lista}

**TAREA:**
Genera un plan de entrenamiento para {dias_semana} días por semana.

**REGLAS ESTRICTAS:**
1. SOLO puedes usar ejercicios de la lista anterior (usando sus IDs exactos)
2. NO inventes nombres nuevos de ejercicios
3. Distribuye los ejercicios balanceadamente entre grupos musculares
4. Para nivel PRINCIPIANTE: 3-4 ejercicios por día, 3 series, 10-12 reps
5. Para nivel INTERMEDIO: 4-5 ejercicios por día, 3-4 series, 8-12 reps
6. Para nivel AVANZADO: 5-6 ejercicios por día, 4-5 series, 6-12 reps
7. Ajusta descansos: Principiante (90s), Intermedio (60s), Avanzado (45s)
8. Evita trabajar el mismo grupo muscular en días consecutivos

**FORMATO DE RESPUESTA REQUERIDO (JSON válido):**
{{
  "plan_semanal": [
    {{
      "dia": 1,
      "nombre_dia": "Día 1 - [Grupos musculares]",
      "ejercicios": [
        {{
          "ejercicio_id": 5,
          "series": 3,
          "repeticiones": "12",
          "descanso_segundos": 60,
          "orden": 1,
          "notas": "Breve consejo técnico"
        }}
      ]
    }}
  ],
  "duracion_estimada_minutos": 45,
  "nivel_recomendado": "{user.nivel}",
  "observaciones": "Recomendaciones generales del plan"
}}

Genera ÚNICAMENTE el JSON sin texto adicional."""

        return prompt

    def _call_gemini_api(self, prompt: str) -> str:
        """
        Realiza la llamada a Gemini AI y retorna la respuesta.

        Args:
            prompt: Prompt construido para la IA

        Returns:
            Respuesta en texto de Gemini

        Raises:
            Exception: Si hay error en la API
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,  # Balance entre creatividad y consistencia
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=2048,
                ),
            )

            return response.text

        except Exception as e:
            raise Exception(f"Error al comunicarse con Gemini AI: {str(e)}")

    def _parse_ai_response(self, response_text: str) -> Dict:
        """
        Parsea la respuesta de texto de Gemini a JSON.

        Limpia el texto (elimina markdown, espacios, etc.) y valida estructura.

        Args:
            response_text: Respuesta raw de Gemini

        Returns:
            Diccionario con plan_semanal parseado

        Raises:
            ValueError: Si el JSON es inválido o no cumple estructura
        """
        try:
            # Limpiar markdown code blocks si existen
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            cleaned = cleaned.strip()

            # Parsear JSON
            data = json.loads(cleaned)

            # Validar estructura mínima
            if "plan_semanal" not in data:
                raise ValueError("Respuesta de IA no contiene 'plan_semanal'")

            if not isinstance(data["plan_semanal"], list):
                raise ValueError("'plan_semanal' debe ser una lista")

            # Validar cada día
            for dia_data in data["plan_semanal"]:
                if "dia" not in dia_data or "ejercicios" not in dia_data:
                    raise ValueError(
                        f"Día inválido en plan: {dia_data}. "
                        "Debe tener 'dia' y 'ejercicios'"
                    )

            return data

        except json.JSONDecodeError as e:
            raise ValueError(f"Respuesta de IA no es JSON válido: {str(e)}")

    @transaction.atomic
    def _create_routine_in_database(
        self, user: User, plan_data: Dict, nombre_rutina: str
    ) -> Dict:
        """
        Crea rutinas y planes semanales en la base de datos.

        Usa transacción atómica para garantizar consistencia.

        Args:
            user: Usuario para quien se crea la rutina
            plan_data: Datos parseados del plan semanal
            nombre_rutina: Nombre de la rutina

        Returns:
            Dict con IDs creados: {'rutina_id': int, 'plan_ids': List[int], 'total_ejercicios': int}
        """
        # Crear rutina principal
        rutina = Rutina.objects.create(
            nombre=nombre_rutina,
            descripcion=plan_data.get("observaciones", "Rutina generada por IA"),
            duracion_minutos=plan_data.get("duracion_estimada_minutos", 60),
            nivel=user.nivel,
        )

        plan_ids = []
        total_ejercicios = 0

        # Mapeo de días
        dia_map = {
            1: DiaSemana.LUNES,
            2: DiaSemana.MARTES,
            3: DiaSemana.MIERCOLES,
            4: DiaSemana.JUEVES,
            5: DiaSemana.VIERNES,
            6: DiaSemana.SABADO,
            7: DiaSemana.DOMINGO,
        }

        # Desactivar planes anteriores del usuario
        PlanSemanal.objects.filter(usuario=user, activo=True).update(activo=False)

        # Crear plan para cada día
        for dia_data in plan_data["plan_semanal"]:
            dia_num = dia_data["dia"]
            ejercicios_del_dia = dia_data["ejercicios"]

            # Crear rutina específica para este día
            rutina_dia = Rutina.objects.create(
                nombre=dia_data.get("nombre_dia", f"{nombre_rutina} - Día {dia_num}"),
                descripcion=f"Día {dia_num} del plan generado por IA",
                duracion_minutos=plan_data.get("duracion_estimada_minutos", 60),
                nivel=user.nivel,
            )

            # Agregar ejercicios a la rutina del día
            for ej_data in ejercicios_del_dia:
                try:
                    ejercicio = Ejercicio.objects.get(id=ej_data["ejercicio_id"])

                    RutinaEjercicio.objects.create(
                        rutina=rutina_dia,
                        ejercicio=ejercicio,
                        series=ej_data.get("series", 3),
                        repeticiones=str(ej_data.get("repeticiones", "12")),
                        descanso_segundos=ej_data.get("descanso_segundos", 60),
                        orden=ej_data.get("orden", 1),
                        notas=ej_data.get("notas", ""),
                    )

                    total_ejercicios += 1

                except Ejercicio.DoesNotExist:
                    # Log pero no falla - IA puede haber dado ID inválido
                    print(
                        f"Advertencia: Ejercicio ID {ej_data['ejercicio_id']} no existe"
                    )

            # Crear plan semanal
            plan = PlanSemanal.objects.create(
                usuario=user,
                rutina=rutina_dia,
                dia_semana=dia_map.get(dia_num, DiaSemana.LUNES),
                activo=True,
                notas=dia_data.get("nombre_dia", ""),
            )

            plan_ids.append(plan.id)

        return {
            "rutina_id": rutina.id,
            "plan_ids": plan_ids,
            "total_ejercicios": total_ejercicios,
        }


# Función helper para uso directo
def generate_routine(
    user_id: int, dias_semana: int = 3, nombre_rutina: Optional[str] = None
) -> Dict:
    """
    Función de conveniencia para generar rutina.

    Uso:
        from accounts.services.routine_generator import generate_routine
        resultado = generate_routine(user_id=1, dias_semana=4)
    """
    service = RoutineGeneratorService()
    return service.generate_routine_for_user(
        user_id=user_id, dias_semana=dias_semana, nombre_rutina=nombre_rutina
    )
