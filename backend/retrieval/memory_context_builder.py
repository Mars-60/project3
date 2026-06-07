"""
memory_context_builder.py

Builds a rich, duration-aware context package for the AI.
Instead of raw event lists, it computes:
  - How long each app/website session lasted
  - Grouped sessions (consecutive same-app runs merged)
  - A human-readable timeline with durations
  - What the user was doing on each app (window titles / OCR)
"""

from datetime import datetime, timedelta
from collections import defaultdict
from backend.retrieval.activity_normalizer import normalize_activities


# ── Constants ────────────────────────────────────────────────────────────────
MAX_PDF_EXCERPTS = 4
PDF_EXCERPT_LENGTH = 500
OCR_SNIPPET_LENGTH = 350
# If no next event, assume the session lasted this many minutes
DEFAULT_SESSION_MINUTES = 5


# ── Helpers ──────────────────────────────────────────────────────────────────

def parse_ts(ts_str):
    """Parse ISO timestamp string to datetime."""
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str)
    except Exception:
        return None


def fmt_time(dt):
    """Format datetime to '10:30 AM'."""
    if not dt:
        return "?"
    return dt.strftime("%I:%M %p").lstrip("0")


def fmt_duration(seconds):
    """Format seconds into human-readable duration."""
    if seconds < 60:
        return f"{int(seconds)}s"
    minutes = int(seconds / 60)
    if minutes < 60:
        return f"{minutes} min"
    hours = minutes // 60
    mins = minutes % 60
    if mins == 0:
        return f"{hours} hr"
    return f"{hours} hr {mins} min"


def compact_text(text, limit):
    t = " ".join((text or "").split())
    return t if len(t) <= limit else t[:limit].rstrip() + "..."


# ── Duration computation ──────────────────────────────────────────────────────

def compute_sessions(activities):
    """
    Given a list of normalized activity dicts (sorted oldest→newest),
    compute duration for each by looking at the next event's timestamp.

    Returns list of session dicts:
      {
        app, title, url, website, source, ocr_text,
        start_dt, end_dt, duration_seconds
      }
    """
    # Sort oldest first so we can compute gaps
    sorted_acts = sorted(
        activities,
        key=lambda a: parse_ts(a["timestamp"]) or datetime.min
    )

    sessions = []
    for i, act in enumerate(sorted_acts):
        start_dt = parse_ts(act["timestamp"])
        if start_dt is None:
            continue

        # Duration = gap to next event
        if i + 1 < len(sorted_acts):
            next_dt = parse_ts(sorted_acts[i + 1]["timestamp"])
            if next_dt and next_dt > start_dt:
                gap = (next_dt - start_dt).total_seconds()
                # Cap individual session at 2 hours (7200s) to avoid
                # counting idle time as usage
                duration = min(gap, 7200)
            else:
                duration = DEFAULT_SESSION_MINUTES * 60
        else:
            duration = DEFAULT_SESSION_MINUTES * 60

        sessions.append({
            "app": act["app_display"],
            "title": act["window_title"] or "",
            "url": act["url"] or "",
            "website": act["website_display"] or "",
            "source": act["source"] or "",
            "ocr_text": act["ocr_text"] or "",
            "start_dt": start_dt,
            "end_dt": start_dt + timedelta(seconds=duration),
            "duration_seconds": duration,
        })

    return sessions


def merge_sessions(sessions):
    """
    Merge consecutive sessions of the same app+title into one.
    This collapses repeated window switches back to the same tab.
    """
    if not sessions:
        return []

    merged = []
    current = dict(sessions[0])

    for s in sessions[1:]:
        same_app = s["app"] == current["app"]
        same_title = s["title"] == current["title"]
        # Merge if same app+title and gap < 5 minutes
        gap = (s["start_dt"] - current["end_dt"]).total_seconds()
        if same_app and same_title and gap < 300:
            current["end_dt"] = s["end_dt"]
            current["duration_seconds"] += s["duration_seconds"]
            if s["ocr_text"] and not current["ocr_text"]:
                current["ocr_text"] = s["ocr_text"]
        else:
            merged.append(current)
            current = dict(s)

    merged.append(current)
    return merged


# ── App / Website aggregation ─────────────────────────────────────────────────

def aggregate_by_app(sessions):
    """
    Returns list of:
      { app, total_seconds, first_seen, last_seen, titles }
    sorted by total time descending.
    """
    app_data = defaultdict(lambda: {
        "total_seconds": 0,
        "first_seen": None,
        "last_seen": None,
        "titles": set(),
    })

    for s in sessions:
        key = s["app"]
        d = app_data[key]
        d["total_seconds"] += s["duration_seconds"]
        if d["first_seen"] is None or s["start_dt"] < d["first_seen"]:
            d["first_seen"] = s["start_dt"]
        if d["last_seen"] is None or s["end_dt"] > d["last_seen"]:
            d["last_seen"] = s["end_dt"]
        if s["title"]:
            d["titles"].add(s["title"])

    result = []
    for app, d in app_data.items():
        result.append({
            "app": app,
            "total_seconds": d["total_seconds"],
            "first_seen": d["first_seen"],
            "last_seen": d["last_seen"],
            "titles": list(d["titles"]),
        })

    return sorted(result, key=lambda x: x["total_seconds"], reverse=True)


