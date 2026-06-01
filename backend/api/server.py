from flask import Flask, request, jsonify
from flask_cors import CORS

from backend.database.db import insert_activity

from datetime import datetime

app = Flask(__name__)

CORS(app)


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


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )