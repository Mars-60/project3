import sqlite3

from backend.collectors import ocr_collector
from backend.database import db


def test_ocr_text_reaches_ocr_text_column(tmp_path, monkeypatch):
    database_path = tmp_path / "activity.db"

    monkeypatch.setattr(
        db,
        "DATABASE_PATH",
        database_path
    )

    db.initialize_database()

    db.insert_activity(
        "2026-06-03T10:00:00",
        "Code.exe",
        "VS Code",
        source="ocr",
        ocr_text="visible editor text"
    )

    conn = sqlite3.connect(
        database_path
    )
    row = conn.execute(
        """
        SELECT url, ocr_text, source
        FROM activity_logs
        """
    ).fetchone()
    conn.close()

    assert row == (
        None,
        "visible editor text",
        "ocr"
    )


def test_ocr_collection_runs_automatically():
    inserted = []

    ocr_collector.reset_ocr_state()

    assert ocr_collector.should_capture_ocr(
        last_capture_time=0,
        current_time=ocr_collector.OCR_INTERVAL_SECONDS
    )

    did_insert = ocr_collector.collect_ocr_activity(
        "Code.exe",
        "VS Code",
        timestamp="2026-06-03T10:00:00",
        capture_func=lambda: "screenshots/active_window.png",
        extract_func=lambda path: "automatic OCR text",
        insert_func=lambda *args, **kwargs: inserted.append(
            (args, kwargs)
        )
    )

    assert did_insert is True
    assert inserted[0][0] == (
        "2026-06-03T10:00:00",
        "Code.exe",
        "VS Code"
    )
    assert inserted[0][1] == {
        "source": "ocr",
        "ocr_text": "automatic OCR text"
    }


def test_duplicate_ocr_snapshots_are_skipped():
    inserted = []

    ocr_collector.reset_ocr_state()

    first_insert = ocr_collector.collect_ocr_activity(
        "Code.exe",
        "VS Code",
        timestamp="2026-06-03T10:00:00",
        capture_func=lambda: "screenshots/active_window.png",
        extract_func=lambda path: "same OCR text",
        insert_func=lambda *args, **kwargs: inserted.append(
            (args, kwargs)
        )
    )

    second_insert = ocr_collector.collect_ocr_activity(
        "Code.exe",
        "VS Code",
        timestamp="2026-06-03T10:00:30",
        capture_func=lambda: "screenshots/active_window.png",
        extract_func=lambda path: "same OCR text",
        insert_func=lambda *args, **kwargs: inserted.append(
            (args, kwargs)
        )
    )

    assert first_insert is True
    assert second_insert is False
    assert len(inserted) == 1
