from backend.ocr.ocr_engine import (
    extract_text
)

text = extract_text(
    "screenshots/active_window.png"
)

print(text)