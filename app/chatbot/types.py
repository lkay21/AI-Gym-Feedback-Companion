from typing import List, TypedDict


class Exercise(TypedDict):
    name: str
    sets: int
    reps: int
    weight: str


class Day(TypedDict):
    workoutType: str
    exercises: List[Exercise]


class Week(TypedDict):
    weekNumber: int
    days: List[Day]


class FitnessPlan(TypedDict):
    planName: str
    weeks: List[Week]