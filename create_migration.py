import sqlite3

conn = sqlite3.connect(
    "data/activity.db"
)

cursor = conn.cursor()

try:
    cursor.execute("""
        ALTER TABLE activity_logs
        ADD COLUMN url TEXT
    """)

    conn.commit()

    print(
        "URL column added successfully."
    )

except Exception as e:
    print(
        "Migration Error:"
    )

    print(e)

conn.close()