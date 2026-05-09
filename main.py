"""
main.py
Private Dormitory Tracking System – Uygulama giriş noktası.
"""

import sys
import os

# Proje kökünü sys.path'e ekle, böylece tüm modüller bulunabilir
sys.path.insert(0, os.path.dirname(__file__))

import resources_rc  # Hafta 10: .qrc dosyasından derlenen kaynaklar

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from database import init_db
from views.login_view import LoginView
from views.main_window import MainWindow
from views.student_portal import StudentPortalWindow


def main():
    # Veritabanını başlat
    init_db()

    app = QApplication(sys.argv)
    app.setApplicationName("Private Dormitory Tracking System")
    # Hafta 10: Tema (Fusion) kullanımı
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))

    # Hafta 10: Qt Style Sheet (QSS) ile genel görünüm ve Dinamik Durumlar (:hover)
    app.setStyleSheet("""
        /* ── Genel metin rengi ───────────────────────── */
        QDialog, QMessageBox, QInputDialog {
            background: #f8fafc;
            color: #1e293b;
        }
        QDialog QLabel, QMessageBox QLabel, QInputDialog QLabel {
            color: #1e293b;
            background: transparent;
        }
        QDialog QPushButton, QMessageBox QPushButton, QInputDialog QPushButton {
            color: #1e293b;
            background: #e2e8f0;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            padding: 6px 16px;
            font-size: 12px;
            min-width: 70px;
        }
        QDialog QPushButton:hover, QMessageBox QPushButton:hover, QInputDialog QPushButton:hover {
            background: #cbd5e1;
        }
        QDialog QLineEdit, QInputDialog QLineEdit {
            color: #1e293b;
            background: white;
            border: 1.5px solid #cbd5e1;
            border-radius: 6px;
            padding: 5px 10px;
        }
        QDialog QComboBox, QDialog QSpinBox, QDialog QDoubleSpinBox, QDialog QDateEdit {
            color: #1e293b;
        }
        QDialog QTextEdit {
            color: #1e293b;
        }
        QDialog QGroupBox {
            color: #1e293b;
        }
        QDialog QCheckBox, QDialog QRadioButton {
            color: #1e293b;
        }

        /* ── QListWidget okunabilirlik ───────────────── */
        QListWidget {
            color: #1e293b;
        }
        QListWidget::item {
            color: #1e293b;
        }

        /* ── Tooltip ─────────────────────────────────── */
        QToolTip {
            background: #1e293b;
            color: #f1f5f9;
            border: 1px solid #334155;
            padding: 4px 8px;
            border-radius: 6px;
        }

        /* ── Scrollbar ───────────────────────────────── */
        QScrollBar:vertical {
            background: #f1f5f9;
            width: 8px;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical {
            background: #cbd5e1;
            border-radius: 4px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover { background: #94a3b8; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
    """)

    # Giriş ekranı
    login = LoginView()
    open_windows = []  # Açık pencereleri referans olarak tut

    def on_staff_login(username, role):
        """Personel/Admin girişi → MainWindow aç."""
        win = MainWindow(username, role)
        win.show()
        open_windows.append(win)
        login.close()

    def on_student_login(student_id, student_name):
        """Öğrenci girişi → StudentPortalWindow aç (Hafta 9: Çoklu Pencere)."""
        portal = StudentPortalWindow(student_id, student_name)
        portal.show()
        open_windows.append(portal)
        login.close()

    login.login_success.connect(on_staff_login)
    login.student_login_success.connect(on_student_login)
    login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
