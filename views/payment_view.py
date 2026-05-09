"""
views/payment_view.py
Ödeme takip ekranı – gecikmiş ödemeler kırmızı vurgulanır.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QComboBox, QDoubleSpinBox, QDateEdit,
    QMessageBox, QAbstractItemView
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor

from models.payment import (add_payment, get_all_payments,
                              mark_paid, delete_payment, get_overdue_payments)
from models.student import get_all_students
from utils.helpers import status_label

COLS = ["ID", "Öğrenci", "Tutar (₺)", "Son Tarih", "Ödeme Tarihi", "Durum"]

STATUS_COLOR = {
    "paid":    QColor("#e6f4ea"),
    "pending": QColor("#fff9c4"),
    "overdue": QColor("#fce8e6"),
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


class PaymentView(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        # Başlık
        top = QHBoxLayout()
        title = QLabel("💳 Ödeme Takibi")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1e293b;")
        top.addWidget(title)
        top.addStretch()

        # Renk açıklamaları
        badge_colors = [("#fff9c4", "#92400e", "Bekliyor"), ("#fce8e6", "#991b1b", "Gecikmiş"), ("#e6f4ea", "#166534", "Ödendi")]
        for bg, fg, text in badge_colors:
            lbl = QLabel(f"  {text}  ")
            lbl.setStyleSheet(f"background:{bg};color:{fg};border:1px solid #ccc;border-radius:6px;font-size:11px;padding:2px 6px;font-weight:bold;")
            top.addWidget(lbl)

        add_btn = action_btn("+ Ödeme Ekle")
        add_btn.clicked.connect(self._open_add)
        top.addWidget(add_btn)
        root.addLayout(top)

        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(len(COLS))
        self.table.setHorizontalHeaderLabels(COLS)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        root.addWidget(self.table)

        # Alt butonlar
        bot = QHBoxLayout()
        bot.addStretch()
        paid_btn = action_btn("✅  Ödendi İşaretle", "#059669", "#047857")
        paid_btn.clicked.connect(self._mark_paid)
        del_btn  = action_btn("🗑️  Sil", "#dc2626", "#b91c1c")
        del_btn.clicked.connect(self._delete)
        bot.addWidget(paid_btn)
        bot.addWidget(del_btn)
        root.addLayout(bot)

    def refresh(self):
        self.table.setRowCount(0)
        for p in get_all_payments():
            r = self.table.rowCount()
            self.table.insertRow(r)
            status = p["status"]
            bg = STATUS_COLOR.get(status, QColor("white"))
            vals = [
                str(p["id"]),
                p.get("student_name", ""),
                f"{p['amount']:.2f}",
                p["due_date"] or "",
                p["paid_date"] or "—",
                status_label(status),
            ]
            for c, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setData(Qt.UserRole, p["id"])
                item.setBackground(bg)
                item.setForeground(QColor("#1e293b"))  # Okunabilir koyu metin
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(r, c, item)

    def _selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).data(Qt.UserRole)

    def _open_add(self):
        dlg = PaymentDialog(parent=self)
        if dlg.exec():
            self.refresh()

    def _mark_paid(self):
        pid = self._selected_id()
        if not pid:
            QMessageBox.information(self, "Uyarı", "Lütfen bir ödeme seçin.")
            return
        ok, msg = mark_paid(pid)
        if ok:
            self.refresh()
        else:
            QMessageBox.critical(self, "Hata", msg)

    def _delete(self):
        pid = self._selected_id()
        if not pid:
            QMessageBox.information(self, "Uyarı", "Lütfen bir ödeme seçin.")
            return
        reply = QMessageBox.question(self, "Onay", "Bu ödeme kaydı silinsin mi?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            ok, msg = delete_payment(pid)
            if ok:
                self.refresh()
            else:
                QMessageBox.critical(self, "Hata", msg)


class PaymentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ödeme Ekle")
        self.setMinimumWidth(380)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background:#f8fafc; color:#1e293b; font-family:'Segoe UI';")
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        form = QFormLayout()
        form.setSpacing(10)
        inp_style = "background:white;border:1.5px solid #cbd5e1;border-radius:6px;padding:5px;"

        self.student_cb = QComboBox()
        self.student_cb.setStyleSheet(inp_style)
        for s in get_all_students():
            self.student_cb.addItem(f"{s['name']} ({s['tc_no']})", s["id"])

        self.amount_sb = QDoubleSpinBox()
        self.amount_sb.setRange(0, 100000)
        self.amount_sb.setSuffix(" ₺")
        self.amount_sb.setValue(4500)
        self.amount_sb.setStyleSheet(inp_style)

        self.due_date_e = QDateEdit(QDate.currentDate())
        self.due_date_e.setCalendarPopup(True)
        self.due_date_e.setStyleSheet(inp_style)

        form.addRow("Öğrenci *",    self.student_cb)
        form.addRow("Tutar *",      self.amount_sb)
        form.addRow("Son Tarih *",  self.due_date_e)
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
        if not sid:
            QMessageBox.warning(self, "Uyarı", "Öğrenci seçin.")
            return
        ok, msg = add_payment(sid, self.amount_sb.value(),
                              self.due_date_e.date().toString("yyyy-MM-dd"))
        if ok:
            self.accept()
        else:
            QMessageBox.critical(self, "Hata", msg)
