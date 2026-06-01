from backend.database.db import (
    get_recent_activities
)

from backend.ai.context_builder import (
    build_context
)

from backend.ai.gemini_client import (
    ask_gemini
)


def answer_question(question):
    from backend.ai.retriever import (
        retrieve_relevant_activities
    )

    activities = retrieve_relevant_activities(
        question
    )
    context = build_context(
            activities
        )

    prompt = f"""
You are PersonalOS AI.

Below is the user's recent activity history.

{context}

User Question:
{question}

Answer based only on the activity history.
"""

    return ask_gemini(prompt)