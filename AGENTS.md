# AGENTS.md

Bu dosya, NavisToolClient üzerinde çalışacak gelecekteki yapay zekâ ajanları ve geliştiriciler için projeye özel çalışma talimatlarını içerir. Amaç; mevcut mimariyi hızlı anlamak, güvenli değişiklik yapmak ve paketleme/dağıtım akışını bozmamaktır.

## Proje Özeti

NavisToolClient, Autodesk Navisworks eklentilerini birden fazla Navisworks Manage sürümüne dağıtmak için geliştirilmiş Windows odaklı bir Python/PySide6 masaüstü uygulamasıdır. Uygulama, `config.json` içindeki ayarlara göre yerel eklenti kaynak klasörlerini bulur, hedef `ProgramData` plugin dizinlerine kopyalar, kurulum durumunu arayüzde gösterir ve GitHub Releases üzerinden `.exe` güncellemesi kontrol edebilir.

Temel özellikler:

- Navisworks Manage 2022-2025 kurulumlarını algılama.
- Tek sürüme veya tüm algılanan sürümlere eklenti deploy etme.
- Kurulu eklentiyi kaldırma.
- Navisworks gerektirmeyen `DEBUG_PLUGINS` yerel debug hedefi.
- PySide6 ile koyu temalı kompakt masaüstü arayüzü.
- GitHub Releases API ile otomatik güncelleme kontrolü ve `.exe` indirme.

## Mimari ve Çalışma Akışı

1. `main.py`, uygulamanın ana giriş noktasıdır; `QApplication` oluşturur ve `MainWindow` örneğini başlatır.
2. `src/ui/main_window.py`, kullanıcı arayüzünü kurar, hedef listesini gösterir, deploy/uninstall butonlarını bağlar ve update/download akışını yönetir.
3. `src/core/navis_manager.py`, Navisworks sürüm tespiti, eklenti kurulu mu kontrolü, deploy ve uninstall işlemlerinden sorumludur.
4. `src/utils/config_manager.py`, `config.json` dosyasını okur/yazar ve ayarlara erişim sağlar.
5. `src/core/updater/checker.py`, GitHub Releases API ile yeni sürüm kontrolünü arka plan worker sınıflarıyla yapar.
6. `src/core/updater/downloader.py`, güncelleme `.exe` dosyasını stream ederek indirir ve ilerleme sinyalleri üretir.
7. `src/utils/constants.py`, update sistemi için repository, asset uzantısı ve geçici indirme dosyası sabitlerini tutar.

## Önemli Dosyalar

- `README.md`: Kullanıcıya dönük açıklama, kurulum, konfigürasyon ve kullanım dokümantasyonu.
- `requirements.txt`: Çalışma ve paketleme bağımlılıkları. Mevcut pinleri gereksiz değiştirmeyin.
- `config.json`: Eklenti adı, kaynak klasör, sürüm listesi, hedef path şablonu ve kopyalanacak uzantı filtreleri.
- `version.json`: Yayın sürümü metadatası. Uygulama içi görünen sürüm ayrıca `main.py` içindeki `VERSION` sabitinden gelir.
- `icon.ico`: Pencere ve paketlenmiş `.exe` ikonu.
- `setup.py`: PyInstaller ile tek dosya Windows executable üretmek için yardımcı build betiği.
- `main.py`: Paketleme ve geliştirme sırasında tercih edilen giriş noktası.

## Konfigürasyon Notları

`config.json` uygulama davranışını belirler:

- `plugin_name`: Hedef dizinde oluşturulacak eklenti klasörü adı.
- `plugin_owner`: Arayüz footer bilgisinde gösterilir.
- `source_folder_name`: Proje kökündeki eklenti kaynak klasörü.
- `version_folder_prefix`: Sürüm klasörlerinin öneki; örnek: `Navis2024`.
- `navis_versions`: Algılanacak ve deploy edilecek Navisworks sürümleri.
- `target_base_path`: `{version}` placeholder içeren hedef plugin path şablonu.
- `copy_extensions.plugin`: Deploy sırasında kaynak klasörden kopyalanacak dosya uzantıları. Varsayılan olarak `.dll` kullanılır.

Debug mode varsayılan olarak `src/core/navis_manager.py` içinde `DEBUG_MODE = True` şeklindedir. Bu durumda UI içinde `LOCAL DEBUG` hedefi görünür ve deploy işlemi `DEBUG_PLUGINS/<plugin_name>/` altına yapılır.

## Geliştirme Kuralları

