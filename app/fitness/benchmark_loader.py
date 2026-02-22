"""
Fitness benchmark and reference data loader.

Loads standard fitness benchmarks on application startup for use in
comparisons and personalized recommendations.

This module is intentionally independent of AI or UI logic.
"""

from typing import Dict, Any


def _normalize_categories(raw: Any) -> Dict[str, Dict[str, Any]]:
    """
    Normalize raw benchmark input into a predictable structure.

    Expected output format:
        {
            "category": { ... category_data ... },
            "category_2": { ... }
        }

    If raw data is invalid, returns an empty dict.
    """
    if not isinstance(raw, dict):
        return {}

    normalized: Dict[str, Dict[str, Any]] = {}
    for category, category_data in raw.items():
        if not isinstance(category, str) or not category:
            continue
        if not isinstance(category_data, dict):
            continue
        normalized[category] = category_data
    return normalized


def load_fitness_benchmarks() -> Dict[str, Dict[str, Any]]:
    """
    Load fitness benchmarks and reference data on startup.
    
    This function initializes standard fitness benchmarks that can be used
    for comparing user performance and generating recommendations.
    
    Returns:
        dict: Loaded benchmarks data organized by category. Always returns a dict.
        
    Raises:
        Exception: If benchmarks cannot be loaded
    """
    # Placeholder benchmarks loading logic
    # In production, this would load from a database or external source
    raw_benchmarks: Dict[str, Any] = {
        "strength": {
            "male": {
                "age_20_30": {
                    "bench_press_lbs": 185,
                    "squat_lbs": 315,
                    "deadlift_lbs": 405
                },
                "age_30_40": {
                    "bench_press_lbs": 175,
                    "squat_lbs": 295,
                    "deadlift_lbs": 385
                }
            },
            "female": {
                "age_20_30": {
                    "bench_press_lbs": 110,
                    "squat_lbs": 190,
                    "deadlift_lbs": 245
                },
                "age_30_40": {
                    "bench_press_lbs": 100,
                    "squat_lbs": 175,
                    "deadlift_lbs": 225
                }
            }
        },
        "cardio": {
            "male": {
                "age_20_30": {
                    "5k_run_minutes": 22,
                    "10k_run_minutes": 48,
                    "marathon_minutes": 215
                },
                "age_30_40": {
                    "5k_run_minutes": 24,
                    "10k_run_minutes": 52,
                    "marathon_minutes": 235
                }
            },
            "female": {
                "age_20_30": {
                    "5k_run_minutes": 25,
                    "10k_run_minutes": 55,
                    "marathon_minutes": 245
                },
                "age_30_40": {
                    "5k_run_minutes": 27,
                    "10k_run_minutes": 59,
                    "marathon_minutes": 260
                }
            }
        },
        "flexibility": {
            "sit_and_reach_cm": {
                "excellent": 25,
                "good": 17,
                "average": 6,
                "fair": -4,
                "poor": -15
            }
        }
    }

    return _normalize_categories(raw_benchmarks)
