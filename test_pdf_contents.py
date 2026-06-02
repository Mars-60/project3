from backend.database.pdf_db import (
    get_connection,
    initialize_pdf_database
)


initialize_pdf_database()

conn = get_connection()

cursor = conn.cursor()

cursor.execute("""
    SELECT COUNT(*)
    FROM pdf_documents
""")
document_count = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(*)
    FROM pdf_pages
""")
page_count = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(*)
    FROM pdf_chunks
""")
chunk_count = cursor.fetchone()[0]

print(
    "Documents:",
    document_count
)

print(
    "Pages:",
    page_count
)

print(
    "Chunks:",
    chunk_count
)

print(
    "\nFirst 5 chunks:"
)

cursor.execute("""
    SELECT
        id,
        document_id,
        page_start,
        page_end,
        chunk_index,
        text
    FROM pdf_chunks
    ORDER BY id
    LIMIT 5
""")

chunks = cursor.fetchall()

for chunk in chunks:
    (
        chunk_id,
        document_id,
        page_start,
        page_end,
        chunk_index,
        text
    ) = chunk

    print(
        "\nChunk ID:",
        chunk_id
    )

    print(
        "Document ID:",
        document_id
    )

    print(
        "Pages:",
        f"{page_start}-{page_end}"
    )

    print(
        "Chunk Index:",
        chunk_index
    )

    print(
        "Text:"
    )

    print(
        text
    )

conn.close()
