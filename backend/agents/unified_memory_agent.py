from backend.agents.pdf_summary_agent import (
    summarize_pdf_learning
)

from backend.agents.smart_memory_agent import (
    ask_memory
)

from backend.ai.gemini_client import (
    ask_gemini
)

from backend.retrieval.time_retriever import (
    retrieve_by_time
)


STUDY_KEYWORDS = (
    "study",
    "studying",
    "learned",
    "reading",
    "read",
    "pdf"
)


def is_study_question(question):
    question = question.lower()

    for keyword in STUDY_KEYWORDS:
        if keyword in question:
            return True

    return False


def build_activity_context(activities):
    if not activities:
        return (
            "No matching activity logs found."
        )

    context = []

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

        context.append(
            line
        )

    return "\n".join(
        context
    )


def answer_memory_question(question):
    if not is_study_question(
        question
    ):
        return ask_memory(
            question
        )

    activities = retrieve_by_time(
        question
    )

    activity_context = build_activity_context(
        activities
    )

    pdf_summary = summarize_pdf_learning()

    prompt = f"""
You are PersonalOS AI.

The user asked a memory question related to studying,
reading, learning, or PDFs.

Use both sources below to answer the question.

Activity Context:

{activity_context}

PDF Learning Summary:

{pdf_summary}

Question:

{question}

Generate one concise final answer.
If one source is missing information, say that clearly.
Do not invent details.
"""

    return ask_gemini(
        prompt
    )
