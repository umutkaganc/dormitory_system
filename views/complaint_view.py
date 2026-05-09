"""
views/complaint_view.py
Şikayet yönetim ekranı.

Hafta 2: QPushButton, QLineEdit, QLabel, QTextEdit
Hafta 3: QVBoxLayout, QHBoxLayout, QFormLayout
Hafta 5: QMessageBox (Modal Dialog), Non-Modal Dialog (show)
Hafta 6: QComboBox, QTableWidget
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QComboBox, QLineEdit, QTextEdit, QMessageBox,
    QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

from models.complaint import (add_complaint, get_all_complaints,
                               update_complaint_status, delete_complaint)
from models.student import get_all_students
from utils.helpers import status_label

COLS = ["ID", "Öğrenci", "Konu", "Açıklama", "Durum", "Tarih"]

STATUS_COLOR = {
    "open":        QColor("#e8f0fe"),
    "in_progress": QColor("#fff3e0"),
    "resolved":    QColor("#e6f4ea"),
}

TABLE_STYLE = """
QTableWidget { background:white; border:none; gridline-color:#e2e8f0; font-size:12px; alternate-background-color:#f8fafc; }
QTableWidget::item { padding:6px 10px; color:#1e293b; }
QTableWidget::item:selected { background:#4f46e5; color:white; }
QHeaderView::section {
    background:#1e293b; color:white; font-weight:bold;
    font-size:12px; padding:8px 10px; border:none;
}
"""


def action_btn(text, color="#6366f1", hover="#4f46e5"):
    btn = QPushButton(text)
    btn.setFixedHeight(36)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet(f"QPushButton{{background:{color};color:white;border:none;"
                      f"border-radius:8px;padding:0 16px;font-size:12px;font-weight:bold;}}"
                      f"QPushButton:hover{{background:{hover};}}")
    return btn


class ComplaintView(QWidget):
    def __init__(self):
        super().__init__()
        self._detail_windows = []  # Non-modal pencereleri referans olarak tut
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        top = QHBoxLayout()
        title = QLabel("📋 Şikayet Yönetimi")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1e293b;")
        top.addWidget(title)
        top.addStretch()

        # Detay butonu
        detail_btn = action_btn("🔍 Detay Göster", "#7c3aed", "#6d28d9")
        detail_btn.clicked.connect(self._show_detail_nonmodal)
        top.addWidget(detail_btn)

        add_btn = action_btn("+ Şikayet Ekle")
        add_btn.clicked.connect(self._open_add)
        top.addWidget(add_btn)
        root.addLayout(top)

        self.table = QTableWidget()
        self.table.setColumnCount(len(COLS))
        self.table.setHorizontalHeaderLabels(COLS)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        # Hafta 5: Çift tıklama ile non-modal detay penceresi
        self.table.doubleClicked.connect(self._on_double_click)
        root.addWidget(self.table)

        bot = QHBoxLayout()

        # Durum güncelleme
        self.status_cb = QComboBox()
        self.status_cb.addItem("Açık",      "open")
        self.status_cb.addItem("İşlemde",   "in_progress")
        self.status_cb.addItem("Çözüldü",   "resolved")
        self.status_cb.setStyleSheet("""
            QComboBox { background: white; color: #1e293b; border: 1.5px solid #cbd5e1;
                border-radius: 6px; padding: 4px 8px; }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView { color: #1e293b; background: white; }
        """)
        self.status_cb.setFixedHeight(36)
        upd_btn = action_btn("🔄  Durumu Güncelle", "#7c3aed", "#6d28d9")
        upd_btn.clicked.connect(self._update_status)

        hint = QLabel("💡 Tablodaki bir şikayete çift tıklayarak detay penceresini açın")
        hint.setStyleSheet("color: #64748b; font-size: 11px;")
        bot.addWidget(hint)
        bot.addStretch()
        bot.addWidget(QLabel("Durum:"))
        bot.addWidget(self.status_cb)
        bot.addWidget(upd_btn)

        del_btn  = action_btn("🗑️  Sil", "#dc2626", "#b91c1c")
        del_btn.clicked.connect(self._delete)
        bot.addWidget(del_btn)
        root.addLayout(bot)

    def refresh(self):
        self.table.setRowCount(0)
        for c in get_all_complaints():
            r = self.table.rowCount()
            self.table.insertRow(r)
            status = c["status"]
            bg = STATUS_COLOR.get(status, QColor("white"))
            vals = [
                str(c["id"]),
                c["student_name"] if "student_name" in c.keys() else "",
                c["subject"],
                (c["description"] or "")[:60],
                status_label(status),
                (c["created_at"] or "")[:10],
            ]
            for col, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setData(Qt.UserRole, c["id"])
                item.setBackground(bg)
                item.setForeground(QColor("#1e293b"))  # Okunabilir koyu metin
                self.table.setItem(r, col, item)

    def _selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).data(Qt.UserRole)

    def _open_add(self):
        # Hafta 5: Modal Dialog – exec()
        dlg = ComplaintDialog(parent=self)
        if dlg.exec():
            self.refresh()

    def _on_double_click(self, index):
        """Çift tıklamada önce satırı seç, sonra detayı aç."""
        self.table.selectRow(index.row())
        self._show_detail_nonmodal()

    def _show_detail_nonmodal(self):
        """
        Hafta 5: Non-Modal Dialog – show()
        Pencere kapatılmadan ana uygulama kullanılmaya devam edilebilir.
        """
        cid = self._selected_id()
        if not cid:
            QMessageBox.information(self, "Uyarı", "Lütfen bir şikayet seçin.")
            return

        # İlgili şikayet verisini bul
        row = self.table.currentRow()
        student  = self.table.item(row, 1).text()
        subject  = self.table.item(row, 2).text()
        desc     = self.table.item(row, 3).text()
        status   = self.table.item(row, 4).text()
        date     = self.table.item(row, 5).text()

        # Non-modal detay penceresi oluştur
        detail_dlg = QDialog(self)
        detail_dlg.setWindowTitle(f"Şikayet Detayı – #{cid}")
        detail_dlg.setMinimumSize(450, 350)
        detail_dlg.setStyleSheet("background: #f8fafc; font-family: 'Segoe UI';")

        layout = QVBoxLayout(detail_dlg)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        header = QLabel(f"📋 Şikayet #{cid}")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header.setStyleSheet("color: #1e293b;")
        layout.addWidget(header)

        info_style = "color: #334155; font-size: 13px; padding: 4px 0;"
        for label_text, value in [
            ("Öğrenci:", student),
            ("Konu:", subject),
            ("Durum:", status),
            ("Tarih:", date),
        ]:
            row_layout = QHBoxLayout()
            lbl = QLabel(f"<b>{label_text}</b>")
            lbl.setStyleSheet(info_style)
            val = QLabel(value)
            val.setStyleSheet(info_style)
            row_layout.addWidget(lbl)
            row_layout.addWidget(val)
            row_layout.addStretch()
            layout.addLayout(row_layout)

        # Tam açıklama
        from database import get_connection
        conn = get_connection()
        full = conn.execute("SELECT description FROM complaints WHERE id=?", (cid,)).fetchone()
        conn.close()
        full_desc = full["description"] if full and full["description"] else "Açıklama yok"

        desc_label = QLabel("Açıklama:")
        desc_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        desc_label.setStyleSheet("color: #1e293b; margin-top: 8px;")
        layout.addWidget(desc_label)

        # Hafta 2: QTextEdit – Çok satırlı metin gösterimi
        desc_text = QTextEdit()
        desc_text.setPlainText(full_desc)
        desc_text.setReadOnly(True)
        desc_text.setStyleSheet("""
            QTextEdit {
                background: white; border: 1.5px solid #cbd5e1;
                border-radius: 8px; padding: 10px; font-size: 12px; color: #334155;
            }
        """)
        layout.addWidget(desc_text)

        close_btn = QPushButton("Kapat")
        close_btn.setFixedHeight(36)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("background:#6366f1;color:white;border:none;border-radius:8px;padding:0 16px;font-weight:bold;")
        close_btn.clicked.connect(detail_dlg.close)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)

        # Hafta 5: Non-Modal – show() kullanılır, exec() değil!
        detail_dlg.show()
        self._detail_windows.append(detail_dlg)

    def _update_status(self):
        cid = self._selected_id()
        if not cid:
            QMessageBox.information(self, "Uyarı", "Lütfen bir şikayet seçin.")
            return
        new_status = self.status_cb.currentData()
        ok, msg = update_complaint_status(cid, new_status)
        if ok:
            self.refresh()
        else:
            QMessageBox.critical(self, "Hata", msg)

    def _delete(self):
        cid = self._selected_id()
        if not cid:
            QMessageBox.information(self, "Uyarı", "Lütfen bir şikayet seçin.")
            return
        # Hafta 5: QMessageBox.question – Kullanıcıdan onay alma
        reply = QMessageBox.question(self, "Onay", "Bu şikayet silinsin mi?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            ok, msg = delete_complaint(cid)
            if ok:
                self.refresh()
            else:
                QMessageBox.critical(self, "Hata", msg)


class ComplaintDialog(QDialog):
    """Hafta 5: Modal Dialog – exec() ile açılır."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Şikayet Ekle")
        self.setMinimumWidth(400)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background:#f8fafc; color:#1e293b; font-family:'Segoe UI';")
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        form = QFormLayout()
        form.setSpacing(10)
        inp_style = "background:white;border:1.5px solid #cbd5e1;border-radius:6px;padding:5px 10px;"

        self.student_cb = QComboBox()
        self.student_cb.setStyleSheet(inp_style)
        for s in get_all_students():
            self.student_cb.addItem(f"{s['name']} ({s['tc_no']})", s["id"])

        self.subject_e = QLineEdit()
        self.subject_e.setStyleSheet(inp_style)
        self.subject_e.setPlaceholderText("Şikayet konusu")

        # Hafta 2: QTextEdit – çok satırlı metin girişi
        self.desc_e = QTextEdit()
        self.desc_e.setFixedHeight(100)
        self.desc_e.setStyleSheet(inp_style)
        self.desc_e.setPlaceholderText("Açıklama (opsiyonel)")

        form.addRow("Öğrenci *", self.student_cb)
        form.addRow("Konu *",    self.subject_e)
        form.addRow("Açıklama", self.desc_e)
        layout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        save_btn = QPushButton("💾  Kaydet")
        save_btn.setFixedHeight(36)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("background:#6366f1;color:white;border:none;border-radius:8px;padding:0 16px;font-weight:bold;")
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton("İptal")
        cancel_btn.setFixedHeight(36)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("background:#64748b;color:white;border:none;border-radius:8px;padding:0 16px;")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(cancel_btn)
        btns.addWidget(save_btn)
        layout.addLayout(btns)

    def _save(self):
        sid = self.student_cb.currentData()
        subject = self.subject_e.text().strip()
        if not sid:
            QMessageBox.warning(self, "Uyarı", "Öğrenci seçin.")
            return
        if not subject:
            QMessageBox.warning(self, "Uyarı", "Konu zorunludur.")
            return
        ok, msg = add_complaint(sid, subject, self.desc_e.toPlainText().strip())
        if ok:
            self.accept()
        else:
            QMessageBox.critical(self, "Hata", msg)
