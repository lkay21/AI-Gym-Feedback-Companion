"""Tests for remapping LLM fitness plan dates to the generation start date."""

from datetime import date, timedelta

from app.chat_module.gemini_client import _renormalize_fitness_plan_dates


def test_renormalize_maps_wrong_year_blocks_to_consecutive_days():
    base = date(2026, 4, 1)
    entries = [
        {"date_of_workout": "2024-01-01", "exercise_name": "A"},
        {"date_of_workout": "2024-01-01", "exercise_name": "B"},
        {"date_of_workout": "2024-01-02", "exercise_name": "C"},
    ]
    _renormalize_fitness_plan_dates(entries, base)
    assert entries[0]["date_of_workout"] == base.isoformat()
    assert entries[1]["date_of_workout"] == base.isoformat()
    assert entries[2]["date_of_workout"] == (base + timedelta(days=1)).isoformat()


def test_renormalize_single_flat_date_splits_one_entry_per_day_when_possible():
    base = date(2026, 4, 4)
    entries = [{"date_of_workout": "2025-06-01", "exercise_name": f"E{i}"} for i in range(4)]
    _renormalize_fitness_plan_dates(entries, base)
    for i, e in enumerate(entries):
        assert e["date_of_workout"] == (base + timedelta(days=i)).isoformat()


def test_renormalize_caps_extra_blocks_at_day_14():
    base = date(2026, 1, 1)
    entries = [{"date_of_workout": f"2020-01-{i+1:02d}", "exercise_name": str(i)} for i in range(16)]
    _renormalize_fitness_plan_dates(entries, base)
    assert entries[13]["date_of_workout"] == (base + timedelta(days=13)).isoformat()
    assert entries[14]["date_of_workout"] == (base + timedelta(days=13)).isoformat()
    assert entries[15]["date_of_workout"] == (base + timedelta(days=13)).isoformat()
