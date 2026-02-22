"""
Unit tests for the benchmark loader module.

Tests cover:
- Benchmark loading
- Data structure validation
- Error handling
"""

import unittest
from app.fitness.benchmark_loader import load_fitness_benchmarks, _normalize_categories


class TestBenchmarkLoading(unittest.TestCase):
    """Test benchmark loading functionality."""
    
    def test_load_fitness_benchmarks_returns_dict(self):
        """Test that load_fitness_benchmarks returns a dictionary."""
        benchmarks = load_fitness_benchmarks()
        
        self.assertIsInstance(benchmarks, dict)

    def test_load_benchmarks_category_values_are_dicts(self):
        """Test that each category value is a dict for predictable structure."""
        benchmarks = load_fitness_benchmarks()

        for category, data in benchmarks.items():
            self.assertIsInstance(category, str)
            self.assertIsInstance(data, dict)
    
    def test_benchmarks_contains_main_categories(self):
        """Test that benchmarks contain main fitness categories."""
        benchmarks = load_fitness_benchmarks()
        
        self.assertIn('strength', benchmarks)
        self.assertIn('cardio', benchmarks)
        self.assertIn('flexibility', benchmarks)
    
    def test_strength_benchmarks_structure(self):
        """Test strength benchmarks have correct structure."""
        benchmarks = load_fitness_benchmarks()
        strength = benchmarks['strength']
        
        self.assertIn('male', strength)
        self.assertIn('female', strength)
        
        # Check male benchmarks
        self.assertIn('age_20_30', strength['male'])
        self.assertIn('age_30_40', strength['male'])
        
        # Check female benchmarks
        self.assertIn('age_20_30', strength['female'])
        self.assertIn('age_30_40', strength['female'])
    
    def test_strength_benchmarks_contain_exercises(self):
        """Test strength benchmarks contain exercise data."""
        benchmarks = load_fitness_benchmarks()
        male_young = benchmarks['strength']['male']['age_20_30']
        
        self.assertIn('bench_press_lbs', male_young)
        self.assertIn('squat_lbs', male_young)
        self.assertIn('deadlift_lbs', male_young)
    
    def test_cardio_benchmarks_structure(self):
        """Test cardio benchmarks have correct structure."""
        benchmarks = load_fitness_benchmarks()
        cardio = benchmarks['cardio']
        
        self.assertIn('male', cardio)
        self.assertIn('female', cardio)
    
    def test_cardio_benchmarks_contain_events(self):
        """Test cardio benchmarks contain running event data."""
        benchmarks = load_fitness_benchmarks()
        male_young = benchmarks['cardio']['male']['age_20_30']
        
        self.assertIn('5k_run_minutes', male_young)
        self.assertIn('10k_run_minutes', male_young)
        self.assertIn('marathon_minutes', male_young)
    
    def test_flexibility_benchmarks_structure(self):
        """Test flexibility benchmarks have correct structure."""
        benchmarks = load_fitness_benchmarks()
        flexibility = benchmarks['flexibility']
        
        self.assertIn('sit_and_reach_cm', flexibility)
    
    def test_flexibility_benchmarks_contain_ratings(self):
        """Test flexibility benchmarks contain rating levels."""
        benchmarks = load_fitness_benchmarks()
        sit_reach = benchmarks['flexibility']['sit_and_reach_cm']
        
        self.assertIn('excellent', sit_reach)
        self.assertIn('good', sit_reach)
        self.assertIn('average', sit_reach)
        self.assertIn('fair', sit_reach)
        self.assertIn('poor', sit_reach)
    
    def test_benchmark_values_are_numbers(self):
        """Test that benchmark values are numeric."""
        benchmarks = load_fitness_benchmarks()
        
        # Test strength values
        bench_press = benchmarks['strength']['male']['age_20_30']['bench_press_lbs']
        self.assertIsInstance(bench_press, (int, float))
        
        # Test cardio values
        five_k = benchmarks['cardio']['female']['age_30_40']['5k_run_minutes']
        self.assertIsInstance(five_k, (int, float))
        
        # Test flexibility values
        excellent = benchmarks['flexibility']['sit_and_reach_cm']['excellent']
        self.assertIsInstance(excellent, (int, float))


