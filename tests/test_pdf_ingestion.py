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


def run_test():
    temp_dir = Path(
        tempfile.mkdtemp()
    )

    original_database_path = pdf_db.DATABASE_PATH

    try:
        pdf_db.DATABASE_PATH = temp_dir / "activity.db"

        sample_pdf = temp_dir / "sample.pdf"
        sample_pdf.write_bytes(
            b"%PDF-1.4 sample content"
        )

        pdf_ingestor.extract_text_by_page = lambda path: [
            "PersonalOS stores memories locally.",
            "PDF memory uses SQLite FTS search."
        ]

        first_result = pdf_ingestor.ingest_pdf(
            sample_pdf
        )

        second_result = pdf_ingestor.ingest_pdf(
            sample_pdf
        )

        assert first_result["duplicate"] is False
        assert first_result["page_count"] == 2
        assert first_result["chunk_count"] == 1
        assert second_result["duplicate"] is True
        assert second_result["id"] == first_result["id"]

        print(
            "PDF ingestion test passed."
        )

    finally:
        pdf_db.DATABASE_PATH = original_database_path
        shutil.rmtree(
            temp_dir
        )


if __name__ == "__main__":
    run_test()
