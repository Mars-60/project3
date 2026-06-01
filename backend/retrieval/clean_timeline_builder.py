from backend.database.db import (
    get_recent_activities
)


def build_clean_timeline(limit=30):

    activities = get_recent_activities(
        limit
    )

    timeline = []

    for activity in activities:

        timestamp = activity[1]

        app_name = activity[2]

        window_title = activity[3]

        ocr_text = activity[4]

        category = activity[5]

        source = activity[6]

        url = activity[7]

        if source == "ocr":

            line = (
                f"[{timestamp}] "
                f"{app_name} "
                f"(OCR Activity)"
            )

        else:

            line = (
                f"[{timestamp}] "
                f"{app_name} | "
                f"{window_title}"
            )

            if url:
                line += (
                    f" | {url}"
                )

        timeline.append(
            line
        )

    return "\n".join(
        timeline
    )