"""
Service layer for Fitness Plan CRUD in DynamoDB.
"""
from decimal import Decimal
from typing import Any, Dict, List, Optional

from botocore.exceptions import ClientError

from app.dynamodb_module import FITNESS_PLAN_TABLE, get_dynamodb_resource
from app.fitness_plan_module.models import FitnessPlan
from app.core.errors import NotFoundError


def _decimalize(obj: Any) -> Any:
    """Convert float to Decimal for DynamoDB."""
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: _decimalize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_decimalize(x) for x in obj]
    return obj


class FitnessPlanService:
    """CRUD for fitness_plan table."""

    def __init__(self):
        self.dynamodb = get_dynamodb_resource()
        self.table = self.dynamodb.Table(FITNESS_PLAN_TABLE)

    def create(self, plan: FitnessPlan) -> FitnessPlan:
        """Insert a fitness plan entry."""
        try:
            item = plan.to_dict()
            item = _decimalize(item)
            self.table.put_item(Item=item)
            return plan
        except ClientError as e:
            raise Exception(f"Failed to create fitness plan: {e}") from e

    def get(self, user_id: str, workout_id: str) -> Optional[FitnessPlan]:
        """Get one entry by user_id and workout_id."""
        try:
            r = self.table.get_item(
                Key={"user_id": user_id, "workout_id": workout_id}
            )
            if "Item" not in r:
                return None
            return FitnessPlan.from_dict(r["Item"])
        except ClientError as e:
            raise Exception(f"Failed to get fitness plan: {e}") from e

    def get_by_user(
        self,
        user_id: str,
        limit: int = 100,
        workout_id_after: Optional[str] = None,
    ) -> List[FitnessPlan]:
        """List entries for a user, optionally after a workout_id (sort by workout_id)."""
        try:
            params = {
                "KeyConditionExpression": "user_id = :uid",
                "ExpressionAttributeValues": {":uid": user_id},
                "Limit": limit,
                "ScanIndexForward": True,
            }
            if workout_id_after is not None:
                params["KeyConditionExpression"] += " and workout_id > :wid"
                params["ExpressionAttributeValues"][":wid"] = workout_id_after
            r = self.table.query(**params)
            return [FitnessPlan.from_dict(i) for i in r.get("Items", [])]
        except ClientError as e:
            raise Exception(f"Failed to list fitness plans: {e}") from e

    def update(
        self, user_id: str, workout_id: str, updates: Dict[str, Any]
    ) -> FitnessPlan:
        """Partial update of one entry. Skips user_id and workout_id."""
        try:
            updates = {k: v for k, v in updates.items() if k not in ("user_id", "workout_id")}
            if not updates:
                existing = self.get(user_id, workout_id)
                if existing is None:
                    raise NotFoundError("Fitness plan entry not found")
                return existing
            names = {}
            values = {}
            for key, value in updates.items():
                names[f"#{key}"] = key
                values[f":{key}"] = _decimalize(value)
            set_parts = [f"#{k} = :{k}" for k in updates]
            expr = "SET " + ", ".join(set_parts)
            r = self.table.update_item(
                Key={"user_id": user_id, "workout_id": workout_id},
                UpdateExpression=expr,
                ExpressionAttributeNames=names,
                ExpressionAttributeValues=values,
                ReturnValues="ALL_NEW",
            )
            return FitnessPlan.from_dict(r["Attributes"])
        except ClientError as e:
            raise Exception(f"Failed to update fitness plan: {e}") from e

    def delete(self, user_id: str, workout_id: str) -> bool:
        """Delete one entry."""
        try:
            self.table.delete_item(
                Key={"user_id": user_id, "workout_id": workout_id}
            )
            return True
        except ClientError as e:
            raise Exception(f"Failed to delete fitness plan: {e}") from e
