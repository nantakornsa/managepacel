import psycopg2

import psycopg2
from werkzeug.security import generate_password_hash

DATABASE_URL = "postgresql://parcel_user:lBif77XAZLy40ghsUsRIs4XaC5SMb3RC@dpg-d6mh6rtactks7382o8fg-a.singapore-postgres.render.com/parcel_management"

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

username = "admin1"
password = "admin123"

password_hash = generate_password_hash(password)

cur.execute("""
INSERT INTO users (username, password_hash, role)
VALUES (%s, %s, %s)
""", (username, password_hash, "admin"))

conn.commit()

cur.close()
conn.close()

print("✅ เพิ่ม admin สำเร็จ")