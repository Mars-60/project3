import hashlib
from datetime import datetime
from pathlib import Path

from backend.database.pdf_db import (
    get_pdf_document_by_hash,
    initialize_pdf_database,
    insert_pdf_chunk,
    insert_pdf_document,
    insert_pdf_page
)

from backend.pdf.chunker import (
    chunk_text
)

from backend.pdf.text_extractor import (
    extract_text_by_page
)


def calculate_file_hash(file_path):
    digest = hashlib.sha256()

    with open(file_path, "rb") as file:
        for block in iter(
            lambda: file.read(1024 * 1024),
            b""
        ):
            digest.update(
                block
            )

    return digest.hexdigest()


def ingest_pdf(pdf_path):
    initialize_pdf_database()

    path = Path(
        pdf_path
    )

    if not path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    if path.suffix.lower() != ".pdf":
        raise ValueError(
            "Only .pdf files can be ingested."
        )

    file_hash = calculate_file_hash(
        path
    )

    existing_document = get_pdf_document_by_hash(
        file_hash
    )

    if existing_document:
        existing_document["duplicate"] = True
        return existing_document

    pages = extract_text_by_page(
        path
    )

    imported_at = datetime.now().isoformat()

    document_id = insert_pdf_document(
        file_name=path.name,
        file_path=str(path),
        file_hash=file_hash,
        page_count=len(pages),
        imported_at=imported_at
    )

    for page_number, page_text in enumerate(
        pages,
        start=1
    ):
        insert_pdf_page(
            document_id,
            page_number,
            page_text
        )

    chunks = chunk_text(
        pages
    )

    for chunk_index, chunk in enumerate(
        chunks,
        start=1
    ):
        insert_pdf_chunk(
            document_id=document_id,
            file_name=path.name,
            page_start=chunk["page_start"],
            page_end=chunk["page_end"],
            chunk_index=chunk_index,
            text=chunk["text"]
        )

    return {
        "id": document_id,
        "file_name": path.name,
        "file_path": str(path),
        "file_hash": file_hash,
        "page_count": len(pages),
        "chunk_count": len(chunks),
        "imported_at": imported_at,
        "duplicate": False
    }
