from backend.database.db import get_recent_activities

activities = get_recent_activities(5)

print("COUNT:", len(activities))

for row in activities:
    print(row)