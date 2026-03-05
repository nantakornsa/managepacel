from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
import re
import qrcode
from werkzeug.security import generate_password_hash, check_password_hash
import secrets


app = Flask(__name__)
app.secret_key = 'autoproject2026'  # ใช้ session ต้องมี key


# -----------------------------
# ฟังก์ชันเชื่อมฐานข้อมูล
# -----------------------------
def get_db_connection():
    conn = sqlite3.connect('parcel_management.db')
    conn.row_factory = sqlite3.Row  # ให้ผลลัพธ์อ่านเป็นชื่อคอลัมน์ได้
    return conn


# =============================
# 🔹 ระบบล็อกอินจริง (ใหม่)
# =============================

# หน้าแรก → ถ้าล็อกอินแล้วจะเข้า interface เลย
@app.route('/')
def index():

    if 'user_id' in session:

        if session.get('role') == 'user':
            return redirect(url_for('user_interface'))
        else:
            return redirect(url_for('staff_dashboard'))

    return render_template('index.html')


# สมัครสมาชิก
# สมัครสมาชิก
@app.route('/register.html', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        confirm_password = request.form['confirm_password'].strip()

        # ✅ เช็คกรอกข้อมูลครบไหม
        if not username or not password or not confirm_password:
            flash('กรุณากรอกข้อมูลให้ครบ', 'danger')
            return redirect(url_for('register'))

        # ✅ เช็ครหัสผ่านตรงกันไหม
        if password != confirm_password:
            flash('❌ รหัสผ่านไม่ตรงกัน', 'danger')
            return redirect(url_for('register'))

        # ✅ ความยาวอย่างน้อย 8 ตัว
        if len(password) < 8:
            flash('❌ รหัสผ่านต้องอย่างน้อย 8 ตัวอักษร', 'danger')
            return redirect(url_for('register'))

        # ✅ ต้องมีตัวเลขอย่างน้อย 1 ตัว
        import re
        if not re.search(r'\d', password):
            flash('❌ รหัสผ่านต้องมีตัวเลขอย่างน้อย 1 ตัว', 'danger')
            return redirect(url_for('register'))

        conn = get_db_connection()
        c = conn.cursor()
        password_hash = generate_password_hash(password)

        try:
            c.execute(
                'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                (username, password_hash)
            )
            conn.commit()
            flash('✅ สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ', 'success')
            return redirect(url_for('login'))

        except sqlite3.IntegrityError:
            flash('❌ ชื่อผู้ใช้นี้มีอยู่แล้ว', 'danger')

        finally:
            conn.close()

    return render_template('register.html')


# เข้าสู่ระบบ
@app.route('/login.html', methods=['GET', 'POST'])
def login():

    next_page = request.args.get('next')

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?', 
            (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):

            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']

            flash(f'ยินดีต้อนรับ {user["username"]}', 'success')

            if next_page:
                return redirect(next_page)

            # แยกหน้า user / staff
            if user['role'] == 'user':
                return redirect(url_for('user_interface'))
            else:
                return redirect(url_for('staff_dashboard'))

        else:
            flash('❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง', 'danger')

    return render_template('login.html')


# ออกจากระบบ
@app.route('/logout.html')
def logout():
    session.clear()
    flash('ออกจากระบบเรียบร้อยแล้ว', 'info')
    return redirect(url_for('login'))


# หน้า admin
@app.route('/admin.html')
def admin_panel():

    # 🔐 อนุญาตเฉพาะ admin
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('คุณไม่มีสิทธิ์เข้าหน้านี้', 'danger')
        return redirect(url_for('staff_dashboard'))

    conn = get_db_connection()
    staff = conn.execute("SELECT * FROM users WHERE role = 'staff'").fetchall()
    conn.close()

    return render_template('admin.html', staff=staff)

# หน้า staff
# เพิ่ม
@app.route('/admin/add_staff', methods=['POST'])
def add_staff():

    if session.get('role') != 'admin':
        return redirect(url_for('staff_dashboard'))

    username = request.form['username']
    password = request.form['password']

    conn = get_db_connection()
    c = conn.cursor()

    password_hash = generate_password_hash(password)

    c.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, 'staff')
    )

    conn.commit()
    conn.close()

    flash("เพิ่ม Staff สำเร็จ", "success")
    return redirect(url_for('admin_panel'))

# ลบ
@app.route('/admin/delete/<int:user_id>')
def delete_staff(user_id):

    if session.get('role') != 'admin':
        return redirect(url_for('staff_dashboard'))

    conn = get_db_connection()
    conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

    flash("ลบ Staff สำเร็จ", "info")
    return redirect(url_for('admin_panel'))


