"""
views/login_view.py
Giriş ekranı – Personel ve Öğrenci sekmeli.

Hafta 9: İki farklı QWidget (LoginView + StudentPortalWindow) – çoklu pencere yapısı.
Hafta 10: QSS ile özel stil ve tema.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QApplication, QMessageBox,
    QTabWidget  # Hafta 6 & 9: Sekmeli giriş
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPalette, QColor
import hashlib
from database import get_connection, student_login


def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


class LoginView(QWidget):
    login_success = Signal(str, str)         # (username, role) – personel/admin
    student_login_success = Signal(int, str)  # (student_id, student_name) – öğrenci

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Private Dormitory – Giriş")
        self.setFixedSize(480, 600)
        self._setup_ui()

    def _setup_ui(self):
        pal = QPalette()
        pal.setColor(QPalette.Window, QColor("#0f172a"))
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignCenter)
        root.setContentsMargins(40, 30, 40, 30)

        # Dış kart
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet("""
            QFrame#card {
                background: #1e293b;
                border-radius: 20px;
                border: 1px solid #334155;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(16)
        card_layout.setContentsMargins(32, 36, 32, 36)

        # Logo
        icon_lbl = QLabel("🏨")
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 48px; background: transparent;")
        card_layout.addWidget(icon_lbl)

        title = QLabel("Private Dormitory")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 19, QFont.Bold))
        title.setStyleSheet("color: #f8fafc; background: transparent;")
        card_layout.addWidget(title)

        subtitle = QLabel("Yurt Takip Sistemi")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #94a3b8; font-size: 11px; background: transparent; margin-bottom: 6px;")
        card_layout.addWidget(subtitle)

        # ── Sekmeli giriş (Hafta 6 & 9: QTabWidget + Çoklu Pencere) ──
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: #0f172a;
                color: #64748b;
                padding: 8px 24px;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #8b5cf6);
                color: white;
            }
            QTabBar::tab:hover:!selected { background: #1e293b; color: #f1f5f9; }
        """)

        # Sekme 1: Personel / Admin
        self.staff_tab = self._build_staff_tab()
        self.tabs.addTab(self.staff_tab, "👔  Personel")

        # Sekme 2: Öğrenci
        self.student_tab = self._build_student_tab()
        self.tabs.addTab(self.student_tab, "🎓  Öğrenci")

        card_layout.addWidget(self.tabs)
        root.addWidget(card)

    # ── Personel sekmesi ────────────────────────────────────────────
    def _build_staff_tab(self) -> QWidget:
        tab = QWidget()
        tab.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 12, 0, 0)

        layout.addWidget(self._label("Kullanıcı Adı"))
        self.username_input = self._input("Kullanıcı adınızı girin")
        layout.addWidget(self.username_input)

        layout.addWidget(self._label("Şifre"))
        self.password_input = self._input("Şifrenizi girin", echo=True)
        self.password_input.returnPressed.connect(self._do_staff_login)
        layout.addWidget(self.password_input)

        self.staff_error = self._error_lbl()
        layout.addWidget(self.staff_error)

        login_btn = self._login_btn("Giriş Yap")
        login_btn.clicked.connect(self._do_staff_login)
        layout.addWidget(login_btn)

        hint = QLabel("Varsayılan: admin / admin123")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("color: #475569; font-size: 10px; background: transparent;")
        layout.addWidget(hint)
        return tab

    # ── Öğrenci sekmesi ─────────────────────────────────────────────
    def _build_student_tab(self) -> QWidget:
        tab = QWidget()
        tab.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 12, 0, 0)

        layout.addWidget(self._label("TC Kimlik No"))
        self.tc_input = self._input("11 haneli TC No")
        layout.addWidget(self.tc_input)

        layout.addWidget(self._label("Şifre"))
        self.student_pw_input = self._input("Varsayılan: TC Kimlik No", echo=True)
        self.student_pw_input.returnPressed.connect(self._do_student_login)
        layout.addWidget(self.student_pw_input)

        self.student_error = self._error_lbl()
        layout.addWidget(self.student_error)

        login_btn = self._login_btn("Öğrenci Girişi")
        login_btn.clicked.connect(self._do_student_login)
        layout.addWidget(login_btn)

        hint = QLabel("Şifre: İlk girişte TC Kimlik Numaranızdır")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("color: #475569; font-size: 10px; background: transparent;")
        layout.addWidget(hint)
        return tab

    # ── Yardımcılar ─────────────────────────────────────────────────
    def _label(self, text):
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", 10))
        lbl.setStyleSheet("color: #cbd5e1; background: transparent;")
        return lbl

    def _error_lbl(self):
        lbl = QLabel("")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("color: #f87171; font-size: 11px; background: transparent;")
        return lbl

    def _input(self, placeholder, echo=False):
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFixedHeight(42)
        if echo:
            inp.setEchoMode(QLineEdit.Password)
        inp.setStyleSheet("""
            QLineEdit {
                background: #0f172a; color: #f1f5f9;
                border: 1.5px solid #334155; border-radius: 8px;
                padding: 0 12px; font-size: 13px;
            }
            QLineEdit:focus { border-color: #6366f1; }
        """)
        return inp

    def _login_btn(self, text):
        btn = QPushButton(text)
        btn.setFixedHeight(46)
        btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #8b5cf6);
                color: white; border: none; border-radius: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4f46e5, stop:1 #7c3aed);
            }
            QPushButton:pressed { background: #4338ca; }
        """)
        return btn

    # ── Giriş mantığı ───────────────────────────────────────────────
    def _do_staff_login(self):
        self.staff_error.setText("")
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            self.staff_error.setText("Kullanıcı adı ve şifre gereklidir.")
            return
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password_hash = ?",
            (username, hash_password(password))
        ).fetchone()
        conn.close()
        if row:
            self.login_success.emit(username, row["role"])
        else:
            self.staff_error.setText("Kullanıcı adı veya şifre hatalı!")
            self.password_input.clear()

    def _do_student_login(self):
        self.student_error.setText("")
        tc = self.tc_input.text().strip()
        pw = self.student_pw_input.text()
        if not tc or not pw:
            self.student_error.setText("TC No ve şifre gereklidir.")
            return
        row = student_login(tc, pw)
        if row:
            self.student_login_success.emit(row["id"], row["name"])
        else:
            self.student_error.setText("TC No veya şifre hatalı! Kayıtlı öğrenci değilsiniz.")
            self.student_pw_input.clear()
