import sqlite3

from backend.database.db import (
    DATABASE_PATH
)


def get_connection():
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    return sqlite3.connect(
        DATABASE_PATH
    )


def initialize_pdf_database():
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pdf_documents(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_hash TEXT NOT NULL UNIQUE,
            page_count INTEGER NOT NULL,
            imported_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pdf_pages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            page_number INTEGER NOT NULL,
            text TEXT,
            FOREIGN KEY(document_id)
                REFERENCES pdf_documents(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pdf_chunks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            page_start INTEGER NOT NULL,
            page_end INTEGER NOT NULL,
            chunk_index INTEGER NOT NULL,
            text TEXT NOT NULL,
            FOREIGN KEY(document_id)
                REFERENCES pdf_documents(id)
        )
    """)

    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS pdf_chunks_fts
        USING fts5(
            chunk_id UNINDEXED,
            document_id UNINDEXED,
            file_name UNINDEXED,
            text
        )
    """)

    conn.commit()
    conn.close()


def get_pdf_document_by_hash(file_hash):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            file_name,
            file_path,
            file_hash,
            page_count,
            imported_at
        FROM pdf_documents
        WHERE file_hash = ?
    """, (file_hash,))

    row = cursor.fetchone()

    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "file_name": row[1],
        "file_path": row[2],
        "file_hash": row[3],
        "page_count": row[4],
        "imported_at": row[5]
    }


def insert_pdf_document(
    file_name,
    file_path,
    file_hash,
    page_count,
    imported_at
):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pdf_documents
        (
            file_name,
            file_path,
            file_hash,
            page_count,
            imported_at
        )
        VALUES (?, ?, ?, ?, ?)
    """,
    (
        file_name,
        file_path,
        file_hash,
        page_count,
        imported_at
    ))

    document_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return document_id


def insert_pdf_page(
    document_id,
    page_number,
    text
):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pdf_pages
        (
            document_id,
            page_number,
            text
        )
        VALUES (?, ?, ?)
    """,
    (
        document_id,
        page_number,
        text
    ))

    conn.commit()
    conn.close()


def insert_pdf_chunk(
    document_id,
    file_name,
    page_start,
    page_end,
    chunk_index,
    text
):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pdf_chunks
        (
            document_id,
            page_start,
            page_end,
            chunk_index,
            text
        )
        VALUES (?, ?, ?, ?, ?)
    """,
    (
        document_id,
        page_start,
        page_end,
        chunk_index,
        text
    ))

    chunk_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO pdf_chunks_fts
        (
            chunk_id,
            document_id,
            file_name,
            text
        )
        VALUES (?, ?, ?, ?)
    """,
    (
        chunk_id,
        document_id,
        file_name,
        text
    ))

    conn.commit()
    conn.close()

    return chunk_id


def search_pdf_chunks(
    question,
    limit=5
):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            c.id,
            c.document_id,
            d.file_name,
            d.file_path,
            c.page_start,
            c.page_end,
            c.chunk_index,
            c.text,
            bm25(pdf_chunks_fts) AS score
        FROM pdf_chunks_fts
        JOIN pdf_chunks c
            ON c.id = pdf_chunks_fts.chunk_id
        JOIN pdf_documents d
            ON d.id = c.document_id
        WHERE pdf_chunks_fts MATCH ?
        ORDER BY score
        LIMIT ?
    """,
    (
        question,
        limit
    ))

    rows = cursor.fetchall()

    conn.close()

    results = []

    for row in rows:
        results.append(
            {
                "chunk_id": row[0],
                "document_id": row[1],
                "file_name": row[2],
                "file_path": row[3],
                "page_start": row[4],
                "page_end": row[5],
                "chunk_index": row[6],
                "text": row[7],
                "score": row[8]
            }
        )

    return results
