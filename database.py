"""
database.py
Veritabanı bağlantısı ve tablo/başlangıç verisi oluşturma.
"""

import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "dormitory.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # --- USERS ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'staff'
        )
    """)

    # --- ROOMS ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT UNIQUE NOT NULL,
            floor INTEGER NOT NULL,
            capacity INTEGER NOT NULL DEFAULT 2,
            room_type TEXT NOT NULL DEFAULT 'standard',
            status TEXT NOT NULL DEFAULT 'available'
        )
    """)

    # --- STUDENTS ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            tc_no TEXT UNIQUE NOT NULL,
            phone TEXT,
            email TEXT,
            emergency_contact TEXT,
            room_id INTEGER REFERENCES rooms(id),
            check_in_date DATE,
            check_out_date DATE,
            gender TEXT DEFAULT 'Belirtilmedi',
            scholarship INTEGER DEFAULT 0
        )
    """)

    # --- Migration: mevcut tabloya yeni sütunları ekle ---
    try:
        cur.execute("ALTER TABLE students ADD COLUMN gender TEXT DEFAULT 'Belirtilmedi'")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE students ADD COLUMN scholarship INTEGER DEFAULT 0")
    except Exception:
        pass
    # Migration: Öğrenci şifresi için sütun ekle (varsayılan = TC No hash'i)
    try:
        cur.execute("ALTER TABLE students ADD COLUMN password_hash TEXT")
    except Exception:
        pass  # sütun zaten mevcut

    # --- Ödemeler ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
            amount REAL NOT NULL,
            due_date DATE NOT NULL,
            paid_date DATE,
            status TEXT NOT NULL DEFAULT 'pending'
        )
    """)

    # --- Şikayetler ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
            subject TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'open',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --- Varsayılan admin kullanıcısı ---
    cur.execute("""
        INSERT OR IGNORE INTO users (username, password_hash, role)
        VALUES (?, ?, 'admin')
    """, ("admin", hash_password("admin123")))

    # --- Demo odalar ---
    demo_rooms = [
        ("101", 1, 2, "standard", "available"),
        ("102", 1, 2, "standard", "available"),
        ("103", 1, 1, "deluxe",   "available"),
        ("201", 2, 3, "standard", "available"),
        ("202", 2, 2, "deluxe",   "available"),
        ("301", 3, 1, "deluxe",   "available"),
    ]
    cur.executemany("""
        INSERT OR IGNORE INTO rooms (room_number, floor, capacity, room_type, status)
        VALUES (?, ?, ?, ?, ?)
    """, demo_rooms)

    conn.commit()
    conn.close()


def student_login(tc_no: str, password: str):
    """
    Öğrenci girişi: TC No + şifre doğrulama.
    Şifre varsayılan olarak TC No'nun kendisidir.
    Başarılı olursa öğrenci id ve adını döner, yoksa None.
    """
    conn = get_connection()
    pw_hash = hash_password(password)
    # Önce hash'i eşleştirmeye çalış
    row = conn.execute(
        "SELECT id, name, tc_no FROM students WHERE tc_no = ? AND password_hash = ?",
        (tc_no, pw_hash)
    ).fetchone()
    # Eğer kayıtlı hash yoksa: varsayılan şifre = TC No
    if not row:
        row = conn.execute(
            "SELECT id, name, tc_no FROM students WHERE tc_no = ? AND password_hash IS NULL",
            (tc_no,)
        ).fetchone()
        if row and password == tc_no:
            # İlk girişte şifreyi kaydet
            conn.execute(
                "UPDATE students SET password_hash = ? WHERE tc_no = ?",
                (pw_hash, tc_no)
            )
            conn.commit()
    conn.close()
    return row  # sqlite3.Row veya None
