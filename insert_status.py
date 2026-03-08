import psycopg2
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# เพิ่มข้อมูลสถานะเริ่มต้น 3 สถานะ
c.executemany("INSERT INTO parcel_status (status_name) VALUES (?)", [
    ('รับเข้าระบบแล้ว',),
    ('กำลังจัดส่ง',),
    ('จัดส่งสำเร็จ',)
]) 

c.executemany(
    "INSERT INTO sorting_centers (center_name, location) VALUES (?, ?)",
    [
        ('ศูนย์มหาสารคาม', 'มหาสารคาม'),
        ('ศูนย์ขอนแก่น', 'ขอนแก่น'),
        ('ศูนย์กรุงเทพ', 'กรุงเทพ')
    ]
)

conn.commit()
conn.close()

print("✅ เพิ่มข้อมูลสถานะเริ่มต้นเรียบร้อยแล้ว!")