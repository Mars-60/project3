from backend.retrieval.clean_timeline_builder import (
    build_clean_timeline
)

from backend.ai.gemini_client import (
    ask_gemini
)


def generate_daily_summary():

    timeline = build_clean_timeline(
        limit=50
    )

    prompt = f"""
You are PersonalOS AI.

Below is the user's activity timeline.

{timeline}

Generate a concise summary of what the user
has been doing.

Use bullet points.
"""

    return ask_gemini(
        prompt
    )