from backend.database.db import (
    initialize_database,
    insert_activity,
    get_all_activities
)

initialize_database()

insert_activity(
    "2026-05-29T16:00:00",
    "chrome.exe",
    "LeetCode - Binary Search",
    "window_logger"
)

activities = get_all_activities()

for activity in activities:
    print(activity)