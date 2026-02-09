#!/usr/bin/env python3
"""
Dummy upload script stub for manual test documentation.

"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Upload a workout video to the backend (stub).")
    p.add_argument("--file", required=True, help="Path to the video file (e.g., bicep_curl_user_10s.mp4)")
    p.add_argument("--exercise", required=True, help="Exercise label (e.g., bicep_curl)")
    p.add_argument("--endpoint", default=os.environ.get("AGFC_UPLOAD_ENDPOINT", ""), help="Upload URL endpoint")
    p.add_argument("--token", default=os.environ.get("AGFC_AUTH_TOKEN", ""), help="Bearer token (optional)")
    p.add_argument("--timeout", type=int, default=30, help="HTTP timeout seconds (default 30)")
    p.add_argument("--dry-run", action="store_true", help="Do not perform network request; print actions only")
    return p.parse_args()


def human_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    size = float(num_bytes)
    for u in units:
        if size < 1024.0 or u == units[-1]:
            return f"{size:.2f}{u}"
        size /= 1024.0
    return f"{num_bytes}B"


def main() -> int:
    args = parse_args()
    video_path = Path(args.file)

    if not video_path.exists() or not video_path.is_file():
        print(f"[FAIL] File not found: {video_path}")
        return 2

    file_size = video_path.stat().st_size

    # Decide whether we can do a real request
    can_attempt_http = bool(args.endpoint) and not args.dry_run

    print("=== AI Gym Feedback Companion — Upload Script (Stub) ===")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"File: {video_path} ({human_size(file_size)})")
    print(f"Exercise: {args.exercise}")
    print(f"Endpoint: {args.endpoint if args.endpoint else '(not set)'}")
    print(f"Auth token: {'(provided)' if args.token else '(none)'}")
    print(f"Mode: {'HTTP UPLOAD' if can_attempt_http else 'DRY RUN'}")
    print("--------------------------------------------------------")

    if not can_attempt_http:
        print("[PASS] DRY RUN complete.")
        print("What would happen next (when wired to real backend):")
        print(" - POST multipart/form-data with fields:")
        print("   * exercise=<exercise>")
        print("   * file=@<video>")
        print(" - Expect HTTP 200/201 with an asset_id or upload reference.")
        print("Tip: set endpoint via --endpoint or env var AGFC_UPLOAD_ENDPOINT.")
        return 0

    # Try real HTTP upload (best-effort; still "tiny")
    try:
        import requests  # type: ignore
    except Exception:
        print("[FAIL] 'requests' is not installed, cannot perform HTTP upload.")
        print("       Install with: pip install requests")
        print("       Or rerun with --dry-run.")
        return 3

    headers = {}
    if args.token:
        headers["Authorization"] = f"Bearer {args.token}"

    files = {
        "file": (video_path.name, open(video_path, "rb"), "video/mp4"),
    }
    data = {
        "exercise": args.exercise,
    }

    try:
        resp = requests.post(
            args.endpoint,
            headers=headers,
            data=data,
            files=files,
            timeout=args.timeout,
        )
    finally:
        # Ensure file handle closed
        try:
            files["file"][1].close()
        except Exception:
            pass

    print(f"HTTP status: {resp.status_code}")
    body_preview = resp.text[:500].replace("\n", "\\n")
    print(f"Response (first 500 chars): {body_preview}")

    if 200 <= resp.status_code < 300:
        print("[PASS] Upload succeeded.")
        return 0

    print("[FAIL] Upload did not succeed.")
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
