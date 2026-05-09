"""
models/student.py
Öğrenci CRUD işlemleri.
"""

from database import get_connection


def add_student(name, tc_no, phone, email, emergency_contact, room_id, check_in_date, check_out_date=None, gender='Belirtilmedi', scholarship=0):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO students (name, tc_no, phone, email, emergency_contact, room_id, check_in_date, check_out_date, gender, scholarship)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, tc_no, phone, email, emergency_contact, room_id, check_in_date, check_out_date, gender, scholarship))
        _update_room_status(conn, room_id)
        conn.commit()
        return True, "Öğrenci başarıyla eklendi."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


def get_all_students():
    conn = get_connection()
    rows = conn.execute("""
        SELECT s.*, r.room_number
        FROM students s
        LEFT JOIN rooms r ON s.room_id = r.id
        ORDER BY s.name
    """).fetchall()
    conn.close()
    return rows


def get_student_by_id(student_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    conn.close()
    return row


def update_student(student_id, name, tc_no, phone, email, emergency_contact, room_id, check_in_date, check_out_date=None, gender='Belirtilmedi', scholarship=0):
    conn = get_connection()
    try:
        old = conn.execute("SELECT room_id, tc_no FROM students WHERE id = ?", (student_id,)).fetchone()
        # TC değiştiyse şifreyi sıfırla (yeni TC ile giriş yapılabilsin)
        tc_changed = old and old["tc_no"] != tc_no
        if tc_changed:
            conn.execute("""
                UPDATE students SET name=?, tc_no=?, phone=?, email=?, emergency_contact=?,
                room_id=?, check_in_date=?, check_out_date=?, gender=?, scholarship=?,
                password_hash=NULL WHERE id=?
            """, (name, tc_no, phone, email, emergency_contact, room_id, check_in_date, check_out_date, gender, scholarship, student_id))
        else:
            conn.execute("""
                UPDATE students SET name=?, tc_no=?, phone=?, email=?, emergency_contact=?,
                room_id=?, check_in_date=?, check_out_date=?, gender=?, scholarship=? WHERE id=?
            """, (name, tc_no, phone, email, emergency_contact, room_id, check_in_date, check_out_date, gender, scholarship, student_id))
        if old and old["room_id"] != room_id:
            _update_room_status(conn, old["room_id"])
        _update_room_status(conn, room_id)
        conn.commit()
        return True, "Öğrenci güncellendi."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


def delete_student(student_id):
    conn = get_connection()
    try:
        old = conn.execute("SELECT room_id FROM students WHERE id = ?", (student_id,)).fetchone()
        conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
        if old and old["room_id"]:
            _update_room_status(conn, old["room_id"])
        conn.commit()
        return True, "Öğrenci silindi."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


def search_students(query):
    conn = get_connection()
    q = f"%{query}%"
    rows = conn.execute("""
        SELECT s.*, r.room_number
        FROM students s
        LEFT JOIN rooms r ON s.room_id = r.id
        WHERE s.name LIKE ? OR s.tc_no LIKE ? OR s.phone LIKE ?
        ORDER BY s.name
    """, (q, q, q)).fetchall()
    conn.close()
    return rows


def _update_room_status(conn, room_id):
    """Odanın mevcut öğrenci sayısına göre durumunu günceller."""
    if not room_id:
        return
    room = conn.execute("SELECT capacity, status FROM rooms WHERE id = ?", (room_id,)).fetchone()
    if not room or room["status"] == "maintenance":
        return
    count = conn.execute(
        "SELECT COUNT(*) FROM students WHERE room_id = ? AND (check_out_date IS NULL OR check_out_date = '')",
        (room_id,)
    ).fetchone()[0]
    new_status = "occupied" if count >= room["capacity"] else "available"
    conn.execute("UPDATE rooms SET status = ? WHERE id = ?", (new_status, room_id))
