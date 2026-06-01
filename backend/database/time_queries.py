from backend.database.db import (
    get_connection
)


def get_activities_between(
    start_time,
    end_time
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM activity_logs
        WHERE timestamp
        BETWEEN ? AND ?
        ORDER BY timestamp DESC
        """,
        (
            start_time,
            end_time
        )
    )

    activities = cursor.fetchall()

    conn.close()

    return activities