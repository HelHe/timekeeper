from __future__ import annotations 
import json
from pathlib import Path
import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime
from .cli import append_record, APP_DIR 


CONFIG_FILE = APP_DIR / "config.json"
DEFAULT_INTERVAL_MIN = 30 #Popup interval in minutes


def load_config() -> dict:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        try:   
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"interval_min": DEFAULT_INTERVAL_MIN}

def save_config(cfg: dict) -> None:
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")

class ReminderApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Timekeeper Reminder")
        self.root.withdraw() #keep invisible
        self.cfg = load_config()
        self.interval_ms = int(self.cfg.get("interval_min", DEFAULT_INTERVAL_MIN)) * 60_000
        #kick off first prompt at start
        self.root.after(3_000, self.prompt)

    def prompt(self):
        try:
            text=simpledialog.askstring("Timekeeper", "WHat are you doing right now?")
            if text and text.strip():
                p = append_record(text.strip())
        
        except Exception as e:
            # show error but keep alive
            messagebox.showerror("Timekeeper", f"Error: {e}")
        finally:
            self.root.after(self.interval_ms, self.prompt)

def main():
    root = tk.Tk()
    try:
        app = ReminderApp(root)
        root.mainloop()
    finally:
        try:
            root.destroy()
        except Exception:
            pass           
