"""
views/report_view.py
Rapor ve istatistik ekranı – doluluk, aylık gelir grafikleri.

Hafta 6: QProgressBar (doluluk göstergesi)
Hafta 5: QFileDialog (CSV dışa aktarma), QInputDialog (başlık alma)
Hafta 3: QGridLayout (istatistik kartları)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGridLayout, QFrame, QSizePolicy, QPushButton,
    QProgressBar, QFileDialog, QInputDialog, QMessageBox  # Hafta 5 & 6
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

from models.room    import get_all_rooms
from models.student import get_all_students
from models.payment import get_all_payments, get_overdue_payments, get_monthly_summary

try:
    import matplotlib
    matplotlib.use("QtAgg")
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    HAS_MATPLOTLIB = True
except Exception:
    HAS_MATPLOTLIB = False


def stat_card(title: str, value: str, color: str = "#6366f1") -> QFrame:
    card = QFrame()
    card.setStyleSheet(f"""
        QFrame {{
            background: white;
            border-radius: 14px;
            border-left: 5px solid {color};
        }}
    """)
    card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    card.setFixedHeight(100)
    layout = QVBoxLayout(card)
    layout.setContentsMargins(20, 14, 20, 14)
    val_lbl = QLabel(value)
    val_lbl.setFont(QFont("Segoe UI", 26, QFont.Bold))
    val_lbl.setStyleSheet(f"color: {color}; background: transparent;")
    ttl_lbl = QLabel(title)
    ttl_lbl.setFont(QFont("Segoe UI", 11))
    ttl_lbl.setStyleSheet("color: #64748b; background: transparent;")
    layout.addWidget(val_lbl)
    layout.addWidget(ttl_lbl)
    return card


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


class ReportView(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(28, 24, 28, 24)
        self.root.setSpacing(20)

        # Başlık satırı + butonlar
        top = QHBoxLayout()
        title = QLabel("📊 Raporlar & İstatistikler")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #1e293b;")
        top.addWidget(title)
        top.addStretch()

        # Hafta 5: QInputDialog + QFileDialog ile rapor dışa aktarma
        export_btn = action_btn("📥 Rapor Dışa Aktar")
        export_btn.clicked.connect(self._export_report)
        top.addWidget(export_btn)
        self.root.addLayout(top)

        # Hafta 3: QGridLayout – Stat kartları grid
        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(16)
        self.root.addLayout(self.cards_layout)

        # ══ Hafta 6: QProgressBar – Doluluk oranı ══
        progress_frame = QFrame()
        progress_frame.setStyleSheet("background: white; border-radius: 12px; padding: 4px;")
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(20, 14, 20, 14)

        progress_title = QLabel("🏨 Oda Doluluk Oranı")
        progress_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        progress_title.setStyleSheet("color: #1e293b; background: transparent;")
        progress_layout.addWidget(progress_title)

        self.occupancy_bar = QProgressBar()
        self.occupancy_bar.setMinimum(0)
        self.occupancy_bar.setMaximum(100)
        self.occupancy_bar.setValue(0)
        self.occupancy_bar.setTextVisible(True)
        self.occupancy_bar.setFormat("%v% doluluk")
        self.occupancy_bar.setFixedHeight(28)
        self.occupancy_bar.setStyleSheet("""
            QProgressBar {
                border: none; background: #e2e8f0; border-radius: 14px;
                text-align: center; color: #1e293b; font-weight: bold; font-size: 12px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #6366f1,stop:1 #8b5cf6);
                border-radius: 14px;
            }
        """)
        progress_layout.addWidget(self.occupancy_bar)

        self.occupancy_label = QLabel("")
        self.occupancy_label.setStyleSheet("color: #64748b; font-size: 11px; background: transparent;")
        progress_layout.addWidget(self.occupancy_label)
        self.root.addWidget(progress_frame)

        # Grafik alanı
        if HAS_MATPLOTLIB:
            self.fig = Figure(figsize=(12, 5), facecolor="#f1f5f9")
            self.canvas = FigureCanvas(self.fig)
            self.canvas.setMinimumHeight(300)
            self.root.addWidget(self.canvas)
        else:
            warn = QLabel("📦 Grafik görüntülemek için matplotlib kurun:\n  pip install matplotlib")
            warn.setStyleSheet("color:#64748b; font-size:13px; padding:20px;")
            warn.setAlignment(Qt.AlignCenter)
            self.root.addWidget(warn)

        self.root.addStretch()

    def refresh(self):
        # Verileri topla
        rooms    = get_all_rooms()
        students = get_all_students()
        payments = get_all_payments()
        overdue  = get_overdue_payments()

        total_rooms   = len(rooms)
        occupied      = sum(1 for r in rooms if r["status"] == "occupied")
        available     = sum(1 for r in rooms if r["status"] == "available")
        total_students= len(students)
        total_income  = sum(p["amount"] for p in payments if p["status"] == "paid")
        overdue_count = len(overdue)

        # Kartları yenile
        for i in reversed(range(self.cards_layout.count())):
            self.cards_layout.itemAt(i).widget().setParent(None)

        cards = [
            ("Toplam Oda",      str(total_rooms),    "#6366f1"),
            ("Dolu Oda",        str(occupied),        "#ef4444"),
            ("Boş Oda",         str(available),       "#10b981"),
            ("Öğrenci Sayısı",  str(total_students),  "#3b82f6"),
            ("Toplanan Gelir",  f"₺{total_income:,.0f}", "#f59e0b"),
            ("Gecikmiş Ödeme",  str(overdue_count),   "#dc2626"),
        ]
        for idx, (title, val, color) in enumerate(cards):
            self.cards_layout.addWidget(stat_card(title, val, color),
                                        idx // 3, idx % 3)

        # ══ Hafta 6: QProgressBar güncelle ══
        if total_rooms > 0:
            pct = int((occupied / total_rooms) * 100)
            self.occupancy_bar.setValue(pct)
            self.occupancy_label.setText(f"{occupied}/{total_rooms} oda dolu")
        else:
            self.occupancy_bar.setValue(0)
            self.occupancy_label.setText("Oda verisi yok")

        if HAS_MATPLOTLIB:
            self._draw_charts(rooms, payments)

    def _export_report(self):
        """
        Hafta 5: QInputDialog ile kullanıcıdan rapor başlığı al,
        ardından QFileDialog ile dosya konumu seç.
        """
        # QInputDialog – kullanıcıdan başlık alma
        report_title, ok = QInputDialog.getText(
            self,
            "Rapor Başlığı",
            "Rapor için bir başlık girin:"
        )
        if not ok or not report_title.strip():
            return

        # QFileDialog – dosya kaydetme dialogu
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Raporu Kaydet",
            "",
            "CSV Dosyası (*.csv);;Text Dosyası (*.txt)"
        )
        if not file_name:
            return

        try:
            rooms = get_all_rooms()
            students = get_all_students()
            payments = get_all_payments()
            overdue = get_overdue_payments()

            with open(file_name, "w", encoding="utf-8-sig") as f:
                f.write(f"Rapor: {report_title}\n")
                f.write(f"{'='*50}\n\n")

                f.write(f"Toplam Oda: {len(rooms)}\n")
                occupied = sum(1 for r in rooms if r["status"] == "occupied")
                f.write(f"Dolu Oda: {occupied}\n")
                f.write(f"Boş Oda: {sum(1 for r in rooms if r['status'] == 'available')}\n")
                f.write(f"Öğrenci Sayısı: {len(students)}\n")
                total_income = sum(p["amount"] for p in payments if p["status"] == "paid")
                f.write(f"Toplanan Gelir: ₺{total_income:,.2f}\n")
                f.write(f"Gecikmiş Ödeme: {len(overdue)}\n\n")

                # Doluluk oranı
                if len(rooms) > 0:
                    f.write(f"Doluluk Oranı: %{int(occupied/len(rooms)*100)}\n\n")

                # Öğrenci listesi
                f.write("Öğrenci Listesi:\n")
                f.write("-"*40 + "\n")
                for s in students:
                    f.write(f"  {s['name']} - TC: {s['tc_no']} - Oda: {s['room_number'] or 'Yok'}\n")

            # Hafta 5: QMessageBox.information ile bilgi mesajı
            QMessageBox.information(self, "Başarılı",
                                    f"Rapor başarıyla kaydedildi:\n{file_name}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Rapor kaydedilirken hata:\n{e}")

    def _draw_charts(self, rooms, payments):
        self.fig.clear()
        self.fig.set_facecolor("#f1f5f9")

        counts = {
            "Dolu":    sum(1 for r in rooms if r["status"] == "occupied"),
            "Boş":     sum(1 for r in rooms if r["status"] == "available"),
            "Bakımda": sum(1 for r in rooms if r["status"] == "maintenance"),
        }
        labels = [k for k, v in counts.items() if v > 0]
        values = [v for v in counts.values() if v > 0]
        # Renkler sırayla: dolu=kırmızı, boş=yeşil, bakımda=turuncu
        all_colors = {"Dolu": "#ef4444", "Boş": "#10b981", "Bakımda": "#f59e0b"}
        colors = [all_colors[l] for l in labels]

        # ── Sol: Doluluk pasta grafiği ──
        ax1 = self.fig.add_subplot(1, 2, 1)
        if values:
            wedges, texts, autotexts = ax1.pie(
                values, colors=colors,
                autopct="%1.0f%%", startangle=90,
                textprops={"fontsize": 13, "fontweight": "bold"},
                wedgeprops={"linewidth": 2, "edgecolor": "white"},
                pctdistance=0.65,
                radius=0.85,
            )
            for at in autotexts:
                at.set_color("white")
                at.set_fontsize(13)
            # Etiketleri üst üste gelmeden legend ile göster
            ax1.legend(
                wedges, [f"{l}  ({v})" for l, v in zip(labels, values)],
                loc="lower center", bbox_to_anchor=(0.5, -0.14),
                fontsize=11, framealpha=0.8, ncol=len(labels)
            )
        else:
            ax1.text(0.5, 0.5, "Oda verisi yok",
                     ha="center", va="center", transform=ax1.transAxes,
                     fontsize=13, color="#94a3b8")
        ax1.set_title("Oda Doluluk Oranı", fontsize=13, fontweight="bold", pad=14, color="#1e293b")
        ax1.set_facecolor("#f1f5f9")

        # ── Sağ: Aylık gelir çubuk grafiği ──
        ax2 = self.fig.add_subplot(1, 2, 2)
        monthly = get_monthly_summary()
        if monthly:
            months    = [r["month"] for r in monthly]
            totals    = [r["total"]     for r in monthly]
            collected = [r["collected"] for r in monthly]
            x = list(range(len(months)))
            ax2.bar([i - 0.2 for i in x], totals,    width=0.38,
                    label="Tahakkuk", color="#6366f1", alpha=0.85, zorder=3)
            ax2.bar([i + 0.2 for i in x], collected, width=0.38,
                    label="Tahsilat", color="#10b981", alpha=0.85, zorder=3)
            ax2.set_xticks(x)
            ax2.set_xticklabels(months, rotation=30, ha="right", fontsize=9)
            ax2.set_title("Aylık Gelir Özeti (₺)", fontsize=12, fontweight="bold", pad=14, color="#1e293b")
            ax2.legend(fontsize=9, framealpha=0.8)
            ax2.set_facecolor("white")
            ax2.grid(axis="y", linestyle="--", alpha=0.4, zorder=0)
            ax2.spines["top"].set_visible(False)
            ax2.spines["right"].set_visible(False)
        else:
            ax2.text(0.5, 0.5, "Ödeme verisi yok",
                     ha="center", va="center", transform=ax2.transAxes,
                     fontsize=13, color="#94a3b8")
            ax2.set_facecolor("white")
            ax2.set_xticks([])
            ax2.set_yticks([])
            for spine in ax2.spines.values():
                spine.set_visible(False)
            ax2.set_title("Aylık Gelir Özeti (₺)", fontsize=12, fontweight="bold", pad=14, color="#1e293b")

        self.fig.tight_layout(pad=2.5, w_pad=3.0)
        self.canvas.draw()
