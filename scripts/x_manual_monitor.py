#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List


DEFAULT_CONFIG = {
    "output_dir": "./x-manual-output",
    "report_path": "./x-manual-output/reports/latest-report.md",
    "max_posts_per_author": 10,
    "authors": [
        {
            "label": "Example Author",
            "username": "example",
        }
    ],
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def json_dump(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json_dump(data) + "\n", encoding="utf-8")


def append_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_config(config_path: Path) -> Dict[str, Any]:
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    return json.loads(config_path.read_text(encoding="utf-8-sig"))


def write_default_config(config_path: Path) -> None:
    if config_path.exists():
        raise FileExistsError(f"Refusing to overwrite existing config: {config_path}")
    write_json(config_path, DEFAULT_CONFIG)


def ensure_runtime_paths(config: Dict[str, Any]) -> Dict[str, Path]:
    output_dir = Path(config["output_dir"]).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    events_path = output_dir / "events" / "events.jsonl"
    state_path = output_dir / "state" / "state.json"
    report_path = Path(config["report_path"]).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    events_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    return {
        "output_dir": output_dir,
        "events": events_path,
        "state": state_path,
        "report": report_path,
    }


def load_state(state_path: Path) -> Dict[str, Any]:
    return read_json(state_path, {"seen_post_ids": [], "last_ingest_at": None})


def save_state(state_path: Path, state: Dict[str, Any]) -> None:
    state = dict(state)
    state["seen_post_ids"] = sorted(set(state.get("seen_post_ids", [])))
    state["last_ingest_at"] = utc_now_iso()
    write_json(state_path, state)


def normalize_post(row: Dict[str, Any]) -> Dict[str, Any]:
    required = ["post_id", "author", "url", "published_at", "text"]
    missing = [key for key in required if not row.get(key)]
    if missing:
        raise ValueError(f"Post is missing required fields: {', '.join(missing)}")
    return {
        "platform": "x",
        "source_type": "author",
        "post_id": str(row["post_id"]),
        "author": str(row["author"]),
        "url": str(row["url"]),
        "published_at": str(row["published_at"]),
        "text": str(row["text"]),
        "label": str(row.get("label") or row["author"]),
        "collected_at": utc_now_iso(),
    }


def render_report(items: List[Dict[str, Any]]) -> str:
    lines = [
        "# X Manual Monitor Report",
        "",
        f"- Generated at: {utc_now_iso()}",
        f"- New posts: {len(items)}",
        "",
    ]
    if not items:
        lines.append("- No new posts in this ingest.")
        lines.append("")
        return "\n".join(lines)

    for item in items:
        preview = item["text"].replace("\n", " ").strip()
        lines.extend(
            [
                f"## @{item['author']}",
                "",
                f"- Published: {item['published_at']}",
                f"- URL: {item['url']}",
                f"- Preview: {preview[:240]}{'...' if len(preview) > 240 else ''}",
                "",
            ]
        )
    return "\n".join(lines)


@dataclass
class IngestResult:
    new_items: List[Dict[str, Any]]
    skipped_count: int


def ingest_batch(batch_path: Path, config_path: Path) -> Dict[str, Any]:
    config = load_config(config_path)
    paths = ensure_runtime_paths(config)
    state = load_state(paths["state"])
    raw_rows = json.loads(batch_path.read_text(encoding="utf-8-sig"))
    if not isinstance(raw_rows, list):
        raise ValueError("Batch file must contain a JSON array of post objects.")

    seen = set(state.get("seen_post_ids", []))
    new_items: List[Dict[str, Any]] = []
    skipped_count = 0
    for row in raw_rows:
        item = normalize_post(row)
        if item["post_id"] in seen:
            skipped_count += 1
            continue
        new_items.append(item)
        seen.add(item["post_id"])

    state["seen_post_ids"] = sorted(seen)
    save_state(paths["state"], state)
    if new_items:
        append_jsonl(paths["events"], new_items)
    paths["report"].write_text(render_report(new_items), encoding="utf-8")
    return {
        "success": True,
        "new_items": len(new_items),
        "skipped_duplicates": skipped_count,
        "events_path": str(paths["events"]),
        "state_path": str(paths["state"]),
        "report_path": str(paths["report"]),
    }


def check_config(config_path: Path) -> Dict[str, Any]:
    config = load_config(config_path)
    paths = ensure_runtime_paths(config)
    authors = config.get("authors", [])
    issues: List[str] = []
    if not authors:
        issues.append("authors list is empty")
    for author in authors:
        if not author.get("username"):
            issues.append("an author entry is missing username")
    return {
        "success": len(issues) == 0,
        "config_path": str(config_path.resolve()),
        "output_dir": str(paths["output_dir"]),
        "report_path": str(paths["report"]),
        "authors_count": len(authors),
        "max_posts_per_author": config.get("max_posts_per_author", 10),
        "issues": issues,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manual X author monitor")
    parser.add_argument("--config", default="x-manual-monitor.json")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Write a sample config")
    init_parser.add_argument("--force-path", help="Optional explicit path for init output")

    subparsers.add_parser("check", help="Validate config and local paths")

    template_parser = subparsers.add_parser("make-batch-template", help="Create an empty batch template from the watchlist")
    template_parser.add_argument("output_path", help="Path to write the batch template JSON")

    helper_parser = subparsers.add_parser("make-capture-pack", help="Create a capture helper pack for manual browser collection")
    helper_parser.add_argument("output_dir", help="Directory to write helper files into")

    ingest_parser = subparsers.add_parser("ingest", help="Ingest a JSON batch of collected posts")
    ingest_parser.add_argument("batch_path", help="Path to a JSON array of collected posts")
    return parser


def make_batch_template(config_path: Path, output_path: Path) -> Dict[str, Any]:
    config = load_config(config_path)
    authors = config.get("authors", [])
    template: List[Dict[str, Any]] = []
    max_posts = int(config.get("max_posts_per_author", 10))
    for author in authors:
        for index in range(min(max_posts, 3)):
            template.append(
                {
                    "post_id": "",
                    "author": author["username"],
                    "label": author.get("label") or author["username"],
                    "url": f"https://x.com/{author['username']}/status/",
                    "published_at": "",
                    "text": "",
                    "_note": f"Fill slot {index + 1} for @{author['username']}",
                }
            )
    write_json(output_path.resolve(), template)
    return {
        "success": True,
        "template_path": str(output_path.resolve()),
        "rows": len(template),
    }


def make_capture_pack(config_path: Path, output_dir: Path) -> Dict[str, Any]:
    config = load_config(config_path)
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    batch_path = output_dir / "batch-template.json"
    urls_path = output_dir / "author-urls.txt"
    checklist_path = output_dir / "capture-checklist.md"

    template_result = make_batch_template(config_path, batch_path)
    authors = config.get("authors", [])
    urls = [f"https://x.com/{author['username']}" for author in authors]
    urls_path.write_text("\n".join(urls) + ("\n" if urls else ""), encoding="utf-8")

    checklist_lines = [
        "# Capture Checklist",
        "",
        "## Author Pages",
        "",
    ]
    for author in authors:
        checklist_lines.append(f"- @{author['username']}: https://x.com/{author['username']}")
    checklist_lines.extend(
        [
            "",
            "## Manual Steps",
            "",
            "1. Open each author page.",
            "2. Skip irrelevant pinned reposts unless they matter.",
            "3. Copy the newest 3-5 posts into batch-template.json.",
            "4. Fill post_id, url, published_at, and text.",
            "5. Run the ingest command when ready.",
            "",
            "## Ingest Command",
            "",
            f"`python scripts/x_manual_monitor.py ingest \"{batch_path}\" --config \"{config_path.resolve()}\"`",
            "",
        ]
    )
    checklist_path.write_text("\n".join(checklist_lines), encoding="utf-8")
    return {
        "success": True,
        "batch_template": template_result["template_path"],
        "author_urls": str(urls_path),
        "checklist": str(checklist_path),
    }


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    config_override = getattr(args, "force_path", None)
    config_path = Path(config_override or args.config).resolve()

    if args.command == "init":
        write_default_config(config_path)
        print(
            json_dump(
                {
                    "success": True,
                    "message": "Sample config created",
                    "config_path": str(config_path),
                }
            )
        )
        return 0

    if args.command == "check":
        result = check_config(config_path)
        print(json_dump(result))
        return 0 if result.get("success") else 1

    if args.command == "make-batch-template":
        result = make_batch_template(config_path, Path(args.output_path))
        print(json_dump(result))
        return 0 if result.get("success") else 1

    if args.command == "make-capture-pack":
        result = make_capture_pack(config_path, Path(args.output_dir))
        print(json_dump(result))
        return 0 if result.get("success") else 1

    if args.command == "ingest":
        result = ingest_batch(Path(args.batch_path).resolve(), config_path)
        print(json_dump(result))
        return 0 if result.get("success") else 1

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