# -----------------------------
# หน้า interface (หลังล็อกอิน)
# -----------------------------

#หน้า user
@app.route('/user')
def user_interface():

    if 'user_id' not in session:
        flash('กรุณาเข้าสู่ระบบก่อน', 'warning')
        return redirect(url_for('login'))

    if session.get('role') != 'user':
        return redirect(url_for('staff_dashboard'))

    conn = get_db_connection()
    c = conn.cursor()

    query = '''
    SELECT 
        p.tracking_number,
        p.destination,
        p.weight,
        p.size,
        ps.status_name
    FROM parcels p
    LEFT JOIN parcel_status ps 
    ON p.current_status_id = ps.status_id
    WHERE p.sender_id = ?
    ORDER BY p.parcel_id DESC
    '''

    parcels = c.execute(query,(session['user_id'],)).fetchall()
    conn.close()

    return render_template(
        'interface_user.html',
        parcels=parcels
    )
    
# staff
@app.route('/staff_dashboard')
def staff_dashboard():

    if 'user_id' not in session:
        flash('กรุณาเข้าสู่ระบบก่อน', 'warning')
        return redirect(url_for('login'))
    
    if session.get('role') not in ['admin','staff']:
        flash('คุณไม่มีสิทธิ์เข้าหน้านี้', 'danger')
        return redirect(url_for('user_interface'))

    conn = get_db_connection()
    c = conn.cursor()

    query = '''
    SELECT 
        p.parcel_id,
        p.tracking_number,
        p.destination,
        p.weight,
        p.size,
        s.customer_name AS sender_name,
        r.receiver_name AS receiver_name,
        ps.status_name AS status_name
    FROM parcels p
    JOIN customers s ON p.sender_id = s.customer_id
    JOIN receivers r ON p.receiver_id = r.receiver_id
    LEFT JOIN parcel_status ps ON p.current_status_id = ps.status_id
    ORDER BY p.parcel_id DESC;
    '''

    parcels = c.execute(query).fetchall()
    conn.close()

    return render_template(
    'staff_dashboard.html',
    parcels=parcels
)

# -----------------------------
# สร้าง Tracking Number อัตโนมัติ
# -----------------------------
def generate_tracking_number():
    conn = get_db_connection()

    last = conn.execute(
        "SELECT tracking_number FROM parcels ORDER BY parcel_id DESC LIMIT 1"
    ).fetchone()

    conn.close()

    if last and last["tracking_number"]:
        try:
            last_number = int(last["tracking_number"][3:])
        except:
            last_number = 0
        new_number = last_number + 1
    else:
        new_number = 1

    return f"SF{new_number:06d}"

