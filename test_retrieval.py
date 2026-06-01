from backend.database.db import (
    get_recent_activities
)

activities = get_recent_activities()

for activity in activities:
    print(activity)