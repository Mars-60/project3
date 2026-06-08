from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta

from backend.database.db import (
    insert_activity,
    get_connection,
    get_recent_activities
)

app = Flask(__name__)
CORS(app)

# ── Shared lookup tables ──────────────────────────────────────────────────────

SKIP_URLS_GLOBAL = (
    "chrome://", "chrome-extension://",
    "file:///", "edge://", "about:",
    "127.0.0.1", "localhost",
)

APP_NAMES_GLOBAL = {
    "chrome.exe": "Chrome",
    "msedge.exe": "Edge",
    "firefox.exe": "Firefox",
    "code.exe": "VS Code",
    "spotify.exe": "Spotify",
    "whatsapp.root.exe": "WhatsApp",
    "whatsapp.exe": "WhatsApp",
    "chatgpt.exe": "ChatGPT",
    "discord.exe": "Discord",
    "explorer.exe": "File Explorer",
    "notepad.exe": "Notepad",
    "notepad++.exe": "Notepad++",
    "teams.exe": "Microsoft Teams",
    "slack.exe": "Slack",
    "zoom.exe": "Zoom",
    "obsidian.exe": "Obsidian",
    "notion.exe": "Notion",
    "linkedin.exe": "LinkedIn",
    "vlc.exe": "VLC",
    "powershell.exe": "PowerShell",
    "cmd.exe": "Command Prompt",
    "windowsterminal.exe": "Terminal",
    "lockapp.exe": "Lock Screen",
    "snippingtool.exe": "Snipping Tool",
    "mspaint.exe": "Paint",
    "winrar.exe": "WinRAR",
    "7zfm.exe": "7-Zip",
    "taskmgr.exe": "Task Manager",
    "calculator.exe": "Calculator",
}

APP_ICONS_GLOBAL = {
    "Chrome": "🌐", "Edge": "🌐", "Firefox": "🦊", "VS Code": "💻",
    "Spotify": "🎵", "WhatsApp": "💬", "ChatGPT": "🤖", "Discord": "💬",
    "File Explorer": "📁", "Notepad": "📝", "Notepad++": "📝",
    "Microsoft Teams": "👥", "Slack": "💬", "Zoom": "📹",
    "Obsidian": "🗒️", "Notion": "📋", "LinkedIn": "💼", "VLC": "🎬",
    "PowerShell": "⬛", "Terminal": "⬛", "Command Prompt": "⬛",
    "Lock Screen": "🔒", "Snipping Tool": "✂️", "Paint": "🎨",
    "WinRAR": "📦", "7-Zip": "📦", "Task Manager": "📊", "Calculator": "🔢",
}

# Maps second-level domain names → display names
# Covers both exact and subdomain matches
SITE_NAMES_GLOBAL = {
    "leetcode.com": "LeetCode",
    "github.com": "GitHub",
    "youtube.com": "YouTube",
    "codeforces.com": "Codeforces",
    "codechef.com": "CodeChef",
    "claude.ai": "Claude",
    "chatgpt.com": "ChatGPT",
    "openai.com": "ChatGPT",
    "google.com": "Google",
    "google.co.in": "Google",
    "withgoogle.com": "Google",      # rsvp.withgoogle.com, pair.withgoogle.com
    "googleapis.com": "Google",
    "stackoverflow.com": "Stack Overflow",
    "linkedin.com": "LinkedIn",
    "twitter.com": "Twitter",
    "x.com": "Twitter/X",
    "reddit.com": "Reddit",
    "notion.so": "Notion",
    "docs.google.com": "Google Docs",
    "drive.google.com": "Google Drive",
    "mail.google.com": "Gmail",
    "calendar.google.com": "Google Calendar",
    "sheets.google.com": "Google Sheets",
    "netflix.com": "Netflix",
    "spotify.com": "Spotify Web",
    "kaggle.com": "Kaggle",
    "geeksforgeeks.org": "GeeksForGeeks",
    "hackerrank.com": "HackerRank",
    "medium.com": "Medium",
    "dev.to": "Dev.to",
    "npmjs.com": "npm",
    "pypi.org": "PyPI",
    "wikipedia.org": "Wikipedia",
    "glassdoor.com": "Glassdoor",
    "naukri.com": "Naukri",
    "internshala.com": "Internshala",
    "unstop.com": "Unstop",
    "hackerearth.com": "HackerEarth",
    "atcoder.jp": "AtCoder",
    "codingninjas.com": "Coding Ninjas",
    "amazon.in": "Amazon",
    "amazon.com": "Amazon",
    "flipkart.com": "Flipkart",
    "anthropic.com": "Anthropic",
    "microsoft.com": "Microsoft",
    "apple.com": "Apple",
    "codolio.com": "Codolio",
    "support.google.com": "Google Support",
}