# -----------------------------
# หน้าเพิ่มข้อมูลลูกค้า และพัสดุ
# -----------------------------
@app.route('/add_parcel', methods=['GET', 'POST'])
def add_parcel():
    if 'user_id' not in session:
        flash('กรุณาเข้าสู่ระบบก่อน', 'warning')
        return redirect(url_for('login'))

    # 🔐 อนุญาตเฉพาะ staff / admin
    if session.get('role') not in ['admin','staff']:
        flash('คุณไม่มีสิทธิ์เพิ่มพัสดุ', 'danger')
        return redirect(url_for('user_interface'))
    
    
    if request.method == 'GET':
        conn = get_db_connection()
        centers = conn.execute('SELECT * FROM sorting_centers').fetchall()
        conn.close()

        return render_template('add_parcel.html', centers=centers)

    if request.method == 'POST':
        # ------- ดึงข้อมูลผู้ส่ง -------
        s_name = request.form['sender_name']
        s_phone = request.form['sender_phone']
        s_email = request.form['sender_email']
        s_address = request.form['sender_address']

        # ------- ดึงข้อมูลผู้รับ -------
        r_name = request.form['receiver_name']
        r_phone = request.form['receiver_phone']
        r_email = request.form['receiver_email']
        r_address = request.form['receiver_address']

        # ------- ดึงข้อมูลพัสดุ -------
        tracking_number = generate_tracking_number()
        destination = request.form['destination']
        weight = request.form['weight']
        size = request.form['size']
        status_id = request.form['status']
        center_id = request.form['center_id']  

        conn = get_db_connection()
        c = conn.cursor()

        # 1️⃣ เพิ่มผู้ส่ง
        c.execute('INSERT INTO customers (customer_name, phone, email, address) VALUES (?, ?, ?, ?)',
                  (s_name, s_phone, s_email, s_address))
        sender_id = c.lastrowid

        # 2️⃣ เพิ่มผู้รับ
        c.execute('INSERT INTO receivers (receiver_name, phone, email, address) VALUES (?, ?, ?, ?)',
                  (r_name, r_phone, r_email, r_address))
        receiver_id = c.lastrowid

       # 3️⃣ เพิ่มพัสดุ
        # 🔐 สร้าง token สุ่ม 32 ตัวอักษร (ปลอดภัยมาก)
        token = secrets.token_hex(16)

        c.execute('''INSERT INTO parcels (sender_id, receiver_id, tracking_number, weight, size, destination, current_status_id, current_center_id, access_token)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (sender_id, receiver_id, tracking_number, weight, size, destination, status_id, center_id, token)
        )

        parcel_id = c.lastrowid

        conn.commit()
        conn.close()

# -----------------------------
# ✅ สร้าง QR อัตโนมัติ
# -----------------------------
        base_url = request.host_url.rstrip('/')
        qr_url = f"{base_url}/update_status/{token}"

        img = qrcode.make(qr_url)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        qr_folder = os.path.join(base_dir, 'static', 'qr')
        os.makedirs(qr_folder, exist_ok=True)

        file_path = os.path.join(qr_folder, f"{tracking_number}.png")
        img.save(file_path)
        
        flash(f"✅ เพิ่มข้อมูลพัสดุ {tracking_number} สำเร็จแล้ว!", 'success')
        
        return redirect(url_for('staff_dashboard'))


# -----------------------------
# ทดสอบการเชื่อมฐานข้อมูล
# -----------------------------
@app.route('/testdb')
def testdb():
    try:
        conn = get_db_connection()
        data = conn.execute('SELECT * FROM parcels').fetchall()
        conn.close()

        # แปลงผลลัพธ์เป็นข้อความให้อ่านง่ายขึ้น
        if not data:
            return "⚠️ ไม่มีข้อมูลในตาราง parcels"
        else:
            result = "<h3>ข้อมูลในฐานข้อมูล:</h3><ul>"
            for row in data:
                result += f"<li>📦 {row['tracking_number']} → {row['destination']} ({row['current_status_id']})</li>"
            result += "</ul>"
            return result
    except Exception as e:
        return f"❌ เกิดข้อผิดพลาด: {e}"

@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('q', '').strip()  # ดึงคำค้นจากช่อง search (q คือชื่อ input)
    
    conn = get_db_connection()
    query = """
        SELECT 
            p.tracking_number, 
            c.customer_name AS sender, 
            r.receiver_name AS receiver, 
            ps.status_name AS status, 
            p.destination
        FROM parcels p
        JOIN customers c ON p.sender_id = c.customer_id
        JOIN receivers r ON p.receiver_id = r.receiver_id
        JOIN parcel_status ps ON p.current_status_id = ps.status_id
        WHERE p.tracking_number LIKE ? 
           OR c.customer_name LIKE ? 
           OR r.receiver_name LIKE ?
    """
    # ใช้ f'%{keyword}%' เพื่อค้นหาคำที่คล้ายๆ กัน (ไม่ต้องตรงทั้งหมด)
    parcels = conn.execute(query, (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%')).fetchall()
    conn.close()

    # ส่งข้อมูลกลับไปหน้า interface.html พร้อมผลลัพธ์การค้นหา
    return render_template(
        'staff_dashboard.html',
        parcels=parcels,
        keyword=keyword,
        username=session.get('username')
    )

# แสดงหน้าอัปเดตสถานะ
@app.route('/update_status/<token>')
def update_status(token):

    # 🔐 ต้อง login ก่อน
    if 'user_id' not in session:
        flash('กรุณาเข้าสู่ระบบก่อนอัปเดตสถานะ', 'warning')
        return redirect(url_for('login',next=request.url))

    # 🔐 ต้องเป็น admin หรือ staff เท่านั้น
    if session.get('role') not in ['admin', 'staff']:
        flash('คุณไม่มีสิทธิ์เข้าหน้านี้', 'danger')
        return redirect(url_for('staff_dashboard'))

    conn = get_db_connection()
    parcel = conn.execute(
        'SELECT * FROM parcels WHERE access_token = ?',
        (token,)
    ).fetchone()
    
    if not parcel:
        conn.close()
        return "❌ ลิงก์ไม่ถูกต้อง"

    statuses = conn.execute('SELECT * FROM parcel_status').fetchall()
    centers = conn.execute('SELECT * FROM sorting_centers').fetchall()
    conn.close()

    return render_template(
        'update_status.html',
        parcel=parcel,
        statuses=statuses,
        centers=centers
    )


# บันทึกสถานะที่อัปเดต
@app.route('/save_status/<token>', methods=['POST'])
def save_status(token):

    # 🔐 ต้อง login ก่อน
    if 'user_id' not in session:
        flash('กรุณาเข้าสู่ระบบก่อน', 'warning')
        return redirect(url_for('login'))

    # 🔐 ต้องเป็น staff หรือ admin
    if session.get('role') not in ['admin', 'staff']:
        flash('คุณไม่มีสิทธิ์อัปเดตสถานะ', 'danger')
        return redirect(url_for('staff_dashboard'))

    status_id = request.form['status_id']
    center_id = request.form['center_id']
    note = request.form.get('note', '')

    updated_by = session['username']
    updated_role = session['role']  # ✅ ดึง role จริงจาก session

    conn = get_db_connection()
    c = conn.cursor()

       # 🔎 1. หา parcel_id จาก token ก่อน
    parcel = conn.execute(
        'SELECT parcel_id FROM parcels WHERE access_token = ?',
        (token,)
    ).fetchone()

    if not parcel:
        conn.close()
        return "❌ ลิงก์ไม่ถูกต้อง"

    parcel_id = parcel['parcel_id']

     # 🔄 2. อัปเดตสถานะปัจจุบันในตาราง parcels
    c.execute(
        'UPDATE parcels SET current_status_id = ?, current_center_id = ? WHERE parcel_id = ?',
        (status_id, center_id, parcel_id)
    )

    # 📝 3. บันทึกประวัติการอัปเดต
    c.execute('''
        INSERT INTO tracking_events
        (parcel_id, status_id, center_id, note, updated_by, updated_role)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (parcel_id, status_id, center_id, note, updated_by, updated_role))

    conn.commit()
    conn.close()

    flash("อัปเดตสถานะเรียบร้อยแล้ว", "success")
    return redirect(url_for('staff_dashboard'))

