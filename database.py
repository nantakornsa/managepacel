import psycopg2
import os

conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="teen1234",
    port="5432"
)

print("Connected successfully")

cur = conn.cursor()
cur.execute('''
-- ตารางลูกค้า (ผู้ส่ง)
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    address TEXT
);

-- ตารางผู้รับ
CREATE TABLE IF NOT EXISTS receivers (
    receiver_id SERIAL PRIMARY KEY,
    receiver_name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    address TEXT
);

-- ตารางพัสดุ
CREATE TABLE IF NOT EXISTS parcels (
    parcel_id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    tracking_number TEXT UNIQUE NOT NULL,
    weight REAL,
    size TEXT,
    destination TEXT,
    current_status_id INTEGER,
    current_center_id INTEGER,
    FOREIGN KEY (sender_id) REFERENCES customers(customer_id),
    FOREIGN KEY (receiver_id) REFERENCES receivers(receiver_id),
    FOREIGN KEY (current_status_id) REFERENCES parcel_status(status_id),
    FOREIGN KEY (current_center_id) REFERENCES sorting_centers(center_id)
);

-- ตารางคนขับ
CREATE TABLE IF NOT EXISTS drivers (
    driver_id SERIAL PRIMARY KEY,
    driver_name TEXT NOT NULL,
    phone TEXT,
    license_plate TEXT,
    assigned_center_id INTEGER,
    FOREIGN KEY (assigned_center_id) REFERENCES sorting_centers(center_id)
);

-- ตารางศูนย์คัดแยก
CREATE TABLE IF NOT EXISTS sorting_centers (
    center_id SERIAL PRIMARY KEY,
    center_name TEXT NOT NULL,
    location TEXT
);

-- ตารางสถานะพัสดุ
CREATE TABLE IF NOT EXISTS parcel_status (
    status_id SERIAL PRIMARY KEY,
    status_name TEXT NOT NULL
);

-- ตารางบันทึกเหตุการณ์ (Tracking Event)
CREATE TABLE IF NOT EXISTS tracking_events (
    event_id SERIAL PRIMARY KEY,
    parcel_id INTEGER NOT NULL,
    status_id INTEGER NOT NULL,
    center_id INTEGER,
    driver_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    note TEXT,
    updated_by TEXT,
    updated_role TEXT,
    FOREIGN KEY (parcel_id) REFERENCES parcels(parcel_id),
    FOREIGN KEY (status_id) REFERENCES parcel_status(status_id),
    FOREIGN KEY (center_id) REFERENCES sorting_centers(center_id),
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
);

CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user'
);
''')

conn.commit()
cur.close()
conn.close()

print("✅ สร้างฐานข้อมูลเรียบร้อยแล้ว!")