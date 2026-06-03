from collections import Counter

from backend.retrieval.activity_normalizer import (
    normalize_activities
)


MAX_APPS = 8
MAX_WEBSITES = 10
MAX_ACTIVITY_PATTERNS = 10
MAX_OCR_SNIPPETS = 6
MAX_PDF_EXCERPTS = 5
OCR_SNIPPET_LENGTH = 350
PDF_EXCERPT_LENGTH = 500


def count_values(values):
    return Counter(
        value
        for value in values
        if value
    )


def format_counter(counter, limit):
    lines = []

    for value, count in counter.most_common(
        limit
    ):
        lines.append(
            f"- {value}: {count}"
        )

    return lines


def compact_text(text, limit):
    normalized_text = " ".join(
        (text or "").split()
    )

    if len(
        normalized_text
    ) <= limit:
        return normalized_text

    return (
        normalized_text[:limit].rstrip()
        + "..."
    )


def build_activity_patterns(activities):
    patterns = count_values(
        [
            (
                activity["app_display"]
                + " | "
                + activity["window_title"]
            )
            for activity in activities
            if activity["window_title"]
        ]
    )

    return format_counter(
        patterns,
        MAX_ACTIVITY_PATTERNS
    )


def build_ocr_snippets(ocr_records):
    snippets = []
    seen = set()

    for activity in ocr_records:
        snippet = compact_text(
            activity["ocr_text"],
            OCR_SNIPPET_LENGTH
        )

        if not snippet or snippet in seen:
            continue

        snippets.append(
            "- "
            + snippet
        )
        seen.add(
            snippet
        )

        if len(
            snippets
        ) >= MAX_OCR_SNIPPETS:
            break

    return snippets


def build_pdf_excerpts(pdf_context):
    excerpts = []

    for chunk in pdf_context[:MAX_PDF_EXCERPTS]:
        source = (
            f"{chunk['file_name']} "
            f"pages {chunk['page_start']}-{chunk['page_end']}"
        )

        excerpts.append(
            "- "
            + source
            + ": "
            + compact_text(
                chunk["text"],
                PDF_EXCERPT_LENGTH
            )
        )

    return excerpts


def append_section(lines, title, section_lines):
    lines.append(
        title
    )

    if section_lines:
        lines.extend(
            section_lines
        )
    else:
        lines.append(
            "- None found"
        )


def build_memory_context(memory_package):
    activities = normalize_activities(
        memory_package["activities"]
    )
    websites = normalize_activities(
        memory_package["websites"]
    )
    ocr_records = normalize_activities(
        memory_package["ocr_records"]
    )
    pdf_context = memory_package["pdf_context"]
    time_range = memory_package["time_range"]

    app_counts = count_values(
        [
            activity["app_display"]
            for activity in activities
        ]
    )

    website_counts = count_values(
        [
            activity["website_display"]
            for activity in websites
        ]
    )

    lines = [
        "Memory Context Package",
        "",
        "Time Range:",
        f"- {time_range['label']}",
        f"- Activity records: {len(activities)}",
        f"- Website records: {len(websites)}",
        f"- OCR records: {len(ocr_records)}",
        f"- PDF excerpts: {len(pdf_context)}",
        "",
    ]

    append_section(
        lines,
        "Apps:",
        format_counter(
            app_counts,
            MAX_APPS
        )
    )

    append_section(
        lines,
        "Websites:",
        format_counter(
            website_counts,
            MAX_WEBSITES
        )
    )

    append_section(
        lines,
        "Repeated Activity Patterns:",
        build_activity_patterns(
            activities
        )
    )

    append_section(
        lines,
        "OCR Evidence:",
        build_ocr_snippets(
            ocr_records
        )
    )

    append_section(
        lines,
        "PDF Evidence:",
        build_pdf_excerpts(
            pdf_context
        )
    )

    return "\n".join(
        lines
    )
