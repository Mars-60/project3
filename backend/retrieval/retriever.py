from backend.database.db import (
    get_recent_activities
)


def retrieve_context(
    question,
    limit=30
):

    activities = get_recent_activities(
        limit
    )

    question = question.lower()

    relevant = []

    for activity in activities:

        window_title = str(
            activity[3]
        ).lower()

        url = str(
            activity[7]
        ).lower()

        if (
            "website" in question
            or "visit" in question
            or "browser" in question
        ):

            if activity[6] == "browser_extension":

                relevant.append(
                    activity
                )

        else:

            relevant.append(
                activity
            )

    return relevant