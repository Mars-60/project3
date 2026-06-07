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
    from urllib.parse import urlparse

    SKIP_URLS = ("chrome://", "file:///", "chrome-extension://",
                 "127.0.0.1", "localhost", "edge://", "about:")

    APP_NAMES_R = {
        "chrome.exe":"Chrome","msedge.exe":"Edge","firefox.exe":"Firefox",
        "code.exe":"VS Code","spotify.exe":"Spotify",
        "whatsapp.root.exe":"WhatsApp","whatsapp.exe":"WhatsApp",
        "chatgpt.exe":"ChatGPT","discord.exe":"Discord",
        "explorer.exe":"File Explorer","notepad.exe":"Notepad",
        "notepad++.exe":"Notepad++","teams.exe":"Microsoft Teams",
        "slack.exe":"Slack","zoom.exe":"Zoom","obsidian.exe":"Obsidian",
        "notion.exe":"Notion","linkedin.exe":"LinkedIn","vlc.exe":"VLC",
        "powershell.exe":"PowerShell","cmd.exe":"Command Prompt",
        "windowsterminal.exe":"Terminal","lockapp.exe":"Lock Screen",
        "snippingtool.exe":"Snipping Tool","mspaint.exe":"Paint",
        "winrar.exe":"WinRAR","7zfm.exe":"7-Zip",
        "taskmgr.exe":"Task Manager","calculator.exe":"Calculator",
    }
    APP_ICONS_R = {
        "Chrome":"🌐","Edge":"🌐","Firefox":"🦊","VS Code":"💻",
        "Spotify":"🎵","WhatsApp":"💬","ChatGPT":"🤖","Discord":"💬",
        "File Explorer":"📁","Notepad":"📝","Notepad++":"📝",
        "Microsoft Teams":"👥","Slack":"💬","Zoom":"📹","Obsidian":"🗒️",
        "Notion":"📋","LinkedIn":"💼","VLC":"🎬","PowerShell":"⬛",
        "Terminal":"⬛","Command Prompt":"⬛","Lock Screen":"🔒",
        "Snipping Tool":"✂️","Paint":"🎨","WinRAR":"📦","7-Zip":"📦",
        "Task Manager":"📊","Calculator":"🔢",
    }
    SITE_NAMES_R = {
        "leetcode.com":"LeetCode","github.com":"GitHub","youtube.com":"YouTube",
        "codeforces.com":"Codeforces","codechef.com":"CodeChef",
        "claude.ai":"Claude","chatgpt.com":"ChatGPT",
        "chat.openai.com":"ChatGPT","google.com":"Google",
        "google.co.in":"Google","stackoverflow.com":"Stack Overflow",
        "linkedin.com":"LinkedIn","twitter.com":"Twitter","x.com":"Twitter/X",
        "reddit.com":"Reddit","notion.so":"Notion","medium.com":"Medium",
        "geeksforgeeks.org":"GeeksForGeeks","hackerrank.com":"HackerRank",
        "kaggle.com":"Kaggle","wikipedia.org":"Wikipedia",
        "hackerearth.com":"HackerEarth","atcoder.jp":"AtCoder",
        "unstop.com":"Unstop","internshala.com":"Internshala",
        "glassdoor.com":"Glassdoor","naukri.com":"Naukri",
        "amazon.in":"Amazon","amazon.com":"Amazon","openai.com":"OpenAI",
        "anthropic.com":"Anthropic","docs.google.com":"Google Docs",
        "drive.google.com":"Google Drive","mail.google.com":"Gmail",
    }

    try:
        limit = request.args.get("limit", 150, type=int)
        activities = get_recent_activities(limit)
        result = []
        for row in activities:
            app_raw     = row[2] or ""
            app_display = APP_NAMES_R.get(app_raw.lower(), app_raw)
            app_icon_v  = APP_ICONS_R.get(app_display, "⚙️")
            url         = row[7] or ""
            url_is_real = url and not any(url.startswith(s) for s in SKIP_URLS)

            site_display = ""
            if url_is_real:
                try:
                    parsed = urlparse(url)
                    domain = (parsed.netloc or "").lower()
                    if domain.startswith("www."): domain = domain[4:]
                    domain = domain.split(":")[0]
                    for known, name in SITE_NAMES_R.items():
                        if domain == known or domain.endswith("." + known):
                            site_display = name
                            break
                    if not site_display:
                        parts = domain.split(".")
                        first = parts[0] if parts else ""
                        if len(first) > 1 and not first.isdigit():
                            site_display = first.replace("-", " ").title()
                except Exception:
                    pass

            result.append({
                "id":           row[0],
                "timestamp":    row[1],
                "app_raw":      app_raw,
                "app_display":  app_display,
                "app_icon":     app_icon_v,
                "window_title": row[3],
                "ocr_text":     row[4],
                "category":     row[5],
                "source":       row[6],
                "url":          url if url_is_real else "",
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

            from urllib.parse import urlparse

            # CORRECT column: url is row[7], NOT row[4]
            url = row[7] or ""
            domain = ""

            # Skip internal/system URLs entirely
            SKIP_URLS = ("chrome://", "file:///", "chrome-extension://",
                         "127.0.0.1", "localhost", "edge://", "about:")
            url_is_real = url and not any(url.startswith(s) for s in SKIP_URLS)

            if url_is_real:
                try:
                    parsed = urlparse(url)
                    domain = (parsed.netloc or parsed.path).lower()
                    if domain.startswith("www."):
                        domain = domain[4:]
                    domain = domain.split(":")[0]  # strip port
                except Exception:
                    domain = ""

            SITE_NAMES = {
                "leetcode.com": "LeetCode",
                "github.com": "GitHub",
                "youtube.com": "YouTube",
                "codeforces.com": "Codeforces",
                "codechef.com": "CodeChef",
                "claude.ai": "Claude",
                "chatgpt.com": "ChatGPT",
                "chat.openai.com": "ChatGPT",
                "google.com": "Google",
                "google.co.in": "Google",
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
                "claude.ai": "Claude",
                "anthropic.com": "Anthropic",
                "openai.com": "OpenAI",
            }

            APP_NAMES = {
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

            app_raw = (row[2] or "").lower()
            app_display = APP_NAMES.get(app_raw, row[2] or "Unknown")

            # Resolve site display name
            site_display = ""
            if domain:
                for known, name in SITE_NAMES.items():
                    if domain == known or domain.endswith("." + known):
                        site_display = name
                        break
                if not site_display:
                    # Use first meaningful domain part, skip single-letter or numeric
                    parts = domain.split(".")
                    first = parts[0] if parts else ""
                    if len(first) > 1 and not first.isdigit():
                        site_display = first.replace("-", " ").title()
                    # else skip (too short to be meaningful)

            sessions.append({
                "app": app_display,
                "site": site_display,
                "url": url if url_is_real else "",
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