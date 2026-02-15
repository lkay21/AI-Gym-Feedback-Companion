"""
Transformation utilities for converting structured fitness plans into
calendar-ready data.
"""
from __future__ import annotations

import math
from datetime import date, timedelta
from typing import Any, Dict, List

from app.chatbot.types import FitnessPlan


class PlanParseError(ValueError):
	"""Raised when a fitness plan cannot be mapped to a calendar plan."""


def mapLLMPlanToStructuredPlan(raw_response: FitnessPlan, start_date: str) -> Dict[str, Any]:
	"""
	Convert a structured fitness plan into the strict calendar format.
	"""
	start = _parse_start_date(start_date)
	parsed = _parse_llm_response(raw_response)

	plan_name = parsed.get("planName") or "Fitness Plan"
	weeks_data = parsed.get("weeks")
	if not isinstance(weeks_data, list) or not weeks_data:
		raise PlanParseError("weeks must be a non-empty array")

	structured_weeks = _map_weeks_to_calendar(weeks_data, start)

	return {
		"planName": plan_name,
		"startDate": start.isoformat(),
		"weeks": structured_weeks,
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

	raise PlanParseError("LLM response must be a structured FitnessPlan object")


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
	workout_type = day_data.get("workoutType") or "Workout"
	exercises = day_data.get("exercises") if isinstance(day_data.get("exercises"), list) else []

	if not workout_type or not isinstance(workout_type, str):
		workout_type = "Workout" if exercises else "Rest"

	return {
		"date": current_date.isoformat(),
		"workoutType": workout_type,
		"exercises": exercises,
	}
