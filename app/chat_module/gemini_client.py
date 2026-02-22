"""Deprecated: use app.chatbot.gemini_client instead."""
from app.chatbot.gemini_client import GeminiClient

__all__ = ["GeminiClient"]

    def build_fixed_stats_intro(self, health_data: Optional[Dict[str, Any]]) -> str:
        """Build intro from HealthData fixed fields (age, height, weight, gender)."""
        parts = ["Here's what I have on file for you:\n"]
        if health_data:
            if health_data.get('age') is not None:
                parts.append(f"- Age: {health_data['age']}")
            if health_data.get('height') is not None:
                parts.append(f"- Height: {health_data['height']}")
            if health_data.get('weight') is not None:
                parts.append(f"- Weight: {health_data['weight']}")
            if health_data.get('gender'):
                parts.append(f"- Gender: {health_data['gender']}")
        if len(parts) == 1:
            parts[0] = "I'd like to tailor advice to you.\n"
        parts.append("\nWhat is your main fitness goal right now? (e.g. lose weight, build muscle, improve endurance)")
        return "\n".join(parts)

    def generate_follow_up_questions(self, fitness_goal: str, count: int = 3) -> List[str]:
        """Generate 2-3 follow-up questions tailored to the user's fitness goal."""
        prompt = (
            f"The user has stated their fitness goal: \"{fitness_goal}\". "
            f"Generate exactly {min(count, 3)} short, specific follow-up questions to better understand their situation and tailor advice. "
            "Each question should be one sentence, conversational, and relevant to their goal (e.g. experience level, constraints, preferences). "
            "Return ONLY a JSON array of strings, e.g. [\"Question 1?\", \"Question 2?\", \"Question 3?\"] with no other text."
        )
        try:
            response = self.model.generate_content(
                contents=prompt,
                generation_config={'temperature': 0.6, 'max_output_tokens': 512}
            )
            text = response.text.strip() if hasattr(response, 'text') and response.text else ""
            if not text and hasattr(response, 'candidates') and response.candidates:
                text = response.candidates[0].content.parts[0].text.strip()
            if "```" in text:
                text = text.split("```")[1].replace("json", "").strip()
            questions = json.loads(text)
            if isinstance(questions, list) and len(questions) >= 1:
                return questions[:3]
            return []
        except (json.JSONDecodeError, ValueError):
            return [
                "How many days per week can you dedicate to exercise?",
                "Do you have any injuries or limitations I should know about?",
                "What type of activities do you enjoy most?",
            ]

    def generate_two_week_fitness_plan(self, health_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate a 2-week (14-day) fitness plan from user health data.
        Returns a list of exercise entries, each with: date_of_workout, exercise_name,
        exercise_description, rep_count, muscle_group, expected_calories_burnt, weight_to_lift_suggestion.
        """
        from datetime import datetime, timedelta
        start = datetime.utcnow().date()
        date_range = f"{start} to {start + timedelta(days=13)}"
        age = health_data.get("age")
        height = health_data.get("height")
        weight = health_data.get("weight")
        gender = health_data.get("gender")
        goal = health_data.get("fitness_goal")
        ctx = health_data.get("context")
        if isinstance(ctx, str):
            try:
                ctx = json.loads(ctx) if ctx else {}
            except Exception:
                ctx = {}
        qa = (ctx or {}).get("qa_pairs", [])
        qa_str = "\n".join([f"  Q: {x.get('q')} A: {x.get('a')}" for x in qa]) if qa else "  (none)"
        start_str = start.isoformat()
        prompt = f"""You are a certified personal trainer. Create a 2-week (14 days) fitness plan for this user.
Use dates starting from {start_str} for 14 consecutive days (one or more workout days per week as appropriate).

User health data:
- Age: {age}
- Height: {height}
- Weight: {weight}
- Gender: {gender}
- Fitness goal: {goal}

Additional context (Q&A):
{qa_str}

Output a JSON array of workout entries. Each entry is one exercise. Use 2-5 exercises per day over 14 days. Each object MUST have exactly these keys (use null for optional numbers if unsure):
- date_of_workout: string "YYYY-MM-DD"
- exercise_name: string
- exercise_description: string (1-2 sentences)
- rep_count: number (integer)
- muscle_group: string (e.g. Chest, Back, Legs, Shoulders, Core)
- expected_calories_burnt: number (estimate for that exercise)
- weight_to_lift_suggestion: number (in kg, appropriate for the user)

Return ONLY the JSON array, no other text. Example format:
[{{"date_of_workout":"2025-02-15","exercise_name":"Squats","exercise_description":"...","rep_count":12,"muscle_group":"Legs","expected_calories_burnt":45,"weight_to_lift_suggestion":40}},...]
"""
        try:
            response = self.model.generate_content(
                contents=prompt,
                generation_config={"temperature": 0.5, "max_output_tokens": 8192},
            )
            text = response.text.strip() if hasattr(response, "text") and response.text else ""
            if not text and hasattr(response, "candidates") and response.candidates:
                text = response.candidates[0].content.parts[0].text.strip()
            if "```" in text:
                text = text.split("```")[1].replace("json", "").strip()
            plan = json.loads(text)
            if not isinstance(plan, list):
                return []
            out = []
            for item in plan:
                if not isinstance(item, dict):
                    continue
                date_val = item.get("date_of_workout") or item.get("date")
                if not date_val:
                    continue
                out.append({
                    "date_of_workout": str(date_val)[:10],
                    "exercise_name": str(item.get("exercise_name") or item.get("exercise") or "").strip() or "Exercise",
                    "exercise_description": str(item.get("exercise_description") or item.get("description") or "").strip(),
                    "rep_count": int(item["rep_count"]) if item.get("rep_count") is not None else None,
                    "muscle_group": str(item.get("muscle_group") or "").strip(),
                    "expected_calories_burnt": float(item["expected_calories_burnt"]) if item.get("expected_calories_burnt") is not None else None,
                    "weight_to_lift_suggestion": float(item["weight_to_lift_suggestion"]) if item.get("weight_to_lift_suggestion") is not None else None,
                })
            return out
        except (json.JSONDecodeError, ValueError, KeyError, TypeError) as e:
            raise Exception(f"Failed to parse fitness plan from model: {e}") from e

