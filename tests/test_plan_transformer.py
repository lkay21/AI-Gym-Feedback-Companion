import pytest

from app.fitness.plan_transformer import mapLLMPlanToStructuredPlan, PlanParseError


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