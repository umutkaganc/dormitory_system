"""
views/room_view.py
Oda yönetim ekranı – Doluluk renklendirme, Ekle, Düzenle, Sil.

Hafta 6: QTabWidget (Sekmeli arayüz), QListWidget (Liste görüntüleyici), QSlider
Hafta 2: QPushButton, QLabel, QLineEdit
Hafta 3: QVBoxLayout, QHBoxLayout, QFormLayout
Hafta 5: QMessageBox
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QComboBox, QSpinBox, QLineEdit, QMessageBox,
    QAbstractItemView,
    QTabWidget, QListWidget, QListWidgetItem, QSlider  # Hafta 6
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

from models.room import (add_room, get_all_rooms, update_room,
                          delete_room, get_room_occupants)
from utils.helpers import status_label

COLS = ["ID", "Oda No", "Kat", "Kapasite", "Tür", "Durum", "Doluluk"]

TABLE_STYLE = """
QTableWidget { background: white; border: none; gridline-color: #e2e8f0; font-size: 12px; alternate-background-color: #f8fafc; }
QTableWidget::item { padding: 6px 10px; color: #1e293b; }
QTableWidget::item:selected { background: #4f46e5; color: white; }
QHeaderView::section {
    background: #1e293b; color: white; font-weight: bold;
    font-size: 12px; padding: 8px 10px; border: none;
}
"""

STATUS_COLORS = {
    "available":   QColor("#e6f4ea"),
    "occupied":    QColor("#fce8e6"),
    "maintenance": QColor("#fff3e0"),
}


def action_btn(text, color="#6366f1", hover="#4f46e5"):
    btn = QPushButton(text)
    btn.setFixedHeight(36)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{ background:{color}; color:white; border:none;
            border-radius:8px; padding:0 16px; font-size:12px; font-weight:bold; }}
        QPushButton:hover {{ background:{hover}; }}
    """)
    return btn


class RoomView(QWidget):
    """
    Hafta 6: QTabWidget kullanarak iki sekmeli oda yönetimi.
    Sekme 1: Oda Tablosu (QTableWidget)
    Sekme 2: Kat Özeti (QListWidget)
    """

    def __init__(self):
        super().__init__()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        # Başlık + Ekle butonu
        top = QHBoxLayout()
        title = QLabel("🚪 Oda Yönetimi")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1e293b;")
        top.addWidget(title)
        top.addStretch()

        # Renk açıklamaları
        badge_colors = [("#e6f4ea", "#166534", "Boş"), ("#fce8e6", "#991b1b", "Dolu"), ("#fff3e0", "#92400e", "Bakımda")]
        for bg, fg, text in badge_colors:
            lbl = QLabel(f"  {text}  ")
            lbl.setStyleSheet(f"background: {bg}; color: {fg}; border: 1px solid #ccc; border-radius: 6px; font-size: 11px; padding: 2px 6px; font-weight: bold;")
            top.addWidget(lbl)

        add_btn = action_btn("+ Yeni Oda")
        add_btn.clicked.connect(self._open_add)
        top.addWidget(add_btn)
        root.addLayout(top)

        # ══ Hafta 6: QSlider – Kapasite filtresi ══
        slider_layout = QHBoxLayout()
        slider_label = QLabel("🔧 Min. Kapasite Filtresi:")
        slider_label.setStyleSheet("color: #475569; font-size: 12px; font-weight: bold;")
        slider_layout.addWidget(slider_label)

        self.cap_slider = QSlider(Qt.Horizontal)
        self.cap_slider.setMinimum(1)
        self.cap_slider.setMaximum(10)
        self.cap_slider.setValue(1)
        self.cap_slider.setTickPosition(QSlider.TicksBelow)
        self.cap_slider.setTickInterval(1)
        self.cap_slider.setFixedWidth(300)
        self.cap_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px; background: #cbd5e1; border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #6366f1; width: 18px; height: 18px;
                margin: -6px 0; border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #6366f1; border-radius: 3px;
            }
        """)
        self.cap_slider.valueChanged.connect(self._on_slider_changed)
        slider_layout.addWidget(self.cap_slider)

        self.slider_value_lbl = QLabel("1")
        self.slider_value_lbl.setStyleSheet("color: #6366f1; font-weight: bold; font-size: 14px; min-width: 30px;")
        slider_layout.addWidget(self.slider_value_lbl)
        slider_layout.addStretch()
        root.addLayout(slider_layout)

        # ══ Hafta 6: QTabWidget – Sekmeli arayüz ══
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab {
                background: #e2e8f0;
                color: #475569;
                padding: 8px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 12px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: white;
                color: #6366f1;
            }
            QTabBar::tab:hover {
                background: #f1f5f9;
            }
        """)

        # Sekme 1: Oda Tablosu
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        tab1_layout.setContentsMargins(0, 8, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(len(COLS))
        self.table.setHorizontalHeaderLabels(COLS)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(TABLE_STYLE)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.doubleClicked.connect(self._show_occupants)
        tab1_layout.addWidget(self.table)
        self.tabs.addTab(tab1, "📊 Oda Tablosu")

        # ══ Sekme 2: Hafta 6 – QListWidget ile Kat Özeti ══
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        tab2_layout.setContentsMargins(10, 10, 10, 10)
        tab2_info = QLabel("Katlara göre oda dağılımı ve doluluk bilgisi:")
        tab2_info.setStyleSheet("color: #475569; font-size: 12px; margin-bottom: 8px;")
        tab2_layout.addWidget(tab2_info)

        self.floor_list = QListWidget()
        self.floor_list.setStyleSheet("""
            QListWidget {
                background: white; border: none; font-size: 13px;
            }
            QListWidget::item {
                padding: 10px 14px; border-bottom: 1px solid #e2e8f0;
            }
            QListWidget::item:selected {
                background: #e0e7ff; color: #1e1b4b;
            }
        """)
        tab2_layout.addWidget(self.floor_list)
        self.tabs.addTab(tab2, "🏢 Kat Özeti")

        root.addWidget(self.tabs)

        # Alt butonlar
        bot = QHBoxLayout()
        hint = QLabel("💡 Çift tıklayarak oda sakinlerini görüntüleyin")
        hint.setStyleSheet("color: #64748b; font-size: 11px;")
        bot.addWidget(hint)
        bot.addStretch()
        edit_btn = action_btn("✏️  Düzenle", "#0284c7", "#0369a1")
        edit_btn.clicked.connect(self._open_edit)
        del_btn  = action_btn("🗑️  Sil", "#dc2626", "#b91c1c")
        del_btn.clicked.connect(self._delete)
        bot.addWidget(edit_btn)
        bot.addWidget(del_btn)
        root.addLayout(bot)

    def _on_slider_changed(self, value):
        """Hafta 6: QSlider.valueChanged sinyali ile filtreleme."""
        self.slider_value_lbl.setText(str(value))
        self.refresh()

    def refresh(self):
        min_cap = self.cap_slider.value() if hasattr(self, 'cap_slider') else 1
        all_rooms = get_all_rooms()

        # Slider ile filtreleme
        filtered = [r for r in all_rooms if r["capacity"] >= min_cap]

        # Tablo güncelle
        self.table.setRowCount(0)
        for room in filtered:
            r = self.table.rowCount()
            self.table.insertRow(r)
            status = room["status"]
            bg = STATUS_COLORS.get(status, QColor("white"))
            pct = f"{room['occupant_count']}/{room['capacity']}"
            vals = [str(room["id"]), room["room_number"], str(room["floor"]),
                    str(room["capacity"]),
                    "Standart" if room["room_type"] == "standard" else "Deluxe",
                    status_label(status), pct]
            for c, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setData(Qt.UserRole, room["id"])
                item.setBackground(bg)
                item.setForeground(QColor("#1e293b"))  # Her zaman koyu ve okunabilir
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(r, c, item)

        # ══ Hafta 6: QListWidget – Kat Özeti güncelle ══
        if hasattr(self, 'floor_list'):
            self.floor_list.clear()
            floors = {}
            for room in all_rooms:
                floor = room["floor"]
                if floor not in floors:
                    floors[floor] = {"total": 0, "occupied": 0, "available": 0, "maintenance": 0, "rooms": []}
                floors[floor]["total"] += 1
                floors[floor][room["status"]] = floors[floor].get(room["status"], 0) + 1
                floors[floor]["rooms"].append(room["room_number"])

            for floor in sorted(floors.keys()):
                info = floors[floor]
                item_text = (f"🏢 Kat {floor}  —  "
                             f"Toplam: {info['total']} oda  |  "
                             f"Boş: {info.get('available', 0)}  |  "
                             f"Dolu: {info.get('occupied', 0)}  |  "
                             f"Bakımda: {info.get('maintenance', 0)}  |  "
                             f"Odalar: {', '.join(info['rooms'])}")
                list_item = QListWidgetItem(item_text)
                list_item.setForeground(QColor("#1e293b"))
                self.floor_list.addItem(list_item)

    def _selected_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 0).data(Qt.UserRole)

    def _open_add(self):
        dlg = RoomDialog(parent=self)
        if dlg.exec():
            self.refresh()

    def _open_edit(self):
        rid = self._selected_id()
        if not rid:
            QMessageBox.information(self, "Uyarı", "Lütfen bir oda seçin.")
            return
        dlg = RoomDialog(room_id=rid, parent=self)
        if dlg.exec():
            self.refresh()

    def _delete(self):
        rid = self._selected_id()
        if not rid:
            QMessageBox.information(self, "Uyarı", "Lütfen bir oda seçin.")
            return
        reply = QMessageBox.question(self, "Onay", "Bu oda silinsin mi?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            ok, msg = delete_room(rid)
            if ok:
                self.refresh()
            else:
                QMessageBox.critical(self, "Hata", msg)

    def _show_occupants(self):
        rid = self._selected_id()
        if not rid:
            return
        occupants = get_room_occupants(rid)
        if not occupants:
            QMessageBox.information(self, "Oda Sakinleri", "Bu odada aktif öğrenci bulunmuyor.")
            return
        names = "\n".join(f"• {o['name']} ({o['tc_no']})" for o in occupants)
        QMessageBox.information(self, "Oda Sakinleri", names)


class RoomDialog(QDialog):
    def __init__(self, room_id=None, parent=None):
        super().__init__(parent)
        self.room_id = room_id
        self.setWindowTitle("Oda Ekle" if not room_id else "Oda Düzenle")
        self.setMinimumWidth(380)
        self._build_ui()
        if room_id:
            self._load(room_id)

    def _build_ui(self):
        self.setStyleSheet("background: #f8fafc; color: #1e293b; font-family: 'Segoe UI';")
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        form = QFormLayout()
        form.setSpacing(10)

        inp_style = "background:white;border:1.5px solid #cbd5e1;border-radius:6px;padding:5px 10px;"

        self.room_no_e = QLineEdit()
        self.room_no_e.setStyleSheet(inp_style)
        self.floor_sb  = QSpinBox(); self.floor_sb.setRange(1, 30)
        self.floor_sb.setStyleSheet(inp_style)
        self.cap_sb    = QSpinBox(); self.cap_sb.setRange(1, 10)
        self.cap_sb.setStyleSheet(inp_style)

        self.type_cb   = QComboBox()
        self.type_cb.addItem("Standart", "standard")
        self.type_cb.addItem("Deluxe",   "deluxe")
        self.type_cb.setStyleSheet(inp_style)

        self.status_cb = QComboBox()
        self.status_cb.addItem("Boş",     "available")
        self.status_cb.addItem("Dolu",    "occupied")
        self.status_cb.addItem("Bakımda", "maintenance")
        self.status_cb.setStyleSheet(inp_style)

        form.addRow("Oda No *",   self.room_no_e)
        form.addRow("Kat *",      self.floor_sb)
        form.addRow("Kapasite *", self.cap_sb)
        form.addRow("Tür",        self.type_cb)
        form.addRow("Durum",      self.status_cb)
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

    def _load(self, rid):
        from database import get_connection
        conn = get_connection()
        r = conn.execute("SELECT * FROM rooms WHERE id=?", (rid,)).fetchone()
        conn.close()
        if not r:
            return
        self.room_no_e.setText(r["room_number"])
        self.floor_sb.setValue(r["floor"])
        self.cap_sb.setValue(r["capacity"])
        # DB değerine göre doğru index'i bul
        for i in range(self.type_cb.count()):
            if self.type_cb.itemData(i) == r["room_type"]:
                self.type_cb.setCurrentIndex(i)
                break
        for i in range(self.status_cb.count()):
            if self.status_cb.itemData(i) == r["status"]:
                self.status_cb.setCurrentIndex(i)
                break

    def _save(self):
        rn = self.room_no_e.text().strip()
        if not rn:
            QMessageBox.warning(self, "Uyarı", "Oda numarası zorunludur.")
            return
        if self.room_id:
            ok, msg = update_room(self.room_id, rn, self.floor_sb.value(),
                                  self.cap_sb.value(), self.type_cb.currentData(),
                                  self.status_cb.currentData())
        else:
            ok, msg = add_room(rn, self.floor_sb.value(), self.cap_sb.value(),
                               self.type_cb.currentData())
        if ok:
            self.accept()
        else:
            QMessageBox.critical(self, "Hata", msg)