class TestBenchmarkDataConsistency(unittest.TestCase):
    """Test consistency of benchmark data."""
    
    def test_strength_values_reasonable(self):
        """Test that strength values are in reasonable ranges."""
        benchmarks = load_fitness_benchmarks()
        
        # All strength benchmarks should be positive
        male_30_40 = benchmarks['strength']['male']['age_30_40']
        self.assertGreater(male_30_40['bench_press_lbs'], 0)
        self.assertGreater(male_30_40['squat_lbs'], 0)
        self.assertGreater(male_30_40['deadlift_lbs'], 0)
    
    def test_cardio_values_reasonable(self):
        """Test that cardio times are in reasonable ranges."""
        benchmarks = load_fitness_benchmarks()
        
        # All cardio times should be positive minutes
        female_20_30 = benchmarks['cardio']['female']['age_20_30']
        self.assertGreater(female_20_30['5k_run_minutes'], 0)
        self.assertGreater(female_20_30['10k_run_minutes'], 0)
        self.assertGreater(female_20_30['marathon_minutes'], 0)
        
        # Marathon should be longer than 5k
        self.assertGreater(
            female_20_30['marathon_minutes'],
            female_20_30['5k_run_minutes']
        )
    
    def test_flexibility_values_reasonable(self):
        """Test that flexibility values are in reasonable ranges."""
        benchmarks = load_fitness_benchmarks()
        sit_reach = benchmarks['flexibility']['sit_and_reach_cm']
        
        # Values should be in reasonable order
        self.assertGreater(sit_reach['excellent'], sit_reach['good'])
        self.assertGreater(sit_reach['good'], sit_reach['average'])
        self.assertGreater(sit_reach['average'], sit_reach['fair'])
        self.assertGreater(sit_reach['fair'], sit_reach['poor'])
    
    def test_age_progression_makes_sense(self):
        """Test that benchmarks decrease with age."""
        benchmarks = load_fitness_benchmarks()
        
        # Males 20-30 should have better benchmarks than 30-40
        male_young = benchmarks['strength']['male']['age_20_30']['bench_press_lbs']
        male_older = benchmarks['strength']['male']['age_30_40']['bench_press_lbs']
        self.assertGreater(male_young, male_older)


class TestBenchmarkLoadingErrorHandling(unittest.TestCase):
    """Test error handling in benchmark loading."""
    
    def test_load_benchmarks_does_not_raise_exception(self):
        """Test that load_fitness_benchmarks completes without error."""
        try:
            benchmarks = load_fitness_benchmarks()
            self.assertIsNotNone(benchmarks)
        except Exception as e:
            self.fail(f"load_fitness_benchmarks raised {type(e).__name__}: {e}")
    
    def test_repeated_loads_return_same_structure(self):
        """Test that multiple loads return consistent structure."""
        benchmarks1 = load_fitness_benchmarks()
        benchmarks2 = load_fitness_benchmarks()
        
        # Should have same keys
        self.assertEqual(benchmarks1.keys(), benchmarks2.keys())
        
        # Should have same values
        self.assertEqual(
            benchmarks1['strength']['male']['age_20_30']['bench_press_lbs'],
            benchmarks2['strength']['male']['age_20_30']['bench_press_lbs']
        )


class TestBenchmarkNormalization(unittest.TestCase):
    """Test normalization and graceful handling of invalid data."""

    def test_normalize_invalid_raw_returns_empty(self):
        """Test invalid raw input returns empty dict."""
        self.assertEqual(_normalize_categories(None), {})
        self.assertEqual(_normalize_categories([]), {})
        self.assertEqual(_normalize_categories("invalid"), {})

    def test_normalize_skips_invalid_categories(self):
        """Test categories with invalid keys or values are skipped."""
        raw = {
            "strength": {"valid": True},
            "": {"invalid": True},
            123: {"invalid": True},
            "cardio": "not-a-dict"
        }

        normalized = _normalize_categories(raw)

        self.assertIn("strength", normalized)
        self.assertNotIn("", normalized)
        self.assertNotIn(123, normalized)
        self.assertNotIn("cardio", normalized)

    def test_normalize_preserves_valid_categories(self):
        """Test valid category data is preserved."""
        raw = {
            "flexibility": {"sit_and_reach_cm": {"good": 17}}
        }

        normalized = _normalize_categories(raw)

        self.assertEqual(normalized, raw)


class TestBenchmarkAccessPatterns(unittest.TestCase):
    """Test accessing benchmark data with different patterns."""
    
    def test_access_male_strength_benchmark(self):
        """Test accessing male strength benchmark."""
        benchmarks = load_fitness_benchmarks()
        value = benchmarks['strength']['male']['age_30_40']['squat_lbs']
        
        self.assertGreater(value, 0)
    
    def test_access_female_cardio_benchmark(self):
        """Test accessing female cardio benchmark."""
        benchmarks = load_fitness_benchmarks()
        value = benchmarks['cardio']['female']['age_20_30']['10k_run_minutes']
        
        self.assertGreater(value, 0)
    
    def test_access_flexibility_benchmark(self):
        """Test accessing flexibility benchmark."""
        benchmarks = load_fitness_benchmarks()
        value = benchmarks['flexibility']['sit_and_reach_cm']['average']
        
        self.assertIsNotNone(value)


if __name__ == "__main__":
    unittest.main()