- Gereksiz refactor yapmayın; istenen değişiklikle doğrudan ilişkili olmayan uygulama koduna dokunmayın.
- Windows uyumluluğunu koruyun. Hedef dizinler `C:/ProgramData/...` ve Navisworks kurulum yolları Windows formatındadır.
- PySide6 sinyal/slot ve `QThread` akışını bozmayın; uzun süren network/download işlemleri UI thread içinde çalıştırılmamalıdır.
- `ConfigManager` varsayılan olarak çalışma dizinindeki `config.json` dosyasını bekler. Paketleme sırasında bu dosyanın executable ile birlikte erişilebilir olmasına dikkat edin.
- Deploy işlemi hedef plugin klasörünü silip yeniden oluşturur. Bu davranışı değiştirirken kullanıcı verisi kaybı riskini değerlendirin.
- `copy_extensions` filtresini dikkate alın; kaynak klasörlerden sadece izin verilen uzantıların kopyalanması beklenir.
- Update sistemi `.exe` release asset arar. `src/utils/constants.py` içindeki `ASSET_EXTENSION = ".exe"` varsayımını bozmadan değişiklik yapın.
- Sürüm güncellerken `main.py` içindeki `VERSION`, `version.json` ve yayın notları tutarlı olmalıdır.

## Kurulum ve Çalıştırma

Geliştirme ortamı için önerilen akış:

```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Uygulama Windows 10/11 ve Python 3.10+ hedefler. Navisworks yüklü olmayan makinelerde debug hedefi sayesinde deploy mantığı `DEBUG_PLUGINS` klasörüne karşı test edilebilir.

## Test ve Kalite Kontrolleri

Projede ayrı bir test paketi bulunmuyor. Değişiklik sonrası en azından aşağıdaki kontrolleri yapın:

```bash
python -m py_compile main.py src/core/navis_manager.py src/core/updater/checker.py src/core/updater/downloader.py src/ui/main_window.py src/utils/config_manager.py src/utils/constants.py setup.py
python setup.py --help
```

UI veya deploy davranışını değiştirdiyseniz manuel kontrol önerilir:

1. `python main.py` ile uygulamayı başlatın.
2. `LOCAL DEBUG` satırının göründüğünü doğrulayın.
3. Örnek plugin dosyaları varsa deploy/uninstall akışını `DEBUG_PLUGINS` üzerinde deneyin.
4. Network erişimi varsa `Check Updates` butonunun hata vermeden sonuçlandığını kontrol edin.

## Paketleme Notları

`setup.py`, PyInstaller kullanarak tek dosyalık Windows executable üretmek için hazırlanmıştır. Temel komut:

```bash
python setup.py build
```

Beklenen çıktı:

```text
dist/NavisToolClient.exe
```

Betiğin hedefleri:

- `main.py` giriş noktasını paketlemek.
- `--onefile` ve `--windowed` modunda GUI executable üretmek.
- `icon.ico` dosyasını executable ikonu olarak kullanmak.
- `icon.ico`, `config.json` ve `version.json` dosyalarını PyInstaller data dosyası olarak dahil etmek.
- `PySide6` için gerekli hidden import ve collect seçeneklerini sağlamak.
- PyInstaller kurulu değilse anlaşılır hata mesajı vermek.

Paketlenmiş uygulamada `config.json` dosyasının çalışma dizini beklentisine dikkat edin. PyInstaller data dosyaları `_MEIPASS` içine açılır; ikon kullanımı zaten `sys._MEIPASS` kontrolü yapar. Konfigürasyonun son kullanıcı tarafından düzenlenebilir olması gerekiyorsa executable yanına harici `config.json` koyma stratejisi ayrıca değerlendirilebilir.

## Gelecekteki Ajanlar İçin Net Talimatlar

- Önce `README.md`, `config.json`, `main.py`, `src/core/navis_manager.py`, `src/ui/main_window.py` ve updater modüllerini okuyun.
- İstenen görev paketleme ile ilgiliyse önce `setup.py` içindeki PyInstaller argümanlarını kontrol edin.
- Uygulama kodunda değişiklik yapmadan önce mevcut deploy/update akışını anlayın; UI ile core arasındaki bağlantılar `MainWindow` üzerinden yürür.
- Dosya yolu davranışını değiştirirken hem kaynak çalıştırma (`python main.py`) hem de PyInstaller onefile çalıştırma senaryosunu düşünün.
- Bağımlılık eklerken `requirements.txt` dosyasına pinli ve minimum gerekli eklemeyi yapın; mevcut bağımlılık sürümlerini gereksiz yükseltmeyin/düşürmeyin.
- Her değişiklikten sonra en azından syntax kontrolü ve ilgili build yardım komutunu çalıştırın.
