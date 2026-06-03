from collections import Counter
from urllib.parse import urlparse


APP_NAMES = {
    "chrome.exe": "Google Chrome",
    "code.exe": "Visual Studio Code",
    "spotify.exe": "Spotify",
    "whatsapp.root.exe": "WhatsApp",
    "chatgpt.exe": "ChatGPT",
}


WEBSITE_NAMES = {
    "leetcode.com": "LeetCode",
    "github.com": "GitHub",
    "youtube.com": "YouTube",
    "codeforces.com": "Codeforces",
    "codechef.com": "CodeChef",
    "claude.ai": "Claude",
    "chatgpt.com": "ChatGPT",
}


def normalize_app_name(app_name):
    if not app_name:
        return "Unknown App"

    return APP_NAMES.get(
        app_name.lower(),
        app_name
    )


def get_url_domain(url):
    if not url:
        return ""

    parsed_url = urlparse(
        url
    )

    domain = (
        parsed_url.netloc
        or parsed_url.path
    ).lower()

    if domain.startswith(
        "www."
    ):
        domain = domain[4:]

    return domain


def normalize_website_name(url):
    domain = get_url_domain(
        url
    )

    if not domain:
        return ""

    for known_domain, website_name in WEBSITE_NAMES.items():
        if domain == known_domain or domain.endswith(
            "." + known_domain
        ):
            return website_name

    first_domain_part = domain.split(
        "."
    )[0]

    return first_domain_part.replace(
        "-",
        " "
    ).title()


def normalize_activity(row):
    return {
        "id": row[0],
        "timestamp": row[1],
        "app_name": row[2],
        "app_display": normalize_app_name(
            row[2]
        ),
        "window_title": row[3],
        "url": row[4],
        "website_display": normalize_website_name(
            row[4]
        ),
        "ocr_text": row[5],
        "category": row[6],
        "source": row[7],
    }


def normalize_activities(rows):
    return [
        normalize_activity(
            row
        )
        for row in rows
    ]


def matches_intent(activity, intent):
    source = (
        activity["source"] or ""
    ).lower()
    app_name = (
        activity["app_name"] or ""
    ).lower()
    window_title = (
        activity["window_title"] or ""
    ).lower()
    url = (
        activity["url"] or ""
    ).lower()
    ocr_text = (
        activity["ocr_text"] or ""
    ).strip()

    if intent == "apps":
        return bool(
            activity["app_name"]
        )

    if intent == "websites":
        return bool(
            activity["url"]
        ) or source == "browser_extension"

    if intent == "ocr":
        return bool(
            ocr_text
        ) or source == "ocr"

    if intent == "coding":
        combined = (
            app_name
            + " "
            + window_title
            + " "
            + url
            + " "
            + ocr_text.lower()
        )

        return any(
            keyword in combined
            for keyword in (
                "code",
                "github",
                "leetcode",
                "programming",
                "development",
                "python",
                "javascript",
                "debug",
            )
        )

    return True


def filter_activities_by_intent(activities, intent):
    if intent in (
        "general",
        "daily_summary",
        "study",
    ):
        return activities

    return [
        activity
        for activity in activities
        if matches_intent(
            activity,
            intent
        )
    ]


def most_common_values(values, limit=8):
    cleaned_values = [
        value
        for value in values
        if value
    ]

    return [
        value
        for value, count in Counter(
            cleaned_values
        ).most_common(
            limit
        )
    ]


def build_activity_summary(activities, intent):
    apps = most_common_values(
        [
            activity["app_display"]
            for activity in activities
        ]
    )

    websites = most_common_values(
        [
            activity["website_display"]
            for activity in activities
        ]
    )

    ocr_snippets = [
        activity["ocr_text"]
        for activity in activities
        if activity["ocr_text"]
    ][:5]

    lines = [
        f"Intent: {intent}",
        f"Matching record count: {len(activities)}",
    ]

    if apps:
        lines.append(
            "Apps: "
            + ", ".join(
                apps
            )
        )

    if websites:
        lines.append(
            "Websites: "
            + ", ".join(
                websites
            )
        )

    if ocr_snippets:
        lines.append(
            "Recent OCR text:"
        )

        for snippet in ocr_snippets:
            lines.append(
                "- "
                + snippet[:300]
            )

    return "\n".join(
        lines
    )
