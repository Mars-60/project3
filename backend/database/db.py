import sqlite3
from pathlib import Path
DATABASE_PATH=Path("data/activity.db")

def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True,exist_ok=True)
    return sqlite3.connect(DATABASE_PATH)

def initialize_database():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""
     CREATE TABLE IF NOT EXISTS activity_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        app_name TEXT NOT NULL,
        window_title TEXT NOT NULL,
        ocr_text TEXT,
        category TEXT,
        source TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def insert_activity(
    timestamp,
    app_name,
    window_title,
    source,
    ocr_text=None
):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO activity_logs
        (
            timestamp,
            app_name,
            window_title,
            ocr_text,
            source
        )
        VALUES (?, ?, ?, ?, ?)
    """,
    (
        timestamp,
        app_name,
        window_title,
        ocr_text,
        source
    ))

    conn.commit()
    conn.close()

def get_all_activities():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""
    SELECT *
    FROM activity_logs
   """)
    
    activities=cursor.fetchall()
    conn.close()
    return activities

def get_recent_activities(limit=20):
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""
    SELECT *
    FROM activity_logs
    ORDER BY id DESC
    LIMIT ?
    """,(limit,))

    activities=cursor.fetchall()
    conn.close()

    return activities