# NTU 2026 Spring 2 DRL HW3-2 LeaderBoard

Static leaderboard hosted on **GitHub Pages**.
Data lives in `leaderboard.json`; the page fetches it at load time.

## Setup

1. Push this repo to GitHub.
2. Go to **Settings → Pages**, set source to `main` branch, root `/`.
3. Your leaderboard will be live at `https://<user>.github.io/<repo>/`.

## How the evaluation platform submits scores

The platform calls the GitHub **repository_dispatch** API, which triggers the
`update_leaderboard` workflow → runs `scripts/update_score.py` → commits the
updated `leaderboard.json` → GitHub Pages auto-deploys.

### Endpoint

```
POST https://api.github.com/repos/{OWNER}/{REPO}/dispatches
Authorization: Bearer {GITHUB_TOKEN}
Content-Type: application/json
```

### Payload

```json
{
  "event_type": "submit_score",
  "client_payload": {
    "student_id": "r12345678",
    "results": {
      "SeekAndSlayLevel0-v0":  { "kills": 25, "health": 80.0, "ammo": 50 },
      "SeekAndSlayLevel1_6-v0":{ "kills": 18, "health": 60.0, "ammo": 30 },
      "SeekAndSlayLevel2_1-v0":{ "kills": 12, "health": 45.0, "ammo": 20 },
      "SeekAndSlayLevel3_1-v0":{ "kills":  8, "health": 30.0, "ammo": 10 },
      "SeekAndSlayLevel4-v0":  { "kills":  5, "health": 20.0, "ammo":  5 }
    }
  }
}
```

Only include levels the student actually reached.
The `GITHUB_TOKEN` must have **`repo` scope** (create it in Settings → Developer settings → Personal access tokens).

### Example curl

```bash
curl -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/OWNER/REPO/dispatches \
  -d '{
    "event_type": "submit_score",
    "client_payload": {
      "student_id": "r12345678",
      "results": {
        "SeekAndSlayLevel0-v0": {"kills": 25, "health": 80, "ammo": 50}
      }
    }
  }'
```

### Python helper

```python
import httpx, json, os

def submit_score(student_id: str, results: dict):
    """
    results: {level_name: {"kills": int, "health": float, "ammo": int}}
    """
    token = os.environ["GITHUB_TOKEN"]
    owner = "YOUR_OWNER"
    repo  = "YOUR_REPO"

    resp = httpx.post(
        f"https://api.github.com/repos/{owner}/{repo}/dispatches",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        },
        json={
            "event_type": "submit_score",
            "client_payload": {
                "student_id": student_id,
                "results": results,
            },
        },
    )
    resp.raise_for_status()
    print(f"Submitted {student_id}: {resp.status_code}")
```

## Levels & thresholds

| Level | Map | Threshold |
|---|---|:---:|
| SeekAndSlayLevel0-v0 | default | 22 |
| SeekAndSlayLevel1_6-v0 | mixed_enemies | 15 |
| SeekAndSlayLevel2_1-v0 | blue_shadows | 9 |
| SeekAndSlayLevel3_1-v0 | blue_mixed_resized_enemies | 7 |
| SeekAndSlayLevel4-v0 | complete | — |

## Scoring formula

```
Total = Σ(kills_i × w_i) + Σ(health_i × 0.05) + Σ(ammo_i × 0.01)
```

| Level | Weight |
|---|:---:|
| L0 | 1.0 |
| L1 | 1.5 |
| L2 | 2.0 |
| L3 | 2.5 |
| L4 | 3.0 |

## Manual update / delete

```bash
# Update / add a student
python scripts/update_score.py \
  --student-id r12345678 \
  --results '{"SeekAndSlayLevel0-v0": {"kills": 25, "health": 80, "ammo": 50}}'

# Delete a student
python scripts/update_score.py --delete --student-id r12345678
```
