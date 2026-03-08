import psycopg2
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

try:
    # เพิ่มคอลัมน์ access_token
    cur.execute("""
        ALTER TABLE parcels 
        ADD COLUMN access_token TEXT
    """)

    print("✅ เพิ่มคอลัมน์ access_token สำเร็จ")

except Exception as e:
    print("❌ Error:", e)

# บันทึกและปิด
conn.commit()
cur.close()
conn.close()