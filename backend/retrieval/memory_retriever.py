from datetime import datetime, timedelta

from backend.database.db import get_recent_activities
from backend.database.time_queries import get_activities_between
from backend.retrieval.pdf_retriever import retrieve_pdf_context


DEFAULT_RECENT_LIMIT = 150
PDF_CONTEXT_LIMIT = 4


# ── Weekday name → number (Monday=0)
WEEKDAY_MAP = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def resolve_time_range(question):
    """
    Parses the question and returns a dict with
    label, start, end (ISO strings or None).

    Handles:
      - today / yesterday
      - day names: "on Monday", "last Tuesday" etc.
      - hour ranges: "at 3pm", "between 2pm and 4pm",
        "from 10am to 12pm", "in the morning/afternoon/evening"
    """
    q = (question or "").lower()
    now = datetime.now()

    # ── Pick the base DATE first ──────────────────────────────
    base_date = None  # will be a date object

    if "today" in q:
        base_date = now.date()
        day_label = "today"

    elif "yesterday" in q:
        base_date = (now - timedelta(days=1)).date()
        day_label = "yesterday"

    else:
        # Check for weekday names
        for day_name, day_num in WEEKDAY_MAP.items():
            if day_name in q:
                days_ago = (now.weekday() - day_num) % 7
                # "last X" or same weekday today → go back a full week
                if days_ago == 0:
                    days_ago = 7
                base_date = (now - timedelta(days=days_ago)).date()
                day_label = day_name.capitalize()
                break

    if base_date is None:
        # No specific day found — return recent
        return {
            "label": "recent activity",
            "start": None,
            "end": None,
        }

    # ── Now look for time-of-day hints in the question ────────
    start_hour = 0
    end_hour = 23
    time_label = ""

    # "in the morning" → 6–12
    if "morning" in q:
        start_hour, end_hour = 6, 11
        time_label = " (morning)"

    # "in the afternoon" → 12–17
    elif "afternoon" in q:
        start_hour, end_hour = 12, 17
        time_label = " (afternoon)"

    # "in the evening" or "at night" → 18–23
    elif "evening" in q or "night" in q:
        start_hour, end_hour = 18, 23
        time_label = " (evening)"

    else:
        # Try to find explicit hours like "at 3pm", "at 15:00",
        # "between 2pm and 4pm", "from 10am to 12"
        import re

        # Match patterns like 3pm, 3:30pm, 15, 15:30, 10am
        time_pattern = r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?'

        matches = re.findall(time_pattern, q)

        parsed_hours = []
        for h_str, m_str, meridiem in matches:
            h = int(h_str)
            if meridiem == "pm" and h != 12:
                h += 12
            elif meridiem == "am" and h == 12:
                h = 0
            # Ignore year-like numbers
            if 0 <= h <= 23:
                parsed_hours.append(h)

        if len(parsed_hours) == 1:
            # "at 3pm" → 3pm to 3:59pm
            start_hour = parsed_hours[0]
            end_hour = parsed_hours[0]
            time_label = f" (around {parsed_hours[0]:02d}:00)"

        elif len(parsed_hours) >= 2:
            # "between 2pm and 4pm"
            start_hour = min(parsed_hours[:2])
            end_hour = max(parsed_hours[:2])
            time_label = f" ({start_hour:02d}:00–{end_hour:02d}:59)"

    start_str = (
        f"{base_date.strftime('%Y-%m-%d')}T{start_hour:02d}:00:00"
    )
    end_str = (
        f"{base_date.strftime('%Y-%m-%d')}T{end_hour:02d}:59:59"
    )

    return {
        "label": f"{day_label}{time_label}",
        "start": start_str,
        "end": end_str,
    }


def retrieve_activity_rows(time_range):
    if time_range["start"] and time_range["end"]:
        return get_activities_between(
            time_range["start"],
            time_range["end"]
        )
    return get_recent_activities(limit=DEFAULT_RECENT_LIMIT)


def detect_opened_pdfs(activities):
    """
    Returns PDF file names that were actually
    opened/viewed during the time range.
    Only looks at window titles and OCR text
    from activity rows inside the range.
    """
    pdf_names = set()
    for row in activities:
        window_title = (row[3] or "").lower()
        ocr_text = (row[5] or "").lower()
        combined = window_title + " " + ocr_text
        # Look for .pdf mentions
        import re
        found = re.findall(r'[\w\-]+\.pdf', combined)
        for name in found:
            pdf_names.add(name)
    return pdf_names


def retrieve_memory_package(question):
    time_range = resolve_time_range(question)
    activities = retrieve_activity_rows(time_range)

    # Websites = rows that came from browser extension
    # or have a URL (column index 4 is url in your schema)
    websites = [
        row for row in activities
        if row[7] == "browser_extension" or row[4]
    ]

    # OCR records
    ocr_records = [
        row for row in activities
        if row[7] == "ocr" or row[5]
    ]

    # ── Only include PDF context if a PDF was actually
    #    opened during the queried time range ──────────
    pdf_context = []
    pdfs_opened = detect_opened_pdfs(activities)

    if pdfs_opened:
        for pdf_name in pdfs_opened:
            pdf_context.extend(
                retrieve_pdf_context(pdf_name, limit=3)
            )

    return {
        "question": question,
        "time_range": time_range,
        "activities": activities,
        "websites": websites,
        "ocr_records": ocr_records,
        "pdf_context": pdf_context,
    }