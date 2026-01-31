"""
Data models for user profiles and health data
These define the structure of data stored in DynamoDB
"""
from datetime import datetime
from typing import Optional, Dict, List, Any

class UserProfile:
    """User profile model"""
    
    def __init__(
        self,
        user_id: str,
        age: Optional[int] = None,
        height: Optional[float] = None,  # in cm or inches
        weight: Optional[float] = None,  # in kg or lbs
        fitness_goals: Optional[List[str]] = None,
        gender: Optional[str] = None,
        activity_level: Optional[str] = None,  # e.g., "sedentary", "moderate", "active"
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None
    ):
        self.user_id = user_id
        self.age = age
        self.height = height
        self.weight = weight
        self.fitness_goals = fitness_goals or []
        self.gender = gender
        self.activity_level = activity_level
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for DynamoDB storage"""
        return {
            'user_id': self.user_id,
            'age': self.age,
            'height': self.height,
            'weight': self.weight,
            'fitness_goals': self.fitness_goals,
            'gender': self.gender,
            'activity_level': self.activity_level,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Create UserProfile from DynamoDB item"""
        return cls(
            user_id=data.get('user_id'),
            age=data.get('age'),
            height=data.get('height'),
            weight=data.get('weight'),
            fitness_goals=data.get('fitness_goals', []),
            gender=data.get('gender'),
            activity_level=data.get('activity_level'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )


class HealthData:
    """Health data model for workout history and activity metrics"""
    
    def __init__(
        self,
        user_id: str,
        timestamp: str,  # ISO format timestamp
        workout_type: Optional[str] = None,
        duration_minutes: Optional[float] = None,
        calories_burned: Optional[float] = None,
        heart_rate_avg: Optional[int] = None,
        heart_rate_max: Optional[int] = None,
        distance: Optional[float] = None,  # in km or miles
        sets: Optional[int] = None,
        reps: Optional[int] = None,
        weight_lifted: Optional[float] = None,  # in kg or lbs
        notes: Optional[str] = None,
        activity_metrics: Optional[Dict[str, Any]] = None  # Additional flexible metrics
    ):
        self.user_id = user_id
        self.timestamp = timestamp
        self.workout_type = workout_type
        self.duration_minutes = duration_minutes
        self.calories_burned = calories_burned
        self.heart_rate_avg = heart_rate_avg
        self.heart_rate_max = heart_rate_max
        self.distance = distance
        self.sets = sets
        self.reps = reps
        self.weight_lifted = weight_lifted
        self.notes = notes
        self.activity_metrics = activity_metrics or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert health data to dictionary for DynamoDB storage"""
        result = {
            'user_id': self.user_id,
            'timestamp': self.timestamp,
            'workout_type': self.workout_type,
            'duration_minutes': self.duration_minutes,
            'calories_burned': self.calories_burned,
            'heart_rate_avg': self.heart_rate_avg,
            'heart_rate_max': self.heart_rate_max,
            'distance': self.distance,
            'sets': self.sets,
            'reps': self.reps,
            'weight_lifted': self.weight_lifted,
            'notes': self.notes
        }
        
        # Add activity_metrics if present
        if self.activity_metrics:
            result['activity_metrics'] = self.activity_metrics
        
        # Remove None values
        return {k: v for k, v in result.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HealthData':
        """Create HealthData from DynamoDB item"""
        return cls(
            user_id=data.get('user_id'),
            timestamp=data.get('timestamp'),
            workout_type=data.get('workout_type'),
            duration_minutes=data.get('duration_minutes'),
            calories_burned=data.get('calories_burned'),
            heart_rate_avg=data.get('heart_rate_avg'),
            heart_rate_max=data.get('heart_rate_max'),
            distance=data.get('distance'),
            sets=data.get('sets'),
            reps=data.get('reps'),
            weight_lifted=data.get('weight_lifted'),
            notes=data.get('notes'),
            activity_metrics=data.get('activity_metrics', {})
        )

