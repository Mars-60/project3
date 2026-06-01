import sqlite3

conn = sqlite3.connect(
    "data/activity.db"
)

cursor = conn.cursor()

cursor.execute("""
SELECT
    window_title,
    url,
    source
FROM activity_logs
WHERE source='browser_extension'
ORDER BY id DESC
LIMIT 10
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()