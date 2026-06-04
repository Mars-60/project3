from flask import Flask, request, jsonify
from flask_cors import CORS

from backend.database.db import insert_activity

from datetime import datetime

app = Flask(__name__)

CORS(app)

from backend.database.db import (
    insert_activity,
    get_connection,
    get_recent_activities
)

@app.route(
    "/browser_activity",
    methods=["POST"]
)
def browser_activity():

    try:

        data = request.json

        print(
            "Received:",
            data
        )

        insert_activity(
            timestamp=datetime.now().isoformat(),
            app_name="chrome.exe",
            window_title=data["title"],
            url=data["url"],
            source="browser_extension",
            category="browser"
        )

        print(
            "Inserted successfully"
        )

        return jsonify(
            {
                "status": "success"
            }
        )

    except Exception as e:

        print(
            "ERROR:",
            e
        )

        return jsonify(
            {
                "status": "error",
                "message": str(e)
            }
        ), 500


@app.route(
    "/chat",
    methods=["POST"]
)
def chat():

    try:

        data = request.json or {}

        question = data.get(
            "question"
        )

        if not question:
            return jsonify(
                {
                    "status": "error",
                    "message": "question is required"
                }
            ), 400

        from backend.agents.unified_memory_agent import (
            answer_memory_question
        )

        answer = answer_memory_question(
            question
        )

        return jsonify(
            {
                "status": "success",
                "answer": answer
            }
        )

    except Exception as e:

        print(
            "CHAT ERROR:",
            e
        )

        return jsonify(
            {
                "status": "error",
                "message": str(e)
            }
        ), 500

@app.route("/stats")
def stats():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM activity_logs"
    )
    total_logs = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(DISTINCT app_name) FROM activity_logs"
    )
    unique_apps = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(DISTINCT DATE(timestamp)) FROM activity_logs"
    )
    memory_days = cursor.fetchone()[0]

    conn.close()

    return jsonify({
        "logs": total_logs,
        "apps": unique_apps,
        "days": memory_days
    })
@app.route("/recent", methods=["GET"])
def recent():
    limit = request.args.get("limit", 60, type=int)
    activities = get_recent_activities(limit)
    return jsonify({"activities": [list(a) for a in activities]})

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
