# timekeeper/viewer.py
from __future__ import annotations
from datetime import date
import tkinter as tk
from tkinter import ttk


class _TodayViewer(tk.Toplevel):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.title("Timekeeper — Today")
        self.geometry("520x360+160+160")
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        outer = ttk.Frame(self, padding=10)
        outer.pack(fill="both", expand=True)

        self.count_var = tk.StringVar(value="0 entries")
        hdr = ttk.Frame(outer)
        hdr.pack(fill="x", pady=(0, 6))
        ttk.Label(hdr, text="Today’s entries", font=("Segoe UI", 11, "bold")).pack(
            side="left"
        )
        ttk.Label(hdr, textvariable=self.count_var, foreground="#666").pack(
            side="right"
        )

        frame = ttk.Frame(outer)
        frame.pack(fill="both", expand=True)
        self.listbox = tk.Listbox(frame, activestyle="none")
        sb = ttk.Scrollbar(frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=sb.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        btns = ttk.Frame(outer)
        btns.pack(fill="x", pady=(8, 0))
        ttk.Button(btns, text="Refresh", command=self.refresh).pack(side="left")
        ttk.Button(btns, text="Close", command=self._on_close).pack(side="right")

        self.refresh()

    def refresh(self):
        # Lazy import avoids circulars at module import time
        from .cli import _read_day_file

        recs = _read_day_file(date.today())
        self.listbox.delete(0, "end")
        for r in recs:
            ts = r.get("ts", "")[11:16]
            text = r.get("text", "")
            tags = r.get("tags", [])
            tag_str = ("  [" + " ".join("#" + t for t in tags) + "]") if tags else ""
            self.listbox.insert("end", f"{ts}  {text}{tag_str}")
        self.count_var.set(f"{len(recs)} entr{'y' if len(recs) == 1 else 'ies'}")

    def _on_close(self):
        self.withdraw()  # hide instead of destroy for instant reopen


def open_today_viewer(root: tk.Tk) -> None:
    """Open (or raise) the singleton 'today' viewer window."""
    win = getattr(root, "_timekeeper_today_viewer", None)
    if win is None or not win.winfo_exists():
        win = _TodayViewer(root)
        setattr(root, "_timekeeper_today_viewer", win)
    else:
        win.deiconify()
        win.lift()
        try:
            win.focus_force()
        except Exception:
            pass
