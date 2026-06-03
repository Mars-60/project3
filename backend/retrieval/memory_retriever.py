from datetime import (
    datetime,
    timedelta
)

from backend.database.db import (
    get_recent_activities
)

from backend.database.time_queries import (
    get_activities_between
)

from backend.retrieval.pdf_retriever import (
    retrieve_pdf_context
)


DEFAULT_RECENT_LIMIT = 150
PDF_CONTEXT_LIMIT = 6


def resolve_time_range(question):
    normalized_question = (
        question or ""
    ).lower()

    if "today" in normalized_question:
        today = datetime.now()

        return {
            "label": "today",
            "start": (
                today.strftime("%Y-%m-%d")
                + "T00:00:00"
            ),
            "end": (
                today.strftime("%Y-%m-%d")
                + "T23:59:59"
            ),
        }

    if "yesterday" in normalized_question:
        yesterday = (
            datetime.now()
            - timedelta(days=1)
        )

        return {
            "label": "yesterday",
            "start": (
                yesterday.strftime("%Y-%m-%d")
                + "T00:00:00"
            ),
            "end": (
                yesterday.strftime("%Y-%m-%d")
                + "T23:59:59"
            ),
        }

    return {
        "label": "recent activity",
        "start": None,
        "end": None,
    }


def retrieve_activity_rows(time_range):
    if time_range["start"] and time_range["end"]:
        return get_activities_between(
            time_range["start"],
            time_range["end"]
        )

    return get_recent_activities(
        limit=DEFAULT_RECENT_LIMIT
    )


def retrieve_memory_package(question):
    time_range = resolve_time_range(
        question
    )

    activities = retrieve_activity_rows(
        time_range
    )

    websites = [
        activity
        for activity in activities
        if activity[4]
        or activity[7] == "browser_extension"
    ]

    ocr_records = [
        activity
        for activity in activities
        if activity[5]
        or activity[7] == "ocr"
    ]

    pdf_context = retrieve_pdf_context(
        question,
        limit=PDF_CONTEXT_LIMIT
    )

    return {
        "question": question,
        "time_range": time_range,
        "activities": activities,
        "websites": websites,
        "ocr_records": ocr_records,
        "pdf_context": pdf_context,
    }