def aggregate_by_website(sessions):
    """
    Returns list of website usage with durations.
    Only browser sessions with a known website.
    """
    site_data = defaultdict(lambda: {
        "total_seconds": 0,
        "first_seen": None,
        "last_seen": None,
        "titles": set(),
    })

    for s in sessions:
        if not s["website"]:
            continue
        key = s["website"]
        d = site_data[key]
        d["total_seconds"] += s["duration_seconds"]
        if d["first_seen"] is None or s["start_dt"] < d["first_seen"]:
            d["first_seen"] = s["start_dt"]
        if d["last_seen"] is None or s["end_dt"] > d["last_seen"]:
            d["last_seen"] = s["end_dt"]
        if s["title"]:
            d["titles"].add(s["title"])

    result = []
    for site, d in site_data.items():
        result.append({
            "site": site,
            "total_seconds": d["total_seconds"],
            "first_seen": d["first_seen"],
            "last_seen": d["last_seen"],
            "titles": list(d["titles"]),
        })

    return sorted(result, key=lambda x: x["total_seconds"], reverse=True)


# ── Section builders ──────────────────────────────────────────────────────────

def build_app_usage_section(app_agg):
    """Human-readable app usage with durations and time ranges."""
    if not app_agg:
        return ["- No app usage recorded"]

    lines = []
    for a in app_agg[:10]:
        dur = fmt_duration(a["total_seconds"])
        start = fmt_time(a["first_seen"])
        end = fmt_time(a["last_seen"])
        line = f"- {a['app']}: {dur} (from {start} to {end})"

        # Add what they were doing (unique titles, max 3)
        unique_titles = list(dict.fromkeys(
            t for t in a["titles"]
            if t and t.lower() not in ("new tab", "")
        ))[:3]
        if unique_titles:
            line += "\n  What: " + " | ".join(unique_titles)
        lines.append(line)

    return lines


def build_website_usage_section(site_agg):
    """Human-readable website usage with durations."""
    if not site_agg:
        return ["- No website activity recorded"]

    lines = []
    for s in site_agg[:10]:
        dur = fmt_duration(s["total_seconds"])
        start = fmt_time(s["first_seen"])
        end = fmt_time(s["last_seen"])
        line = f"- {s['site']}: {dur} (from {start} to {end})"

        unique_titles = list(dict.fromkeys(
            t for t in s["titles"]
            if t and t.lower() not in ("new tab", "")
        ))[:3]
        if unique_titles:
            line += "\n  Pages visited: " + " | ".join(unique_titles)
        lines.append(line)

    return lines


def build_timeline_section(merged_sessions):
    """
    Chronological timeline with duration for every session.
    Groups short sessions of same app together.
    """
    if not merged_sessions:
        return ["- No activity recorded"]

    lines = []
    for s in merged_sessions:
        dur = fmt_duration(s["duration_seconds"])
        start = fmt_time(s["start_dt"])
        app = s["app"]
        title = s["title"]

        # Skip very short noise (< 10 seconds)
        if s["duration_seconds"] < 10:
            continue

        if title and title.lower() != "new tab":
            line = f"- {start}: {app} — {title} ({dur})"
        else:
            line = f"- {start}: {app} ({dur})"

        # Add OCR hint if available
        if s["ocr_text"]:
            snippet = compact_text(s["ocr_text"], 120)
            line += f"\n  Screen: {snippet}"

        lines.append(line)

    return lines if lines else ["- No significant activity recorded"]


def build_ocr_section(sessions):
    """What was visible on screen (from OCR sessions)."""
    lines = []
    seen = set()
    for s in sessions:
        if not s["ocr_text"]:
            continue
        snippet = compact_text(s["ocr_text"], OCR_SNIPPET_LENGTH)
        if snippet in seen:
            continue
        seen.add(snippet)
        start = fmt_time(s["start_dt"])
        lines.append(f"- [{start}] {s['app']}: {snippet}")
        if len(lines) >= 6:
            break
    return lines if lines else ["- No OCR data"]


def build_pdf_section(pdf_context):
    lines = []
    for chunk in pdf_context[:MAX_PDF_EXCERPTS]:
        source = f"{chunk['file_name']} (pages {chunk['page_start']}-{chunk['page_end']})"
        text = compact_text(chunk["text"], PDF_EXCERPT_LENGTH)
        lines.append(f"- {source}:\n  {text}")
    return lines if lines else ["- No PDF activity"]


# ── Main entry point ──────────────────────────────────────────────────────────

def build_memory_context(memory_package):
    raw_activities = memory_package["activities"]
    pdf_context = memory_package["pdf_context"]
    time_range = memory_package["time_range"]

    if not raw_activities:
        return (
            f"Memory Context Package\n\n"
            f"Time Range: {time_range['label']}\n"
            f"No activity was recorded for this time period."
        )

    # Normalize and compute sessions
    activities = normalize_activities(raw_activities)
    sessions = compute_sessions(activities)
    merged = merge_sessions(sessions)

    # Aggregations
    app_agg = aggregate_by_app(sessions)
    site_agg = aggregate_by_website(sessions)

    # Compute total screen time
    total_seconds = sum(s["duration_seconds"] for s in merged)

    lines = [
        "Memory Context Package",
        "",
        f"Time Range: {time_range['label']}",
        f"Total screen time: {fmt_duration(total_seconds)}",
        f"Activity records: {len(raw_activities)}",
        "",

        "── App Usage (with duration) ──",
        *build_app_usage_section(app_agg),
        "",

        "── Website Usage (with duration) ──",
        *build_website_usage_section(site_agg),
        "",

        "── Full Timeline (chronological) ──",
        *build_timeline_section(merged),
        "",

        "── Screen Content (OCR) ──",
        *build_ocr_section(sessions),
    ]

    if pdf_context:
        lines += [
            "",
            "── PDF Content (opened this period) ──",
            *build_pdf_section(pdf_context),
        ]

    return "\n".join(lines)