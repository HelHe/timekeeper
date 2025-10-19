from __future__ import annotations
import json, os, sys
import itertools
from datetime import date, datetime, timezone, timedelta
from pathlib import Path

APP_DIR = Path(os.environ.get("TIMEKEEPER_HOME", Path.home()/".timekeeperlog"))

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
    print(f"=== {header} ({len(recs)} entr{'y' if len(recs)==1 else 'ies'}) ===")
    for r in recs:
        ts = r.get("ts", "")[11:16] #HH:MM from iso
        text = r.get("text", "")
        tags = r.get("tags", [])
        tag_str = f" [{' '.join('#'+t for t in tags)}]" if tags else ""
        print(f"{ts} {text}{tag_str}")
    print()

def cmd_show_today() -> int:
    d = date.today()
    _print_records(d, _read_day_file(d))
    return 0

def cmd_show_day(s: str) -> int:
    try:
        y, m, d = (int(x) for x in s.split("-"))
        the_day = date(y, m, d)
    except Exception:
        print("Invalid date. use YYYY-MM-DD.")
        return 2
    _print_records(the_day, _read_day_file(the_day))
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
    cmd = sys.argv[1] if len(sys.argv) > 1 else "log"
    if cmd == "log":
        raise SystemExit(cmd_log())
    print("Timekeeper log")







 