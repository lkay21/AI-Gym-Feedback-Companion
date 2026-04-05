#!/usr/bin/env python3
"""
Build a JSON object of environment variables to inject into the ECS task definition.

Used by .github/workflows/cd.yml. Two sources (explicit GitHub secrets win on key clash):

1. Repository secret ECS_TASK_ENV_JSON — JSON object of KEY/values.

2. Per-secret env vars in ALLOWLIST — the workflow passes ${{ secrets.NAME }} into the
   same NAME; non-empty values are merged (overriding JSON).

ALLOWLIST matches the backend .env surface this project deploys to ECS; extend both
this tuple and cd.yml when adding variables.

Prints a single-line JSON object to stdout for jq --argjson.
"""
from __future__ import annotations

import json
import os
import sys

ALLOWLIST = (
    "SECRET_KEY",
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "GEMINI_API_KEY",
    "AWS_REGION",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "DYNAMODB_USER_PROFILES_TABLE",
    "DYNAMODB_HEALTH_DATA_TABLE",
    "SESSION_COOKIE_SECURE",
    "CORS_ORIGINS",
)


def main() -> None:
    merged: dict[str, str] = {}

    raw_json = os.environ.get("ECS_TASK_ENV_JSON", "").strip()
    if raw_json:
        try:
            parsed = json.loads(raw_json)
        except json.JSONDecodeError as e:
            print(f"ECS_TASK_ENV_JSON is not valid JSON: {e}", file=sys.stderr)
            sys.exit(1)
        if not isinstance(parsed, dict):
            print("ECS_TASK_ENV_JSON must be a JSON object", file=sys.stderr)
            sys.exit(1)
        for key, value in parsed.items():
            if value is None:
                continue
            merged[str(key)] = str(value)

    for key in ALLOWLIST:
        value = os.environ.get(key, "").strip()
        if value:
            merged[key] = value

    if not merged.get("SUPABASE_URL") or not merged.get("SUPABASE_ANON_KEY"):
        print(
            "Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set (via ECS_TASK_ENV_JSON "
            "and/or individual GitHub secrets).",
            file=sys.stderr,
        )
        sys.exit(1)

    print(json.dumps(merged, separators=(",", ":")))


if __name__ == "__main__":
    main()
