# X Manual Monitor Workflow

## Why this skill exists

This skill is for the low-cost case:

- the user only follows a small set of X authors
- the user is willing to use a logged-in browser session
- the user wants notes, not enterprise-grade automation

## Recommended operating pattern

1. Keep the watchlist small.
2. Open each author profile directly.
3. Generate a batch template.
4. Read only the newest visible posts.
5. Save the collected posts to a JSON batch.
6. Run `ingest` to deduplicate and update the report.

## Why profile pages beat homepage surfing

- less irrelevant content
- easier author-level filtering
- easier deduplication
- lower attention cost

## Suggested cadence

- once daily for personal research
- twice daily for fast-moving topics
- avoid constant refreshing

## Low-friction operator loop

```powershell
python scripts/x_manual_monitor.py init --config .\x-manual-monitor.json
python scripts/x_manual_monitor.py check --config .\x-manual-monitor.json
python scripts/x_manual_monitor.py make-batch-template .\batch.json --config .\x-manual-monitor.json
python scripts/x_manual_monitor.py ingest .\batch.json --config .\x-manual-monitor.json
```
