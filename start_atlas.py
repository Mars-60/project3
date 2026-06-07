"""
start_atlas.py — One-click launcher for Atlas.
Run this file instead of running main.py and server.py separately.
It starts both the window logger AND the Flask server together.

Usage: python start_atlas.py
"""

import threading
import time
import subprocess
import sys
import os
import webbrowser
from pathlib import Path

# ── Make sure we're running from the project root ─────────────────────────────
script_dir = Path(__file__).parent
os.chdir(script_dir)
sys.path.insert(0, str(script_dir))

print("=" * 50)
print("  Atlas — Starting up...")
print("=" * 50)


def run_window_logger():
    """Runs the window activity logger in a background thread."""
    import time as _time
    from backend.collectors.ocr_collector import (
        OCR_INTERVAL_SECONDS,
        collect_ocr_activity,
        should_capture_ocr,
    )
    from backend.collectors.window_logger import (
        get_window_info,
        has_window_changed,
    )
    from backend.database.db import initialize_database, insert_activity
    from backend.utils.time_utils import get_current_timestamp

    initialize_database()
    print("[Atlas] ✓ Window logger started")

    last_ocr_capture_time = 0

    while True:
        try:
            app_name, window_title = get_window_info()

            if window_title and has_window_changed(app_name, window_title):
                timestamp = get_current_timestamp()
                insert_activity(timestamp, app_name, window_title, "window_logger")
                print(f"[Logger] {app_name} → {window_title}")

            current_time = _time.monotonic()
            if window_title and should_capture_ocr(last_ocr_capture_time, current_time, OCR_INTERVAL_SECONDS):
                last_ocr_capture_time = current_time
                if collect_ocr_activity(app_name, window_title):
                    print(f"[OCR] Captured for {app_name}")

        except Exception as e:
            print(f"[Logger] Error: {e}")

        _time.sleep(1)


def run_flask_server():
    """Runs the Flask API server."""
    from backend.api.server import app
    print("[Atlas] ✓ Flask server started at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


def open_browser():
    """Opens the Atlas dashboard after server warms up."""
    time.sleep(2)  # Wait for Flask to start
    atlas_html = script_dir / "frontend" / "atlas.html"
    url = atlas_html.as_uri()
    print(f"[Atlas] ✓ Opening dashboard: {url}")
    webbrowser.open(url)


# ── Start everything ──────────────────────────────────────────────────────────

# Window logger in background thread (daemon so it stops when main exits)
logger_thread = threading.Thread(target=run_window_logger, daemon=True)
logger_thread.start()

# Open browser in background thread
browser_thread = threading.Thread(target=open_browser, daemon=True)
browser_thread.start()

print("[Atlas] ✓ All services starting...")
print("[Atlas]   Press Ctrl+C to stop Atlas")
print("=" * 50)

# Flask server runs in main thread (blocking)
try:
    run_flask_server()
except KeyboardInterrupt:
    print("\n[Atlas] Stopped. Goodbye!")