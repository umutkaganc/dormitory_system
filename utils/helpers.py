"""
utils/helpers.py
Ortak yardımcı fonksiyonlar: tarih, validasyon, mesaj.
"""

import re
from datetime import date


def today_str() -> str:
    return date.today().isoformat()


def validate_tc(tc: str) -> bool:
    """11 haneli TC Kimlik No formatını kontrol eder."""
    return bool(re.fullmatch(r"[1-9]\d{10}", tc.strip()))


def validate_phone(phone: str) -> bool:
    """Türkiye cep telefonu formatını kontrol eder (05XX veya +905XX)."""
    digits = re.sub(r"[\s\-()]", "", phone)
    return bool(re.fullmatch(r"(\+90|0)?5\d{9}", digits))


def validate_email(email: str) -> bool:
    if not email:
        return True  # E-posta isteğe bağlı
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))


def status_label(status: str) -> str:
    """DB status değerini Türkçe etikete çevirir."""
    labels = {
        "available": "Boş",
        "occupied":  "Dolu",
        "maintenance": "Bakımda",
        "pending":  "Bekliyor",
        "paid":     "Ödendi",
        "overdue":  "Gecikmiş",
        "open":        "Açık",
        "in_progress": "İşlemde",
        "resolved":    "Çözüldü",
        "admin": "Yönetici",
        "staff": "Personel",
    }
    return labels.get(status, status)


def status_color(status: str) -> str:
    """Her durum için arka plan rengi (hex)."""
    colors = {
        "available":   "#e6f4ea",
        "occupied":    "#fce8e6",
        "maintenance": "#fff3e0",
        "pending":     "#fff9c4",
        "paid":        "#e6f4ea",
        "overdue":     "#fce8e6",
        "open":        "#e8f0fe",
        "in_progress": "#fff3e0",
        "resolved":    "#e6f4ea",
    }
    return colors.get(status, "#ffffff")