# แสดงประวัติการเคลื่อนไหวของพัสดุ
@app.route('/tracking/<int:parcel_id>')
def tracking_history(parcel_id):
    conn = get_db_connection()

    # ดึงข้อมูลพัสดุหลัก (เลขพัสดุ, ผู้ส่ง, ผู้รับ)
    parcel = conn.execute('''
        SELECT p.tracking_number, 
               c.customer_name AS sender_name, 
               r.receiver_name AS receiver_name, 
               p.destination
        FROM parcels p
        JOIN customers c ON p.sender_id = c.customer_id
        JOIN receivers r ON p.receiver_id = r.receiver_id
        WHERE p.parcel_id = ?
    ''', (parcel_id,)).fetchone()

    # ดึงข้อมูลการเคลื่อนไหวทั้งหมดจาก tracking_events
    events = conn.execute('''
        SELECT t.timestamp, ps.status_name, sc.center_name, t.note, t.updated_by
        FROM tracking_events t
        JOIN parcel_status ps ON t.status_id = ps.status_id
        JOIN sorting_centers sc ON t.center_id = sc.center_id
        WHERE t.parcel_id = ?
        ORDER BY t.timestamp ASC
    ''', (parcel_id,)).fetchall()

    conn.close()
    return render_template('tracking_history.html', parcel=parcel, events=events)


@app.route('/generate_qr/<tracking_number>')
def generate_qr(tracking_number):

    conn = get_db_connection()
    parcel = conn.execute(
        'SELECT access_token FROM parcels WHERE tracking_number = ?',
        (tracking_number,)
    ).fetchone()
    conn.close()

    if not parcel:
        return "❌ ไม่พบพัสดุ"

    token = parcel['access_token']

    from flask import request
    base_url = request.host_url.rstrip('/')
    qr_url = f"{base_url}/update_status/{token}"

    img = qrcode.make(qr_url)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    qr_folder = os.path.join(base_dir, 'static', 'qr')
    os.makedirs(qr_folder, exist_ok=True)

    file_path = os.path.join(qr_folder, f"{tracking_number}.png")
    img.save(file_path)

    flash(f"สร้าง QR Code สำหรับ {tracking_number} สำเร็จ", "success")

    return redirect(url_for('staff_dashboard'))


# -----------------------------
# ค้นหาพัสดุจาก tracking number
# -----------------------------
@app.route('/tracking_by_number/<tracking_number>')
def tracking_by_number(tracking_number):
    conn = get_db_connection()

    parcel = conn.execute(
        'SELECT parcel_id FROM parcels WHERE tracking_number = ?',
        (tracking_number,)
    ).fetchone()

    conn.close()

    if parcel:
        return redirect(url_for('tracking_history', parcel_id=parcel['parcel_id']))
    else:
        return "❌ ไม่พบข้อมูลพัสดุ"

# -----------------------------
# เริ่มรันเว็บ
# -----------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)