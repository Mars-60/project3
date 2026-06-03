from backend.retrieval.memory_context_builder import (
    build_memory_context
)

from backend.retrieval.memory_retriever import (
    resolve_time_range
)


def test_resolve_time_range_defaults_to_recent_activity():
    time_range = resolve_time_range(
        "What was I focused on?"
    )

    assert time_range == {
        "label": "recent activity",
        "start": None,
        "end": None,
    }


def test_memory_context_builder_includes_all_evidence_types():
    memory_package = {
        "question": "What was I focused on today?",
        "time_range": {
            "label": "today",
            "start": "2026-06-03T00:00:00",
            "end": "2026-06-03T23:59:59",
        },
        "activities": [
            (
                1,
                "2026-06-03T10:00:00",
                "Code.exe",
                "unified_memory_agent.py - Visual Studio Code",
                None,
                None,
                None,
                "window_logger"
            ),
            (
                2,
                "2026-06-03T10:01:00",
                "chrome.exe",
                "GitHub",
                "https://github.com/example/project",
                None,
                "browser",
                "browser_extension"
            ),
            (
                3,
                "2026-06-03T10:02:00",
                "Code.exe",
                "VS Code",
                None,
                "Memory Retrieval V2 implementation notes",
                None,
                "ocr"
            ),
        ],
        "websites": [
            (
                2,
                "2026-06-03T10:01:00",
                "chrome.exe",
                "GitHub",
                "https://github.com/example/project",
                None,
                "browser",
                "browser_extension"
            ),
        ],
        "ocr_records": [
            (
                3,
                "2026-06-03T10:02:00",
                "Code.exe",
                "VS Code",
                None,
                "Memory Retrieval V2 implementation notes",
                None,
                "ocr"
            ),
        ],
        "pdf_context": [
            {
                "file_name": "systems.pdf",
                "page_start": 1,
                "page_end": 2,
                "text": "Operating system process and thread notes."
            }
        ],
    }

    context = build_memory_context(
        memory_package
    )

    assert "Visual Studio Code" in context
    assert "GitHub" in context
    assert "Memory Retrieval V2 implementation notes" in context
    assert "systems.pdf pages 1-2" in context
