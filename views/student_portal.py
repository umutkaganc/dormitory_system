"""
views/student_portal.py
Öğrenci Paneli – Giriş yapan öğrencinin kendi verilerini görüntülediği,
şikayet açabildiği salt-okunur ekran.

Hafta 9: QWidget (non-modal pencere olarak açılır), QDialog (şikayet formu)
Hafta 10: QSS ile stil
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSizePolicy, QDialog, QFormLayout,
    QLineEdit, QTextEdit, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

from database import get_connection
from models.complaint import add_complaint, get_all_complaints
from utils.helpers import status_label


def _card(title: str, value: str, color: str = "#6366f1") -> QFrame:
    """İstatistik / bilgi kartı."""
    frame = QFrame()
    frame.setStyleSheet(f"""
        QFrame {{
            background: white;
            border-radius: 14px;
            border-left: 5px solid {color};
        }}
    """)
    frame.setFixedHeight(90)
    frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(18, 12, 18, 12)
    val_lbl = QLabel(value)
    val_lbl.setFont(QFont("Segoe UI", 20, QFont.Bold))
    val_lbl.setStyleSheet(f"color: {color}; background: transparent;")
    ttl_lbl = QLabel(title)
    ttl_lbl.setFont(QFont("Segoe UI", 10))
    ttl_lbl.setStyleSheet("color: #64748b; background: transparent;")
    layout.addWidget(val_lbl)
    layout.addWidget(ttl_lbl)
    return frame


def _action_btn(text, color="#6366f1", hover="#4f46e5"):
    btn = QPushButton(text)
    btn.setFixedHeight(38)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: {color}; color: white; border: none;
            border-radius: 8px; padding: 0 20px;
            font-size: 12px; font-weight: bold;
        }}
        QPushButton:hover {{ background: {hover}; }}
    """)
    return btn


TABLE_STYLE = """
QTableWidget { background: white; border: none; gridline-color: #e2e8f0; font-size: 12px; }
QTableWidget::item { padding: 6px 10px; color: #1e293b; }
QTableWidget::item:selected { background: #4f46e5; color: white; }
QHeaderView::section {
    background: #1e293b; color: white; font-weight: bold;
    font-size: 12px; padding: 8px 10px; border: none;
}
"""

STATUS_COLOR = {
    "paid":    QColor("#e6f4ea"),
    "pending": QColor("#fff9c4"),
    "overdue": QColor("#fce8e6"),
    "open":        QColor("#e8f0fe"),
    "in_progress": QColor("#fff3e0"),
    "resolved":    QColor("#e6f4ea"),
}


