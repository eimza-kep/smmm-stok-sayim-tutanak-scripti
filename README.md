# SMMM & KOBİ Fiili Stok Sayım ve Envanter Tutanak Portalı

[![CI Test Suite](https://github.com/eimza-kep/smmm-stok-sayim-tutanak-scripti/actions/workflows/ci.yml/badge.svg)](https://github.com/eimza-kep/smmm-stok-sayim-tutanak-scripti/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://python.org)
[![PHP: 7.4+](https://img.shields.io/badge/PHP-7.4%2B-purple.svg)](https://php.net)

Mali müşavirler (SMMM/YMM), denetçiler, depo yöneticileri ve işletmeler için; 213 sayılı Vergi Usul Kanunu (VUK m. 186-191) ve Tekdüzen Hesap Planı hükümleri doğrultusunda **dönem sonu ve ara fiili stok sayımlarını dijitalleştiren**, **197/397 envanter farklarını otomatik hesaplayan** ve **resmi sayım heyeti tutanağını yazdıran** açık kaynaklı kurumsal yazılım.

---

## 🎯 Temel Yetenekler

- **VUK 186 Standartlarında Sayım Girişi:** Mükellef VKN/TCKN, vergi dairesi, depo adı, sayım heyeti (komisyon başkanı, sayım memuru, SMMM) ve sayım türü seçimi.
- **Dinamik Emtia Tablosu:** Sınırsız stok kalemi ekleme, barkod/stok kodu, kayıtlı stok, fiili sayım, birim maliyet ve anlık fark tutarı hesabı.
- **Otomatik 197 / 397 Muhasebe Fark Tespiti:** Sayım noksanları ve sayım fazlalarını otomatik belirler, net fark tutarını raporlar.
- **Resmi Heyet İmzalı Tutanak Çıktısı:** Vergi denetimlerinde ibraz edilebilir, kanuni formatta yazdırılabilir veya PDF olarak kaydedilebilir envanter tutanağı üretir.
- **SMMM & Mali İşler Yönetim Paneli (`/admin`):**
  - Tüm sayım tutanaklarının arşivlenmesi ve mükellefe göre filtrelenmesi.
  - Tutanak durum takibi: "Tutanak Tanzim Edildi", "Heyet Onayladı", "SMMM Tarafından Tasdik Edildi", "197/397 Yevmiye Kaydı Yapıldı".
  - Sayılan toplam emtia kalemi analitiği.
  - Excel uyumlu UTF-8 BOM destekli tek tıkla **CSV Dışa Aktarımı**.
- **Sıfır Bağımlılık (Zero-Dependency):**
  - **Python Motoru:** Dahili SQLite veritabanı ile tek tıkla lokalde veya sunucuda çalışır (`server.py`).
  - **PHP Motoru:** Paylaşımlı hosting ve cPanel için hazır JSON REST backend (`api.php`).
  - **Offline Mod:** İnternetsiz çalışma ve yerel tarayıcı hafızası (`localStorage`) desteği.

---

## 🚀 Hızlı Başlangıç

### Windows (Tek Tıkla Çalıştır)
1. Repoyu klonlayın veya zip olarak indirin.
2. `Baslat.bat` dosyasına çift tıklayın.
3. Otomatik olarak açılır:
   - Sayım Formu: `http://localhost:8088`
   - SMMM Yönetim Paneli: `http://localhost:8088/admin`

### Linux & macOS
```bash
git clone https://github.com/eimza-kep/smmm-stok-sayim-tutanak-scripti.git
cd smmm-stok-sayim-tutanak-scripti
chmod +x baslat.sh
./baslat.sh
```

### PHP / Paylaşımlı Hosting
Dosyaları sunucunuzdaki `/stok-sayim/` veya `/envanter/` dizinine yükleyin. `api.php` otomatik olarak JSON veritabanını oluşturup yönetecektir.

---

## 📊 Mimari ve Dosya Yapısı

```
smmm-stok-sayim-tutanak-scripti/
├── index.html              # Sayım formu, dinamik emtia tablosu ve resmi tutanak çıktısı
├── admin.html              # SMMM dosya ve envanter takip paneli
├── server.py               # Standalone Python SQLite HTTP sunucusu (Port 8088)
├── api.php                 # PHP tabanlı REST backend
├── Baslat.bat              # Windows tek tıkla başlatıcı
├── baslat.sh               # Linux / macOS başlatıcı
├── scripts/
│   └── test_sayim.py       # Otomatik test paketi
├── .github/
│   └── workflows/ci.yml    # GitHub Actions CI testi
└── README.md               # Dokümantasyon
```

---

## 🧪 Testleri Çalıştırma

```bash
python scripts/test_sayim.py
```

---

## ⚖️ Lisans

Bu proje [MIT Lisansı](LICENSE) kapsamında açık kaynak olarak sunulmuştur.
