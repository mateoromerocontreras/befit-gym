"""AI Routine Generator service powered by Gemini."""

import json
import time
import logging
from functools import wraps
from typing import Dict, List, Optional
import re
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
    UserTrainingWeekday,
)

logger = logging.getLogger(__name__)


def _extract_retry_seconds(error_message: str) -> Optional[int]:
    """Extract retry delay in seconds from Gemini quota error text."""
    patterns = [
        r"retry in\s+([0-9]+(?:\.[0-9]+)?)s",
        r"retry_delay\s*\{\s*seconds:\s*([0-9]+)\s*\}",
    ]

    for pattern in patterns:
        match = re.search(pattern, error_message, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return int(float(match.group(1)))

    return None


def _is_quota_error(error_message: str) -> bool:
    lowered = error_message.lower()
    return "429" in error_message or "quota" in lowered or "rate-limit" in lowered


def _is_daily_quota_error(error_message: str) -> bool:
    lowered = error_message.lower()
    return "perday" in lowered or "daily" in lowered or "generaterequestsperday" in lowered


def _format_quota_error(error_message: str) -> str:
    retry_seconds = _extract_retry_seconds(error_message)
    if retry_seconds:
        return (
            _("Gemini quota exceeded. Retry in approximately %(seconds)s seconds.")
            % {"seconds": retry_seconds}
        )
    return _("Gemini quota exceeded. Please retry later or review your API billing/quota.")

def exponential_backoff_retry(max_retries=3, base_delay=2):
    """Decorator for exponential backoff retry on quota errors (429).

    Args:
        max_retries: Maximum number of retries (default: 3)
        base_delay: Base delay in seconds, doubles each retry (default: 2s)

    Retry delays: 2s, 4s, 8s for default configuration.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error_message = str(e)
                    is_quota_error = _is_quota_error(error_message)
                    is_daily_quota = _is_daily_quota_error(error_message)

                    if is_quota_error and retries < max_retries and not is_daily_quota:
                        exponential_delay = base_delay * (2 ** retries)
                        retry_hint_delay = _extract_retry_seconds(error_message)
                        delay = max(exponential_delay, retry_hint_delay or 0)
                        logger.warning(
                            f"Quota error (429) on attempt {retries + 1}/{max_retries + 1}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                        retries += 1
                    else:
                        raise

            raise Exception(_("Max retries exceeded for Gemini API call"))
        return wrapper
    return decorator


class RoutineGeneratorService:
    """Generate personalized routines using Gemini AI."""

    DEFAULT_TRAINING_WEEKDAYS = [
        Weekday.MONDAY,
        Weekday.WEDNESDAY,
        Weekday.FRIDAY,
    ]

    def __init__(self, raise_on_missing_key: bool = True):
        """Initialize service and configure Gemini AI."""
        api_key = settings.GOOGLE_API_KEY
        self.model = None

        if not api_key and raise_on_missing_key:
            raise ValueError(
                _("GEMINI_API_KEY is not configured. ")
                + _("Define the environment variable or add it in settings.py")
            )

        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    def _get_user_training_weekdays(self, user: User) -> List[int]:
        configured_days = list(
            user.training_weekdays.values_list("weekday", flat=True).order_by("weekday")
        )
        if configured_days:
            return configured_days
        return [int(day) for day in self.DEFAULT_TRAINING_WEEKDAYS]

    def _resolve_training_weekdays(
        self,
        user: User,
        training_days: int,
        training_weekdays: Optional[List[int]] = None,
    ) -> List[int]:
        if training_weekdays:
            selected = sorted(list(dict.fromkeys(training_weekdays)))
        else:
            selected = self._get_user_training_weekdays(user)

        selected = [int(day) for day in selected if 1 <= int(day) <= 7]

        if not selected:
            selected = [int(day) for day in self.DEFAULT_TRAINING_WEEKDAYS]

        if training_days and training_days < len(selected):
            selected = selected[:training_days]

        return selected

    def get_generation_precheck(
        self,
        user_id: int,
        training_days: int = 3,
        training_weekdays: Optional[List[int]] = None,
    ) -> Dict:
        user = self._get_user_profile(user_id)
        selected_weekdays = self._resolve_training_weekdays(
            user=user,
            training_days=training_days,
            training_weekdays=training_weekdays,
        )
        available_exercises = self._get_available_exercises(user)
        equipment_count = user.preferred_equipment.count()
        has_api_key = bool(settings.GOOGLE_API_KEY)

        missing = []
        if not has_api_key:
            missing.append("api_key")
        if equipment_count == 0:
            missing.append("equipment")
        if available_exercises == []:
            missing.append("compatible_exercises")
        if not selected_weekdays:
            missing.append("training_weekdays")

        return {
            "ready": len(missing) == 0,
            "missing": missing,
            "checks": {
                "api_key": has_api_key,
                "equipment_count": equipment_count,
                "compatible_exercises_count": len(available_exercises),
                "training_weekdays": selected_weekdays,
            },
        }

    def generate_routine_for_user(
        self,
        user_id: int,
        training_days: int = 3,
        routine_name: Optional[str] = None,
        training_weekdays: Optional[List[int]] = None,
        **legacy_kwargs,
    ) -> Dict:
        """Generate a complete training plan for a user."""
        if "dias_semana" in legacy_kwargs and training_days == 3:
            training_days = legacy_kwargs["dias_semana"]
        if "nombre_rutina" in legacy_kwargs and not routine_name:
            routine_name = legacy_kwargs["nombre_rutina"]
        if "dias_entrenamiento" in legacy_kwargs and not training_weekdays:
            training_weekdays = legacy_kwargs["dias_entrenamiento"]

        try:
            user = self._get_user_profile(user_id)
            selected_weekdays = self._resolve_training_weekdays(
                user=user,
                training_days=training_days,
                training_weekdays=training_weekdays,
            )
            training_days = len(selected_weekdays)

            precheck = self.get_generation_precheck(
                user_id=user_id,
                training_days=training_days,
                training_weekdays=selected_weekdays,
            )
            if not precheck["ready"]:
                missing_map = {
                    "api_key": _("Missing GEMINI_API_KEY configuration"),
                    "equipment": _("No equipment selected for this user"),
                    "compatible_exercises": _("No exercises are compatible with selected equipment"),
                    "training_weekdays": _("No training weekdays configured"),
                }
                reasons = [missing_map.get(code, code) for code in precheck["missing"]]
                raise ValueError(
                    _("Cannot generate routine. Missing requirements: %(requirements)s")
                    % {"requirements": ", ".join(reasons)}
                )

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

            for attempt in range(1):
                ai_response = self._call_gemini_api(prompt)
                try:
                    plan_data = self._parse_ai_response(ai_response)
                    break
                except ValueError as parse_error:
                    last_parse_error = parse_error

            if plan_data is None and last_parse_error is not None:
                plan_data = self._generate_plan_day_by_day(
                    user=user,
                    available_exercises=available_exercises,
                    training_days=training_days,
                )

            result = self._create_routine_in_database(
                user=user,
                plan_data=plan_data,
                routine_name=routine_name or f"AI Plan - {user.get_goal_display()}",
                selected_weekdays=selected_weekdays,
            )

            return {
                "success": True,
                "routine_id": result["routine_id"],
                "plan_ids": result["plan_ids"],
                "message": _("Routine generated successfully for %(days)s days")
                % {"days": training_days},
                "exercises_count": result["total_exercises"],
                "training_weekdays": selected_weekdays,
                # Legacy keys
                "rutina_id": result["routine_id"],
                "mensaje": _("Routine generated successfully for %(days)s days")
                % {"days": training_days},
                "ejercicios_count": result["total_exercises"],
                "dias_entrenamiento": selected_weekdays,
            }

        except Exception as e:
            error_message = str(e)
            if _is_quota_error(error_message):
                quota_message = _format_quota_error(error_message)
                return {
                    "success": False,
                    "error": f"QUOTA_EXCEEDED: {quota_message}",
                    "message": quota_message,
                    "mensaje": quota_message,
                }

            return {
                "success": False,
                "error": error_message,
                "message": _("Error generating routine: %(error)s") % {"error": error_message},
                "mensaje": _("Error generating routine: %(error)s") % {"error": error_message},
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

    def _get_available_exercises(self, user: User, limit: int = 20) -> List[Dict]:
        """Filter exercises based on user's available equipment.
        
        Args:
            user: User instance with preferred equipment
            limit: Maximum number of exercises to return (default: 20)
                   Prevents context window saturation in Gemini prompts
        
        Returns:
            List of exercise dictionaries, prioritized by relevance
        """
        equipment_ids = user.preferred_equipment.values_list("id", flat=True)

        if not equipment_ids:
            return []

        # Get all available exercises
        available_exercises = (
            Exercise.objects.filter(equipment__id__in=equipment_ids)
            .distinct()
            .values("id", "name", "muscle_group", "difficulty", "description")
        )

        exercises_list = list(available_exercises)
        
        # Optimize: limit to most relevant exercises to avoid token saturation
        if len(exercises_list) > limit:
            logger.info(
                f"Optimizing exercise list from {len(exercises_list)} to {limit} exercises "
                f"to prevent context window saturation"
            )
            
            # Prioritization strategy:
            # 1. Match user difficulty level first
            # 2. Distribute across muscle groups
            # 3. Prefer compound movements (full_body, legs, back, chest)
            
            priority_muscle_groups = ["FULL_BODY", "LEGS", "BACK", "CHEST", "SHOULDERS"]
            user_difficulty = user.level if hasattr(user, 'level') else "INTERMEDIATE"
            
            # Score exercises
            scored_exercises = []
            for ex in exercises_list:
                score = 0
                # Difficulty match
                if ex.get("difficulty") == user_difficulty:
                    score += 3
                # Priority muscle group
                if ex.get("muscle_group") in priority_muscle_groups:
                    score += priority_muscle_groups.index(ex.get("muscle_group", "")) + 2
                scored_exercises.append((score, ex))
            
            # Sort by score (descending) and take top N
            scored_exercises.sort(key=lambda x: x[0], reverse=True)
            exercises_list = [ex for _, ex in scored_exercises[:limit]]
            
            logger.debug(f"Selected top {len(exercises_list)} exercises based on user profile")

        return exercises_list

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

    def _build_day_prompt(
        self,
        user: User,
        available_exercises: List[Dict],
        training_days: int,
        day_number: int,
        previous_muscle_groups: List[str],
    ) -> str:
        """Build a compact prompt for a single training day."""
        exercise_list = "\n".join(
            [
                f"- ID: {ex['id']} | Name: {ex['name']} | Group: {ex['muscle_group']}"
                for ex in available_exercises
            ]
        )

        exercise_count_map = {
            "BEGINNER": 3,
            "INTERMEDIATE": 4,
            "ADVANCED": 5,
        }
        series_map = {
            "BEGINNER": 3,
            "INTERMEDIATE": 4,
            "ADVANCED": 4,
        }
        repetitions_map = {
            "BEGINNER": "10-12",
            "INTERMEDIATE": "8-12",
            "ADVANCED": "6-10",
        }
        rest_map = {
            "BEGINNER": 90,
            "INTERMEDIATE": 60,
            "ADVANCED": 45,
        }

        blocked_groups = ", ".join(previous_muscle_groups) if previous_muscle_groups else "none"

        return f"""Return ONLY valid JSON for day {day_number} of a {training_days}-day training plan.

User goal: {user.goal}
User level: {user.level}
Avoid using these main muscle groups as primary focus from the previous day: {blocked_groups}

Available exercises:
{exercise_list}

Rules:
1. Use ONLY exercise IDs from the list.
2. Do NOT invent exercises.
3. Prioritize a different muscle focus than the previous day.
4. Return exactly {exercise_count_map.get(user.level, 3)} exercises.
5. Use {series_map.get(user.level, 3)} series per exercise unless variation is needed.
6. Use repetitions near {repetitions_map.get(user.level, '10-12')}.
7. Use rest around {rest_map.get(user.level, 60)} seconds.
8. Keep notes very short (max 8 words).

Required JSON schema:
{{
  "day": {day_number},
  "day_name": "Day {day_number} - [main focus]",
  "exercises": [
    {{
      "exercise_id": 1,
      "series": {series_map.get(user.level, 3)},
      "repetitions": "{repetitions_map.get(user.level, '10-12')}",
      "rest_seconds": {rest_map.get(user.level, 60)},
      "order": 1,
      "notes": "Short tip"
    }}
  ]
}}"""

    @exponential_backoff_retry(max_retries=3, base_delay=2)
    def _call_gemini_api(self, prompt: str) -> str:
        """Call Gemini AI and return text response.
        
        Includes exponential backoff retry for quota errors (429):
        - Attempt 1: immediate
        - Attempt 2: wait 2s
        - Attempt 3: wait 4s
        - Attempt 4: wait 8s
        
        Logs response time for performance monitoring.
        """
        start_time = time.time()
        if not self.model:
            raise Exception(_("Gemini model is not initialized. Check GEMINI_API_KEY configuration."))
        
        try:
            logger.info(f"Calling Gemini API with model: {settings.GEMINI_MODEL}")
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=settings.GEMINI_TEMPERATURE,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=4096,
                    response_mime_type="application/json",
                ),
            )

            elapsed_time = time.time() - start_time
            response_length = len(response.text) if response.text else 0
            
            logger.info(
                f"Gemini API responded successfully in {elapsed_time:.2f}s. "
                f"Response length: {response_length} characters"
            )
            
            return response.text

        except Exception as e:
            elapsed_time = time.time() - start_time
            error_message = str(e)
            
            logger.error(
                f"Gemini API error after {elapsed_time:.2f}s: {error_message[:200]}"
            )
            
            if _is_quota_error(error_message):
                # Re-raise to trigger exponential backoff decorator
                raise
            
            raise Exception(_("Error communicating with Gemini AI: %(error)s") % {"error": str(e)})

    def _clean_ai_json_text(self, response_text: str) -> str:
        """Normalize raw Gemini text before JSON parsing.
        
        Handles multiple markdown code block formats:
        - ```json ... ```
        - ``` ... ```
        - Plain JSON
        - JSON with leading/trailing text
        
        This method is designed to be infalible against common Gemini response formats.
        """
        if not response_text:
            return "{}"
        
        cleaned = response_text.strip()
        
        # Strategy 1: Remove markdown code blocks (multiple variants)
        # Handle ```json
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        # Handle ```javascript, ```typescript, etc.
        elif cleaned.startswith("```") and cleaned[3:].split()[0].isalpha():
            first_newline = cleaned.find("\n")
            if first_newline > 0:
                cleaned = cleaned[first_newline + 1:]
        # Handle plain ```
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        
        # Remove closing ```
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        # Remove any remaining tick marks at boundaries
        cleaned = cleaned.strip("`")
        cleaned = cleaned.strip()
        
        # Strategy 2: Extract JSON object if embedded in text
        if "{" in cleaned and "}" in cleaned:
            start_pos = cleaned.find("{")
            end_pos = cleaned.rfind("}") + 1
            
            # Validate we have a complete JSON structure
            if start_pos >= 0 and end_pos > start_pos:
                cleaned = cleaned[start_pos:end_pos]
        
        # Strategy 3: Remove common prefixes/suffixes
        cleaned = cleaned.strip()
        
        logger.debug(f"Cleaned JSON length: {len(cleaned)} characters")
        
        return cleaned

    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse Gemini response into validated JSON."""
        try:
            cleaned = self._clean_ai_json_text(response_text)
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

    def _parse_ai_day_response(self, response_text: str, expected_day: int) -> Dict:
        """Parse a single-day Gemini JSON response."""
        cleaned = self._clean_ai_json_text(response_text)
        raw_data = json.loads(cleaned)

        if "weekly_plan" in raw_data or "plan_semanal" in raw_data:
            data = self._parse_ai_response(cleaned)

            if "weekly_plan" in data:
                day_data = data["weekly_plan"][0]
            else:
                day_data = data["plan_semanal"][0]
        else:
            day_data = raw_data

        exercises_key = "exercises" if "exercises" in day_data else "ejercicios"
        if "day" not in day_data and "dia" not in day_data:
            raise ValueError(_("AI day response does not contain 'day'"))
        if exercises_key not in day_data or not isinstance(day_data[exercises_key], list):
            raise ValueError(_("AI day response does not contain a valid exercises list"))

        day_number = day_data.get("day", day_data.get("dia"))
        if day_number != expected_day:
            day_data["day"] = expected_day

        return day_data

    def _extract_day_muscle_groups(
        self, day_data: Dict, available_exercises: List[Dict]
    ) -> List[str]:
        """Infer muscle groups used in a generated day."""
        exercise_map = {exercise["id"]: exercise for exercise in available_exercises}
        muscle_groups = []

        for exercise_data in day_data.get("exercises", day_data.get("ejercicios", [])):
            exercise_id = exercise_data.get("exercise_id", exercise_data.get("ejercicio_id"))
            exercise = exercise_map.get(exercise_id)
            if exercise and exercise["muscle_group"] not in muscle_groups:
                muscle_groups.append(exercise["muscle_group"])

        return muscle_groups

    def _generate_plan_day_by_day(
        self, user: User, available_exercises: List[Dict], training_days: int
    ) -> Dict:
        """Fallback generator that requests one training day at a time."""
        weekly_plan = []
        previous_muscle_groups: List[str] = []

        for day_number in range(1, training_days + 1):
            day_prompt = self._build_day_prompt(
                user=user,
                available_exercises=available_exercises,
                training_days=training_days,
                day_number=day_number,
                previous_muscle_groups=previous_muscle_groups,
            )

            last_error = None
            day_data = None

            for day_attempt in range(2):
                ai_response = self._call_gemini_api(day_prompt)
                try:
                    day_data = self._parse_ai_day_response(ai_response, day_number)
                    break
                except ValueError as parse_error:
                    last_error = parse_error

            if day_data is None and last_error is not None:
                raise last_error

            previous_muscle_groups = self._extract_day_muscle_groups(
                day_data, available_exercises
            )
            weekly_plan.append(day_data)

        duration_map = {
            "BEGINNER": 45,
            "INTERMEDIATE": 60,
            "ADVANCED": 75,
        }

        return {
            "weekly_plan": weekly_plan,
            "estimated_duration_minutes": duration_map.get(user.level, 45),
            "recommended_level": user.level,
            "observations": "AI-generated plan based on your profile and available equipment.",
        }

    @transaction.atomic
    def _create_routine_in_database(
        self, user: User, plan_data: Dict, routine_name: str, selected_weekdays: List[int]
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

        WeeklyPlan.objects.filter(user=user).delete()

        weekly_plan_items = plan_data.get("weekly_plan", plan_data.get("plan_semanal", []))

        for day_data in weekly_plan_items:
            day_number = day_data.get("day", day_data.get("dia"))
            day_exercises = day_data.get("exercises", day_data.get("ejercicios", []))
            day_index = max(0, int(day_number or 1) - 1)
            weekday_value = selected_weekdays[day_index] if day_index < len(selected_weekdays) else selected_weekdays[-1]

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
                weekday=weekday_value,
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
    training_weekdays: Optional[List[int]] = None,
    **legacy_kwargs,
) -> Dict:
    """Convenience function to generate a routine."""
    if "dias_semana" in legacy_kwargs and training_days == 3:
        training_days = legacy_kwargs["dias_semana"]
    if "nombre_rutina" in legacy_kwargs and not routine_name:
        routine_name = legacy_kwargs["nombre_rutina"]
    if "dias_entrenamiento" in legacy_kwargs and not training_weekdays:
        training_weekdays = legacy_kwargs["dias_entrenamiento"]

    service = RoutineGeneratorService()
    return service.generate_routine_for_user(
        user_id=user_id,
        training_days=training_days,
        routine_name=routine_name,
        training_weekdays=training_weekdays,
    )
