#!/usr/bin/env python3
"""
update_score.py — update leaderboard.json with a student's results.

Usage (called from GitHub Actions or locally):

  python scripts/update_score.py \
      --student-id r12345678 \
      --results '{"SeekAndSlayLevel0-v0": {"kills": 25, "health": 80, "ammo": 50}, ...}'

  # Or via individual flags:
  python scripts/update_score.py \
      --student-id r12345678 \
      --level SeekAndSlayLevel0-v0 --kills 25 --health 80 --ammo 50 \
      --level SeekAndSlayLevel1_6-v0 --kills 18 --health 60 --ammo 30

  # Delete an entry:
  python scripts/update_score.py --delete --student-id r12345678
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "leaderboard.json"

LEVELS = [
    "SeekAndSlayLevel0-v0",
    "SeekAndSlayLevel1_6-v0",
    "SeekAndSlayLevel2_1-v0",
    "SeekAndSlayLevel3_1-v0",
    "SeekAndSlayLevel4-v0",
]

LEVEL_THRESHOLDS = {
    "SeekAndSlayLevel0-v0":  22,
    "SeekAndSlayLevel1_6-v0": 15,
    "SeekAndSlayLevel2_1-v0":  9,
    "SeekAndSlayLevel3_1-v0":  7,
    "SeekAndSlayLevel4-v0":   None,
}

LEVEL_WEIGHTS = {
    "SeekAndSlayLevel0-v0":   1.0,
    "SeekAndSlayLevel1_6-v0": 1.5,
    "SeekAndSlayLevel2_1-v0": 2.0,
    "SeekAndSlayLevel3_1-v0": 2.5,
    "SeekAndSlayLevel4-v0":   3.0,
}


def compute_score(levels: dict) -> float:
    score = 0.0
    for name, weight in LEVEL_WEIGHTS.items():
        e = levels.get(name)
        if e is None:
            continue
        score += e.get("kills", 0) * weight
        score += e.get("health", 0) * 0.05
        score += e.get("ammo", 0) * 0.01
    return round(score, 2)


def load() -> list:
    if not DATA_FILE.exists():
        return []
    return json.loads(DATA_FILE.read_text())


def save(data: list):
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def validate_results(results: dict):
    unknown = set(results.keys()) - set(LEVELS)
    if unknown:
        sys.exit(f"ERROR: Unknown level(s): {sorted(unknown)}")
    for name, vals in results.items():
        for field in ("kills", "health", "ammo"):
            if field not in vals:
                sys.exit(f"ERROR: Missing field '{field}' for level '{name}'")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--student-id", required=True)
    parser.add_argument("--results", default=None,
                        help="JSON string: {level: {kills, health, ammo}, ...}")
    parser.add_argument("--delete", action="store_true",
                        help="Remove the student's entry")
    # Alternative per-level flags (used when --results not supplied)
    parser.add_argument("--level",  action="append", dest="levels",  default=[])
    parser.add_argument("--kills",  action="append", dest="kills",   default=[], type=int)
    parser.add_argument("--health", action="append", dest="health",  default=[], type=float)
    parser.add_argument("--ammo",   action="append", dest="ammo",    default=[], type=int)

    args = parser.parse_args()
    data = load()

    # ── Delete mode ─────────────────────────────────────────────────
    if args.delete:
        before = len(data)
        data = [e for e in data if e["student_id"] != args.student_id]
        if len(data) == before:
            sys.exit(f"ERROR: Student '{args.student_id}' not found.")
        save(data)
        print(f"Deleted entry for {args.student_id}")
        return

    # ── Parse results ────────────────────────────────────────────────
    if args.results:
        try:
            results = json.loads(args.results)
        except json.JSONDecodeError as e:
            sys.exit(f"ERROR: Invalid JSON in --results: {e}")
    elif args.levels:
        if not (len(args.levels) == len(args.kills) == len(args.health) == len(args.ammo)):
            sys.exit("ERROR: --level/--kills/--health/--ammo must appear the same number of times.")
        results = {
            lvl: {"kills": k, "health": h, "ammo": a}
            for lvl, k, h, a in zip(args.levels, args.kills, args.health, args.ammo)
        }
    else:
        sys.exit("ERROR: Provide either --results JSON or --level/--kills/--health/--ammo flags.")

    validate_results(results)

    now = datetime.now(timezone.utc).isoformat()
    existing = next((e for e in data if e["student_id"] == args.student_id), None)

    if existing:
        existing["levels"] = results
        existing["submission_time"] = now
        print(f"Updated entry for {args.student_id}")
    else:
        data.append({
            "student_id": args.student_id,
            "submission_time": now,
            "levels": results,
        })
        print(f"Added new entry for {args.student_id}")

    score = compute_score(results)
    print(f"Total score: {score}")
    save(data)


if __name__ == "__main__":
    main()
