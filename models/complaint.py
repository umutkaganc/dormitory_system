"""
models/complaint.py
Şikayet CRUD işlemleri.
"""

from database import get_connection


def add_complaint(student_id, subject, description=""):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO complaints (student_id, subject, description, status)
            VALUES (?, ?, ?, 'open')
        """, (student_id, subject, description))
        conn.commit()
        return True, "Şikayet kaydedildi."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


def get_all_complaints():
    conn = get_connection()
    rows = conn.execute("""
        SELECT c.*, s.name AS student_name
        FROM complaints c
        JOIN students s ON c.student_id = s.id
        ORDER BY c.created_at DESC
    """).fetchall()
    conn.close()
    return rows


def update_complaint_status(complaint_id, new_status):
    conn = get_connection()
    try:
        conn.execute("""
            UPDATE complaints SET status = ? WHERE id = ?
        """, (new_status, complaint_id))
        conn.commit()
        return True, "Durum güncellendi."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


def delete_complaint(complaint_id):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM complaints WHERE id = ?", (complaint_id,))
        conn.commit()
        return True, "Şikayet silindi."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()
