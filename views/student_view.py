"""
views/student_view.py
Öğrenci yönetim ekranı – Liste, Ekle, Düzenle, Sil, Ara.

Hafta 2: QPushButton, QLineEdit, QLabel, QCheckBox, QRadioButton, Signal/Slot
Hafta 3: QVBoxLayout, QHBoxLayout, QFormLayout, QSpacerItem
Hafta 4: Sinyal bağlama (clicked, textChanged, returnPressed)
Hafta 5: QMessageBox (information, warning, critical, question) – Modal Dialog
Hafta 6: QComboBox, QTableWidget, QIntValidator, QRegularExpressionValidator
Hafta 9: QDialog ve QWidget Kullanımı, Çoklu Pencereler, exec() ve show() farkı
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QFormLayout, QComboBox, QDateEdit, QMessageBox,
    QFrame, QSizePolicy, QAbstractItemView,
    QCheckBox, QRadioButton, QGroupBox, QSpacerItem  # Hafta 2 & 3
)
from PySide6.QtCore import Qt, QDate, QRegularExpression
from PySide6.QtGui import (
    QFont, QColor,
    QRegularExpressionValidator  # Hafta 6: Validator
)

from models.student import (add_student, get_all_students, update_student,
                             delete_student, search_students)
from models.room import get_available_rooms, get_all_rooms
from utils.helpers import validate_tc, validate_phone, validate_email, today_str

COLS = ["ID", "Ad Soyad", "TC No", "Telefon", "E-posta", "Oda", "Giriş Tarihi", "Cinsiyet", "Burs"]

TABLE_STYLE = """
QTableWidget {
    background: white;
    border: none;
    gridline-color: #e2e8f0;
    font-size: 12px;
    alternate-background-color: #f8fafc;
}
QTableWidget::item { padding: 6px 10px; color: #1e293b; }
QTableWidget::item:selected { background: #4f46e5; color: white; }
QHeaderView::section {
    background: #1e293b;
    color: white;
    font-weight: bold;
    font-size: 12px;
    padding: 8px 10px;
    border: none;
}
"""


def page_header(title: str) -> QLabel:
    lbl = QLabel(title)
    lbl.setFont(QFont("Segoe UI", 18, QFont.Bold))
    lbl.setStyleSheet("color: #1e293b;")
    return lbl


def action_btn(text, color="#6366f1", hover="#4f46e5", text_color="white"):
    btn = QPushButton(text)
    btn.setFixedHeight(36)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: {color}; color: {text_color};
            border: none; border-radius: 8px; padding: 0 16px; font-size: 12px; font-weight: bold;
        }}
        QPushButton:hover {{ background: {hover}; }}
    """)
    return btn


class StudentView(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        # Başlık + butonlar
        top = QHBoxLayout()
        top.addWidget(page_header("🎓 Öğrenci Yönetimi"))
        top.addStretch()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Ad veya TC No ile ara...")
        self.search_input.setFixedWidth(260)
        self.search_input.setStyleSheet("""
            QLineEdit { background: white; color: #1e293b; border: 1.5px solid #cbd5e1;
                        border-radius: 8px; padding: 6px 12px; font-size: 12px; }
            QLineEdit:focus { border-color: #6366f1; }
        """)
        # Hafta 2/4: textChanged sinyali ile arama
        self.search_input.textChanged.connect(self._search)
        top.addWidget(self.search_input)
        add_btn = action_btn("+ Yeni Öğrenci")
        # Hafta 2/4: clicked sinyali
        add_btn.clicked.connect(self._open_add)
        top.addWidget(add_btn)
        root.addLayout(top)

        # Hafta 6: QTableWidget – Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(len(COLS))
        self.table.setHorizontalHeaderLabels(COLS)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        root.addWidget(self.table)

        # Alt butonlar
        bot = QHBoxLayout()
        bot.addStretch()
        edit_btn = action_btn("✏️  Düzenle", "#0284c7", "#0369a1")
        edit_btn.clicked.connect(self._open_edit)
        del_btn  = action_btn("🗑️  Sil", "#dc2626", "#b91c1c")
        del_btn.clicked.connect(self._delete)
        bot.addWidget(edit_btn)
        bot.addWidget(del_btn)
        root.addLayout(bot)

    def refresh(self):
        self._populate(get_all_students())

    def _search(self, text):
        if text.strip():
            self._populate(search_students(text.strip()))
        else:
            self.refresh()

    def _populate(self, rows):
        self.table.setRowCount(0)
        for row in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            # Hafta 2: Cinsiyet ve Burs bilgileri de gösteriliyor
            gender = row["gender"] if "gender" in row.keys() else "—"
            scholarship = "✅ Evet" if (row["scholarship"] if "scholarship" in row.keys() else 0) else "❌ Hayır"
            vals = [
                str(row["id"]),
                row["name"],
                row["tc_no"],
                row["phone"] or "",
                row["email"] or "",
                row["room_number"] or "—",
                row["check_in_date"] or "",
                gender or "—",
                scholarship,
            ]
            for c, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setData(Qt.UserRole, row["id"])
                item.setForeground(QColor("#1e293b"))  # Okunabilir koyu metin
                self.table.setItem(r, c, item)

    def _selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).data(Qt.UserRole)

    def _open_add(self):
        # Hafta 5 / Hafta 9: Modal Dialog (exec() kullanımı)
        # exec() kullanıldığında kullanıcı dialog kapanmadan ana pencereye geri dönemez.
        dlg = StudentDialog(parent=self)
        if dlg.exec():
            self.refresh()

    def _open_edit(self):
        sid = self._selected_id()
        if not sid:
            # Hafta 5: QMessageBox.information
            QMessageBox.information(self, "Uyarı", "Lütfen bir öğrenci seçin.")
            return
        dlg = StudentDialog(student_id=sid, parent=self)
        if dlg.exec():
            self.refresh()

    def _delete(self):
        sid = self._selected_id()
        if not sid:
            QMessageBox.information(self, "Uyarı", "Lütfen bir öğrenci seçin.")
            return
        # Hafta 5: QMessageBox.question – onay alma
        reply = QMessageBox.question(self, "Onay", "Bu öğrenci silinsin mi?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            ok, msg = delete_student(sid)
            if ok:
                self.refresh()
            else:
                # Hafta 5: QMessageBox.critical
                QMessageBox.critical(self, "Hata", msg)


class StudentDialog(QDialog):
    """
    Öğrenci ekleme/düzenleme dialogu.
    Hafta 2: QCheckBox, QRadioButton, QLineEdit, QPushButton, QLabel
    Hafta 3: QFormLayout, QSpacerItem
    Hafta 6: QIntValidator, QRegularExpressionValidator, QComboBox
    Hafta 9: QDialog Sınıfı Kullanımı, Çoklu Pencere
    """

    def __init__(self, student_id=None, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.setWindowTitle("Öğrenci Ekle" if not student_id else "Öğrenci Düzenle")
        self.setMinimumWidth(480)
        self._build_ui()
        if student_id:
            self._load(student_id)

    def _build_ui(self):
        self.setStyleSheet("background: #f8fafc; font-family: 'Segoe UI';")
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        # Hafta 3: QFormLayout
        form = QFormLayout()
        form.setSpacing(10)

        inp_style = "background:white;border:1.5px solid #cbd5e1;border-radius:6px;padding:5px 10px;"

        def inp(ph=""):
            e = QLineEdit()
            e.setPlaceholderText(ph)
            e.setStyleSheet(inp_style)
            return e

        self.name_e     = inp("Zorunlu")
        self.tc_e       = inp("11 haneli TC No")
        self.phone_e    = inp("05XX XXX XX XX")
        self.email_e    = inp("ornek@email.com")
        self.emerg_e    = inp("Ad Soyad – Telefon")

        # ══ Hafta 6: QRegularExpressionValidator – TC No: sadece 11 rakam ══
        tc_validator = QRegularExpressionValidator(QRegularExpression(r"^\d{0,11}$"))
        self.tc_e.setValidator(tc_validator)

        # ══ Hafta 6: QRegularExpressionValidator – E-posta formatı ══
        email_regex = QRegularExpression(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        email_validator = QRegularExpressionValidator(email_regex)
        self.email_e.setValidator(email_validator)

        # Hafta 6: QComboBox – Oda seçimi
        self.room_cb = QComboBox()
        self.room_cb.setStyleSheet(inp_style)
        self._load_rooms()

        self.checkin_e = QDateEdit(QDate.currentDate())
        self.checkin_e.setCalendarPopup(True)
        self.checkin_e.setStyleSheet(inp_style)

        form.addRow("Ad Soyad *",        self.name_e)
        form.addRow("TC No *",           self.tc_e)
        form.addRow("Telefon",           self.phone_e)
        form.addRow("E-posta",           self.email_e)
        form.addRow("Acil İletişim",     self.emerg_e)
        form.addRow("Oda",               self.room_cb)
        form.addRow("Giriş Tarihi",      self.checkin_e)
        layout.addLayout(form)

        # ══ Hafta 3: QSpacerItem – form ile yeni alanlar arası boşluk ══
        layout.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # ══ Hafta 2: QRadioButton – Cinsiyet seçimi ══
        gender_group = QGroupBox("Cinsiyet")
        gender_group.setStyleSheet("""
            QGroupBox {
                background: white; border: 1.5px solid #cbd5e1;
                border-radius: 8px; padding: 12px; margin-top: 8px;
                font-weight: bold; color: #334155;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px; padding: 0 6px;
            }
        """)
        gender_layout = QHBoxLayout(gender_group)
        self.radio_male   = QRadioButton("Erkek")
        self.radio_female = QRadioButton("Kadın")
        self.radio_other  = QRadioButton("Belirtilmedi")
        self.radio_other.setChecked(True)  # Varsayılan
        for rb in [self.radio_male, self.radio_female, self.radio_other]:
            rb.setStyleSheet("color: #334155; font-size: 12px; background: transparent;")
            gender_layout.addWidget(rb)
        layout.addWidget(gender_group)

        # ══ Hafta 2: QCheckBox – Burs durumu ══
        self.scholarship_cb = QCheckBox("Burslu Öğrenci")
        self.scholarship_cb.setStyleSheet("""
            QCheckBox {
                color: #334155; font-size: 12px;
                spacing: 8px; padding: 6px;
            }
            QCheckBox::indicator {
                width: 18px; height: 18px;
                border-radius: 4px;
                border: 2px solid #6366f1;
            }
            QCheckBox::indicator:checked {
                background: #6366f1;
                border-color: #6366f1;
            }
        """)
        layout.addWidget(self.scholarship_cb)

        # Hafta 3: QSpacerItem – butonlar öncesi boşluk
        layout.addItem(QSpacerItem(20, 12, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Butonlar
        btns = QHBoxLayout()
        btns.addStretch()
        save_btn = action_btn("💾  Kaydet")
        # Hafta 2/4: clicked sinyali
        save_btn.clicked.connect(self._save)
        cancel_btn = action_btn("İptal", "#64748b", "#475569")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(cancel_btn)
        btns.addWidget(save_btn)
        layout.addLayout(btns)

    def _load_rooms(self):
        self.room_cb.clear()
        self.room_cb.addItem("— Oda Yok —", None)
        for r in get_available_rooms():
            self.room_cb.addItem(
                f"Oda {r['room_number']} (Kat {r['floor']}, "
                f"{r['occupant_count']}/{r['capacity']} kişi)",
                r["id"]
            )

    def _load(self, sid):
        from database import get_connection
        conn = get_connection()
        s = conn.execute("SELECT * FROM students WHERE id=?", (sid,)).fetchone()
        conn.close()
        if not s:
            return
        # Mevcut odayı da ekle (düzenleme sırasında görünmesi için)
        if s["room_id"]:
            from database import get_connection as gc
            c = gc()
            room = c.execute("SELECT * FROM rooms WHERE id=?", (s["room_id"],)).fetchone()
            c.close()
            if room:
                exists = any(self.room_cb.itemData(i) == s["room_id"]
                             for i in range(self.room_cb.count()))
                if not exists:
                    self.room_cb.addItem(
                        f"Oda {room['room_number']} (Kat {room['floor']}) [Mevcut]",
                        room["id"]
                    )
                idx = next((i for i in range(self.room_cb.count())
                            if self.room_cb.itemData(i) == s["room_id"]), 0)
                self.room_cb.setCurrentIndex(idx)

        self.name_e.setText(s["name"] or "")
        self.tc_e.setText(s["tc_no"] or "")
        self.phone_e.setText(s["phone"] or "")
        self.email_e.setText(s["email"] or "")
        self.emerg_e.setText(s["emergency_contact"] or "")
        if s["check_in_date"]:
            self.checkin_e.setDate(QDate.fromString(s["check_in_date"], "yyyy-MM-dd"))

        # Hafta 2: QRadioButton durumunu yükle
        gender = s["gender"] if "gender" in s.keys() else "Belirtilmedi"
        if gender == "Erkek":
            self.radio_male.setChecked(True)
        elif gender == "Kadın":
            self.radio_female.setChecked(True)
        else:
            self.radio_other.setChecked(True)

        # Hafta 2: QCheckBox durumunu yükle
        scholarship = s["scholarship"] if "scholarship" in s.keys() else 0
        self.scholarship_cb.setChecked(bool(scholarship))

    def _save(self):
        name  = self.name_e.text().strip()
        tc    = self.tc_e.text().strip()
        phone = self.phone_e.text().strip()
        email = self.email_e.text().strip()
        emerg = self.emerg_e.text().strip()
        room_id      = self.room_cb.currentData()
        checkin_date = self.checkin_e.date().toString("yyyy-MM-dd")

        # Hafta 2: QRadioButton'dan cinsiyet değerini oku
        if self.radio_male.isChecked():
            gender = "Erkek"
        elif self.radio_female.isChecked():
            gender = "Kadın"
        else:
            gender = "Belirtilmedi"

        # Hafta 2: QCheckBox'tan burs durumunu oku
        scholarship = 1 if self.scholarship_cb.isChecked() else 0

        # Hafta 5: QMessageBox ile hata mesajları
        if not name:
            QMessageBox.warning(self, "Uyarı", "Ad Soyad zorunludur.")
            return
        if not validate_tc(tc):
            QMessageBox.warning(self, "Uyarı", "Geçersiz TC Kimlik Numarası (11 hane, 1 ile başlar).")
            return
        if phone and not validate_phone(phone):
            QMessageBox.warning(self, "Uyarı", "Geçersiz telefon numarası.")
            return
        if email and not validate_email(email):
            QMessageBox.warning(self, "Uyarı", "Geçersiz e-posta adresi.")
            return

        if self.student_id:
            ok, msg = update_student(self.student_id, name, tc, phone, email, emerg,
                                     room_id, checkin_date, gender=gender, scholarship=scholarship)
        else:
            ok, msg = add_student(name, tc, phone, email, emerg, room_id, checkin_date,
                                  gender=gender, scholarship=scholarship)

        if ok:
            self.accept()
        else:
            QMessageBox.critical(self, "Hata", msg)
