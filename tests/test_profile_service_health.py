"""
Unit tests for HealthDataService (profile_module.service).

Mocks DynamoDB so service code runs without AWS. Exercises get_health_profile,
create_or_update_health_profile, and helpers to improve coverage.
"""
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.profile_module.models import HealthData, HEALTH_PROFILE_TIMESTAMP


@pytest.fixture
def mock_dynamodb_table():
    """Mock DynamoDB table with get_item, put_item, query, update_item."""
    table = MagicMock()
    # Default: no item
    table.get_item.return_value = {}
    table.query.return_value = {"Items": []}
    return table


@pytest.fixture
def mock_dynamodb_resource(mock_dynamodb_table):
    """Mock DynamoDB resource that returns our table for any Table(name)."""
    resource = MagicMock()
    resource.Table.return_value = mock_dynamodb_table
    return resource


@pytest.fixture
def health_service_with_mock_db(monkeypatch, mock_dynamodb_resource):
    """Patch get_dynamodb_resource and return real HealthDataService."""
    monkeypatch.setattr(
        "app.profile_module.service.get_dynamodb_resource",
        lambda: mock_dynamodb_resource,
    )
    from app.profile_module.service import HealthDataService
    return HealthDataService()


def test_get_health_profile_returns_none_when_no_item(health_service_with_mock_db, mock_dynamodb_table):
    """get_health_profile returns None when DynamoDB has no item."""
    mock_dynamodb_table.get_item.return_value = {}
    svc = health_service_with_mock_db
    result = svc.get_health_profile("user-1")
    assert result is None
    mock_dynamodb_table.get_item.assert_called_once()
    call_kw = mock_dynamodb_table.get_item.call_args[1]
    assert call_kw["Key"]["user_id"] == "user-1"
    assert call_kw["Key"]["timestamp"] == HEALTH_PROFILE_TIMESTAMP


def test_get_health_profile_returns_health_data_when_item_exists(health_service_with_mock_db, mock_dynamodb_table):
    """get_health_profile returns HealthData when DynamoDB has an item."""
    mock_dynamodb_table.get_item.return_value = {
        "Item": {
            "user_id": "user-1",
            "timestamp": HEALTH_PROFILE_TIMESTAMP,
            "age": 30,
            "height": 175.0,
            "weight": 70.0,
            "gender": "male",
            "fitness_goal": "build muscle",
            "context": '{"pending_fixed": [], "qa_pairs": []}',
        }
    }
    svc = health_service_with_mock_db
    result = svc.get_health_profile("user-1")
    assert result is not None
    assert result.user_id == "user-1"
    assert result.age == 30
    assert result.height == 175.0
    assert result.weight == 70.0
    assert result.gender == "male"
    assert result.fitness_goal == "build muscle"
    assert isinstance(result.context, dict)
    assert result.context.get("pending_fixed") == []


def test_get_health_profile_handles_decimal_from_dynamodb(health_service_with_mock_db, mock_dynamodb_table):
    """get_health_profile correctly converts Decimal to float."""
    mock_dynamodb_table.get_item.return_value = {
        "Item": {
            "user_id": "user-1",
            "timestamp": HEALTH_PROFILE_TIMESTAMP,
            "age": Decimal("25"),
            "height": Decimal("170.5"),
            "weight": Decimal("65.0"),
            "gender": "female",
        }
    }
    svc = health_service_with_mock_db
    result = svc.get_health_profile("user-1")
    assert result.age == 25
    assert result.height == 170.5
    assert result.weight == 65.0


def test_create_or_update_health_profile_creates_new(health_service_with_mock_db, mock_dynamodb_table):
    """create_or_update_health_profile creates new record when none exists."""
    mock_dynamodb_table.get_item.return_value = {}
    svc = health_service_with_mock_db
    result = svc.create_or_update_health_profile(
        "user-new",
        age=28,
        height=180.0,
        weight=75.0,
        gender="male",
        fitness_goal="lose weight",
    )
    assert result is not None
    assert result.user_id == "user-new"
    assert result.age == 28
    assert result.height == 180.0
    assert result.weight == 75.0
    assert result.gender == "male"
    assert result.fitness_goal == "lose weight"
    mock_dynamodb_table.put_item.assert_called_once()
    put_item = mock_dynamodb_table.put_item.call_args[1]["Item"]
    assert put_item["user_id"] == "user-new"
    assert put_item["timestamp"] == HEALTH_PROFILE_TIMESTAMP
    assert put_item["age"] == 28


