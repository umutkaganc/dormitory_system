"""
models/payment.py
Ödeme CRUD işlemleri.
"""

from database import get_connection
from datetime import date


def add_payment(student_id, amount, due_date):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO payments (student_id, amount, due_date, status)
            VALUES (?, ?, ?, 'pending')
        """, (student_id, amount, due_date))
        conn.commit()
        return True, "Ödeme kaydı oluşturuldu."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


def get_all_payments():
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.*, s.name AS student_name
        FROM payments p
        JOIN students s ON p.student_id = s.id
        ORDER BY p.due_date DESC
    """).fetchall()
    conn.close()
    return _mark_overdue(rows)


def get_payments_by_student(student_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM payments WHERE student_id = ? ORDER BY due_date DESC
    """, (student_id,)).fetchall()
    conn.close()
    return _mark_overdue(rows)


def get_overdue_payments():
    conn = get_connection()
    today = date.today().isoformat()
    rows = conn.execute("""
        SELECT p.*, s.name AS student_name
        FROM payments p
        JOIN students s ON p.student_id = s.id
        WHERE p.status = 'pending' AND p.due_date < ?
        ORDER BY p.due_date
    """, (today,)).fetchall()
    conn.close()
    return rows


def mark_paid(payment_id, paid_date=None):
    if not paid_date:
        paid_date = date.today().isoformat()
    conn = get_connection()
    try:
        conn.execute("""
            UPDATE payments SET status='paid', paid_date=? WHERE id=?
        """, (paid_date, payment_id))
        conn.commit()
        return True, "Ödeme onaylandı."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


def delete_payment(payment_id):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM payments WHERE id = ?", (payment_id,))
        conn.commit()
        return True, "Ödeme kaydı silindi."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


def get_monthly_summary():
    """Aylık gelir özeti döner (raporlama için)."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT strftime('%Y-%m', due_date) AS month,
               SUM(amount) AS total,
               SUM(CASE WHEN status='paid' THEN amount ELSE 0 END) AS collected
        FROM payments
        GROUP BY month
        ORDER BY month
    """).fetchall()
    conn.close()
    return rows


def _mark_overdue(rows):
    """Vadesi geçmiş pending ödemeleri overdue olarak işaretler (geçici, DB yazmaz)."""
    today = date.today().isoformat()
    result = []
    for r in rows:
        d = dict(r)
        if d["status"] == "pending" and d["due_date"] and d["due_date"] < today:
            d["status"] = "overdue"
        result.append(d)
    return result
