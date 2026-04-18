---
name: chaunyx-skill
description: Monitor a fixed watchlist of X authors through a logged-in browser session instead of the X API. Use when Codex needs to manually visit selected X profiles, collect recent public posts from those authors, deduplicate them, summarize them in Chinese, and append a local Markdown report. Prefer this skill when the user only follows a small set of authors and wants a lower-cost, browser-driven workflow rather than official X API billing.
---

# Chauny X Skill

## First Move

Always initialize or inspect the local config before running a monitoring session:

```powershell
python scripts/x_manual_monitor.py init
python scripts/x_manual_monitor.py check
```

Do not start a collection session before `check` succeeds.

## What This Skill Covers

- Keep a watchlist of fixed X authors.
- Drive a logged-in browser session to open those author pages.
- Collect recent public posts from those author pages.
- Deduplicate posts across sessions with a local state file.
- Save JSONL events and Markdown reports.
- Optionally summarize the collected posts in Chinese before writing the report.

## Safety Defaults

- Keep this workflow read-only.
- Only visit public posts from explicitly selected authors.
- Use the browser session only while the user intends to monitor X.
- Do not rely on homepage `For You` noise for routine monitoring.
- Prefer author profile pages or a curated List page over open-ended browsing.

## Workflow

### 1. Create the config

```powershell
python scripts/x_manual_monitor.py init --config .\x-manual-monitor.json
```

Then edit the generated JSON:

- Add `authors` entries with `username` and optional `label`.
- Set `max_posts_per_author` to a small number like `5` to `15`.
- Set `report_path` if you want a stable Markdown notes file.

### 2. Validate the local setup

```powershell
python scripts/x_manual_monitor.py check --config .\x-manual-monitor.json
```

This verifies:

- config structure
- output directory
- report path
- watchlist size

### 3. Collect posts through the browser

Use a logged-in browser session and visit each author in the watchlist.

Preferred page shape:

```text
https://x.com/<username>
```

For each author:

1. Open the profile page.
2. Read the newest visible posts.
3. Ignore ads, pinned reposts, and irrelevant replies unless the user asked for them.
4. Capture a compact JSON record per post with:
   - `post_id`
   - `author`
   - `url`
   - `published_at`
   - `text`
5. Save the batch to a JSON file.

You can generate a starter template first:

```powershell
python scripts/x_manual_monitor.py make-batch-template .\batch-template.json --config .\x-manual-monitor.json
```

Then replace the empty fields with the posts you copied from the browser.

For an easier operator workflow, create a helper pack:

```powershell
python scripts/x_manual_monitor.py make-capture-pack .\capture-pack --config .\x-manual-monitor.json
```

This generates:

- `batch-template.json`
- `author-urls.txt`
- `capture-checklist.md`

### 4. Ingest and deduplicate

```powershell
python scripts/x_manual_monitor.py ingest .\batch.json --config .\x-manual-monitor.json
```

This will:

- skip already-seen posts
- append new events to JSONL
- regenerate the Markdown report

### 5. Repeat later

Run the same process again with a new batch file. The skill will keep deduplicating against prior runs.

## Browser Collection Notes

This skill is intentionally built for a small fixed author set. It is not meant for broad discovery.

For reliable collection:

- prefer the profile page of each author
- collect only the newest few posts
- keep the watchlist small
- run on a human-paced cadence such as once or twice daily

## Output Shape

Each collected post should look like:

```json
{
  "post_id": "1899999999999999999",
  "author": "example",
  "url": "https://x.com/example/status/1899999999999999999",
  "published_at": "2026-04-18T09:20:00Z",
  "text": "Example post text"
}
```

## Fast Manual Collection

Use this minimal routine for each author:

1. Open `https://x.com/<username>`.
2. Skip pinned reposts unless they matter.
3. Open the newest 3 to 5 posts you care about.
4. Copy these fields into the batch template:
   - post id from the URL
   - username
   - full post URL
   - timestamp shown by X
   - post text
5. Save the JSON file.
6. Run `ingest`.

## Resources (optional)

### scripts/
- `x_manual_monitor.py`: config, dedupe, ingest, and report generation

### references/
- `workflow.md`: rationale and execution notes for browser-driven author monitoring