def test_create_or_update_health_profile_updates_existing(health_service_with_mock_db, mock_dynamodb_table):
    """create_or_update_health_profile updates existing record."""
    mock_dynamodb_table.get_item.return_value = {
        "Item": {
            "user_id": "user-1",
            "timestamp": HEALTH_PROFILE_TIMESTAMP,
            "age": 25,
            "height": 170.0,
            "weight": 65.0,
            "gender": "female",
        }
    }
    mock_dynamodb_table.update_item.return_value = {
        "Attributes": {
            "user_id": "user-1",
            "timestamp": HEALTH_PROFILE_TIMESTAMP,
            "age": 25,
            "height": 170.0,
            "weight": 65.0,
            "gender": "female",
            "fitness_goal": "build muscle",
        }
    }
    svc = health_service_with_mock_db
    result = svc.create_or_update_health_profile("user-1", fitness_goal="build muscle")
    assert result is not None
    assert result.fitness_goal == "build muscle"
    mock_dynamodb_table.update_item.assert_called_once()
    call_kw = mock_dynamodb_table.update_item.call_args[1]
    assert call_kw["Key"]["user_id"] == "user-1"
    assert "UpdateExpression" in call_kw
    assert "fitness_goal" in str(call_kw.get("ExpressionAttributeNames", {}))


def test_create_or_update_health_profile_with_context(health_service_with_mock_db, mock_dynamodb_table):
    """create_or_update_health_profile stores context as JSON."""
    mock_dynamodb_table.get_item.return_value = {}
    svc = health_service_with_mock_db
    ctx = {"pending_fixed": [], "qa_pairs": [{"q": "a", "a": "b"}], "pending_questions": []}
    result = svc.create_or_update_health_profile("user-1", age=30, context=ctx)
    assert result.context == ctx
    put_item = mock_dynamodb_table.put_item.call_args[1]["Item"]
    assert "context" in put_item
    assert isinstance(put_item["context"], str)
    import json
    assert json.loads(put_item["context"]) == ctx


def test_decimalize_for_dynamodb_float():
    """_decimalize_for_dynamodb converts float to Decimal."""
    from app.profile_module.service import _decimalize_for_dynamodb
    assert _decimalize_for_dynamodb(3.14) == Decimal("3.14")
    assert _decimalize_for_dynamodb(100) == 100  # int unchanged


def test_decimalize_for_dynamodb_dict():
    """_decimalize_for_dynamodb recurses into dict."""
    from app.profile_module.service import _decimalize_for_dynamodb
    out = _decimalize_for_dynamodb({"a": 1.5, "b": "x"})
    assert out["a"] == Decimal("1.5")
    assert out["b"] == "x"


def test_get_health_data_returns_none_when_missing(health_service_with_mock_db, mock_dynamodb_table):
    """get_health_data returns None when item not found."""
    mock_dynamodb_table.get_item.return_value = {}
    svc = health_service_with_mock_db
    result = svc.get_health_data("user-1", "2025-01-01T00:00:00")
    assert result is None


def test_get_health_data_returns_health_data_when_found(health_service_with_mock_db, mock_dynamodb_table):
    """get_health_data returns HealthData when item exists."""
    mock_dynamodb_table.get_item.return_value = {
        "Item": {
            "user_id": "user-1",
            "timestamp": "2025-01-01T00:00:00",
            "age": 30,
        }
    }
    svc = health_service_with_mock_db
    result = svc.get_health_data("user-1", "2025-01-01T00:00:00")
    assert result is not None
    assert result.user_id == "user-1"
    assert result.timestamp == "2025-01-01T00:00:00"
    assert result.age == 30


def test_create_health_data_calls_put_item(health_service_with_mock_db, mock_dynamodb_table):
    """create_health_data puts item to DynamoDB."""
    mock_dynamodb_table.get_item.return_value = {}
    svc = health_service_with_mock_db
    health_data = HealthData(
        user_id="user-1",
        timestamp=HEALTH_PROFILE_TIMESTAMP,
        age=25,
        height=175.0,
        weight=70.0,
        gender="male",
    )
    result = svc.create_health_data(health_data)
    assert result == health_data
    mock_dynamodb_table.put_item.assert_called_once()
    put_item = mock_dynamodb_table.put_item.call_args[1]["Item"]
    assert put_item["user_id"] == "user-1"
    assert put_item["age"] == 25
