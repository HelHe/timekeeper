import threading
import pystray
from PIL import Image, ImageDraw


class Tray:
    def __init__(self, on_log_now, on_open_logs, on_exit, on_view_today=None):
        # Build the menu items first
        items = [
            pystray.MenuItem("Log now", lambda *_: on_log_now()),
        ]
        if on_view_today:
            items.append(pystray.MenuItem("View today", lambda *_: on_view_today()))
        items.extend(
            [
                pystray.MenuItem("Open log folder", lambda *_: on_open_logs()),
                pystray.MenuItem("Exit", lambda *_: on_exit()),
            ]
        )

        self._icon = pystray.Icon(
            name="Timekeeper",
            title="Timekeeper",
            icon=self._make_image(),
            menu=pystray.Menu(*items),  # ← unpack the list into Menu(...)
        )
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()

    def stop(self):
        try:
            self._icon.stop()
        except Exception:
            pass

    @staticmethod
    def _make_image():
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.ellipse((8, 8, 56, 56), outline=(0, 0, 0, 255), width=3)
        d.line((32, 16, 32, 30), fill=(0, 0, 0, 255), width=3)
        d.line((32, 30, 44, 44), fill=(0, 0, 0, 255), width=3)
        return img
