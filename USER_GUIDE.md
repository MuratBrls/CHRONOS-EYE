# CHRONOS-EYE - Kullanım Rehberi / User Guide 👁️

**AI Tabanlı Semantik Medya Arama Motoru**  
**AI-Powered Semantic Media Search Engine**

---

## 📚 İçindekiler / Table of Contents

1. [Kurulum / Installation](#kurulum--installation)
2. [İlk Kurulum / First Setup](#ilk-kurulum--first-setup)
3. [Masaüstü Uygulama / Desktop App](#masaüstü-uygulama--desktop-app)
4. [Web Arayüzü / Web Interface](#web-arayüzü--web-interface)
5. [Medya İndeksleme / Media Indexing](#medya-indeksleme--media-indexing)
6. [Arama Yapma / Searching](#arama-yapma--searching)
7. [İpuçları / Tips](#ipuçları--tips)
8. [Sorun Giderme / Troubleshooting](#sorun-giderme--troubleshooting)

---

## Kurulum / Installation

### Gereksinimler / Requirements

- **Python**: 3.10 veya üzeri / 3.10 or higher
- **İşletim Sistemi / OS**: Windows 10/11
- **RAM**: En az 8GB / Minimum 8GB
- **GPU**: CUDA destekli (opsiyonel ama önerilir) / CUDA-capable (optional but recommended)

### Adım 1: Repository'yi İndirin / Download Repository

```bash
git clone https://github.com/MuratBrls/CHRONOS-EYE.git
cd CHRONOS-EYE
```

### Adım 2: Sanal Ortam Oluşturun / Create Virtual Environment

```bash
python -m venv venv
.\venv\Scripts\activate
```

### Adım 3: Bağımlılıkları Yükleyin / Install Dependencies

```bash
pip install -r requirements.txt
```

**İlk kurulum 5-10 dakika sürebilir çünkü:**
- PyTorch ve CUDA kütüphaneleri büyük dosyalardır
- AI modelleri otomatik indirilecek (~1GB)

---

## İlk Kurulum / First Setup

### 1. Ortam Değişkenleri (Opsiyonel) / Environment Variables (Optional)

`.env.template` dosyasını `.env` olarak kopyalayın:

```bash
copy .env.template .env
```

### 2. İlk Çalıştırma / First Run

**Masaüstü Uygulama:**
```bash
python src/app.py
```

**Web Arayüzü:**
```bash
python web_app/server.py
```

### 3. AI Modeli İndirilmesi / AI Model Download

İlk çalıştırmada:
- CLIP modeli otomatik indirilecek (~500MB)
- İndirme sadece bir kez yapılır
- İnternet bağlantısı gereklidir

---

## Masaüstü Uygulama / Desktop App

### Başlatma / Launch

```bash
python src/app.py
```

### Arayüz / Interface

#### 1. Arama Motoru Sekmesi / Search Engine Tab

**Özellikler:**
- 🔍 Doğal dil araması
- 🖼️ Küçük resim önizlemeleri
- 📊 Eşleşme yüzdeleri
- 💾 Veritabanı istatistikleri

**Nasıl Kullanılır:**

1. **Arama kutusuna** sorgunuzu yazın
   - Örnek: "kadın yürüyor"
   - Örnek: "gün batımı manzara"

2. **"Search Locally" butonuna** tıklayın

3. **İlk aramada** AI modeli yüklenecek (30 saniye)

4. **Sonuçlara çift tıklayın** dosyayı açmak için

#### 2. Medya İndeksleyici Sekmesi / Media Indexer Tab

**Özellikler:**
- 📁 Klasör seçimi
- ⚡ Artımlı/Tam indeksleme
- 💻 VRAM optimizasyonu
- 📈 İlerleme çubuğu

**Nasıl Kullanılır:**

1. **"Browse..."** ile klasör seçin
2. **İndeksleme Modu** seçin:
   - `Incremental`: Sadece yeni dosyalar (hızlı)
   - `Full Re-index`: Tüm dosyalar (yavaş)
3. **VRAM Quantization** ayarlayın:
   - `float16`: Daha az bellek (önerilen)
   - `float32`: Daha yüksek hassasiyet
4. **"START INDEXING ENGINE"** tıklayın

---

## Web Arayüzü / Web Interface

### Başlatma / Launch

```bash
python web_app/server.py
```

Tarayıcıda açın: **http://localhost:8000**

### Özellikler / Features

**✅ Aynı özellikler, farklı arayüz:**
- Modern, responsive tasarım
- Koyu tema (mavi/mor)
- Gerçek zamanlı ilerleme
- Herhangi bir tarayıcıdan erişim

### Arama / Search

1. **"Search Engine" sekmesi** açık
2. Arama kutusuna sorgunuzu **yazın**
3. **"Search Locally"** tıklayın
4. Sonuçlara **tıklayın** dosyayı açmak için

### İndeksleme / Indexing

1. **"Media Indexer" sekmesine** geçin
2. Klasör yolunu **yazın** (örn: `C:\Users\...\Videos`)
   - VEYA **"Browse Folder"** butonunu kullanın
3. Ayarları yapın ve **"START INDEXING ENGINE"** tıklayın
4. **İlerleme çubuğunu** izleyin

---

## Medya İndeksleme / Media Indexing

### Desteklenen Formatlar / Supported Formats

**Videolar / Videos:**
- `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`, `.flv`, `.wmv`, `.m4v`

**Resimler / Images:**
- `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`

### İndeksleme Süreci / Indexing Process

1. **Dosya Taraması**: Klasördeki medya dosyalarını bulur
2. **Çıkarma**: 
   - Videolardan anahtar kareler (~30 kare/video)
   - Resimlerden doğrudan
3. **AI İşleme**: CLIP modeli semantic embeddings oluşturur
4. **Veritabanı**: ChromaDB'ye kaydeder

### Performans / Performance

| GPU | İşleme Hızı |
|-----|-------------|
| NVIDIA RTX 3060+ | ~50-100 medya/dakika |
| CPU Only | ~5-10 medya/dakika |

### İpuçları / Tips

✅ **İlk indeksleme için:**
- Küçük bir klasörle başlayın (10-20 dosya)
- GPU varsa `float16` kullanın
- Ağ sürücülerinden değil, yerel diskten indeksleyin

✅ **Tekrar indeksleme:**
- `Incremental` modu kullanın
- Sadece yeni dosyalar işlenir
- Çok daha hızlı

---

## Arama Yapma / Searching

### Sorgu Örnekleri / Query Examples

**Temel Arama / Basic Search:**
```
woman
man
person
landscape
city
```

**Detaylı Arama / Detailed Search:**
```
woman walking outdoor
sunset over mountains
person jumping
red dress
cinematic shot
```

**Sahne Tanımlama / Scene Description:**
```
indoor office
night scene
drone shot
close up
wide angle
```

### Sonuçları Anlama / Understanding Results

**Eşleşme Yüzdesi / Match Percentage:**
- **40%+**: Çok iyi eşleşme / Excellent match
- **30-40%**: İyi eşleşme / Good match
- **20-30%**: Zayıf eşleşme / Weak match
- **<20%**: Gösterilmez / Not shown

**Neden düşük skorlar?**
- Veritabanında tam eşleşme yok
- Sorgu çok spesifik
- Daha genel kelimeler deneyin

### Arama İpuçları / Search Tips

✅ **Başarılı aramalar için:**
1. **Basit başlayın**: "woman" yerine "young woman in red dress at sunset"
2. **Çeşitleyin**: Sonuç yoksa farklı kelimeler deneyin
3. **İngilizce kullanın**: AI modeli İngilizce eğitilmiştir
4. **Görsel öğelere odaklanın**: "mutlu" yerine "gülümseyen"

❌ **Kaçının:**
- Çok uzun cümleler
- Soyut kavramlar ("aşk", "özgürlük")
- Ses içeriği ("müzik", "ses")
- Metadata ("2024", "Canon EOS")

---

## İpuçları / Tips

### Performans Optimizasyonu / Performance Optimization

**GPU Kullanımı:**
```python
# Otomatik GPU tespiti aktif
# CUDA varsa otomatik kullanılır
```

**Bellek Yönetimi:**
- `float16` quantization kullanın (2x daha az VRAM)
- Batch size'ı azaltın (varsayılan: 32 → 16)
- Büyük videolar için scene detection kapalı tutun

**Hız:**
- İlk arama yavaştır (model yükleme)
- Sonraki aramalar anlıktır
- Veritabanı büyüdükçe aramalar yavaşlamaz

### En İyi Uygulamalar / Best Practices

**📁 Klasör Organizasyonu:**
```
Media/
├── Photos/
│   ├── 2024/
│   ├── 2023/
├── Videos/
    ├── Projects/
    ├── Personal/
```

**⚡ İndeksleme Stratejisi:**
1. Önce küçük klasörler
2. Test aramaları yapın
3. Sonra tüm koleksiyonu indeksleyin
4. Yeni dosyalar için `Incremental` kullanın

**🔍 Arama Stratejisi:**
1. Genel terimlerle başlayın
2. Sonuçlara bakın
3. Daha spesifik terimlere geçin
4. Farklı kelimeler deneyin

---

## Sorun Giderme / Troubleshooting

### Sık Karşılaşılan Sorunlar / Common Issues

#### 1. "ModuleNotFoundError: No module named 'chromadb'"

**Çözüm:**
```bash
.\venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. "CUDA out of memory"

**Çözüm:**
- `int8` quantization kullanın
- Batch size azaltın
- Küçük model kullanın: `clip-vit-base-patch32`

#### 3. Arama sonucu yok / No search results

**Nedenler:**
- Veritabanı boş → İndeksleme yapın
- Sorgu çok spesifik → Daha genel deneyin
- Threshold çok yüksek → %20'ye düşürün

#### 4. İndeksleme çok yavaş / Indexing too slow

**Çözümler:**
- GPU kullandığınızdan emin olun
- `float16` quantization seçin
- Scene detection'ı kapatın
- Daha az kare çıkarın

#### 5. Web arayüzü açılmıyor / Web interface won't open

**Kontrol edin:**
```bash
# Port 8000 kullanımda mı?
netstat -ano | findstr :8000

# Server çalışıyor mu?
python web_app/server.py
```

### Log Dosyaları / Log Files

**Konsol çıktısına bakın:**
- Hata mesajları ayrıntılıdır
- Model yükleme durumu gösterilir
- İndeksleme ilerlemesi raporlanır

---

## İleri Seviye / Advanced

### Model Seçimi / Model Selection

CHRONOS-EYE otomatik olarak model seçer:
- **512-dim DB** → `clip-vit-base-patch32` (hızlı)
- **768-dim DB** → `clip-vit-large-patch14` (kesin)

### Veritabanı Yönetimi / Database Management

**Konum / Location:**
```
chromadb_storage/
```

**Temizleme / Cleanup:**
```bash
# Veritabanını sıfırla
Remove-Item -Recurse chromadb_storage
# Yeniden indeksleyin
```

**Yedekleme / Backup:**
```bash
# Tüm klasörü kopyalayın
Copy-Item -Recurse chromadb_storage chromadb_storage_backup
```

### Özelleştirme / Customization

**Kod düzenleyerek:**
- Threshold değiştirin (`src/app.py`)
- Kare sayısını ayarlayın (`utils/frame_sampler.py`)
- Batch size değiştirin (`index.py`)

---

## Sıkça Sorulan Sorular / FAQ

**S: Hangi dillerde arama yapabilirim?**  
C: AI model İngilizce eğitilmiştir, en iyi sonuçlar İngilizce sorgularla gelir.

**S: Videolarda ses aranabilir mi?**  
C: Hayır, sadece görsel içerik aranır. Ses özelliği gelecekte eklenebilir.

**S: Kaç dosya indeksleyebilirim?**  
C: Sınır yoktur, ancak büyük veritabanları (>10,000 dosya) daha fazla disk ve RAM kullanır.

**S: Internet gerekli mi?**  
C: Sadece ilk kurulumda (model indirme). Sonrasında tamamen çevrimdışı çalışır.

**S: Masaüstü ve web aynı anda çalışabilir mi?**  
C: Evet! Aynı veritabanını paylaşırlar.

---

## Destek / Support

**Sorunlarınız için / For issues:**
- GitHub Issues: https://github.com/MuratBrls/CHRONOS-EYE/issues
- README dosyasını okuyun
- Bu rehberi kontrol edin

**Katkıda bulunun / Contribute:**
- Pull requests memnuniyetle karşılanır
- Fork → Edit → PR

---

## Lisans / License

MIT License - Detaylar için LICENSE dosyasına bakın.

---

**CHRONOS-EYE ile medya koleksiyonunuzu akıllı şekilde arayın! 👁️✨**

**Search your media collection intelligently with CHRONOS-EYE! 👁️✨**
