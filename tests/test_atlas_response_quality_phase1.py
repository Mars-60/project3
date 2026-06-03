from backend.retrieval.activity_normalizer import (
    filter_activities_by_intent,
    normalize_activity,
    normalize_app_name,
    normalize_website_name
)

from backend.retrieval.query_intent import (
    detect_query_intent
)


def test_detects_app_intent_variations():
    assert detect_query_intent(
        "What apps did I use today?"
    ) == "apps"
    assert detect_query_intent(
        "What software was I using?"
    ) == "apps"
    assert detect_query_intent(
        "What programs did I open?"
    ) == "apps"


def test_detects_ocr_screen_intent():
    assert detect_query_intent(
        "What was on my screen?"
    ) == "ocr"
    assert detect_query_intent(
        "What was I reading?"
    ) == "ocr"
    assert detect_query_intent(
        "What was visible recently?"
    ) == "ocr"


def test_normalizes_apps_and_websites():
    assert normalize_app_name(
        "chrome.exe"
    ) == "Google Chrome"
    assert normalize_app_name(
        "Code.exe"
    ) == "Visual Studio Code"
    assert normalize_website_name(
        "https://leetcode.com/"
    ) == "LeetCode"
    assert normalize_website_name(
        "https://github.com/example/project"
    ) == "GitHub"


def test_ocr_intent_filters_to_ocr_records():
    activities = [
        normalize_activity(
            (
                1,
                "2026-06-03T10:00:00",
                "Code.exe",
                "VS Code",
                None,
                "visible editor text",
                None,
                "ocr"
            )
        ),
        normalize_activity(
            (
                2,
                "2026-06-03T10:01:00",
                "chrome.exe",
                "LeetCode",
                "https://leetcode.com/",
                None,
                "browser",
                "browser_extension"
            )
        ),
    ]

    matching_activities = filter_activities_by_intent(
        activities,
        "ocr"
    )

    assert len(
        matching_activities
    ) == 1
    assert matching_activities[0]["ocr_text"] == "visible editor text"
