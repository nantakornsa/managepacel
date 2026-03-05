import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('parcel_management.db')
c = conn.cursor()

password_hash = generate_password_hash("1234")

c.execute("""
INSERT INTO users (username, password_hash, role)
VALUES (?, ?, ?)
""", ('admin', password_hash, 'admin'))

conn.commit()
conn.close()

print("✅ สร้าง admin ได้แล้ว")