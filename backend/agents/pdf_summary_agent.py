from backend.ai.gemini_client import (
    ask_gemini
)

from backend.retrieval.pdf_retriever import (
    retrieve_pdf_context
)


def summarize_pdf_learning():
    chunks = retrieve_pdf_context(
        (
            "learning study studied topic topics concept concepts "
            "technology technologies subject subjects covered main "
            "overview summary deadlock concurrency database operating "
            "system process thread"
        ),
        limit=12
    )

    if not chunks:
        return (
            "No stored PDF content found to summarize."
        )

    context = []

    for chunk in chunks:
        source = (
            f"[{chunk['file_name']} "
            f"pages {chunk['page_start']}-{chunk['page_end']}]"
        )

        context.append(
            source
            + "\n"
            + chunk["text"]
        )

    pdf_context = "\n\n".join(
        context
    )

    prompt = f"""
You are PersonalOS AI.

The PDF excerpts below were retrieved from the user's
stored PDF memory.

Generate a concise learning summary that explains:

- What topics were studied
- The main concepts
- Technologies or subjects covered

The summary should answer:
"What was I studying in this PDF?"

Use only the PDF excerpts below.
If details are missing, say they are missing.

PDF Excerpts:

{pdf_context}
"""

    return ask_gemini(
        prompt
    )
