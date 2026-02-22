"""
Transformation utilities for converting fitness plan data into
calendar-ready format for the frontend.
"""
from __future__ import annotations

import json
import math
import re
from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict


class PlanParseError(ValueError):
	"""Raised when fitness plan data cannot be mapped to calendar format."""

def mapLLMPlanToStructuredPlan(raw_response: Any, start_date: str) -> Dict[str, Any]:
    """
    Convert a raw LLM response (text or loosely structured JSON) into the
    strict structured plan format used by the frontend.
    """
    start = _parse_start_date(start_date)
    parsed = _parse_llm_response(raw_response)

    plan_name = _safe_str(
        parsed.get("planName")
        or parsed.get("plan_name")
        or parsed.get("title")
        or parsed.get("name")
    ) or "Fitness Plan"

    weeks_data = _extract_weeks(parsed)
    if not weeks_data:
        raise PlanParseError("No weeks or days found in LLM response")

    structured_weeks = _map_weeks_to_calendar(weeks_data, start)

    return {
        "planName": plan_name,
        "startDate": start.isoformat(),
        "weeks": structured_weeks,
    }


def mapDatabasePlanToCalendar(plan_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convert database fitness plan entries (from DynamoDB) into the calendar format
    expected by the frontend.
    
    Expected format of plan_entries:
    [
        {
            "date_of_workout": "2026-02-22",
            "exercise_name": "Bench Press",
            "exercise_description": "...",
            "rep_count": 10,
            "muscle_group": "Chest",
            "expected_calories_burnt": 50,
            "weight_to_lift_suggestion": 75
        },
        ...
    ]
    
    Returns calendar structure with 2 weeks of workouts.
    """
    if not plan_entries:
        return {
            "planName": "Your 2-Week Fitness Plan",
            "weeks": []
        }
    
    # Group exercises by date
    exercises_by_date: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for entry in plan_entries:
        date_str = entry.get("date_of_workout")
        if date_str:
            exercises_by_date[date_str].append(entry)
    
    # Sort dates and determine week structure
    sorted_dates = sorted(exercises_by_date.keys())
    if not sorted_dates:
        return {
            "planName": "Your 2-Week Fitness Plan",
            "weeks": []
        }
    
    start_date = date.fromisoformat(sorted_dates[0])
    
    # Build week structure
    weeks: List[Dict[str, Any]] = []
    current_date = start_date
    
    for week_num in range(1, 3):  # 2 weeks
        week_days: List[Dict[str, Any]] = []
        for day_in_week in range(7):
            date_str = current_date.isoformat()
            exercises = exercises_by_date.get(date_str, [])
            
            week_days.append({
                "date": date_str,
                "workoutType": "Workout" if exercises else "Rest",
                "exercises": [
                    {
                        "name": ex.get("exercise_name", ""),
                        "sets": 3,  # Default sets
                        "reps": ex.get("rep_count", 0),
                        "weight": f"{ex.get('weight_to_lift_suggestion', 0)} lbs",
                        "muscleGroup": ex.get("muscle_group", ""),
                        "calories": ex.get("expected_calories_burnt", 0),
                        "description": ex.get("exercise_description", "")
                    }
                    for ex in exercises
                ]
            })
            current_date += timedelta(days=1)
        
        weeks.append({
            "weekNumber": week_num,
            "days": week_days
        })
    
    return {
        "planName": "Your 2-Week Fitness Plan",
        "startDate": start_date.isoformat(),
        "weeks": weeks
    }


def _parse_start_date(start_date: str) -> date:
    if not isinstance(start_date, str) or not start_date.strip():
        raise PlanParseError("startDate is required and must be an ISO date string")
    try:
        return date.fromisoformat(start_date)
    except ValueError as exc:
        raise PlanParseError("startDate must be in YYYY-MM-DD format") from exc


def _parse_llm_response(raw_response: Any) -> Dict[str, Any]:
    if isinstance(raw_response, dict):
        return raw_response

    if raw_response is None:
        raise PlanParseError("LLM response is empty")

    text = str(raw_response).strip()
    if not text:
        raise PlanParseError("LLM response is empty")

    # Attempt strict JSON parsing first
    parsed_json = _try_parse_json(text)
    if parsed_json is not None:
        return parsed_json

    # Attempt to extract JSON from markdown or text
    json_block = _extract_json_block(text)
    if json_block:
        parsed_json = _try_parse_json(json_block)
        if parsed_json is not None:
            return parsed_json

    # Fallback to heuristic text parsing
    parsed_text = _parse_text_plan(text)
    if parsed_text:
        return parsed_text

    raise PlanParseError("Unable to parse LLM response into a plan")


def _try_parse_json(text: str) -> Optional[Dict[str, Any]]:
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        return None
    return result if isinstance(result, dict) else None


def _extract_json_block(text: str) -> Optional[str]:
    code_fence = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text, re.IGNORECASE)
    if code_fence:
        return code_fence.group(1)

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return None


def _parse_text_plan(text: str) -> Optional[Dict[str, Any]]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return None

    weeks: Dict[int, List[Dict[str, Any]]] = {}
    current_week = 1

    week_regex = re.compile(r"week\s*(\d+)", re.IGNORECASE)
    day_regex = re.compile(
        r"^(day\s*(\d+)|monday|tuesday|wednesday|thursday|friday|saturday|sunday|rest\s*day)",
        re.IGNORECASE,
    )

    for line in lines:
        week_match = week_regex.search(line)
        if week_match:
            current_week = int(week_match.group(1))
            weeks.setdefault(current_week, [])
            continue

        if not day_regex.search(line):
            continue

        day_entry = _parse_day_line(line)
        if day_entry:
            weeks.setdefault(current_week, []).append(day_entry)

    if not weeks:
        return None

    return {
        "planName": None,
        "weeks": [
            {
                "weekNumber": week_num,
                "days": days,
            }
            for week_num, days in sorted(weeks.items(), key=lambda item: item[0])
        ],
    }


def _parse_day_line(line: str) -> Optional[Dict[str, Any]]:
    clean = re.sub(r"^[-*\d.\s]+", "", line).strip()
    if not clean:
        return None

    workout_type = None
    exercises: List[Dict[str, Any]] = []

    if re.search(r"rest\s*day", clean, re.IGNORECASE):
        workout_type = "Rest"
    else:
        parts = re.split(r"[:\-]", clean, maxsplit=1)
        if len(parts) == 2:
            workout_type = _safe_str(parts[1]).split("(")[0].strip()
            if workout_type and " - " in workout_type:
                workout_type = workout_type.split(" - ")[0].strip()

        exercises = _parse_exercises(clean)
        if not workout_type:
            workout_type = "Workout" if exercises else "Rest"

    return {
        "workoutType": workout_type,
        "exercises": exercises,
    }


def _parse_exercises(text: str) -> List[Dict[str, Any]]:
    exercises: List[Dict[str, Any]] = []
    chunks = re.split(r";|\n|\|", text)
    for chunk in chunks:
        match = re.search(
            r"(?P<name>[A-Za-z0-9\-() /]+)\s*(?P<sets>\d+)\s*[xX]\s*(?P<reps>\d+)",
            chunk,
        )
        if not match:
            continue

        name = _safe_str(match.group("name"))
        if not name:
            continue

        weight_match = re.search(r"(\d+\s*%|RPE\s*\d+|bodyweight)", chunk, re.IGNORECASE)
        exercises.append(
            {
                "name": name,
                "sets": _safe_int(match.group("sets")),
                "reps": _safe_int(match.group("reps")),
                "weight": weight_match.group(1) if weight_match else "",
            }
        )

    return exercises


def _extract_weeks(parsed: Dict[str, Any]) -> List[Dict[str, Any]]:
    weeks = parsed.get("weeks")
    if isinstance(weeks, list) and weeks:
        return weeks

    days = parsed.get("days")
    if isinstance(days, list) and days:
        return [{"weekNumber": 1, "days": days}]

    return []


def _map_weeks_to_calendar(weeks_data: List[Dict[str, Any]], start: date) -> List[Dict[str, Any]]:
    flat_days = _flatten_days(weeks_data)
    total_days = max(len(flat_days), len(weeks_data) * 7)
    if total_days % 7 != 0:
        total_days = int(math.ceil(total_days / 7.0) * 7)

    structured_weeks: List[Dict[str, Any]] = []
    day_index = 0
    for week_number in range(1, (total_days // 7) + 1):
        week_days: List[Dict[str, Any]] = []
        for _ in range(7):
            current_date = start + timedelta(days=day_index)
            day_data = flat_days[day_index] if day_index < len(flat_days) else {}
            normalized_day = _normalize_day(day_data, current_date)
            week_days.append(normalized_day)
            day_index += 1

        structured_weeks.append({"weekNumber": week_number, "days": week_days})

    return structured_weeks


def _flatten_days(weeks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    days: List[Dict[str, Any]] = []
    for week in weeks_data:
        week_days = week.get("days") if isinstance(week, dict) else None
        if not isinstance(week_days, list):
            continue
        for day in week_days:
            if isinstance(day, dict):
                days.append(day)
    return days


def _normalize_day(day_data: Dict[str, Any], current_date: date) -> Dict[str, Any]:
    workout_type = _safe_str(
        day_data.get("workoutType")
        or day_data.get("workout_type")
        or day_data.get("type")
    )

    exercises_raw = day_data.get("exercises")
    exercises = _normalize_exercises(exercises_raw)

    if not workout_type:
        workout_type = "Workout" if exercises else "Rest"

    return {
        "date": current_date.isoformat(),
        "workoutType": workout_type,
        "exercises": exercises,
    }


def _normalize_exercises(exercises_raw: Any) -> List[Dict[str, Any]]:
    if not isinstance(exercises_raw, list):
        return []

    normalized: List[Dict[str, Any]] = []
    for exercise in exercises_raw:
        if not isinstance(exercise, dict):
            continue
        name = _safe_str(exercise.get("name") or exercise.get("exercise"))
        if not name:
            continue

        normalized.append(
            {
                "name": name,
                "sets": _safe_int(exercise.get("sets")),
                "reps": _safe_int(exercise.get("reps")),
                "weight": _safe_str(exercise.get("weight")) or "",
            }
        )

    return normalized


def _safe_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0