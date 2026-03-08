import psycopg2
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# เพิ่ม column ถ้ายังไม่มี
cur.execute("""
ALTER TABLE parcels
ADD COLUMN IF NOT EXISTS access_token TEXT;
""")

print("✅ ตรวจสอบ column access_token แล้ว")

# สร้าง unique index ถ้ายังไม่มี
cur.execute("""
CREATE UNIQUE INDEX IF NOT EXISTS idx_access_token
ON parcels(access_token);
""")

print("✅ ตรวจสอบ UNIQUE INDEX แล้ว")

conn.commit()
cur.close()
conn.close()

print("🎉 เสร็จเรียบร้อย!")