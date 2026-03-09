"""AI Routine Generator service powered by Gemini."""

import json
from typing import Dict, List, Optional
from django.conf import settings
from django.db import transaction
from django.utils.translation import gettext_lazy as _
import google.generativeai as genai
from accounts.models import (
    User,
    Exercise,
    Routine,
    RoutineExercise,
    WeeklyPlan,
    Weekday,
)


class RoutineGeneratorService:
    """Generate personalized routines using Gemini AI."""

    def __init__(self):
        """Initialize service and configure Gemini AI."""
        api_key = settings.GOOGLE_API_KEY
        if not api_key:
            raise ValueError(
                _("GEMINI_API_KEY is not configured. ")
                + _("Define the environment variable or add it in settings.py")
            )

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    def generate_routine_for_user(
        self,
        user_id: int,
        training_days: int = 3,
        routine_name: Optional[str] = None,
        **legacy_kwargs,
    ) -> Dict:
        """Generate a complete training plan for a user."""
        if "dias_semana" in legacy_kwargs and training_days == 3:
            training_days = legacy_kwargs["dias_semana"]
        if "nombre_rutina" in legacy_kwargs and not routine_name:
            routine_name = legacy_kwargs["nombre_rutina"]

        try:
            user = self._get_user_profile(user_id)

            available_exercises = self._get_available_exercises(user)

            if not available_exercises:
                raise ValueError(
                    _("User %(email)s has no configured equipment. ")
                    % {"email": user.email}
                    + _("Select available equipment first.")
                )

            prompt = self._build_prompt(
                user=user,
                available_exercises=available_exercises,
                training_days=training_days,
            )

            last_parse_error = None
            plan_data = None

            for attempt in range(3):
                ai_response = self._call_gemini_api(prompt)
                try:
                    plan_data = self._parse_ai_response(ai_response)
                    break
                except ValueError as parse_error:
                    last_parse_error = parse_error

            if plan_data is None and last_parse_error is not None:
                raise last_parse_error

            result = self._create_routine_in_database(
                user=user,
                plan_data=plan_data,
                routine_name=routine_name or f"AI Plan - {user.get_goal_display()}",
            )

            return {
                "success": True,
                "routine_id": result["routine_id"],
                "plan_ids": result["plan_ids"],
                "message": _("Routine generated successfully for %(days)s days")
                % {"days": training_days},
                "exercises_count": result["total_exercises"],
                # Legacy keys
                "rutina_id": result["routine_id"],
                "mensaje": _("Routine generated successfully for %(days)s days")
                % {"days": training_days},
                "ejercicios_count": result["total_exercises"],
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": _("Error generating routine: %(error)s") % {"error": str(e)},
                "mensaje": _("Error generating routine: %(error)s") % {"error": str(e)},
            }

    def _get_user_profile(self, user_id: int) -> User:
        """Get full user profile."""
        try:
            user = User.objects.prefetch_related("preferred_equipment").get(
                id=user_id
            )
            return user
        except User.DoesNotExist:
            raise ValueError(_("User with ID %(id)s does not exist") % {"id": user_id})

    def _get_available_exercises(self, user: User) -> List[Dict]:
        """Filter exercises based on user's available equipment."""
        equipment_ids = user.preferred_equipment.values_list("id", flat=True)

        if not equipment_ids:
            return []

        available_exercises = (
            Exercise.objects.filter(equipment__id__in=equipment_ids)
            .distinct()
            .values("id", "name", "muscle_group", "difficulty", "description")
        )

        return list(available_exercises)

    def _build_prompt(
        self, user: User, available_exercises: List[Dict], training_days: int
    ) -> str:
        """Build optimized Gemini prompt."""
        exercise_list = "\n".join(
            [
                f"- ID: {ex['id']} | Name: {ex['name']} | "
                f"Group: {ex['muscle_group']} | Difficulty: {ex['difficulty']}"
                for ex in available_exercises
            ]
        )

        goal_map = {
            "LOSE_WEIGHT": "lose weight and reduce body fat",
            "GAIN_MUSCLE": "gain muscle mass and volume",
            "TONE": "tone and define muscles",
            "STRENGTH": "increase maximal strength",
            "ENDURANCE": "improve cardio and muscular endurance",
            "GENERAL_HEALTH": "maintain general health and fitness",
        }

        goal_description = goal_map.get(user.goal, "improve physical condition")

        prompt = f"""You are a certified personal trainer expert in workout programming.

**USER PROFILE:**
- Goal: {goal_description}
- Experience level: {user.get_level_display()}
- Age: {user.age or 'Not specified'}
- Weight: {user.weight or 'Not specified'} kg
- Height: {user.height or 'Not specified'} m

**AVAILABLE EXERCISES (USER EQUIPMENT):**
{exercise_list}

**TASK:**
Generate a training plan for {training_days} days per week.

**STRICT RULES:**
1. Use ONLY exercises from the list above (exact IDs)
2. Do NOT invent new exercise names
3. Balance exercises across muscle groups
4. BEGINNER: 3-4 exercises/day, 3 sets, 10-12 reps
5. INTERMEDIATE: 4-5 exercises/day, 3-4 sets, 8-12 reps
6. ADVANCED: 5-6 exercises/day, 4-5 sets, 6-12 reps
7. Rest times: Beginner (90s), Intermediate (60s), Advanced (45s)
8. Avoid training same muscle group on consecutive days

**REQUIRED RESPONSE FORMAT (valid JSON):**
{{
    "weekly_plan": [
    {{
            "day": 1,
            "day_name": "Day 1 - [Muscle groups]",
            "exercises": [
        {{
                    "exercise_id": 5,
          "series": 3,
                    "repetitions": "12",
                    "rest_seconds": 60,
                    "order": 1,
                    "notes": "Short technical tip"
        }}
      ]
    }}
  ],
    "estimated_duration_minutes": 45,
    "recommended_level": "{user.level}",
    "observations": "General recommendations for the plan"
}}

Return ONLY the JSON with no extra text."""

        return prompt

    def _call_gemini_api(self, prompt: str) -> str:
        """Call Gemini AI and return text response."""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=4096,
                    response_mime_type="application/json",
                ),
            )

            return response.text

        except Exception as e:
            raise Exception(_("Error communicating with Gemini AI: %(error)s") % {"error": str(e)})

    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse Gemini response into validated JSON."""
        try:
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            cleaned = cleaned.strip()

            if "{" in cleaned and "}" in cleaned:
                cleaned = cleaned[cleaned.find("{") : cleaned.rfind("}") + 1]

            data = json.loads(cleaned)

            weekly_plan_key = "weekly_plan" if "weekly_plan" in data else "plan_semanal"

            if weekly_plan_key not in data:
                raise ValueError(_("AI response does not contain 'weekly_plan'"))

            if not isinstance(data[weekly_plan_key], list):
                raise ValueError(_("'weekly_plan' must be a list"))

            for day_data in data[weekly_plan_key]:
                day_key = "day" if "day" in day_data else "dia"
                exercises_key = (
                    "exercises" if "exercises" in day_data else "ejercicios"
                )
                if day_key not in day_data or exercises_key not in day_data:
                    raise ValueError(
                        _("Invalid day entry in plan: %(day)s") % {"day": day_data}
                    )

            return data

        except json.JSONDecodeError as e:
            raise ValueError(_("AI response is not valid JSON: %(error)s") % {"error": str(e)})

    @transaction.atomic
    def _create_routine_in_database(
        self, user: User, plan_data: Dict, routine_name: str
    ) -> Dict:
        """Create routines and weekly plans in database atomically."""
        routine = Routine.objects.create(
            name=routine_name,
            description=plan_data.get("observations", plan_data.get("observaciones", "AI-generated routine")),
            duration_minutes=plan_data.get("estimated_duration_minutes", plan_data.get("duracion_estimada_minutos", 60)),
            level=user.level,
        )

        plan_ids = []
        total_exercises = 0

        weekday_map = {
            1: Weekday.MONDAY,
            2: Weekday.TUESDAY,
            3: Weekday.WEDNESDAY,
            4: Weekday.THURSDAY,
            5: Weekday.FRIDAY,
            6: Weekday.SATURDAY,
            7: Weekday.SUNDAY,
        }

        WeeklyPlan.objects.filter(user=user).delete()

        weekly_plan_items = plan_data.get("weekly_plan", plan_data.get("plan_semanal", []))

        for day_data in weekly_plan_items:
            day_number = day_data.get("day", day_data.get("dia"))
            day_exercises = day_data.get("exercises", day_data.get("ejercicios", []))

            day_routine = Routine.objects.create(
                name=day_data.get("day_name", day_data.get("nombre_dia", f"{routine_name} - Day {day_number}")),
                description=f"Day {day_number} from AI-generated plan",
                duration_minutes=plan_data.get("estimated_duration_minutes", plan_data.get("duracion_estimada_minutos", 60)),
                level=user.level,
            )

            for exercise_data in day_exercises:
                try:
                    exercise_id = exercise_data.get("exercise_id", exercise_data.get("ejercicio_id"))
                    exercise = Exercise.objects.get(id=exercise_id)

                    RoutineExercise.objects.create(
                        routine=day_routine,
                        exercise=exercise,
                        series=exercise_data.get("series", 3),
                        repetitions=str(exercise_data.get("repetitions", exercise_data.get("repeticiones", "12"))),
                        rest_seconds=exercise_data.get("rest_seconds", exercise_data.get("descanso_segundos", 60)),
                        order=exercise_data.get("order", exercise_data.get("orden", 1)),
                        notes=exercise_data.get("notes", exercise_data.get("notas", "")),
                    )

                    total_exercises += 1

                except Exercise.DoesNotExist:
                    print(
                        _("Warning: Exercise ID %(id)s does not exist")
                        % {"id": exercise_data.get("exercise_id", exercise_data.get("ejercicio_id"))}
                    )

            plan = WeeklyPlan.objects.create(
                user=user,
                routine=day_routine,
                weekday=weekday_map.get(day_number, Weekday.MONDAY),
                active=True,
                notes=day_data.get("day_name", day_data.get("nombre_dia", "")),
            )

            plan_ids.append(plan.id)

        return {
            "routine_id": routine.id,
            "plan_ids": plan_ids,
            "total_exercises": total_exercises,
        }


def generate_routine(
    user_id: int,
    training_days: int = 3,
    routine_name: Optional[str] = None,
    **legacy_kwargs,
) -> Dict:
    """Convenience function to generate a routine."""
    if "dias_semana" in legacy_kwargs and training_days == 3:
        training_days = legacy_kwargs["dias_semana"]
    if "nombre_rutina" in legacy_kwargs and not routine_name:
        routine_name = legacy_kwargs["nombre_rutina"]

    service = RoutineGeneratorService()
    return service.generate_routine_for_user(
        user_id=user_id, training_days=training_days, routine_name=routine_name
    )
