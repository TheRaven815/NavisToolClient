# 🏗️ Navisworks Tool Client

Bu araç, Navisworks için geliştirilen pluginlerin (eklentilerin) kurulum ve güncelleme süreçlerini otomatize etmek için tasarlanmıştır. Belirlenen Navisworks sürümlerini otomatik olarak algılar, eski plugin dosyalarını temizler ve güncel sürümleri ilgili dizinlere güvenli bir şekilde aktarır.

## 🌟 Öne Çıkan Özellikler

- **Otomatik Algılama:** Bilgisayarınızda yüklü olan Navisworks Manage sürümlerini (2022-2025+) otomatik olarak tespit eder.
- **Temiz Kurulum:** Yeni plugin dosyalarını kopyalamadan önce, hedef klasördeki eski kalıntıları tamamen temizler.
- **Çoklu Dağıtım:** Tek tıkla birden fazla Navisworks sürümüne aynı anda kurulum yapabilir.
- **Otomatik Güncelleme:** Uygulamanın kendisi için yeni bir sürüm olup olmadığını kontrol eder ve tek tıkla günceller.
- **Modern Arayüz:** PySide6 ile geliştirilmiş, minimalist ve göz yormayan karanlık tema (Dark Mode) desteği.
- **Kolay Konfigürasyon:** `config.json` dosyası üzerinden plugin adı, kaynak klasör ve hedef yollar kolayca değiştirilebilir.

## 📋 Gereksinimler

- **Windows İşletim Sistemi** (Navisworks gereği)
- **Python 3.8+**
- **Navisworks Manage** (Eklentilerin kurulacağı ana yazılım)

## 🚀 Kurulum

1. Depoyu bilgisayarınıza klonlayın:
   ```bash
   git clone https://github.com/TheRaven815/NavisToolClient.git
   cd NavisToolClient
   ```

2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

## 🛠️ Yapılandırma (config.json)

Uygulamanın çalışması için root dizininde bulunan `config.json` dosyasını kendi projenize göre düzenleyebilirsiniz:

```json
{
    "plugin_name": "NavisIFCExport",
    "source_folder_name": "NavisIFCExport",
    "version_folder_prefix": "Navis",
    "navis_versions": [ "2022", "2023", "2024", "2025" ],
    "target_base_path": "C:/ProgramData/Autodesk/Navisworks Manage {version}/Plugins"
}
```

- `plugin_name`: Kurulacak olan pluginin klasör adı.
- `source_folder_name`: Kaynak dosyaların bulunduğu klasör.
- `target_base_path`: Navisworks'ün pluginleri okuduğu standart dizin.

## 📖 Kullanım

1. Kaynak klasörünüzü (örn: `NavisIFCExport`) projenin içine yerleştirin. Her sürüm için alt klasör yapısı şu şekilde olmalıdır:
   ```text
   NavisIFCExport/
   ├── Navis2022/
   │   └── (plugin dosyaları...)
   ├── Navis2023/
   │   └── (plugin dosyaları...)
   ```

2. Uygulamayı başlatın:
   ```bash
   python run.py
   ```

3. **"Check for Updates"**: Uygulamanın sağ alt köşesindeki buton ile GitHub üzerinden yeni bir versiyon olup olmadığını kontrol edebilirsiniz.
   - Yeni bir `.exe` versiyonu bulunduğunda uygulama bunu otomatik olarak indirir.
   - İndirme tamamlandığında uygulama kendini kapatır ve yeni versiyonu başlatır.

Uygulama, hedef klasörde aynı isimli bir plugin varsa önce onu **siler**, ardından taze kopyaları yerleştirir. İşlem sonunda size detaylı bir rapor sunar.

## 📂 Proje Yapısı

- `src/core/`: Versiyon tespiti ve dosya kopyalama mantığı.
  - `src/core/updater/`: GitHub üzerinden EXE güncelleme ve indirme mantığı.
- `src/ui/`: PySide6 tabanlı kullanıcı arayüzü dosyaları.
- `src/utils/`: Konfigürasyon ve sabitler (constants).
- `run.py`: Uygulamanın ana giriş noktası.

---
**Geliştiren:** [TheRaven815](https://github.com/TheRaven815)
