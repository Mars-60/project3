from backend.database.pdf_db import (
    initialize_pdf_database,
    search_pdf_chunks
)

import re


def build_fts_query(question):
    words = re.findall(
        r"[A-Za-z0-9]+",
        question.lower()
    )

    return " OR ".join(
        words
    )


def retrieve_pdf_context(
    question,
    limit=5
):
    initialize_pdf_database()

    if not question:
        return []

    fts_query = build_fts_query(
        question
    )

    if not fts_query:
        return []

    return search_pdf_chunks(
        fts_query,
        limit
    )
