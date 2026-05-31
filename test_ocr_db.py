from backend.ocr.ocr_engine import extract_text

from backend.database.db import (
    insert_activity,
    get_all_activities
)

text = extract_text(
    "screenshots/active_window.png"
)

insert_activity(
    "2026-05-31T10:00:00",
    "Code.exe",
    "VS Code",
    "ocr",
    text
)

activities = get_all_activities()

print(activities[-1])