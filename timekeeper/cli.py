from __future__ import annotations
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path

APP_DIR = Path(os.environ.get("TIMEKEEPER_HOME", Path.home()/".timekeeperlog"))

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







 