# Window titles to skip — only true browser noise, not page names
SKIP_TITLES = {
    "new tab", "newtab", "",
}


def normalize_app(raw_name):
    """Convert exe name to human display name."""
    if not raw_name:
        return "Unknown"
    return APP_NAMES_GLOBAL.get(raw_name.lower(), raw_name)


def normalize_site(url, window_title=""):
    """
    Convert a URL to a clean website display name.
    Returns empty string for internal/system URLs that should be skipped.
    """
    from urllib.parse import urlparse

    if not url:
        return ""

    # Skip system/internal URLs
    if any(url.startswith(s) for s in SKIP_URLS_GLOBAL):
        return ""

    # Skip if window title is noise
    if window_title and window_title.lower().strip() in SKIP_TITLES:
        return ""

    try:
        parsed = urlparse(url)
        full_domain = (parsed.netloc or "").lower()
        if not full_domain:
            return ""

        # Strip port
        full_domain = full_domain.split(":")[0]

        # Strip www.
        if full_domain.startswith("www."):
            full_domain = full_domain[4:]

        # Try exact match first
        if full_domain in SITE_NAMES_GLOBAL:
            return SITE_NAMES_GLOBAL[full_domain]

        # Try suffix match (handles subdomains)
        for known, name in SITE_NAMES_GLOBAL.items():
            if full_domain.endswith("." + known) or full_domain == known:
                return name

        # Fallback: use the REGISTERED domain (second-to-last part before TLD)
        # e.g. rsvp.withgoogle.com → withgoogle
        #      chat.openai.com → openai
        #      www.codeforces.com → codeforces
        parts = full_domain.split(".")
        if len(parts) >= 2:
            # Use second-to-last part (registered domain name)
            registered = parts[-2]
            # Skip if too short or numeric (e.g. 127 from 127.0.0.1)
            if len(registered) > 2 and not registered.isdigit():
                return registered.replace("-", " ").title()

        return ""

    except Exception:
        return ""



# ── Browser collector ─────────────────────────────────────────────────────────
@app.route("/browser_activity", methods=["POST"])
def browser_activity():
    try:
        data = request.json
        insert_activity(
            timestamp=datetime.now().isoformat(),
            app_name="chrome.exe",
            window_title=data["title"],
            url=data["url"],
            source="browser_extension",
            category="browser"
        )
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ── Chat ──────────────────────────────────────────────────────────────────────
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json or {}
        question = data.get("question")
        if not question:
            return jsonify({"status": "error", "message": "question is required"}), 400

        from backend.agents.unified_memory_agent import answer_memory_question
        answer = answer_memory_question(question)
        return jsonify({"status": "success", "answer": answer})
    except Exception as e:
        print("CHAT ERROR:", e)
        return jsonify({"status": "error", "message": str(e)}), 500


# ── Basic stats ───────────────────────────────────────────────────────────────
@app.route("/stats")
def stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM activity_logs")
    total_logs = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT app_name) FROM activity_logs")
    unique_apps = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT DATE(timestamp)) FROM activity_logs")
    memory_days = cursor.fetchone()[0]
    conn.close()
    return jsonify({"logs": total_logs, "apps": unique_apps, "days": memory_days})


