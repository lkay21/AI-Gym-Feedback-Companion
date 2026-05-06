"""
Gemini client used by the chat module.

Historically this module had helper methods that the health-onboarding flow
relies on: `build_fixed_stats_intro` and `generate_follow_up_questions`.
We now implement those on top of the shared GeminiClient in
`app.chatbot.gemini_client`.
"""

from datetime import date, timedelta
from typing import Any, Dict, List, Optional
import ast
import json

from app.chatbot.gemini_client import GeminiClient as BaseGeminiClient


def _day_key(entry: Dict[str, Any]) -> str:
    d = entry.get("date_of_workout") or ""
    return str(d)[:10]


def _split_evenly(items: List[Dict[str, Any]], n: int) -> List[List[Dict[str, Any]]]:
    if n <= 0:
        return [items]
    L = len(items)
    if L == 0:
        return []
    base, extra = divmod(L, n)
    chunks: List[List[Dict[str, Any]]] = []
    idx = 0
    for i in range(n):
        sz = base + (1 if i < extra else 0)
        chunks.append(items[idx : idx + sz])
        idx += sz
    return chunks


def _renormalize_fitness_plan_dates(entries: List[Dict[str, Any]], start: date) -> None:
    """
    Force workout dates onto consecutive calendar days beginning at `start`.

    The model often emits stale years; we treat its dates only as day-grouping hints
    (same string = same day), then remap to [start, start+1, ...].
    """
    if not entries:
        return

    blocks: List[List[Dict[str, Any]]] = []
    for e in entries:
        if not blocks:
            blocks.append([e])
        elif _day_key(e) == _day_key(blocks[-1][0]):
            blocks[-1].append(e)
        else:
            blocks.append([e])

    def apply_day(block: List[Dict[str, Any]], d: date) -> None:
        ds = d.isoformat()
        for x in block:
            x["date_of_workout"] = ds

    if len(blocks) == 1:
        n_days = min(14, max(1, len(entries)))
        for i, chunk in enumerate(_split_evenly(entries, n_days)):
            apply_day(chunk, start + timedelta(days=i))
        return

    for i, block in enumerate(blocks):
        apply_day(block, start + timedelta(days=min(i, 13)))


def _extract_json_array_candidate(text: str) -> str:
    """
    Extract the most likely JSON array payload from model output.

    Handles common wrappers like markdown code fences and prose before/after
    the array.
    """
    if not text:
        return ""

    cleaned = text.strip()

    # Prefer fenced payloads first (```json ... ``` or ``` ... ```).
    if "```" in cleaned:
        parts = cleaned.split("```")
        for i in range(1, len(parts), 2):
            block = parts[i].strip()
            if block.lower().startswith("json"):
                block = block[4:].strip()
            if "[" in block and "]" in block:
                cleaned = block
                break

    # Find first balanced [...] sequence.
    start_idx = cleaned.find("[")
    if start_idx == -1:
        return cleaned

    depth = 0
    in_string = False
    escape = False
    for idx in range(start_idx, len(cleaned)):
        ch = cleaned[idx]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
        elif ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return cleaned[start_idx : idx + 1]

    # Unbalanced array; return suffix from first '[' as best effort.
    return cleaned[start_idx:]


def _parse_plan_payload(text: str) -> List[Dict[str, Any]]:
    """
    Parse model output into a Python list of dict entries.

    Try strict JSON first, then a permissive Python-literal parse to recover
    from common model artifacts like single quotes or trailing commas.
    """
    candidate = _extract_json_array_candidate(text)

    parsed: Any
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        parsed = ast.literal_eval(candidate)

    if not isinstance(parsed, list):
        return []
    return [item for item in parsed if isinstance(item, dict)]


