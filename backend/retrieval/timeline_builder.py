from backend.database.db import (
    get_recent_activities
)


def build_timeline(limit=20):

    activities = get_recent_activities(
        limit
    )

    timeline = []

    for activity in activities:

        timestamp = activity[1]

        app_name = activity[2]

        window_title = activity[3]

        url = activity[4]

        source = activity[7]

        line = (
            f"[{timestamp}] "
            f"{app_name} | "
            f"{window_title}"
        )

        if url:
            line += (
                f" | {url}"
            )

        line += (
            f" | {source}"
        )

        timeline.append(
            line
        )

    return "\n".join(
        timeline
    )