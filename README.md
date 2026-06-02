# 🏢 Özel Yurt Takip Sistemi: Dijital Yurt ve Öğrenci Yönetim Otomasyonu

Bu proje, özel öğrenci yurtlarındaki zaman alan kayıt, ödeme, oda tahsisi ve personel yönetimi süreçlerini dijitalleştirip otomatize etmek amacıyla geliştirilmiş kapsamlı bir görsel programlama projesidir. Modern ve kullanıcı dostu bir arayüz üzerinden yurt yöneticilerine anlık veri takibi ve kolay yönetim imkanı sunar.

Python PySide6 SQLite

## 🚀 Özellikler
- **Kapsamlı Öğrenci Yönetimi:** Öğrenci kayıt, silme, güncelleme ve TC kimlik no / isim bazlı hızlı arama işlemleri.
- **Dinamik Oda Takibi:** Odaların doluluk oranları, kalan boş yatak kapasiteleri ve öğrencilerin odalara interaktif olarak atanması.
- **Finansal İşlemler (Aidat Takibi):** Öğrenci taksit ödemeleri, geciken ödemelerin tespiti ve makbuz/ödeme kayıtlarının tutulması.
- **Personel Modülü:** Yurtta görevli personelin (güvenlik, temizlik, idari vb.) kayıtlarının ve iletişim bilgilerinin yönetimi.
- **Modern ve Temiz Arayüz:** Kullanıcı deneyimini (UX) merkeze alan, yüksek kontrastlı ve okunaklı, profesyonel masaüstü tasarım.
- **Rol Tabanlı Erişim:** Yönetici ve yetkilendirilmiş personel için güvenli giriş (Login) sistemi.

## 🧠 Modüller ve Katkıda Bulunanlar
Proje, Görsel Programlama II dersi kapsamında geliştirilmiş olup, ekip üyelerinin iş bölümü şu şekildedir:

**Geliştirici Ekip:**
- **Umut Kağan Ceylan** (Arayüz Tasarımı, UI/UX Optimizasyonu ve Sistem Entegrasyonu)
- **Yiğit Alakuş** (Veritabanı Mimarisi, Backend Mantığı ve Veri İşlemleri)
- **Yakup Sevinç** (Modül Geliştirme, Hata Ayıklama ve Test Süreçleri)

## 🛠️ Kurulum
Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin:

### Gereksinimler
- **Python 3.13+** → [python.org](https://www.python.org/downloads/) adresinden indirilebilir
- **pip** (Python ile birlikte otomatik gelir)

---

### 🔵 Yöntem 1 — Git ile Klonlama

1. **Repoyu Klonlayın:**
```bash
git clone https://github.com/kullaniciadi/dormitory_system.git
cd dormitory_system
```

2. **Sanal Ortam Oluşturun (Önerilen):**
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
```

3. **Bağımlılıkları Yükleyin:**
```bash
pip install -r requirements.txt
```

4. **Uygulamayı Başlatın:**
```bash
python main.py
```

---

### 🟢 Yöntem 2 — ZIP Dosyasından Kurulum

1. **ZIP dosyasını indirin** ve bilgisayarınızda istediğiniz bir konuma çıkartın.

2. **Komut İstemi (CMD) veya PowerShell'i açın** ve projenin klasörüne gidin:
```bash
cd C:\...\dormitory_system
```
> 💡 Dosya Gezgini'nde klasörü açıp adres çubuğuna `cmd` yazıp Enter'a basarak da aynı klasörde terminal açabilirsiniz.

3. **Sanal Ortam Oluşturun (Önerilen):**
```bash
python -m venv venv
venv\Scripts\activate
```

4. **Bağımlılıkları Yükleyin:**
```bash
pip install -r requirements.txt
```

> `requirements.txt` dosyası projenin ihtiyaç duyduğu tek harici kütüphane olan **PySide6**'yı içermektedir.  
> `sqlite3`, `hashlib`, `re`, `os`, `sys`, `datetime` gibi modüller Python standart kütüphanesine dahildir — ayrıca kurulum gerektirmez.

5. **Uygulamayı Başlatın:**
```bash
python main.py
```

## ▶️ Kullanım
Uygulamayı başlattığınızda sistem sizi aşağıdaki süreçlerden geçirir:

**🔍 Giriş Ekranı (Login):**
- Güvenli erişim için yönetici kullanıcı adı ve şifrenizi girin.
- Rol tabanlı yetkilendirme ile sisteme giriş yapın.

**📊 Öğrenci ve Oda Paneli:**
- Sol menüden "Öğrenciler" sekmesine tıklayarak tüm kayıtlı öğrencileri listeleyin.
- "Odalar" sekmesinden hangi odada kaç boş yatak kaldığını görsel tablolar üzerinden anlık olarak analiz edin.

**💰 Kasa ve Ödemeler:**
- Öğrencilerin aylık ödemelerini sisteme girin, kalan borçlarını hesaplayın ve finansal durumu takip edin.

## 📂 Dosya Yapısı (Özet)
```
dormitory_system/
├── main.py              # Uygulamanın giriş noktası
├── database.py          # SQLite veritabanı bağlantı ve CRUD işlemleri
├── requirements.txt     # Harici bağımlılıklar (PySide6)
├── resources.qrc        # Qt kaynak dosyası (ikonlar vb.)
├── resources_rc.py      # Derlenmiş Qt kaynakları
├── models/              # Veritabanı tablo modellerinin Python sınıfları
├── views/               # PySide6 arayüz ekranları (Giriş, Ana Ekran vb.)
├── utils/               # Yardımcı fonksiyonlar ve araçlar
├── icons/               # Uygulama içi ikon dosyaları
└── dormitory.db         # SQLite veritabanı dosyası (çalışma zamanında oluşur)
```

## 🔬 Proje Geliştirme Süreci
Proje, yazılım mühendisliği prensiplerine uygun olarak modüler bir mimariyle geliştirilmiştir. Veri güvenliği ve programın çökmeden (Exception Handling) stabil çalışması ön planda tutulmuştur.

## 🆕 Son Güncellemeler
**Versiyon 2.0 - Haziran 2026**
- ✅ Proje **C# .NET / SQL Server** altyapısından **Python / PySide6 / SQLite** altyapısına taşındı.
- ✅ `requirements.txt` eklenerek bağımlılık yönetimi standart hale getirildi.
- ✅ Veritabanı kurulumu artık tamamen otomatik; harici bir sunucu bağlantısı gerekmez.

**Versiyon 1.0 - Mayıs 2026**
- ✅ Öğrenci kayıt tablolarındaki kontrast ve renk sorunları giderilerek yüksek erişilebilirlik (Accessibility) sağlandı.
- ✅ TC Kimlik No gibi kritik veriler için 11 haneli doğrulama (Validation) mekanizmaları eklendi.
- ✅ Tüm uyarı ve durum mesajları (Status Labels) tamamen Türkçeleştirildi.
- ✅ Proje sunumu için profesyonel README dokümantasyonu hazırlandı.