class StudentPortalWindow(QMainWindow):
    """
    Öğrencinin kendi bilgilerini gördüğü, şikayet açabildiği ana pencere.
    Hafta 9: QMainWindow alt sınıfı olarak farklı bir pencere (QWidget).
    """

    def __init__(self, student_id: int, student_name: str):
        super().__init__()
        self.student_id = student_id
        self.student_name = student_name
        self.setWindowTitle(f"Öğrenci Paneli – {student_name}")
        self.setMinimumSize(900, 620)
        self._build_ui()
        self._load_data()

    # ── UI ──────────────────────────────────────────────────────────
    def _build_ui(self):
        # Hafta 10: QSS ile koyu tema
        self.setStyleSheet("QMainWindow { background: #f1f5f9; }")

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Üst bar ──
        topbar = QFrame()
        topbar.setFixedHeight(60)
        topbar.setStyleSheet("background: #0f172a;")
        tb_layout = QHBoxLayout(topbar)
        tb_layout.setContentsMargins(24, 0, 24, 0)

        logo = QLabel("🏨  DormTrack  –  Öğrenci Paneli")
        logo.setFont(QFont("Segoe UI", 13, QFont.Bold))
        logo.setStyleSheet("color: #f8fafc;")
        tb_layout.addWidget(logo)
        tb_layout.addStretch()

        welcome = QLabel(f"👤  {self.student_name}")
        welcome.setStyleSheet("color: #94a3b8; font-size: 12px;")
        tb_layout.addWidget(welcome)

        logout_btn = QPushButton("Çıkış")
        logout_btn.setFixedSize(70, 32)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton { background: #7f1d1d; color: #fca5a5;
                border: none; border-radius: 6px; font-size: 11px; font-weight: bold; }
            QPushButton:hover { background: #991b1b; }
        """)
        logout_btn.clicked.connect(self.close)
        tb_layout.addWidget(logout_btn)
        root.addWidget(topbar)

        # ── İçerik ──
        content = QWidget()
        content.setStyleSheet("background: #f1f5f9;")
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(28, 24, 28, 24)
        c_layout.setSpacing(20)

        # Bilgi kartları
        self.cards_row = QHBoxLayout()
        self.cards_row.setSpacing(16)
        c_layout.addLayout(self.cards_row)

        # Kişisel bilgi kartı
        info_frame = QFrame()
        info_frame.setStyleSheet("background: white; border-radius: 14px;")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(20, 16, 20, 16)
        info_layout.setSpacing(8)
        info_title = QLabel("📋  Kişisel Bilgilerim")
        info_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        info_title.setStyleSheet("color: #1e293b;")
        info_layout.addWidget(info_title)
        self.info_labels = {}
        for field in ["Ad Soyad", "TC No", "Telefon", "E-posta", "Oda", "Giriş Tarihi", "Cinsiyet", "Burs"]:
            row = QHBoxLayout()
            key_lbl = QLabel(f"{field}:")
            key_lbl.setFixedWidth(110)
            key_lbl.setStyleSheet("color: #64748b; font-size: 12px; font-weight: bold;")
            val_lbl = QLabel("—")
            val_lbl.setStyleSheet("color: #1e293b; font-size: 12px;")
            row.addWidget(key_lbl)
            row.addWidget(val_lbl)
            row.addStretch()
            info_layout.addLayout(row)
            self.info_labels[field] = val_lbl
        c_layout.addWidget(info_frame)

        # Ödemelerim tablosu
        pay_title = QLabel("💳  Ödeme Geçmişim")
        pay_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        pay_title.setStyleSheet("color: #1e293b;")
        c_layout.addWidget(pay_title)

        self.pay_table = QTableWidget()
        self.pay_table.setColumnCount(4)
        self.pay_table.setHorizontalHeaderLabels(["Tutar (₺)", "Son Tarih", "Ödeme Tarihi", "Durum"])
        self.pay_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.pay_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.pay_table.verticalHeader().setVisible(False)
        self.pay_table.setStyleSheet(TABLE_STYLE)
        self.pay_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.pay_table.setMaximumHeight(160)
        c_layout.addWidget(self.pay_table)

        # Şikayetlerim tablosu + ekle butonu
        comp_row = QHBoxLayout()
        comp_title = QLabel("📋  Şikayetlerim")
        comp_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        comp_title.setStyleSheet("color: #1e293b;")
        comp_row.addWidget(comp_title)
        comp_row.addStretch()
        add_comp_btn = _action_btn("+ Şikayet Aç")
        add_comp_btn.clicked.connect(self._open_complaint_dialog)
        comp_row.addWidget(add_comp_btn)
        c_layout.addLayout(comp_row)

        self.comp_table = QTableWidget()
        self.comp_table.setColumnCount(4)
        self.comp_table.setHorizontalHeaderLabels(["Konu", "Açıklama", "Durum", "Tarih"])
        self.comp_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.comp_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.comp_table.verticalHeader().setVisible(False)
        self.comp_table.setStyleSheet(TABLE_STYLE)
        self.comp_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.comp_table.setMaximumHeight(160)
        c_layout.addWidget(self.comp_table)

        root.addWidget(content)

    # ── Veri yükleme ────────────────────────────────────────────────
    def _load_data(self):
        conn = get_connection()

        # Öğrenci bilgileri
        s = conn.execute("""
            SELECT s.*, r.room_number
            FROM students s
            LEFT JOIN rooms r ON s.room_id = r.id
            WHERE s.id = ?
        """, (self.student_id,)).fetchone()

        if s:
            burs = "✅ Evet" if s["scholarship"] else "❌ Hayır"
            self.info_labels["Ad Soyad"].setText(s["name"])
            self.info_labels["TC No"].setText(s["tc_no"])
            self.info_labels["Telefon"].setText(s["phone"] or "—")
            self.info_labels["E-posta"].setText(s["email"] or "—")
            self.info_labels["Oda"].setText(s["room_number"] or "Atanmadı")
            self.info_labels["Giriş Tarihi"].setText(s["check_in_date"] or "—")
            self.info_labels["Cinsiyet"].setText(s["gender"] or "—")
            self.info_labels["Burs"].setText(burs)

        # Ödemeler
        payments = conn.execute(
            "SELECT * FROM payments WHERE student_id = ? ORDER BY due_date DESC",
            (self.student_id,)
        ).fetchall()

        # İstatistik kartları
        for i in reversed(range(self.cards_row.count())):
            w = self.cards_row.itemAt(i).widget()
            if w:
                w.setParent(None)

        paid_count   = sum(1 for p in payments if p["status"] == "paid")
        pending_count = sum(1 for p in payments if p["status"] == "pending")
        overdue_count = sum(1 for p in payments if p["status"] == "overdue")
        total_paid   = sum(p["amount"] for p in payments if p["status"] == "paid")

        for title, val, color in [
            ("Ödenen",    str(paid_count),     "#10b981"),
            ("Bekleyen",  str(pending_count),  "#f59e0b"),
            ("Gecikmiş",  str(overdue_count),  "#ef4444"),
            ("Toplam Ödeme", f"₺{total_paid:,.0f}", "#6366f1"),
        ]:
            self.cards_row.addWidget(_card(title, val, color))

        # Ödeme tablosu
        self.pay_table.setRowCount(0)
        STATUS_COLORS_PAY = {"paid": "#e6f4ea", "pending": "#fff9c4", "overdue": "#fce8e6"}
        for p in payments:
            r = self.pay_table.rowCount()
            self.pay_table.insertRow(r)
            bg = QColor(STATUS_COLORS_PAY.get(p["status"], "white"))
            for c, v in enumerate([
                f"{p['amount']:.2f}",
                p["due_date"] or "",
                p["paid_date"] or "—",
                status_label(p["status"]),
            ]):
                item = QTableWidgetItem(v)
                item.setBackground(bg)
                item.setForeground(QColor("#1e293b"))
                item.setTextAlignment(Qt.AlignCenter)
                self.pay_table.setItem(r, c, item)

        # Şikayetler
        complaints = conn.execute(
            "SELECT * FROM complaints WHERE student_id = ? ORDER BY created_at DESC",
            (self.student_id,)
        ).fetchall()
        conn.close()

        self.comp_table.setRowCount(0)
        STATUS_COLORS_COMP = {"open": "#e8f0fe", "in_progress": "#fff3e0", "resolved": "#e6f4ea"}
        for c_row in complaints:
            r = self.comp_table.rowCount()
            self.comp_table.insertRow(r)
            bg = QColor(STATUS_COLORS_COMP.get(c_row["status"], "white"))
            for c, v in enumerate([
                c_row["subject"],
                (c_row["description"] or "")[:50],
                status_label(c_row["status"]),
                (c_row["created_at"] or "")[:10],
            ]):
                item = QTableWidgetItem(v)
                item.setBackground(bg)
                item.setForeground(QColor("#1e293b"))
                item.setTextAlignment(Qt.AlignCenter)
                self.comp_table.setItem(r, c, item)

    # ── Şikayet dialog ──────────────────────────────────────────────
    def _open_complaint_dialog(self):
        """Hafta 9: Modal QDialog ile şikayet formu."""
        dlg = StudentComplaintDialog(self.student_id, parent=self)
        if dlg.exec():
            self._load_data()  # Tabloyu yenile


class StudentComplaintDialog(QDialog):
    """
    Öğrencinin kendi adına şikayet açtığı modal dialog.
    Hafta 9: QDialog – exec() ile modal olarak açılır.
    Hafta 10: QSS ile stillendirilmiş.
    """

    def __init__(self, student_id: int, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.setWindowTitle("Şikayet Aç")
        self.setMinimumWidth(420)
        self._build_ui()

    def _build_ui(self):
        # Hafta 10: Widget bazlı QSS
        self.setStyleSheet("background: #f8fafc; color: #1e293b; font-family: 'Segoe UI';")
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        header = QLabel("📋  Yeni Şikayet")
        header.setFont(QFont("Segoe UI", 15, QFont.Bold))
        header.setStyleSheet("color: #1e293b;")
        layout.addWidget(header)

        inp_style = "background: white; border: 1.5px solid #cbd5e1; border-radius: 6px; padding: 5px 10px; color: #1e293b;"

        form = QFormLayout()
        form.setSpacing(10)

        self.subject_e = QLineEdit()
        self.subject_e.setPlaceholderText("Konu başlığı")
        self.subject_e.setStyleSheet(inp_style)

        self.desc_e = QTextEdit()
        self.desc_e.setPlaceholderText("Şikayetinizi detaylıca açıklayın...")
        self.desc_e.setFixedHeight(110)
        self.desc_e.setStyleSheet(inp_style)

        form.addRow("Konu *",      self.subject_e)
        form.addRow("Açıklama",   self.desc_e)
        layout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        cancel_btn = QPushButton("İptal")
        cancel_btn.setFixedHeight(36)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("background:#64748b;color:white;border:none;border-radius:8px;padding:0 16px;")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("💾  Gönder")
        save_btn.setFixedHeight(36)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton { background: #6366f1; color: white; border: none;
                border-radius: 8px; padding: 0 16px; font-weight: bold; }
            QPushButton:hover { background: #4f46e5; }
        """)
        save_btn.clicked.connect(self._save)
        btns.addWidget(cancel_btn)
        btns.addWidget(save_btn)
        layout.addLayout(btns)

    def _save(self):
        subject = self.subject_e.text().strip()
        if not subject:
            QMessageBox.warning(self, "Uyarı", "Konu zorunludur.")
            return
        ok, msg = add_complaint(self.student_id, subject, self.desc_e.toPlainText().strip())
        if ok:
            QMessageBox.information(self, "Başarılı", "Şikayetiniz iletildi.")
            self.accept()
        else:
            QMessageBox.critical(self, "Hata", msg)
