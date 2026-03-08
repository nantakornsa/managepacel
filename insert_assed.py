import psycopg2
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

try:
    # เพิ่มคอลัมน์ access_token
    cursor.execute("""
        ALTER TABLE parcels 
        ADD COLUMN access_token TEXT
    """)

    print("✅ เพิ่มคอลัมน์ access_token สำเร็จ")

except sqlite3.OperationalError as e:
    print("❌ Error:", e)

# บันทึกและปิด
conn.commit()
conn.close()