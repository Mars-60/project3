INTENT_KEYWORDS = {
    "apps": (
        "app",
        "apps",
        "application",
        "applications",
        "software",
        "program",
        "programs",
    ),
    "websites": (
        "website",
        "websites",
        "site",
        "sites",
        "browser",
        "browsing",
        "visited",
        "visit",
        "url",
        "urls",
    ),
    "ocr": (
        "screen",
        "visible",
        "reading",
        "read",
        "display",
        "displayed",
        "shown",
        "see",
        "saw",
    ),
    "coding": (
        "coding",
        "code",
        "development",
        "developer",
        "programming",
        "debug",
        "debugging",
        "github",
        "leetcode",
    ),
    "study": (
        "study",
        "studying",
        "learning",
        "learned",
        "course",
        "pdf",
        "pdfs",
    ),
    "daily_summary": (
        "daily summary",
        "today summary",
        "summarize today",
        "summary today",
        "what did i do today",
        "recap today",
    ),
}


def detect_query_intent(question):
    normalized_question = (
        question or ""
    ).lower()

    if not normalized_question:
        return "general"

    for intent in (
        "daily_summary",
        "ocr",
        "apps",
        "websites",
        "coding",
        "study",
    ):
        for keyword in INTENT_KEYWORDS[intent]:
            if keyword in normalized_question:
                return intent

    return "general"


def is_time_specific(question):
    normalized_question = (
        question or ""
    ).lower()

    return (
        "today" in normalized_question
        or "yesterday" in normalized_question
    )
