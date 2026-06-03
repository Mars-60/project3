
import sqlite3

conn = sqlite3.connect("data/activity.db")

cursor = conn.cursor()

cursor.execute("""
SELECT COUNT(*)
FROM activity_logs
WHERE source='ocr'
""")

print(cursor.fetchone())

conn.close()