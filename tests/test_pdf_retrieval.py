import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

from backend.database import pdf_db
from backend.pdf import pdf_ingestor
from backend.retrieval.pdf_retriever import (
    retrieve_pdf_context
)


def run_test():
    temp_dir = Path(
        tempfile.mkdtemp()
    )

    original_database_path = pdf_db.DATABASE_PATH

    try:
        pdf_db.DATABASE_PATH = temp_dir / "activity.db"

        sample_pdf = temp_dir / "retrieval.pdf"
        sample_pdf.write_bytes(
            b"%PDF-1.4 retrieval content"
        )

        pdf_ingestor.extract_text_by_page = lambda path: [
            "The alpha project uses local memory.",
            "The beta project uses semantic search later."
        ]

        pdf_ingestor.ingest_pdf(
            sample_pdf
        )

        results = retrieve_pdf_context(
            "alpha local memory",
            limit=5
        )

        assert results
        assert isinstance(
            results[0],
            dict
        )
        assert "alpha project" in results[0]["text"].lower()
        assert results[0]["file_name"] == "retrieval.pdf"

        print(
            "PDF retrieval test passed."
        )

    finally:
        pdf_db.DATABASE_PATH = original_database_path
        shutil.rmtree(
            temp_dir
        )


if __name__ == "__main__":
    run_test()
