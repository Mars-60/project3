from datetime import datetime

from backend.database.time_queries import (
    get_activities_between
)


today = datetime.now()

start_time = (
    today.strftime(
        "%Y-%m-%d"
    )
    + "T00:00:00"
)

end_time = (
    today.strftime(
        "%Y-%m-%d"
    )
    + "T23:59:59"
)

activities = get_activities_between(
    start_time,
    end_time
)

print(
    "TOTAL:",
    len(activities)
)

for activity in activities[:10]:
    print(activity)