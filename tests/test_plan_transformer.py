import pytest

from app.fitness.plan_transformer import (
    PlanParseError,
    mapDatabasePlanToCalendar,
    mapLLMPlanToStructuredPlan,
)


def test_map_llm_plan_to_structured_plan_json():
    raw = {
        "planName": "2 Week Plan",
        "weeks": [
            {
                "weekNumber": 1,
                "days": [
                    {
                        "workoutType": "Upper Body",
                        "exercises": [
                            {"name": "Bench Press", "sets": 3, "reps": 8, "weight": "70%"}
                        ],
                    }
                ],
            }
        ],
    }

    structured = mapLLMPlanToStructuredPlan(raw, "2026-02-15")

    assert structured["planName"] == "2 Week Plan"
    assert structured["startDate"] == "2026-02-15"
    assert len(structured["weeks"]) == 1
    assert len(structured["weeks"][0]["days"]) == 7
    assert structured["weeks"][0]["days"][0]["date"] == "2026-02-15"
    assert structured["weeks"][0]["days"][0]["workoutType"] == "Upper Body"


def test_map_llm_plan_to_structured_plan_text():
    raw = """
    Week 1
    Day 1: Upper Body - Bench Press 3x8
    Day 2: Rest Day
    """

    structured = mapLLMPlanToStructuredPlan(raw, "2026-02-15")

    assert structured["startDate"] == "2026-02-15"
    assert structured["weeks"][0]["days"][0]["date"] == "2026-02-15"
    assert structured["weeks"][0]["days"][0]["workoutType"] == "Upper Body"
    assert structured["weeks"][0]["days"][1]["workoutType"] == "Rest"


def test_map_llm_plan_to_structured_plan_invalid_start_date():
    with pytest.raises(PlanParseError):
        mapLLMPlanToStructuredPlan({}, "invalid-date")


def test_map_database_plan_to_calendar_snapshot_fields():
    plan_entries = [
        {
            "date_of_workout": "2026-02-15",
            "exercise_name": "Bench Press",
            "exercise_description": "Chest compound movement",
            "rep_count": 8,
            "muscle_group": "Chest",
            "expected_calories_burnt": 50,
            "weight_to_lift_suggestion": 75,
        },
        {
            "date_of_workout": "2026-02-15",
            "exercise_name": "Incline Press",
            "exercise_description": "Upper chest focus",
            "rep_count": 10,
            "muscle_group": "Chest",
            "expected_calories_burnt": 45,
            "weight_to_lift_suggestion": 65,
        },
    ]

    structured = mapDatabasePlanToCalendar(plan_entries)
    day = structured["weeks"][0]["days"][0]

    assert day["date"] == "2026-02-15"
    assert day["workoutType"] == "Chest Focus"
    assert day["title"] == "Chest Focus"
    assert day["targetMuscleGroups"] == ["Chest"]
    assert day["estimatedDurationMinutes"] == 20
    assert day["totalExpectedCaloriesBurnt"] == 95
    assert day["exercises"][0]["name"] == "Bench Press"
    assert day["exercises"][0]["duration"] == "10 min"
    assert day["exercises"][0]["weight"] == "75 lbs"


def test_map_database_plan_to_calendar_rest_day_defaults():
    plan_entries = [
        {
            "date_of_workout": "2026-02-16",
            "exercise_name": "Bodyweight Squat",
            "rep_count": 12,
        }
    ]

    structured = mapDatabasePlanToCalendar(plan_entries)
    first_day = structured["weeks"][0]["days"][0]
    second_day = structured["weeks"][0]["days"][1]

    assert first_day["date"] == "2026-02-16"
    assert first_day["workoutType"] == "Workout"
    assert first_day["exercises"][0]["weight"] == ""

    assert second_day["workoutType"] == "Rest"
    assert second_day["exercises"] == []
    assert second_day["estimatedDurationMinutes"] == 0