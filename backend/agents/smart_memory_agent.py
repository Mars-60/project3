from backend.ai.gemini_client import (
    ask_gemini
)

from backend.database.db import (
    get_recent_activities
)

from backend.retrieval.activity_normalizer import (
    build_activity_summary,
    filter_activities_by_intent,
    normalize_activities
)

from backend.retrieval.query_intent import (
    detect_query_intent,
    is_time_specific
)

from backend.retrieval.memory_retriever import (
    retrieve_by_time
)

def ask_memory(question):

    intent = detect_query_intent(
        question
    )

    rows = retrieve_by_time(
        question
    )

    if not rows and not is_time_specific(
        question
    ):
        rows = get_recent_activities(
            limit=100
        )

    activities = normalize_activities(
        rows
    )

    matching_activities = filter_activities_by_intent(
        activities,
        intent
    )

    if not matching_activities:
        return (
            "No matching activities found."
        )

    summary = build_activity_summary(
        matching_activities,
        intent
    )

    prompt = f"""
You are PersonalOS AI.

The activity summary below was built from all matching
activity records in the selected time range.

Use the normalized app and website names.
Do not show raw URLs or executable names.

YOU MUST ONLY use information present in the summary.

Do NOT invent activities.

Activity Summary:

{summary}

Question:

{question}

Do not recalculate dates.
Assume the summarized records already correspond
to the requested time period.

Answer naturally and concisely.
For app or website questions, use a short bullet list.
"""

    return ask_gemini(
        prompt
    )
