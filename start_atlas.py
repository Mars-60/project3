"""
start_atlas.py — Silent background launcher for Atlas.
Runs the window logger + Flask server with no visible window.
Dashboard is opened manually by the user via atlas.html.
"""

import threading
import sys
import os
from pathlib import Path

# ── Run from project root ─────────────────────────────────────────────────────
script_dir = Path(__file__).parent
os.chdir(script_dir)
sys.path.insert(0, str(script_dir))

# ── Redirect all output to a log file (required for pythonw.exe / silent mode)
# ── This also gives users a log to check if something goes wrong ─────────────
log_path = script_dir / "atlas.log"
try:
    _log_file = open(log_path, "a", buffering=1, encoding="utf-8")
    sys.stdout = _log_file
    sys.stderr = _log_file
except Exception:
    pass  # If log file fails, just suppress output silently

def log(msg):
    try:
        print(msg, flush=True)
    except Exception:
        pass


log("=" * 50)
log("  Atlas — Starting up (silent mode)")
log("=" * 50)


def run_window_logger():
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
    log("[Atlas] Window logger started")

    last_ocr_capture_time = 0

    while True:
        try:
            app_name, window_title = get_window_info()

            if window_title and has_window_changed(app_name, window_title):
                timestamp = get_current_timestamp()
                insert_activity(timestamp, app_name, window_title, "window_logger")
                log(f"[Logger] {app_name} → {window_title}")

            current_time = _time.monotonic()
            if window_title and should_capture_ocr(last_ocr_capture_time, current_time, OCR_INTERVAL_SECONDS):
                last_ocr_capture_time = current_time
                if collect_ocr_activity(app_name, window_title):
                    log(f"[OCR] Captured for {app_name}")

        except Exception as e:
            log(f"[Logger] Error: {e}")

        _time.sleep(1)


def run_flask_server():
    from backend.api.server import app
    log("[Atlas] Flask server started at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


# ── Start window logger in background thread ──────────────────────────────────
logger_thread = threading.Thread(target=run_window_logger, daemon=True)
logger_thread.start()

log("[Atlas] All services running silently.")
log("[Atlas] Open frontend/atlas.html in your browser to view the dashboard.")

# ── Flask runs in main thread (blocking) ─────────────────────────────────────
try:
    run_flask_server()
except KeyboardInterrupt:
    log("[Atlas] Stopped.")
except Exception as e:
    log(f"[Atlas] Fatal error: {e}")