import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("parcel_management.db")
c = conn.cursor()

username = "admin"
password = "admin123"

password_hash = generate_password_hash(password)

c.execute("""
INSERT INTO users (username, password_hash, role)
VALUES (?, ?, ?)
""", (username, password_hash, "admin"))

conn.commit()
conn.close()

print("✅ เพิ่ม admin สำเร็จ")