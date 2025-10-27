from __future__ import annotations
import json
from pathlib import Path
import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime
from .cli import append_record, APP_DIR
import os, sys, webbrowser
from .tray import Tray


CONFIG_FILE = APP_DIR / "config.json"
DEFAULT_INTERVAL_MIN = 1  # Popup interval in minutes
DEFAULT_ALWAYS_ON_TOP = True


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


def _open_folder(path: Path) -> None:
    if os.name == "nt":
        os.startfile(str(path))
    elif sys.platform == "darwin":
        os.system(f'open "{path}"')
    else:
        webbrowser.open(path.as_uri())


class ReminderApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Timekeeper Reminder")
        self.root.attributes("-topmost", True)
        self.root.withdraw()  # keep hidden until prompt
        self.cfg = load_config()
        self.interval_ms = (
            int(self.cfg.get("interval_min", DEFAULT_INTERVAL_MIN)) * 60_000
        )
        self.tray = Tray(
            on_log_now=lambda: self.root.after(0, self.prompt),
            on_open_logs=lambda: _open_folder(APP_DIR),
            on_exit=lambda: self.root.after(0, self.root.quit),
            on_view_today=lambda: self.root.after(0, self.open_today),
        )
        self.tray.start()
        # kick off first prompt at start
        self.root.after(3_000, self.prompt)

    def open_today(self) -> None:
        self.root.deiconify()
        self.root.update_idletasks()
        try:
            from .viewer import open_today_viewer

            open_today_viewer(self.root)
        finally:
            self.root.withdraw()

    def prompt(self):
        try:
            text = simpledialog.askstring(
                "Timekeeper",
                "What are you doing right now?",
                parent=self.root,
            )
            if text and text.strip():
                p = append_record(text.strip())

        except Exception as e:
            # show error but keep alive
            messagebox.showerror("Timekeeper", f"Error: {e}")
        finally:
            self.root.withdraw()
            self.root.after(self.interval_ms, self.prompt)


def main() -> int:
    root = tk.Tk()
    try:
        ReminderApp(root)
        root.mainloop()
        return 0
    finally:
        try:
            root.destroy()
        except Exception:
            pass
