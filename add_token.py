import sqlite3

conn = sqlite3.connect('parcel_management.db')
c = conn.cursor()

try:
    # เพิ่ม column ก่อน (ถ้ายังไม่มี)
    c.execute("ALTER TABLE parcels ADD COLUMN access_token TEXT;")
    print("✅ เพิ่ม column access_token สำเร็จ")
except sqlite3.OperationalError:
    print("⚠️ column access_token มีอยู่แล้ว")

# สร้าง unique index แยก (แทน UNIQUE constraint)
try:
    c.execute("CREATE UNIQUE INDEX idx_access_token ON parcels(access_token);")
    print("✅ สร้าง UNIQUE INDEX สำเร็จ")
except sqlite3.OperationalError:
    print("⚠️ UNIQUE INDEX มีอยู่แล้ว")

conn.commit()
conn.close()

print("🎉 เสร็จเรียบร้อย!")