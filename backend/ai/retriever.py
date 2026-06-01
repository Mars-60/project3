from backend.database.db import (
    get_recent_activities
)


def retrieve_relevant_activities(
    question,
    limit=20
):
    activities = get_recent_activities(
        limit
    )

    question = question.lower()

    filtered = []

    for activity in activities:

        app_name = (
            activity[2] or ""
        ).lower()

        window_title = (
            activity[3] or ""
        ).lower()

        ocr_text = (
            activity[4] or ""
        ).lower()

        combined = (
            app_name
            + " "
            + window_title
            + " "
            + ocr_text
        )

        question_words = (
            question.split()
        )

        for word in question_words:

            if word in combined:
                filtered.append(
                    activity
                )
                break

    if filtered:
        return filtered

    return activities