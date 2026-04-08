# NTU 2026 Spring DRL HW3-2 Leaderboard

Static leaderboard for the NTU Deep Reinforcement Learning course (HW3-2), hosted on **GitHub Pages**.
Scores are stored in `leaderboard.json` and displayed at the GitHub Pages URL of this repo.

## How submissions are received

The evaluation platform triggers score updates by calling the GitHub **repository_dispatch** API:

```
POST https://api.github.com/repos/{OWNER}/{REPO}/dispatches
Authorization: Bearer {GITHUB_TOKEN}
Content-Type: application/json
```

Payload:

```json
{
  "event_type": "submit_score",
  "client_payload": {
    "student_id": "r12345678",
    "results": {
      "SeekAndSlayLevel0-v0":  { "kills": 25, "health": 80.0, "ammo": 50 },
      "SeekAndSlayLevel1_6-v0":{ "kills": 18, "health": 60.0, "ammo": 30 },
      "SeekAndSlayLevel3_1-v0":{ "kills": 12, "health": 45.0, "ammo": 20 },
      "SeekAndSlayLevel2_3-v0":{ "kills":  8, "health": 30.0, "ammo": 10 },
      "SeekAndSlayLevel4-v0":  { "kills":  5, "health": 20.0, "ammo":  5 }
    },
    "audit": {
      "repository": "ntu-rl-2026-spring2-hw3/r12345678_repo",
      "run_id":     "12345678901",
      "run_url":    "https://github.com/ntu-rl-2026-spring2-hw3/r12345678_repo/actions/runs/12345678901",
      "sha":        "abc123def456...",
      "actor":      "r12345678"
    }
  }
}
```

This triggers the `update_leaderboard` workflow → `scripts/update_score.py` → commits updated `leaderboard.json` → GitHub Pages auto-deploys.

The `GITHUB_TOKEN` must have **`repo` scope**.

## Ranking & scoring

Entries are ranked by **total score** (higher is better):

```
Final Score = Σ weight × (kills × 1.0 + health × 0.01 + ammo × 0.005)
```

| Tier | Levels | Weight |
|---|---|:---:|
| Easy | L0 | ×1 |
| Medium | L1.6, L3.1, L2.3 | ×2 |
| Final | L4 | ×3 |

Health (0–100) and ammo (0–200) each contribute at most 1 point per level before weighting, ensuring kills remains the dominant scoring factor. Difficulty-tier weights reward performance on harder levels.

| Level | Map | Kill threshold to pass |
|---|---|:---:|
| SeekAndSlayLevel0-v0 | default | 18 |
| SeekAndSlayLevel1_6-v0 | mixed_enemies | 9 |
| SeekAndSlayLevel3_1-v0 | blue_mixed_resized | 9 |
| SeekAndSlayLevel2_3-v0 | red_mixed_enemies | 9 |
| SeekAndSlayLevel4-v0 | complete | — |

## Admin: re-judging all submissions

When `judge.py` in `hw3-2-judge-workflow` is updated, you can re-evaluate every
existing submission **without asking students to re-commit**. Each student's
workflow checks out the judge from `main` at run time, so re-running their last
GitHub Actions run will pick up the new judge automatically.

The flow:

1. Push the new `judge.py` to `hw3-2-judge-workflow` `main`.
2. Pull this repo and back up + clear `leaderboard.json` (Baselines are kept):
   ```bash
   git pull
   python scripts/clear_leaderboard.py
   git add leaderboard.json
   git commit -m "leaderboard: clear for re-judge"
   git push
   ```
   `clear_leaderboard.py` writes a timestamped backup to `backup/` (gitignored)
   and prints the exact command to run next.
3. Wait until the `Update Leaderboard` workflow is idle in the Actions tab.
4. Trigger re-runs of every student's last judge run:
   ```bash
   python scripts/rerun_all.py --from backup/leaderboard.<timestamp>.json --dry-run
   python scripts/rerun_all.py --from backup/leaderboard.<timestamp>.json
   ```
   The script reads the student list and `audit.run_url` from the backup file
   and calls `gh run rerun` against each student's repo. Entries whose
   `student_id` starts with `Baseline` are skipped. Requires `gh` authenticated
   as an org admin.
5. Each re-run dispatches `submit_score` back here. The `Update Leaderboard`
   workflow has a top-level `concurrency: { group: leaderboard-writer,
   cancel-in-progress: false }` so the 15+ writers serialize on a single
   queue — no `git push` races, no dropped submissions.

To re-judge a single student instead of everyone:

```bash
python scripts/rerun_all.py --only b12508026
```
