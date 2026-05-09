"""
models/room.py
Oda CRUD işlemleri.
"""

from database import get_connection


def add_room(room_number, floor, capacity, room_type="standard"):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO rooms (room_number, floor, capacity, room_type, status)
            VALUES (?, ?, ?, ?, 'available')
        """, (room_number, floor, capacity, room_type))
        conn.commit()
        return True, "Oda başarıyla eklendi."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


def get_all_rooms():
    conn = get_connection()
    rows = conn.execute("""
        SELECT r.*,
               (SELECT COUNT(*) FROM students s
                WHERE s.room_id = r.id
                AND (s.check_out_date IS NULL OR s.check_out_date = '')) AS occupant_count
        FROM rooms r
        ORDER BY r.floor, r.room_number
    """).fetchall()
    conn.close()
    return rows


def get_room_by_id(room_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM rooms WHERE id = ?", (room_id,)).fetchone()
    conn.close()
    return row


def get_available_rooms():
    conn = get_connection()
    rows = conn.execute("""
        SELECT r.*,
               (SELECT COUNT(*) FROM students s
                WHERE s.room_id = r.id
                AND (s.check_out_date IS NULL OR s.check_out_date = '')) AS occupant_count
        FROM rooms r
        WHERE r.status != 'maintenance'
          AND (SELECT COUNT(*) FROM students s
               WHERE s.room_id = r.id
               AND (s.check_out_date IS NULL OR s.check_out_date = '')) < r.capacity
        ORDER BY r.floor, r.room_number
    """).fetchall()
    conn.close()
    return rows


def update_room(room_id, room_number, floor, capacity, room_type, status):
    conn = get_connection()
    try:
        conn.execute("""
            UPDATE rooms SET room_number=?, floor=?, capacity=?, room_type=?, status=?
            WHERE id=?
        """, (room_number, floor, capacity, room_type, status, room_id))
        conn.commit()
        return True, "Oda güncellendi."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


def delete_room(room_id):
    conn = get_connection()
    try:
        count = conn.execute(
            "SELECT COUNT(*) FROM students WHERE room_id = ?", (room_id,)
        ).fetchone()[0]
        if count > 0:
            return False, "Bu odada kayıtlı öğrenciler var. Önce öğrencileri aktarın."
        conn.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
        conn.commit()
        return True, "Oda silindi."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


def get_room_occupants(room_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM students
        WHERE room_id = ? AND (check_out_date IS NULL OR check_out_date = '')
    """, (room_id,)).fetchall()
    conn.close()
    return rows
