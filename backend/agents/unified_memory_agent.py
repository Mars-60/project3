from backend.ai.gemini_client import (
    ask_gemini
)

from backend.retrieval.memory_context_builder import (
    build_memory_context
)

from backend.retrieval.memory_retriever import (
    retrieve_memory_package
)


def answer_memory_question(question):
    memory_package = retrieve_memory_package(
        question
    )

    memory_context = build_memory_context(
        memory_package
    )

    prompt = f"""
You are Atlas, the memory reasoning layer for PersonalOS AI.

Use the memory context as evidence.
Do not invent activities, websites, files, PDFs, or screen contents.
Do not expose raw database implementation details.

Infer the answer naturally from the evidence when possible.
If the evidence is weak or missing, say what is missing.

Question:

{question}

Memory Context:

{memory_context}

Answer concisely and helpfully.
"""

    return ask_gemini(
        prompt
    )
