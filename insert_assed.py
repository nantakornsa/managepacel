import sqlite3

# เชื่อมต่อฐานข้อมูล
conn = sqlite3.connect("parcel_management.db")
cursor = conn.cursor()

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