"""
views/main_window.py
Ana pencere – QMainWindow ile menü çubuğu, araç çubuğu, durum çubuğu,
sol navigasyon çubuğu + içerik alanı.

Hafta 7 konuları: QMainWindow, QAction, MenuBar, Toolbar, StatusBar
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QFrame, QSizePolicy, QStackedWidget,
    QMessageBox, QFileDialog, QInputDialog
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont, QColor, QPalette, QIcon, QAction

from views.student_view   import StudentView
from views.room_view      import RoomView
from views.payment_view   import PaymentView
from views.complaint_view import ComplaintView
from views.report_view    import ReportView

NAV_STYLE = """
    QPushButton {{
        background: transparent;
        color: #94a3b8;
        text-align: left;
        padding: 12px 20px;
        border-radius: 10px;
        font-size: 13px;
        border: none;
    }}
    QPushButton:hover {{
        background: #1e293b;
        color: #f1f5f9;
    }}
    QPushButton:checked {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #6366f1,stop:1 #8b5cf6);
        color: white;
        font-weight: bold;
    }}
"""

NAV_LABELS = ["🎓  Öğrenciler", "🚪  Odalar", "💳  Ödemeler", "📋  Şikayetler", "📊  Raporlar"]


class MainWindow(QMainWindow):
    """Hafta 7: QMainWindow kullanımı – menü, araç çubuğu, durum çubuğu."""

    def __init__(self, username: str, role: str):
        super().__init__()
        self.username = username
        self.role = role
        self.setWindowTitle("Private Dormitory Tracking System")
        self.setMinimumSize(1200, 700)
        self._build_ui()
        self._build_menubar()    # Hafta 7: Menü Çubuğu
        self._build_toolbar()    # Hafta 7: Araç Çubuğu
        self._build_statusbar()  # Hafta 7: Durum Çubuğu

    # ── Menü Çubuğu (Hafta 7) ─────────────────────────────────
    def _build_menubar(self):
        menubar = self.menuBar()

        # --- Dosya Menüsü ---
        file_menu = menubar.addMenu("Dosya")

        # QAction – Dışa Aktar (Hafta 7: QAction + Kısayol)
        self.export_action = QAction(QIcon(":/icons/export.svg"), "Dışa Aktar (CSV)", self)
        self.export_action.setShortcut("Ctrl+E")
        self.export_action.setStatusTip("Verileri CSV dosyasına aktar")
        self.export_action.triggered.connect(self._export_csv)
        file_menu.addAction(self.export_action)

        file_menu.addSeparator()

        # QAction – Çıkış (Hafta 7: QAction + Kısayol)
        self.exit_action = QAction(QIcon(":/icons/logout.svg"), "Çıkış", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.setStatusTip("Uygulamadan çık")
        self.exit_action.triggered.connect(self.close)
        
        # Hafta 10: .qrc'den QIcon Kullanımı
        self.settings_action = QAction(QIcon(":/icons/settings.svg"), "Ayarlar", self)
        self.settings_action.setStatusTip("Uygulama ayarlarını aç")
        self.settings_action.triggered.connect(self._open_settings)
        file_menu.addAction(self.settings_action)
        
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        # --- Görünüm Menüsü ---
        view_menu = menubar.addMenu("Görünüm")
        page_names = ["Öğrenciler", "Odalar", "Ödemeler", "Şikayetler", "Raporlar"]
        for idx, name in enumerate(page_names):
            action = QAction(f"{NAV_LABELS[idx]}", self)
            action.triggered.connect(lambda checked, i=idx: self._switch_page(i))
            view_menu.addAction(action)

        # --- Yardım Menüsü ---
        help_menu = menubar.addMenu("Yardım")
        about_action = QAction("ℹ️  Hakkında", self)
        about_action.setShortcut("F1")
        about_action.setStatusTip("Uygulama hakkında bilgi")
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    # ── Araç Çubuğu (Hafta 7) ─────────────────────────────────
    def _build_toolbar(self):
        toolbar = self.addToolBar("Ana Araçlar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setStyleSheet("""
            QToolBar {
                background: #1e293b;
                border: none;
                padding: 4px;
                spacing: 6px;
            }
            QToolButton {
                color: #e2e8f0;
                background: transparent;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QToolButton:hover {
                background: #334155;
                color: white;
            }
        """)

        # Toolbar'a aksiyonları ekle
        toolbar.addAction(self.export_action)
        toolbar.addSeparator()

        # Hızlı sayfa geçiş butonları
        for idx, label in enumerate(NAV_LABELS):
            action = QAction(label, self)
            action.triggered.connect(lambda checked, i=idx: self._switch_page(i))
            toolbar.addAction(action)

        toolbar.addSeparator()
        toolbar.addAction(self.exit_action)

    # ── Durum Çubuğu (Hafta 7) ────────────────────────────────
    def _build_statusbar(self):
        self.statusBar().showMessage("Hazır – Öğrenciler sayfası aktif")
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background: #0f172a;
                color: #94a3b8;
                font-size: 11px;
                padding: 4px 12px;
            }
        """)

    # ── Ana UI ─────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ── Sidebar ──────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background: #0f172a;")
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(12, 20, 12, 20)
        sb_layout.setSpacing(4)

        # Logo
        logo = QLabel("🏨  DormTrack")
        logo.setFont(QFont("Segoe UI", 14, QFont.Bold))
        logo.setStyleSheet("color: #f8fafc; padding: 10px 8px 20px 8px;")
        sb_layout.addWidget(logo)

        # Nav butonları
        self.nav_buttons = []
        for idx, label in enumerate(NAV_LABELS):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setFont(QFont("Segoe UI", 11))
            btn.setStyleSheet(NAV_STYLE)
            btn.clicked.connect(lambda checked, i=idx: self._switch_page(i))
            sb_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sb_layout.addStretch()

        # Kullanıcı bilgisi + çıkış
        user_frame = QFrame()
        user_frame.setStyleSheet("background: #1e293b; border-radius: 10px;")
        uf_layout = QVBoxLayout(user_frame)
        uf_layout.setContentsMargins(12, 10, 12, 10)
        user_lbl = QLabel(f"👤 {self.username}")
        user_lbl.setStyleSheet("color: #f1f5f9; font-weight: bold; font-size: 12px;")
        role_lbl = QLabel("Yönetici" if self.role == "admin" else "Personel")
        role_lbl.setStyleSheet("color: #64748b; font-size: 10px;")
        uf_layout.addWidget(user_lbl)
        uf_layout.addWidget(role_lbl)

        logout_btn = QPushButton("Çıkış Yap")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton {
                background: #7f1d1d; color: #fca5a5; border: none;
                border-radius: 6px; padding: 6px; font-size: 11px;
            }
            QPushButton:hover { background: #991b1b; }
        """)
        logout_btn.clicked.connect(self._logout)
        uf_layout.addWidget(logout_btn)
        sb_layout.addWidget(user_frame)

        main_layout.addWidget(sidebar)

        # ── İçerik alanı ─────────────────────────────────────
        content_wrapper = QFrame()
        content_wrapper.setStyleSheet("background: #f1f5f9;")
        cw_layout = QVBoxLayout(content_wrapper)
        cw_layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        self.stack.addWidget(StudentView())
        self.stack.addWidget(RoomView())
        self.stack.addWidget(PaymentView())
        self.stack.addWidget(ComplaintView())
        self.stack.addWidget(ReportView())

        cw_layout.addWidget(self.stack)
        main_layout.addWidget(content_wrapper)

        # Başlangıç sayfası
        self._switch_page(0)

    def _switch_page(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        # Sayfayı yenile (varsa)
        page = self.stack.currentWidget()
        if hasattr(page, "refresh"):
            page.refresh()
        # Hafta 7: StatusBar ile sayfa bilgisi göster
        page_names = ["Öğrenciler", "Odalar", "Ödemeler", "Şikayetler", "Raporlar"]
        self.statusBar().showMessage(f"📄 {page_names[index]} sayfası aktif")

    def _export_csv(self):
        """Hafta 5: QFileDialog kullanarak CSV dışa aktarma."""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Raporu Dışa Aktar",
            "",
            "CSV Dosyası (*.csv);;Tüm Dosyalar (*)"
        )
        if file_name:
            try:
                from models.student import get_all_students
                from models.room import get_all_rooms
                students = get_all_students()
                with open(file_name, "w", encoding="utf-8-sig") as f:
                    f.write("ID,Ad Soyad,TC No,Telefon,E-posta,Oda,Giriş Tarihi,Cinsiyet,Burs\n")
                    for s in students:
                        f.write(f"{s['id']},{s['name']},{s['tc_no']},{s['phone'] or ''},{s['email'] or ''},"
                                f"{s['room_number'] or ''},{s['check_in_date'] or ''},"
                                f"{s.get('gender', '')},{s.get('scholarship', 0)}\n")
                QMessageBox.information(self, "Başarılı", f"Veri başarıyla dışa aktarıldı:\n{file_name}")
                self.statusBar().showMessage(f"✅ CSV dışa aktarıldı: {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dışa aktarma sırasında hata:\n{e}")

    def _show_about(self):
        """Yardım / Hakkında penceresi."""
        QMessageBox.information(
            self, "Hakkında",
            "🏨  Private Dormitory Tracking System\n"
            "────────────────────────────────────\n"
            "Görsel Programlama II – Proje Ödevi\n"
            "PySide6 (Qt for Python) ile geliştirilmiştir.\n\n"
            "📌  Kullanım Kılavuzu\n"
            "• Öğrenciler  –  Öğrenci kayıt, düzenleme ve arama\n"
            "• Odalar       –  Oda yönetimi ve kat özeti\n"
            "• Ödemeler   –  Kira tahakkuk ve tahsilat takibi\n"
            "• Şikayetler  –  Şikayet açma ve durum güncelleme\n"
            "• Raporlar    –  İstatistik ve gelir grafikleri\n\n"
            "⌨️  Kısayollar\n"
            "• Ctrl+E  –  Verileri CSV olarak dışa aktar\n"
            "• Ctrl+Q  –  Uygulamadan çık\n"
            "• F1        –  Bu yardım penceresini aç\n\n"
            "💡  İpucu: Tablolarda satıra çift tıklayarak\n"
            "     detay penceresini açabilirsiniz."
        )

    def _open_settings(self):
        # Hafta 9: Modal QDialog kullanımı
        QMessageBox.information(self, "Ayarlar", "Ayarlar menüsü yakında eklenecektir.")

    def _logout(self):
        from views.login_view import LoginView
        self.login = LoginView()
        self.login.login_success.connect(self._reopen)
        self.login.show()
        self.close()

    def _reopen(self, username, role):
        self.new_win = MainWindow(username, role)
        self.new_win.show()
        self.login.close()