# ── Recent logs ───────────────────────────────────────────────────────────────
@app.route("/recent", methods=["GET"])
def recent():
    """
    Returns activity logs with normalized app names and site names.
    Schema: id(0),timestamp(1),app_name(2),window_title(3),
            ocr_text(4),category(5),source(6),url(7)
    """
    try:
        limit = request.args.get("limit", 150, type=int)
        activities = get_recent_activities(limit)
        result = []
        for row in activities:
            app_raw      = row[2] or ""
            app_display  = normalize_app(app_raw)
            app_icon_v   = APP_ICONS_GLOBAL.get(app_display, "⚙️")
            url          = row[7] or ""
            window_title = row[3] or ""
            site_display = normalize_site(url, window_title)

            result.append({
                "id":           row[0],
                "timestamp":    row[1],
                "app_raw":      app_raw,
                "app_display":  app_display,
                "app_icon":     app_icon_v,
                "window_title": window_title,
                "ocr_text":     row[4],
                "category":     row[5],
                "source":       row[6],
                "url":          url if not any(url.startswith(s) for s in SKIP_URLS_GLOBAL) else "",
                "site_display": site_display,
            })
        return jsonify({"activities": result})
    except Exception as e:
        print("RECENT ERROR:", e)
        return jsonify({"activities": []})


# ── Duration-aware dashboard stats ───────────────────────────────────────────
@app.route("/dashboard_stats", methods=["GET"])
def dashboard_stats():
    """
    Returns per-app and per-website duration data for a date range.
    Query params:
      date  = YYYY-MM-DD  (default: today)
      range = today | yesterday | week  (default: today)
    """
    try:
        range_param = request.args.get("range", "today")
        now = datetime.now()

        if range_param == "yesterday":
            day = now - timedelta(days=1)
            start = day.strftime("%Y-%m-%d") + "T00:00:00"
            end   = day.strftime("%Y-%m-%d") + "T23:59:59"
            label = "Yesterday"
        elif range_param == "week":
            start = (now - timedelta(days=6)).strftime("%Y-%m-%d") + "T00:00:00"
            end   = now.strftime("%Y-%m-%d") + "T23:59:59"
            label = "Last 7 days"
        else:
            start = now.strftime("%Y-%m-%d") + "T00:00:00"
            end   = now.strftime("%Y-%m-%d") + "T23:59:59"
            label = "Today"

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM activity_logs WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp ASC",
            (start, end)
        )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return jsonify({
                "label": label,
                "total_seconds": 0,
                "apps": [],
                "websites": [],
                "hourly": []
            })

        DEFAULT_SESSION = 5 * 60  # 5 minutes
        MAX_SESSION = 7200         # cap at 2 hours

        # Compute durations
        sessions = []
        for i, row in enumerate(rows):
            ts_str = row[1]
            try:
                start_dt = datetime.fromisoformat(ts_str)
            except Exception:
                continue

            if i + 1 < len(rows):
                try:
                    next_dt = datetime.fromisoformat(rows[i+1][1])
                    gap = (next_dt - start_dt).total_seconds()
                    duration = min(max(gap, 0), MAX_SESSION)
                except Exception:
                    duration = DEFAULT_SESSION
            else:
                duration = DEFAULT_SESSION

            # Use shared normalization functions defined at module level
            url         = row[7] or ""
            window_title_r = row[3] or ""
            app_display = normalize_app(row[2])
            site_display = normalize_site(url, window_title_r)

            sessions.append({
                "app":      app_display,
                "site":     site_display,
                "url":      url,
                "start_dt": start_dt,
                "duration": duration,
            })

        # Aggregate apps
        from collections import defaultdict
        app_totals = defaultdict(float)
        for s in sessions:
            app_totals[s["app"]] += s["duration"]

        apps_sorted = sorted(
            [{"name": k, "seconds": int(v)} for k, v in app_totals.items()],
            key=lambda x: x["seconds"], reverse=True
        )[:8]

        # Aggregate websites
        site_totals = defaultdict(float)
        for s in sessions:
            if s["site"]:
                site_totals[s["site"]] += s["duration"]

        sites_sorted = sorted(
            [{"name": k, "seconds": int(v)} for k, v in site_totals.items()],
            key=lambda x: x["seconds"], reverse=True
        )[:8]

        # Hourly breakdown (for bar chart)
        hourly = defaultdict(float)
        for s in sessions:
            hour = s["start_dt"].hour
            hourly[hour] += s["duration"]

        hourly_list = [
            {"hour": h, "seconds": int(hourly.get(h, 0))}
            for h in range(24)
        ]

        total_seconds = int(sum(s["duration"] for s in sessions))

        return jsonify({
            "label": label,
            "total_seconds": total_seconds,
            "apps": apps_sorted,
            "websites": sites_sorted,
            "hourly": hourly_list,
        })

    except Exception as e:
        print("DASHBOARD STATS ERROR:", e)
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)