from backend.retrieval.time_retriever import (
    retrieve_by_time
)

from backend.ai.gemini_client import (
    ask_gemini
)


def ask_memory(question):

    activities = retrieve_by_time(
        question
    )

    if not activities:
        return (
            "No matching activities found."
        )

    context = []

    for activity in activities:

        timestamp = activity[1]

        app_name = activity[2]

        window_title = activity[3]

        source = activity[6]

        url = activity[7]

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

        context.append(
            line
        )

    timeline = "\n".join(
        context
    )

    prompt = f"""
You are PersonalOS AI.

The activity logs below were already retrieved
specifically to answer the user's question.

The logs represent the correct time period
requested by the user.

You MUST ONLY use information present in the logs.

Do NOT invent activities.

Activity Logs:

{timeline}

Question:

{question}

Do not recalculate dates.
Assume the retrieved logs already correspond
to the requested time period.

Answer only from the logs.
"""
    return ask_gemini(
        prompt
    )