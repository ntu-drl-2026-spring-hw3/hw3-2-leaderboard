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

Entries are ranked **first by number of levels reached** (more levels always beats fewer), then by final score as a tiebreaker:

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
| SeekAndSlayLevel0-v0 | default | 15 |
| SeekAndSlayLevel1_6-v0 | mixed_enemies | 5 |
| SeekAndSlayLevel3_1-v0 | blue_mixed_resized | 5 |
| SeekAndSlayLevel2_3-v0 | red_mixed_enemies | 5 |
| SeekAndSlayLevel4-v0 | complete | — |
