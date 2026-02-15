"""
LLM service for generating structured JSON responses via OpenAI.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional, cast

from openai import APIConnectionError, APIError, APITimeoutError, OpenAI, RateLimitError
from app.chatbot.types import FitnessPlan


logger = logging.getLogger(__name__)


def generate_llm_response(
    *,
    prompt: str,
    context: Optional[List[Dict[str, str]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate a structured JSON response from OpenAI.

    Returns:
        {
          "success": bool,
          "data": object | None,
          "error": str | None,
          "raw": str | None
        }
    """
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")

    if not api_key:
        logger.error("OPENAI_API_KEY is not set")
        return _error("AI service is not configured properly", raw=None)

    if not prompt or not isinstance(prompt, str):
        return _error("Prompt is required", raw=None)

    context = context or []
    metadata = metadata or {}
    schema = metadata.get("schema")
    expect_fitness_plan = metadata.get("expectFitnessPlan", False)

    messages = _build_messages(prompt, context)
    client = OpenAI(api_key=api_key)

    raw, usage = _call_openai(client, model_name, messages)
    if raw is None:
        return _error("Failed to generate AI response", raw=None)

    parsed = _parse_json(raw)
    if parsed is None:
        retry_prompt = f"{prompt}\n\nReturn ONLY valid JSON."
        retry_messages = _build_messages(retry_prompt, context)
        raw_retry, usage = _call_openai(client, model_name, retry_messages)
        if raw_retry is None:
            return _error("Failed to generate AI response", raw=None)

        parsed = _parse_json(raw_retry)
        if parsed is None:
            return _error("Failed to parse JSON response", raw=raw_retry)
        raw = raw_retry

    if not _validate_schema(parsed, schema):
        return _error("Response does not match expected schema", raw=raw)

    if expect_fitness_plan:
        try:
            validateFitnessPlanSchema(parsed)
        except ValueError as exc:
            logger.error("Validation error: %s", exc)
            return _error(str(exc), raw=raw)

    return {
        "success": True,
        "data": cast(FitnessPlan, parsed) if expect_fitness_plan else parsed,
        "error": None,
        "raw": raw,
    }


def _build_messages(prompt: str, context: List[Dict[str, str]]) -> List[Dict[str, str]]:
    system_message = {
        "role": "system",
        "content": "You are a fitness planning assistant. Respond ONLY in valid JSON.",
    }
    messages = [system_message]
    messages.extend(context)
    messages.append({"role": "user", "content": prompt})
    return messages


def _call_openai(
    client: OpenAI,
    model_name: str,
    messages: List[Dict[str, str]],
) -> tuple[Optional[str], Optional[Dict[str, Any]]]:
    try:
        logger.info("OpenAI model used: %s", model_name)
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content if response.choices else None
        usage = None
        if hasattr(response, "usage") and response.usage:
            usage = {
                "prompt_tokens": getattr(response.usage, "prompt_tokens", None),
                "completion_tokens": getattr(response.usage, "completion_tokens", None),
                "total_tokens": getattr(response.usage, "total_tokens", None),
            }
            logger.info("OpenAI token usage: %s", usage)
        return content.strip() if content else None, usage
    except (RateLimitError, APITimeoutError, APIConnectionError) as exc:
        logger.error("OpenAI network error: %s", exc)
        return None, None
    except APIError as exc:
        logger.error("OpenAI API error: %s", exc)
        return None, None
    except Exception as exc:
        logger.error("Unexpected OpenAI error: %s", exc)
        return None, None


def _parse_json(raw: str) -> Optional[Dict[str, Any]]:
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


def _validate_schema(data: Dict[str, Any], schema: Optional[Dict[str, Any]]) -> bool:
    if schema is None:
        return isinstance(data, dict)

    required = schema.get("required", [])
    properties = schema.get("properties", {})

    if not isinstance(data, dict):
        return False

    for key in required:
        if key not in data:
            return False

    for key, rules in properties.items():
        if key not in data:
            continue
        expected_type = rules.get("type")
        if expected_type and not _matches_type(data[key], expected_type):
            return False

    return True


def _matches_type(value: Any, expected_type: str) -> bool:
    type_map = {
        "string": str,
        "number": (int, float),
        "integer": int,
        "object": dict,
        "array": list,
        "boolean": bool,
    }
    python_type = type_map.get(expected_type)
    return isinstance(value, python_type) if python_type else True


def _error(message: str, raw: Optional[str]) -> Dict[str, Any]:
    logger.error(message)
    return {
        "success": False,
        "data": None,
        "error": message,
        "raw": raw,
    }


def validateFitnessPlanSchema(data: Any) -> Dict[str, Any]:
    """
    Validate the expected fitness plan schema.

    Returns:
        {"valid": bool, "errors": list}

    Raises:
        ValueError: if invalid, with a descriptive error message.
    """
    errors: List[str] = []

    if not isinstance(data, dict):
        errors.append("Plan payload must be an object")
        return _raise_or_return(errors)

    plan_name = data.get("planName")
    if not isinstance(plan_name, str) or not plan_name.strip():
        errors.append("planName must be a non-empty string")

    weeks = data.get("weeks")
    if not isinstance(weeks, list) or not weeks:
        errors.append("weeks must be a non-empty array")
        return _raise_or_return(errors)

    for w_index, week in enumerate(weeks):
        if not isinstance(week, dict):
            errors.append(f"weeks[{w_index}] must be an object")
            continue

        if not isinstance(week.get("weekNumber"), (int, float)):
            errors.append(f"weeks[{w_index}].weekNumber must be a number")

        days = week.get("days")
        if not isinstance(days, list):
            errors.append(f"weeks[{w_index}].days must be an array")
            continue

        for d_index, day in enumerate(days):
            if not isinstance(day, dict):
                errors.append(f"weeks[{w_index}].days[{d_index}] must be an object")
                continue

            workout_type = day.get("workoutType")
            if not isinstance(workout_type, str) or not workout_type.strip():
                errors.append(f"weeks[{w_index}].days[{d_index}].workoutType must be a non-empty string")

            exercises = day.get("exercises")
            if not isinstance(exercises, list):
                errors.append(f"weeks[{w_index}].days[{d_index}].exercises must be an array")
                continue

            for e_index, exercise in enumerate(exercises):
                if not isinstance(exercise, dict):
                    errors.append(
                        f"weeks[{w_index}].days[{d_index}].exercises[{e_index}] must be an object"
                    )
                    continue

                name = exercise.get("name")
                if not isinstance(name, str) or not name.strip():
                    errors.append(
                        f"weeks[{w_index}].days[{d_index}].exercises[{e_index}].name must be a non-empty string"
                    )

                if not isinstance(exercise.get("sets"), (int, float)):
                    errors.append(
                        f"weeks[{w_index}].days[{d_index}].exercises[{e_index}].sets must be a number"
                    )

                if not isinstance(exercise.get("reps"), (int, float)):
                    errors.append(
                        f"weeks[{w_index}].days[{d_index}].exercises[{e_index}].reps must be a number"
                    )

                weight = exercise.get("weight")
                if not isinstance(weight, str):
                    errors.append(
                        f"weeks[{w_index}].days[{d_index}].exercises[{e_index}].weight must be a string"
                    )

    return _raise_or_return(errors)


def _raise_or_return(errors: List[str]) -> Dict[str, Any]:
    if errors:
        raise ValueError("; ".join(errors))
    return {"valid": True, "errors": []}