def _ensure_two_week_workout_coverage(entries: List[Dict[str, Any]], start: date) -> List[Dict[str, Any]]:
    """
    Ensure at least one workout entry exists for each of 14 consecutive days.

    Snapshot UI surfaces workout days prominently. If the model returns sparse
    entries, fill missing days with a lightweight recovery workout entry so the
    generated plan still spans two weeks without requiring UI changes.
    """
    by_day: Dict[str, List[Dict[str, Any]]] = {}
    for entry in entries:
        key = str(entry.get("date_of_workout") or "")[:10]
        if not key:
            continue
        by_day.setdefault(key, []).append(entry)

    for i in range(14):
        day = (start + timedelta(days=i)).isoformat()
        if day in by_day:
            continue
        filler = {
            "date_of_workout": day,
            "exercise_name": "Active Recovery Walk",
            "exercise_description": "Light cardio and mobility work to support recovery.",
            "rep_count": 1,
            "muscle_group": "Full Body",
            "expected_calories_burnt": 120.0,
            "weight_to_lift_suggestion": None,
        }
        by_day[day] = [filler]

    out: List[Dict[str, Any]] = []
    for i in range(14):
        day = (start + timedelta(days=i)).isoformat()
        out.extend(by_day[day])
    return out


class GeminiClient(BaseGeminiClient):
    """
    Chat-module specific Gemini client.

    Inherits the core text-generation behaviour from `app.chatbot.gemini_client.GeminiClient`
    and adds a couple of small helpers used by the health-onboarding flow.
    """

    def build_fixed_stats_intro(self, health: Dict[str, Any]) -> str:
        """
        Build a short, human-readable intro summarizing any fixed stats we already
        know (age, height, weight, gender), then prompt the user for their main
        fitness goal.
        """
        parts: List[str] = []
        age = health.get("age")
        height = health.get("height")
        weight = health.get("weight")
        gender = health.get("gender")

        if age:
            parts.append(f"- Age: {age} years")
        if height:
            parts.append(f"- Height: {height}")
        if weight:
            parts.append(f"- Weight: {weight}")
        if gender:
            parts.append(f"- Gender: {gender}")

        if parts:
            prefix = "Here's what I know about you so far:\n" + "\n".join(parts) + "\n\n"
        else:
            prefix = ""

        return (
            prefix
            + "What is your main fitness goal right now? "
            "(for example: lose weight, build muscle, improve endurance, get toned, etc.)"
        )

    def generate_follow_up_questions(self, fitness_goal: str, count: int = 3) -> List[str]:
        """
        Ask Gemini to propose a small number of short follow-up questions that help
        refine the user's plan based on their stated fitness goal.

        Returns a list of plain-text questions.
        """
        prompt = (
            "The user has told you their main fitness goal:\n\n"
            f"  \"{fitness_goal}\"\n\n"
            "Generate a small list of concise follow-up questions (one per line) "
            "that would help you personalise their 2-week workout plan. "
            f"Return ONLY {count} short questions, no bullet markers, no numbering."
        )

        try:
            raw = self.model.generate_content(
                contents=[prompt],
                generation_config={"temperature": 0.6, "max_output_tokens": 512},
            )
            text = ""
            if hasattr(raw, "text") and raw.text:
                text = raw.text.strip()
            elif hasattr(raw, "candidates") and raw.candidates:
                text = raw.candidates[0].content.parts[0].text.strip()
            if not text:
                return []

            # Split into lines, clean up, drop empties, cap at count
            questions = [line.strip("-• ").strip() for line in text.splitlines()]
            questions = [q for q in questions if q]
            return questions[:count]
        except Exception:
            # On any failure, fall back to a generic set
            fallback = [
                "Do you have any injuries or limitations I should know about?",
                "How many days per week can you realistically work out?",
                "What kinds of workouts or equipment do you enjoy or have access to?",
            ]
            return fallback[:count]

    def generate_two_week_fitness_plan(
        self,
        health_data: Dict[str, Any],
        *,
        plan_start_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate a 2-week fitness plan based on the user's health profile.

        This mirrors the behaviour used previously in the fitness plan generation
        flow: we ask Gemini for structured JSON and normalise it into a list of
        plain dicts with stable keys that the fitness_plan module expects.
        """
        start = plan_start_date or date.today()
        last = start + timedelta(days=13)
        allowed_dates = [
            (start + timedelta(days=i)).isoformat()
            for i in range(14)
        ]
        prompt = (
            "You are a fitness planner.\n"
            "Generate a 2-week workout plan for the user profile below.\n\n"
            "OUTPUT RULES (MANDATORY):\n"
            "1) Return ONLY a JSON array. No prose, no markdown, no code fences.\n"
            "2) Use strict JSON with double quotes for all keys and string values.\n"
            "3) Every object MUST contain exactly these keys:\n"
            '   "date_of_workout", "exercise_name", "exercise_description", '
            '"rep_count", "muscle_group", "expected_calories_burnt", "weight_to_lift_suggestion".\n'
            "4) date_of_workout MUST be YYYY-MM-DD and MUST be one of these dates only:\n"
            f"   {', '.join(allowed_dates)}\n"
            "5) rep_count is integer or null.\n"
            "6) expected_calories_burnt is number or null.\n"
            "7) weight_to_lift_suggestion is number or null.\n"
            "8) If a value is unknown, use null (never use placeholders like N/A).\n"
            "9) Return EXACTLY 14 entries: one workout entry per day across the 14 dates.\n"
            "10) Before returning, ensure the output is valid JSON parseable by json.loads.\n\n"
            f"User profile: {json.dumps(health_data)}"
        )

        try:
            response = self.model.generate_content(
                contents=[prompt],
                generation_config={"temperature": 0.2, "max_output_tokens": 8192},
            )
            text = ""
            if hasattr(response, "text") and response.text:
                text = response.text.strip()
            elif hasattr(response, "candidates") and response.candidates:
                text = response.candidates[0].content.parts[0].text.strip()

            try:
                plan = _parse_plan_payload(text)
            except (json.JSONDecodeError, ValueError, SyntaxError):
                # If the model produced malformed JSON-ish output, ask it to rewrite
                # the same payload as strict JSON-only array and parse again.
                repair_prompt = (
                    "Rewrite the following content as STRICT JSON ONLY.\n"
                    "Requirements:\n"
                    "- Output must be a JSON array only.\n"
                    "- Use double quotes for all keys/strings.\n"
                    "- No markdown, no commentary.\n\n"
                    f"{text}"
                )
                repaired = self.model.generate_content(
                    contents=[repair_prompt],
                    generation_config={"temperature": 0.0, "max_output_tokens": 8192},
                )
                repaired_text = ""
                if hasattr(repaired, "text") and repaired.text:
                    repaired_text = repaired.text.strip()
                elif hasattr(repaired, "candidates") and repaired.candidates:
                    repaired_text = repaired.candidates[0].content.parts[0].text.strip()
                try:
                    plan = _parse_plan_payload(repaired_text)
                except (json.JSONDecodeError, ValueError, SyntaxError):
                    return []

            if not plan:
                return []

            out: List[Dict[str, Any]] = []
            for item in plan:
                if not isinstance(item, dict):
                    continue
                date_val = item.get("date_of_workout") or item.get("date")
                if not date_val:
                    continue
                out.append(
                    {
                        "date_of_workout": str(date_val)[:10],
                        "exercise_name": str(
                            item.get("exercise_name") or item.get("exercise") or ""
                        )
                        .strip()
                        or "Exercise",
                        "exercise_description": str(
                            item.get("exercise_description")
                            or item.get("description")
                            or ""
                        ).strip(),
                        "rep_count": int(item["rep_count"])
                        if item.get("rep_count") is not None
                        else None,
                        "muscle_group": str(item.get("muscle_group") or "").strip(),
                        "expected_calories_burnt": float(
                            item["expected_calories_burnt"]
                        )
                        if item.get("expected_calories_burnt") is not None
                        else None,
                        "weight_to_lift_suggestion": float(
                            item["weight_to_lift_suggestion"]
                        )
                        if item.get("weight_to_lift_suggestion") is not None
                        else None,
                    }
                )
            _renormalize_fitness_plan_dates(out, start)
            return _ensure_two_week_workout_coverage(out, start)
        except (json.JSONDecodeError, ValueError, KeyError, TypeError, SyntaxError) as e:
            raise Exception(f"Failed to parse fitness plan from model: {e}") from e


__all__ = ["GeminiClient"]

