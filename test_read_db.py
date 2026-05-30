from backend.database.db import get_all_activities

activities = get_all_activities()

for activity in activities:
    print(activity)