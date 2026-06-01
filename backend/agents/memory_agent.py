from backend.retrieval.retriever import (
    retrieve_context
)

from backend.ai.gemini_client import (
    ask_gemini
)


def ask_memory(question):

    activities = retrieve_context(
        question
    )

    context = []

    for activity in activities:

        timestamp = activity[1]

        app_name = activity[2]

        window_title = activity[3]

        ocr_text = activity[4]

        category = activity[5]

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

        context.append(
            line
        )

    timeline = "\n".join(
        context
    )

    prompt = f"""
You are PersonalOS AI.

Below is the user's relevant activity history.

{timeline}

Answer the following question:

{question}
"""

    response = ask_gemini(
        prompt
    )

    return response