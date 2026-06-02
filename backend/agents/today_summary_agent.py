from datetime import datetime

from backend.database.time_queries import (
    get_activities_between
)

from backend.ai.gemini_client import (
    ask_gemini
)


def generate_today_summary():

    today = datetime.now()

    start_time = (
        today.strftime("%Y-%m-%d")
        + "T00:00:00"
    )

    end_time = (
        today.strftime("%Y-%m-%d")
        + "T23:59:59"
    )

    activities = get_activities_between(
        start_time,
        end_time
    )

    print(
        "ACTIVITY COUNT:",
        len(activities)
    )

    if not activities:
        return (
            "No activities recorded today."
        )

    context = []

    for activity in activities:

        app_name = activity[2]

        window_title = activity[3]

        source = activity[6]

        url = activity[7]

        line = (
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

        context.append(
            line
        )

    timeline = "\n".join(
        context
    )

    prompt = f"""
You are PersonalOS AI.

You MUST ONLY use information present in the logs.

Do NOT invent activities.

If information is missing,
say that it is missing.

Below is today's activity:

{timeline}

Generate a concise summary.

Use bullet points.
"""

    return ask_gemini(
        prompt
    )