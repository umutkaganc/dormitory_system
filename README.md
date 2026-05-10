# 🏢 Özel Yurt Takip Sistemi: Dijital Yurt ve Öğrenci Yönetim Otomasyonu

Bu proje, özel öğrenci yurtlarındaki zaman alan kayıt, ödeme, oda tahsisi ve personel yönetimi süreçlerini dijitalleştirip otomatize etmek amacıyla geliştirilmiş kapsamlı bir görsel programlama projesidir. Modern ve kullanıcı dostu bir arayüz üzerinden yurt yöneticilerine anlık veri takibi ve kolay yönetim imkanı sunar.

C# .NET Veritabanı (SQL) Windows Forms 

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

1. **Repoyu Klonlayın:**
```bash
git clone https://github.com/kullaniciadi/dormitory_system.git
cd dormitory_system
```

2. **Gereksinimleri Kurun ve Çalıştırın:**
- Projeyi **Visual Studio** (veya uyumlu bir IDE) ile açın.
- Projede kullanılan Veritabanı bağlantı yolunu (Connection String) kendi bilgisayarınıza göre güncelleyin.
- `Start` (Başlat) butonuna basarak projeyi derleyin ve çalıştırın.

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
- **Forms/:** Uygulamanın görsel arayüzlerini (Giriş, Ana Ekran, Öğrenci Kayıt vb.) barındıran form dosyaları.
- **Models/:** Veritabanı tablolarının C# nesne karşılıkları (Öğrenci, Oda, Personel sınıfları).
- **DataAccess/:** Veritabanı bağlantı (CRUD - Ekle, Oku, Güncelle, Sil) işlemlerinin yürütüldüğü backend katmanı.
- **Resources/:** Uygulama içerisinde kullanılan ikonlar, resimler ve tasarım materyalleri.

## 🔬 Proje Geliştirme Süreci
Proje, yazılım mühendisliği prensiplerine uygun olarak modüler bir mimariyle geliştirilmiştir. Veri güvenliği ve programın çökmeden (Exception Handling) stabil çalışması ön planda tutulmuştur.

## 🆕 Son Güncellemeler
**Versiyon 1.0 - Mayıs 2026**
- ✅ Öğrenci kayıt tablolarındaki kontrast ve renk sorunları giderilerek yüksek erişilebilirlik (Accessibility) sağlandı.
- ✅ TC Kimlik No gibi kritik veriler için 11 haneli doğrulama (Validation) mekanizmaları eklendi.
- ✅ Tüm uyarı ve durum mesajları (Status Labels) tamamen Türkçeleştirildi.
- ✅ Proje sunumu için profesyonel README dokümantasyonu hazırlandı.
