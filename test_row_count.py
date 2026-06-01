import sqlite3

conn = sqlite3.connect(
    "data/activity.db"
)

cursor = conn.cursor()

cursor.execute("""
SELECT COUNT(*)
FROM activity_logs
""")

print(
    "TOTAL ROWS:",
    cursor.fetchone()[0]
)

cursor.execute("""
SELECT *
FROM activity_logs
ORDER BY id DESC
LIMIT 10
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()