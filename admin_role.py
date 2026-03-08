import psycopg2
import os
from werkzeug.security import generate_password_hash

DATABASE_URL = os.environ.get("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

password_hash = generate_password_hash("1234")

cur.execute("""
INSERT INTO users (username, password_hash, role)
VALUES (%s, %s, %s)
""", ('admin', password_hash, 'admin'))

conn.commit()
cur.close()
conn.close()

print("✅ สร้าง admin ได้แล้ว")