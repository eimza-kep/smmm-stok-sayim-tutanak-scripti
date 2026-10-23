# SMMM & KOBİ Fiili Stok Sayım ve Envanter Tutanak Portalı

[![CI Test Suite](https://github.com/eimza-kep/smmm-stok-sayim-tutanak-scripti/actions/workflows/ci.yml/badge.svg)](https://github.com/eimza-kep/smmm-stok-sayim-tutanak-scripti/actions/workflows/ci.yml)
[![Canlı Demo](https://img.shields.io/badge/Demo-Canl%C4%B1%20Test%20Et-brightgreen.svg)](https://eimza-kep.github.io/smmm-stok-sayim-tutanak-scripti/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://python.org)
[![PHP: 7.4+](https://img.shields.io/badge/PHP-7.4%2B-purple.svg)](https://php.net)
[![Docker Support](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](Dockerfile)

Mali müşavirler (SMMM/YMM), denetçiler, depo yöneticileri ve işletmeler için; 213 sayılı Vergi Usul Kanunu (VUK m. 186-191) ve Tekdüzen Hesap Planı hükümleri doğrultusunda **Kamera ile Barkod/QR Okutarak Sayım Yapan**, **GİB e-İrsaliye Sevk Kalemleri ile Anlık Mutabakat Sağlayan**, **197/397 Envanter Farklarını Otomatik Hesaplayan** ve **Resmi Sayım Heyeti Tutanağını Basan** açık kaynaklı kurumsal envanter yazılımı.

---

## 🎯 Temel Yetenekler ve Özellikler

- **📷 Kamera ile Barkod / QR Kod Okuyucu (HTML5 Barcode Scanner):**
  - Akıllı telefon veya bilgisayar kamerasıyla sıfır ek donanım / el terminali gerektirmeden EAN-13, Code-128 ve QR kodları tarar.
  - Web Audio API ile dahili sesli teyit ("bip") ve haptik titreşim (`navigator.vibrate`) geri bildirimi.
  - Barkodu okunan ürünün fiili sayım miktarını otomatik 1 artırır; listede yoksa anında yeni kalem olarak ekler.
- **🧾 GİB e-İrsaliye Otomatik Karşılaştırma ve Mutabakat Motoru:**
  - Sevk irsaliyesi kalemleri (UBL-TR 2.1 XML veya JSON) ile depoda fiilen sayılan emtiayı otomatik eşleştirir.
  - Eksik teslimat (Fire / Noksan) ve fazla teslimat miktarlarını anında tespit eder.
  - 213 Sayılı VUK m.186 uyarınca **197 Sayım ve Tesellüm Noksanları** ve **397 Sayım ve Tesellüm Fazlaları** yevmiye hesap açıklamalarını otomatik üretir.
- **VUK 186 Standartlarında Sayım Girişi:**
  - Mükellef VKN/TCKN, vergi dairesi, depo adı, sayım heyeti (komisyon başkanı, sayım memuru, SMMM) ve sayım türü seçimi.
- **Dinamik Emtia Tablosu:**
  - Sınırsız stok kalemi ekleme, kayıtlı/irsaliye stoku, fiili sayım, birim maliyet ve anlık fark tutarı hesabı.
- **Resmi Heyet İmzalı Tutanak Çıktısı:**
  - Vergi denetimlerinde ibraz edilebilir, kanuni formatta yazdırılabilir veya PDF olarak kaydedilebilir e-İrsaliye mutabakat dökümlü resmi envanter tutanağı üretir.
- **SMMM & Mali İşler Yönetim Paneli (`admin.html`):**
  - Tüm sayım tutanaklarının arşivlenmesi ve mükellefe göre filtrelenmesi.
  - Tutanak durum takibi: "Tutanak Tanzim Edildi", "SMMM Tarafından Tasdik Edildi", "197/397 Yevmiye Kaydı Yapıldı", "İtiraz / Yeniden Sayım".
  - `📷 Barkodlu` ve `🧾 e-İrsaliye` rozetleri ile dosya ayrıştırma.
  - Excel uyumlu UTF-8 BOM destekli tek tıkla **CSV Dışa Aktarımı**.
- **Sıfır Bağımlılık (Zero-Dependency) Çift Motorlu Mimari:**
  - **Python Motoru:** Dahili SQLite veritabanı ile tek tıkla lokalde veya sunucuda çalışır (`server.py`).
  - **PHP Motoru:** Paylaşımlı hosting ve cPanel için hazır JSON REST backend (`api.php`).
  - **Offline Mod:** İnternetsiz çalışma ve yerel tarayıcı hafızası (`localStorage`) desteği.

---

## 🚀 Hızlı Başlangıç ve Kurulum Rehberi

### Seçenek 1: Windows (Tek Tıkla Çalıştır)
1. Repoyu klonlayın veya indirin:
   ```bash
   git clone https://github.com/eimza-kep/smmm-stok-sayim-tutanak-scripti.git
   cd smmm-stok-sayim-tutanak-scripti
   ```
2. `Baslat.bat` dosyasına çift tıklayın.
3. Otomatik olarak açılır:
   - Sayım Formu: `http://localhost:8088`
   - SMMM Yönetim Paneli: `http://localhost:8088/admin`

### Seçenek 2: Linux & macOS
```bash
git clone https://github.com/eimza-kep/smmm-stok-sayim-tutanak-scripti.git
cd smmm-stok-sayim-tutanak-scripti
chmod +x baslat.sh
./baslat.sh
```

### Seçenek 3: Docker ile Çalıştırma
```bash
# Docker imajını derleyin ve başlatın
docker build -t smmm-stok-sayim-scripti .
docker run -d -p 8088:8088 --name smmm-stok-sayim smmm-stok-sayim-scripti

# Tarayıcıdan erişin:
# http://localhost:8088
```

### Seçenek 4: PHP / Paylaşımlı Hosting (cPanel / Plesk)
Dosyaları sunucunuzdaki `/stok-sayim/` veya `/envanter/` ana dizinine yükleyin. `api.php` otomatik olarak JSON veritabanını (`stok_sayimlar.json`) oluşturup yönetecektir.

---

## 🔌 REST API Referansı

| Metot | Uç Nokta (Endpoint) | Açıklama |
| :--- | :--- | :--- |
| `POST` | `/api/sayim-kaydet` | Yeni sayım tutanağı kaydeder (`barcode_count_used`, `eirsaliye_matched` destekli). |
| `GET` | `/api/sayimlar` | Tüm stok sayım tutanaklarını JSON formatında döndürür. |
| `POST` | `/api/eirsaliye-mutabakat` | Fiili sayım ile e-İrsaliye sevk kalemlerini karşılaştırır ve 197/397 farklarını hesaplar. |
| `POST` | `/api/durum-guncelle` | Sayım tutanağının tasdik durumunu günceller (`tracking_code`, `status`). |
| `GET` | `/health` | Servis sağlık durumunu ve port bilgisini döndürür. |

---

## 📊 Mimari ve Dosya Yapısı

```
smmm-stok-sayim-tutanak-scripti/
├── index.html                    # Sayım formu, kamera barkod okuyucu ve resmi tutanak çıktısı
├── admin.html                    # SMMM dosya ve envanter takip paneli (Barkod & e-İrsaliye rozetli)
├── server.py                     # Standalone Python SQLite HTTP sunucusu (Port 8088)
├── api.php                       # PHP tabanlı REST backend
├── Baslat.bat                    # Windows tek tıkla başlatıcı
├── baslat.sh                     # Linux / macOS başlatıcı
├── Dockerfile                    # Docker konteyner konfigürasyonu
├── scripts/
│   ├── eirsaliye_mutabakat_engine.py  # e-İrsaliye UBL XML ve mutabakat motoru
│   └── test_sayim.py             # Otomatik birim test paketi
├── .github/
│   └── workflows/ci.yml          # GitHub Actions CI testi
└── README.md                     # Kapsamlı dokümantasyon
```

---

## 🧪 Testleri Çalıştırma

Tüm mutabakat ve veri tabanı akışları birim testlerle korunmaktadır:

```bash
python scripts/test_sayim.py
```

---

## 🌐 E-Dönüşüm Açık Kaynak Ekosistemi

Bu tutanak yönetim aracı, [@eimza-kep](https://github.com/eimza-kep) açık kaynak ekosisteminin envanter ve muhasebe denetim modülüdür. İlgili diğer araçlar:

* 📊 [muhasebe-excel-sablonlari](https://github.com/eimza-kep/muhasebe-excel-sablonlari) - Amortisman, stok ve gelir tablosu kontrol Excel şablonları.
* 🏢 [kobi-finans-yonetim-excel-sablonlari](https://github.com/eimza-kep/kobi-finans-yonetim-excel-sablonlari) - Stok takip, kritik seviye uyarı ve başabaş analizi araçları.
* 📄 [e-fatura-xml-goruntuleyici](https://github.com/eimza-kep/e-fatura-xml-goruntuleyici) - e-İrsaliye fiili sevk ve mal teslim bilgisi ayrıştırma aracı.
* 📨 [muhasebe-mukellef-evrak-scripti](https://github.com/eimza-kep/muhasebe-mukellef-evrak-scripti) - Mükelleflerden aylık evrak ve fatura toplama portali.
* 🌟 [awesome-turkiye-e-donusum](https://github.com/eimza-kep/awesome-turkiye-e-donusum) - Türkiye e-Dönüşüm açık kaynak araçları ve kütüphaneleri kürasyonu.

---

## ⚖️ Lisans

Bu proje [MIT Lisansı](LICENSE) kapsamında açık kaynak olarak sunulmuştur.
