"""
Gemini client used by the chat module.

Historically this module had helper methods that the health-onboarding flow
relies on: `build_fixed_stats_intro` and `generate_follow_up_questions`.
We now implement those on top of the shared GeminiClient in
`app.chatbot.gemini_client`.
"""

from datetime import date, timedelta
from typing import Any, Dict, List, Optional
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
        prompt = (
            "You are a fitness planner. Based on the following user profile, generate a "
            "2-week workout plan as JSON ONLY (a JSON array). "
            f"Schedule every workout on one of these 14 consecutive calendar days only: "
            f"from {start.isoformat()} through {last.isoformat()} (inclusive). "
            "Do not use any other dates, years, or past months — only those dates.\n"
            "Each array entry should include:\n"
            "  - date_of_workout (ISO date YYYY-MM-DD, must be one of the 14 days above)\n"
            "  - exercise_name\n"
            "  - exercise_description\n"
            "  - rep_count (number, e.g. 10)\n"
            "  - muscle_group\n"
            "  - expected_calories_burnt (number)\n"
            "  - weight_to_lift_suggestion (number or null)\n\n"
            f"User profile: {json.dumps(health_data)}"
        )

        try:
            response = self.model.generate_content(
                contents=[prompt],
                generation_config={"temperature": 0.5, "max_output_tokens": 8192},
            )
            text = ""
            if hasattr(response, "text") and response.text:
                text = response.text.strip()
            elif hasattr(response, "candidates") and response.candidates:
                text = response.candidates[0].content.parts[0].text.strip()

            # Strip Markdown fences if the model wrapped JSON in ```json ... ```
            if "```" in text:
                text = text.split("```")[1].replace("json", "").strip()

            plan = json.loads(text)
            if not isinstance(plan, list):
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
            return out
        except (json.JSONDecodeError, ValueError, KeyError, TypeError) as e:
            raise Exception(f"Failed to parse fitness plan from model: {e}") from e


__all__ = ["GeminiClient"]

