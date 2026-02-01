"""
Unit tests for the UserProfile model.

Tests cover:
- UserProfile creation and attributes
- from_dict() factory method
- String representation
- Field validation
"""

import unittest
from app.database.models import UserProfile


class TestUserProfileCreation(unittest.TestCase):
    """Test UserProfile object creation."""
    
    def test_create_user_profile_with_all_fields(self):
        """Test creating a UserProfile with all fields."""
        profile = UserProfile(
            name="John Doe",
            age=30,
            gender="male",
            height="5'10\"",
            weight="180 lbs",
            fitness_goals=["lose weight", "build muscle"]
        )
        
        self.assertEqual(profile.name, "John Doe")
        self.assertEqual(profile.age, 30)
        self.assertEqual(profile.gender, "male")
        self.assertEqual(profile.height, "5'10\"")
        self.assertEqual(profile.weight, "180 lbs")
        self.assertEqual(profile.fitness_goals, ["lose weight", "build muscle"])
    
    def test_create_user_profile_minimal(self):
        """Test creating a UserProfile with only required field."""
        profile = UserProfile(name="Jane Doe")
        
        self.assertEqual(profile.name, "Jane Doe")
        self.assertIsNone(profile.age)
        self.assertIsNone(profile.gender)
        self.assertIsNone(profile.height)
        self.assertIsNone(profile.weight)
        self.assertEqual(profile.fitness_goals, [])
    
    def test_create_user_profile_with_partial_fields(self):
        """Test creating a UserProfile with some fields."""
        profile = UserProfile(
            name="Alice",
            age=25,
            weight="140 lbs"
        )
        
        self.assertEqual(profile.name, "Alice")
        self.assertEqual(profile.age, 25)
        self.assertIsNone(profile.gender)
        self.assertIsNone(profile.height)
        self.assertEqual(profile.weight, "140 lbs")


class TestUserProfileFromDict(unittest.TestCase):
    """Test UserProfile.from_dict() factory method."""
    
    def test_from_dict_with_all_fields(self):
        """Test from_dict with complete data."""
        data = {
            'name': 'Bob Smith',
            'age': 35,
            'gender': 'male',
            'height': '6\'0\"',
            'weight': '190 lbs',
            'fitness_goals': ['endurance', 'strength']
        }
        
        profile = UserProfile.from_dict(data)
        
        self.assertEqual(profile.name, 'Bob Smith')
        self.assertEqual(profile.age, 35)
        self.assertEqual(profile.gender, 'male')
        self.assertEqual(profile.height, '6\'0\"')
        self.assertEqual(profile.weight, '190 lbs')
        self.assertEqual(profile.fitness_goals, ['endurance', 'strength'])
    
    def test_from_dict_with_partial_data(self):
        """Test from_dict with incomplete data."""
        data = {
            'name': 'Carol',
            'age': 28
        }
        
        profile = UserProfile.from_dict(data)
        
        self.assertEqual(profile.name, 'Carol')
        self.assertEqual(profile.age, 28)
        self.assertIsNone(profile.gender)
        self.assertIsNone(profile.height)
        self.assertIsNone(profile.weight)
        self.assertEqual(profile.fitness_goals, [])
    
    def test_from_dict_with_empty_dict(self):
        """Test from_dict with empty dictionary."""
        data = {}
        
        profile = UserProfile.from_dict(data)
        
        self.assertIsNone(profile.name)
        self.assertIsNone(profile.age)
        self.assertIsNone(profile.gender)
        self.assertIsNone(profile.height)
        self.assertIsNone(profile.weight)
        self.assertEqual(profile.fitness_goals, [])
    
    def test_from_dict_with_extra_fields(self):
        """Test that from_dict ignores extra fields."""
        data = {
            'name': 'David',
            'age': 40,
            'extra_field': 'should be ignored',
            'another_field': 123
        }
        
        profile = UserProfile.from_dict(data)
        
        self.assertEqual(profile.name, 'David')
        self.assertEqual(profile.age, 40)
        self.assertFalse(hasattr(profile, 'extra_field'))
        self.assertFalse(hasattr(profile, 'another_field'))


class TestUserProfileStringRepresentation(unittest.TestCase):
    """Test UserProfile string representation."""
    
    def test_repr_with_full_profile(self):
        """Test __repr__ with complete profile."""
        profile = UserProfile(
            name="Emma",
            age=26,
            gender="female"
        )
        
        repr_str = repr(profile)
        
        self.assertIn("UserProfile", repr_str)
        self.assertIn("Emma", repr_str)
        self.assertIn("26", repr_str)
        self.assertIn("female", repr_str)
    
    def test_repr_with_minimal_profile(self):
        """Test __repr__ with minimal profile."""
        profile = UserProfile(name="Frank")
        
        repr_str = repr(profile)
        
        self.assertIn("UserProfile", repr_str)
        self.assertIn("Frank", repr_str)


class TestUserProfileFitnessGoals(unittest.TestCase):
    """Test UserProfile fitness goals handling."""
    
    def test_fitness_goals_default_empty(self):
        """Test that fitness_goals defaults to empty list."""
        profile = UserProfile(name="Grace")
        
        self.assertEqual(profile.fitness_goals, [])
        self.assertIsInstance(profile.fitness_goals, list)
    
    def test_fitness_goals_from_dict(self):
        """Test fitness_goals from dictionary."""
        data = {
            'name': 'Henry',
            'fitness_goals': ['cardio', 'flexibility', 'core strength']
        }
        
        profile = UserProfile.from_dict(data)
        
        self.assertEqual(len(profile.fitness_goals), 3)
        self.assertIn('cardio', profile.fitness_goals)
        self.assertIn('flexibility', profile.fitness_goals)
        self.assertIn('core strength', profile.fitness_goals)
    
    def test_fitness_goals_empty_list_from_dict(self):
        """Test empty fitness_goals list from dictionary."""
        data = {
            'name': 'Iris',
            'fitness_goals': []
        }
        
        profile = UserProfile.from_dict(data)
        
        self.assertEqual(profile.fitness_goals, [])


class TestUserProfileDataTypes(unittest.TestCase):
    """Test UserProfile with various data types."""
    
    def test_age_as_integer(self):
        """Test age stored as integer."""
        profile = UserProfile(name="Jack", age=32)
        
        self.assertIsInstance(profile.age, int)
        self.assertEqual(profile.age, 32)
    
    def test_age_from_dict_as_integer(self):
        """Test age from dictionary stored correctly."""
        data = {'name': 'Karen', 'age': 29}
        profile = UserProfile.from_dict(data)
        
        self.assertIsInstance(profile.age, int)
        self.assertEqual(profile.age, 29)
    
    def test_fitness_goals_as_list(self):
        """Test fitness_goals stored as list."""
        goals = ['goal1', 'goal2', 'goal3']
        profile = UserProfile(name="Leo", fitness_goals=goals)
        
        self.assertIsInstance(profile.fitness_goals, list)
        self.assertEqual(len(profile.fitness_goals), 3)


if __name__ == "__main__":
    unittest.main()
