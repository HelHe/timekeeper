from __future__ import annotations
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path

APP_DIR = Path(os.environ.get("TIMEKEEPER_HOME", Path.home()/".timekeeperlog"))

def _tags_from(text: str) -> list[str]:
    # tag extractor
    
