from __future__ import annotations
import json, os, sys
import itertools
from datetime import date, datetime, timezone, timedelta
from pathlib import Path

APP_DIR = Path(os.environ.get("TIMEKEEPER_HOME", Path.home() / ".timekeeperlog"))


# Tag helper
def _filter_by_tag(recs: list[dict], tag: str | None) -> list[dict]:
    """Return only records that contain the tag (case insensitive)"""
    if not tag:
        return recs
    tag = tag.lstrip("#").lower()
    out: list[dict] = []
    for r in recs:
        tags = [t.lower() for t in r.get("tags", [])]
        if tag in tags:
            out.append(r)
    return out


# Helper to return a days log file into a list of dicts
def _read_day_file(d: date) -> list[dict]:
    """Return list of records for a given day"""
    p = _log_path(datetime(d.year, d.month, d.day, tzinfo=timezone.utc))
    if not p.exists():
        return []
    recs: list[dict] = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                recs.append(json.loads(line))
            except json.JSONDecodeError:
                # Skip malformed lines
                pass
    return recs


# Help to print records, either today or show day yyyy-mm-dd
def _print_records(day: date, recs: list[dict]) -> None:
    header = day.isoformat()
    print(f"=== {header} ({len(recs)} entr{'y' if len(recs) == 1 else 'ies'}) ===")
    for r in recs:
        ts = r.get("ts", "")[11:16]  # HH:MM from iso
        text = r.get("text", "")
        tags = r.get("tags", [])
        tag_str = f" [{' '.join('#' + t for t in tags)}]" if tags else ""
        print(f"{ts} {text}{tag_str}")
    print()


def cmd_show_today(tag: str | None = None) -> int:
    d = date.today()
    recs = _filter_by_tag(_read_day_file(d), tag)
    _print_records(d, recs)
    return 0


def cmd_show_day(s: str, tag: str | None = None) -> int:
    try:
        y, m, d = (int(x) for x in s.split("-"))
        the_day = date(y, m, d)
    except Exception:
        print("Invalid date. use YYYY-MM-DD.")
        return 2
    recs = _filter_by_tag(_read_day_file(the_day), tag)
    _print_records(the_day, recs)
    return 0


def _tags_from(text: str) -> list[str]:
    # Tag extractor
    tags = []
    for word in text.split():
        if word.startswith("#") and len(word) > 1:
            tags.append(word[1:])
    return tags


# Define log path
def _log_path(dt: datetime) -> Path:
    y, m, d = dt.strftime("%Y"), dt.strftime("%m"), dt.strftime("%d")
    return APP_DIR / y / m / f"{y}-{m}-{d}.jsonl"


# Appending to file
def append_record(text: str) -> Path:
    now = datetime.now(timezone.utc)
    p = _log_path(now)
    p.parent.mkdir(parents=True, exist_ok=True)
    rec = {"ts": now.isoformat(), "text": text, "tags": _tags_from(text)}
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return p


def cmd_log() -> int:
    try:
        entry = input("What are you doing? ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n(cancelled)")
        return 1
    if not entry:
        print("(empty, not saved)")
        return 0
    p = append_record(entry)
    print(f"Saved -> {p}")
    return 0


def main():
    # usage: timekeeper [log|show] [--today|--day YYYY-MM-DD] [--tag name]
    args = sys.argv[1:]
    tag = None
    if "--tag" in args:
        i = args.index("--tag")
        try:
            tag = args[i + 1]
        except IndexError:
            print("Expected a tag after --tag")
            return 2
        args = args[:i] + args[i + 2 :]

    if not args:
        return cmd_log()

    cmd = args[0]
    if cmd in ("remind", "reminder", "start"):
        from .reminder import main as reminder_main

        reminder_main()
        return 0
    if cmd == "log":
        return cmd_log()

    if cmd == "show":
        if not args[1:]:
            return cmd_show_today(tag)
        sub = args[1]
        if sub == "--today":
            return cmd_show_today(tag)
        if sub == "--day" and len(args) >= 3:
            return cmd_show_day(args[2], tag)
        print("Usage: timekeeper show [--today | --day YYYY-MM-DD | --tag name]")
        return 2

    print("Usage: timekeeper [log | show ...]")
    return 2
