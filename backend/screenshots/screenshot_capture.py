from PIL import ImageGrab
from pathlib import Path

import pygetwindow as gw

def capture_screen():
    screenshot=ImageGrab.grab()
    Path("screenshots").mkdir(
        exist_ok=True
    )
    screenshot.save(
        "screenshots/test_capture.png"
    )
    return "screenshots/test_capture.png"

def capture_active_window():
    window = gw.getActiveWindow()

    if window is None:
        return None

    screenshot = ImageGrab.grab(
        bbox=(
            window.left,
            window.top,
            window.left + window.width,
            window.top + window.height
        )
    )

    Path("screenshots").mkdir(
        exist_ok=True
    )

    screenshot.save(
        "screenshots/active_window.png"
    )

    return "screenshots/active_window.png"