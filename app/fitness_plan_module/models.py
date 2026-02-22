"""
Fitness Plan model for DynamoDB fitness_plan table.
Schema: user_id (PK), workout_id (SK), date_of_workout, exercise_name, exercise_description,
        rep_count, muscle_group, expected_calories_burnt, weight_to_lift_suggestion.
"""
from decimal import Decimal  # DynamoDB returns Decimal for numbers
from typing import Any, Dict, Optional


class FitnessPlan:
    """Single workout entry in the fitness plan (one row per user_id + workout_id)."""

    def __init__(
        self,
        user_id: str,
        workout_id: str,
        date_of_workout: Optional[str] = None,  # e.g. ISO date "2025-02-15"
        exercise_name: Optional[str] = None,
        exercise_description: Optional[str] = None,
        rep_count: Optional[int] = None,
        muscle_group: Optional[str] = None,
        expected_calories_burnt: Optional[float] = None,
        weight_to_lift_suggestion: Optional[float] = None,  # kg or lbs
    ):
        self.user_id = user_id
        self.workout_id = workout_id
        self.date_of_workout = date_of_workout
        self.exercise_name = exercise_name
        self.exercise_description = exercise_description
        self.rep_count = rep_count
        self.muscle_group = muscle_group
        self.expected_calories_burnt = expected_calories_burnt
        self.weight_to_lift_suggestion = weight_to_lift_suggestion

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict (Python types for API; service decimalizes for DynamoDB)."""
        result = {
            "user_id": self.user_id,
            "workout_id": self.workout_id,
            "date_of_workout": self.date_of_workout,
            "exercise_name": self.exercise_name,
            "exercise_description": self.exercise_description,
            "rep_count": self.rep_count,
            "muscle_group": self.muscle_group,
            "expected_calories_burnt": self.expected_calories_burnt,
            "weight_to_lift_suggestion": self.weight_to_lift_suggestion,
        }
        return {k: v for k, v in result.items() if v is not None}

    @classmethod
    def _num(cls, value: Any) -> Optional[float]:
        if value is None:
            return None
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, (int, float)):
            return float(value)
        return None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FitnessPlan":
        """Create FitnessPlan from DynamoDB item (Decimal -> float for numbers)."""
        rep_count = data.get("rep_count")
        if isinstance(rep_count, Decimal):
            rep_count = int(rep_count)
        return cls(
            user_id=data.get("user_id"),
            workout_id=data.get("workout_id"),
            date_of_workout=data.get("date_of_workout"),
            exercise_name=data.get("exercise_name"),
            exercise_description=data.get("exercise_description"),
            rep_count=rep_count,
            muscle_group=data.get("muscle_group"),
            expected_calories_burnt=cls._num(data.get("expected_calories_burnt")),
            weight_to_lift_suggestion=cls._num(data.get("weight_to_lift_suggestion")),
        )
