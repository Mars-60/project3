# test_ocr_data.py

import sqlite3

conn = sqlite3.connect("data/activity.db")

cursor = conn.cursor()

cursor.execute("""
SELECT
    id,
    timestamp,
    app_name,
    substr(ocr_text, 1, 150)
FROM activity_logs
WHERE ocr_text IS NOT NULL
AND trim(ocr_text) != ''
ORDER BY id DESC
LIMIT 10
""")

rows = cursor.fetchall()

print("OCR RECORDS:", len(rows))

for row in rows:
    print("\n----------------")
    print(row)

conn.close()