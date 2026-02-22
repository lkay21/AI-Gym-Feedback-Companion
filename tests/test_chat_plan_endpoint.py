import json
import sys
import types
from datetime import date, timedelta

import pytest


supabase_stub = types.SimpleNamespace(create_client=lambda *args, **kwargs: None, Client=object)
botocore_exceptions_stub = types.SimpleNamespace(ClientError=Exception)
botocore_stub = types.SimpleNamespace(exceptions=botocore_exceptions_stub)
boto3_stub = types.SimpleNamespace(resource=lambda *args, **kwargs: None, client=lambda *args, **kwargs: None)

sys.modules.setdefault("supabase", supabase_stub)
sys.modules.setdefault("botocore", botocore_stub)
sys.modules.setdefault("botocore.exceptions", botocore_exceptions_stub)
sys.modules.setdefault("boto3", boto3_stub)

from app.main import create_app


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({"TESTING": True})
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def mock_authenticated_user(monkeypatch):
    """Mock authenticated user session"""
    from app.chat_module import routes as chat_routes
    monkeypatch.setattr(chat_routes, "get_authenticated_user_id", lambda: "test_user_123")


def test_generate_plan_success(client, monkeypatch, mock_authenticated_user):
    """Test successful 2-week plan generation from database"""
    from app.chat_module import routes as chat_routes
    from datetime import timedelta
    
    # Mock health profile
    class MockHealthProfile:
        def to_dict(self):
            return {
                "age": 25,
                "height": 175,
                "weight": 70,
                "gender": "male",
                "fitness_goal": "build muscle"
            }
    
    class MockHealthDataService:
        def get_health_profile(self, user_id):
            return MockHealthProfile()
    
    # Mock Gemini client for 2-week plan generation
    class MockGeminiClient:
        def generate_two_week_fitness_plan(self, health_dict):
            start_date = date.today()
            return [
                {
                    "date_of_workout": (start_date + timedelta(days=i)).isoformat(),
                    "exercise_name": f"Exercise {i+1}",
                    "exercise_description": f"Description for exercise {i+1}",
                    "rep_count": 10,
                    "muscle_group": "Chest" if i % 2 == 0 else "Back",
                    "expected_calories_burnt": 50,
                    "weight_to_lift_suggestion": 20
                }
                for i in range(14)  # 14 days of exercises
            ]
    
    # Mock FitnessPlanService and FitnessPlan
    class MockFitnessPlan:
        def __init__(self, **kwargs):
            self.user_id = kwargs.get('user_id')
            self.workout_id = kwargs.get('workout_id')
            self.date_of_workout = kwargs.get('date_of_workout')
            self.exercise_name = kwargs.get('exercise_name')
            self.exercise_description = kwargs.get('exercise_description')
            self.rep_count = kwargs.get('rep_count')
            self.muscle_group = kwargs.get('muscle_group')
            self.expected_calories_burnt = kwargs.get('expected_calories_burnt')
            self.weight_to_lift_suggestion = kwargs.get('weight_to_lift_suggestion')
        
        def to_dict(self):
            return {
                "user_id": self.user_id,
                "workout_id": self.workout_id,
                "date_of_workout": self.date_of_workout,
                "exercise_name": self.exercise_name,
                "exercise_description": self.exercise_description,
                "rep_count": self.rep_count,
                "muscle_group": self.muscle_group,
                "expected_calories_burnt": self.expected_calories_burnt,
                "weight_to_lift_suggestion": self.weight_to_lift_suggestion
            }
    
    class MockFitnessPlanService:
        def create(self, plan):
            pass
        
        def get_by_user(self, user_id):
            """Return mock fitness plan objects for the user"""
            start_date = date.today()
            return [
                MockFitnessPlan(
                    user_id=user_id,
                    workout_id=f"workout_{i}",
                    date_of_workout=(start_date + timedelta(days=i)).isoformat(),
                    exercise_name=f"Exercise {i+1}",
                    exercise_description=f"Description for exercise {i+1}",
                    rep_count=10,
                    muscle_group="Chest" if i % 2 == 0 else "Back",
                    expected_calories_burnt=50,
                    weight_to_lift_suggestion=20
                )
                for i in range(14)  # 14 days of exercises
            ]
    
    # Apply mocks
    monkeypatch.setattr("app.profile_module.service.HealthDataService", MockHealthDataService)
    monkeypatch.setattr(chat_routes, "GeminiClient", MockGeminiClient)
    
    # Mock inside the routes module imports
    def mock_import(*args, **kwargs):
        class Holder:
            FitnessPlan = MockFitnessPlan
            FitnessPlanService = MockFitnessPlanService
            HealthDataService = MockHealthDataService
        if args and args[0] == "app.fitness_plan_module.models":
            return Holder()
        if args and args[0] == "app.fitness_plan_module.service":
            return Holder()
        if args and args[0] == "app.profile_module.service":
            return Holder()
        if args and "plan_transformer" in args[0]:
            from app.fitness import plan_transformer
            return plan_transformer
        raise ImportError(f"Cannot import {args}")
    
    # Simpler approach: just patch inside test
    import sys
    original_fitness_plan_service = sys.modules.get("app.fitness_plan_module.service")
    original_fitness_plan_models = sys.modules.get("app.fitness_plan_module.models")
    
    # Create mock modules
    import types
    mock_service_module = types.ModuleType("mock_service")
    mock_service_module.FitnessPlanService = MockFitnessPlanService
    
    mock_models_module = types.ModuleType("mock_models")
    mock_models_module.FitnessPlan = MockFitnessPlan
    
    monkeypatch.setitem(sys.modules, "app.fitness_plan_module.service", mock_service_module)
    monkeypatch.setitem(sys.modules, "app.fitness_plan_module.models", mock_models_module)
    
    response = client.post("/api/chat/plan", json={})
    
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert "structuredPlan" in payload
    assert payload["structuredPlan"]["planName"] == "Your 2-Week Fitness Plan"
    assert len(payload["structuredPlan"]["weeks"]) == 2  # 2 weeks
    assert "Retrieved fitness plan with" in payload["message"]


def test_generate_plan_no_health_profile(client, monkeypatch, mock_authenticated_user):
    """Test error when user has no health profile"""
    from app.chat_module import routes as chat_routes
    
    class MockHealthDataService:
        def get_health_profile(self, user_id):
            return None
    
    monkeypatch.setattr("app.profile_module.service.HealthDataService", MockHealthDataService)
    
    response = client.post("/api/chat/plan", json={})
    
    assert response.status_code == 400
    payload = response.get_json()
    assert "No health profile found" in payload["error"]
    assert payload.get("requiresOnboarding") is True


def test_generate_plan_not_authenticated(client):
    """Test error when user is not authenticated"""
    response = client.post("/api/chat/plan", json={})
    
    assert response.status_code == 401
    payload = response.get_json()
    assert "Not authenticated" in payload["error"]