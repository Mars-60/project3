from difflib import SequenceMatcher

from backend.database.db import insert_activity
from backend.ocr.ocr_engine import extract_text
from backend.screenshots.screenshot_capture import capture_active_window
from backend.utils.time_utils import get_current_timestamp

OCR_INTERVAL_SECONDS = 30
OCR_SIMILARITY_THRESHOLD = 0.90

last_ocr_text = None


def normalize_ocr_text(text):
    return " ".join(
        (text or "").split()
    )


def is_significantly_different(
    previous_text,
    current_text,
    similarity_threshold=OCR_SIMILARITY_THRESHOLD
):
    if not previous_text:
        print("OCR similarity score: N/A")
        return True

    similarity = SequenceMatcher(
        None,
        previous_text,
        current_text
    ).ratio()

    print(f"OCR similarity score: {similarity:.3f}")

    return similarity < similarity_threshold


def should_capture_ocr(
    last_capture_time,
    current_time,
    interval_seconds=OCR_INTERVAL_SECONDS
):
    return current_time - last_capture_time >= interval_seconds


def collect_ocr_activity(
    app_name,
    window_title,
    timestamp=None,
    capture_func=capture_active_window,
    extract_func=extract_text,
    insert_func=insert_activity
):
    global last_ocr_text

    print("OCR collection started")

    screenshot_path = capture_func()

    if not screenshot_path:
        print("OCR skipped: screenshot not captured")
        return False

    print(f"Screenshot captured: {screenshot_path}")

    ocr_text = normalize_ocr_text(
        extract_func(
            screenshot_path
        )
    )

    print(f"OCR text length: {len(ocr_text)}")

    if not ocr_text:
        print("OCR skipped: empty text")
        return False

    if not is_significantly_different(
        last_ocr_text,
        ocr_text
    ):
        print("OCR skipped: similar to previous capture")
        return False

    insert_func(
        timestamp or get_current_timestamp(),
        app_name,
        window_title,
        source="ocr",
        ocr_text=ocr_text
    )

    last_ocr_text = ocr_text

    print("OCR record inserted")

    return True


def reset_ocr_state():
    global last_ocr_text

    last_ocr_text = None
