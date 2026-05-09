# 🚀 NavisToolClient

**NavisToolClient** is a modern desktop deployment client for Autodesk Navisworks plugins. Built with Python and PySide6, it automates copying your plugin files into the correct Navisworks `Plugins` directories across multiple installed versions — with a single click.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![UI](https://img.shields.io/badge/UI-PySide6-orange.svg)
![Version](https://img.shields.io/badge/version-1.0.2-green.svg)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🏗️ **Multi-Version Detection** | Automatically detects Navisworks Manage 2022–2025 installations |
| ⬆️ **One-Click Deployment** | Copies all plugin files to the correct `ProgramData` paths |
| 🗑️ **Uninstall Support** | Removes the deployed plugin from any specific version |
| 🛠️ **Local Debug Mode** | Deploy to a local `./DEBUG_PLUGINS` folder without needing Navisworks installed |
| ✅ **Install Status Badges** | Each version row shows whether the plugin is currently deployed |
| 🔄 **Auto-Update System** | Checks GitHub Releases and downloads new versions automatically |
| 🎨 **Dark UI** | Compact, dark-themed interface built with PySide6 |

---

## 🗂️ Project Structure

```
NavisToolClient/
│
├── main.py                       # Entry point, version constant
├── config.json                   # Plugin configuration (edit this!)
├── version.json                  # Current app version metadata
├── requirements.txt              # Python dependencies
├── icon.ico                      # Window icon
│
├── NavisIFCExport/               # Your plugin source files (see config.json)
│   ├── Navis2022/                # Files for Navisworks 2022
│   │   ├── NavisIFCExport.dll
│   │   └── ...
│   ├── Navis2023/
│   ├── Navis2024/
│   └── Navis2025/
│
├── DEBUG_PLUGINS/                # Local deploy target (auto-created on first debug deploy)
│
└── src/
    ├── ui/
    │   └── main_window.py        # Main GUI window
    ├── core/
    │   ├── navis_manager.py      # Deploy / uninstall / detection logic
    │   └── updater/
    │       ├── checker.py        # GitHub release checker (background thread)
    │       └── downloader.py     # Update downloader (background thread)
    └── utils/
        ├── config_manager.py     # JSON config reader/writer
        └── constants.py          # REPO_URL, update filename, etc.
```

---

## ⚙️ Configuration — `config.json`

All plugin behaviour is controlled by this single file:

```json
{
    "plugin_name": "NavisIFCExport",
    "source_folder_name": "NavisIFCExport",
    "version_folder_prefix": "Navis",
    "navis_versions": ["2022", "2023", "2024", "2025"],
    "target_base_path": "C:/ProgramData/Autodesk/Navisworks Manage {version}/Plugins"
}
```

| Key | Description |
|---|---|
| `plugin_name` | The name of the plugin folder created inside the Navisworks `Plugins` directory. Also used for uninstall (the folder to delete). |
| `source_folder_name` | Name of the local source folder at the project root that contains your plugin builds. |
| `version_folder_prefix` | Prefix for version-specific subdirectories inside the source folder (e.g. `Navis` → `Navis2022`, `Navis2023`). |
| `navis_versions` | List of Navisworks version years to check for and deploy to. |
| `target_base_path` | Destination path template. Use `{version}` as a placeholder — it gets replaced with the year string (e.g. `2024`). |

---

## 📁 Plugin Source Folder — Naming Rules

The client expects your source files to be organized in **version-named subfolders** inside the folder named `source_folder_name`.

### Folder naming pattern:
```
{source_folder_name}/{version_folder_prefix}{version}/
```

### Example (default config):
```
NavisIFCExport/
├── Navis2022/
│   ├── NavisIFCExport.dll
│   ├── Newtonsoft.Json.dll
│   └── ...
├── Navis2023/
│   └── ...
├── Navis2024/
│   └── ...
└── Navis2025/
    └── ...
```

> **Important:** Only **files** (not subfolders) in each version directory are copied. All files in the source version folder are deployed flat into the `{plugin_name}` folder at the target path.

### Target path example for Navisworks 2024:
```
C:/ProgramData/Autodesk/Navisworks Manage 2024/Plugins/NavisIFCExport/
```

---

## 🛠️ Installation

### Prerequisites
- Python 3.10 or newer
- Windows 10/11

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/TheRaven815/NavisToolClient.git
   cd NavisToolClient
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your plugin in `config.json`** (see above).

5. **Place your built plugin DLLs** into the correct version subfolders.

6. **Run the application:**
   ```bash
   python main.py
   ```

---

## 🖥️ Using the Interface

### Main Window

The interface lists all **detected Navisworks installations** on the machine. Each row shows:

- 🟢 **Green dot + "Installed" badge** — the plugin is currently deployed to this version
- ⚪ **Grey dot + "Not Installed"** — the plugin has not been deployed yet
- 🟡 **Yellow dot** — special LOCAL DEBUG entry (see below)

### Deploying

- **Deploy** (per row): Deploys the plugin only to that specific Navisworks version.
- **Deploy Plugin to All Detected Versions** (main button): Deploys to every detected version at once.

> Deployment removes any existing plugin folder at the target path first, then copies all files fresh. This ensures no stale files remain.

### Uninstalling

Each row where the plugin is **already installed** shows an **Uninstall** button. Clicking it will:
1. Ask for confirmation.
2. Delete the plugin folder from the Navisworks `Plugins` directory.

### Refreshing

Click **↻ Refresh** to re-scan the machine for Navisworks installations and re-check plugin deployment status without restarting the app.

---

## 🧪 Local Debug Mode

Debug mode is enabled by default (`DEBUG_MODE = True` in `src/core/navis_manager.py`). It adds a special **LOCAL DEBUG** entry to the list that deploys your plugin files to:

```
./DEBUG_PLUGINS/<plugin_name>/
```

This lets you test the deployment logic without touching any real Navisworks installation.

> **Note:** Debug mode always uses the **first version** in `navis_versions` as the source folder for the debug deploy. For example, if your list is `["2022", "2023"]`, it reads from `NavisIFCExporter/Navis2022/`.

To disable debug mode for production builds, set:
```python
self.DEBUG_MODE = False
```
in `src/core/navis_manager.py`.

---

## 🔄 Auto-Update System

The app includes a built-in update checker powered by the **GitHub Releases API**.

1. Click **Check for Updates** in the bottom-right corner.
2. The app queries the configured GitHub repository for the latest release.
3. If a newer version is found, a dialog shows the release notes and asks whether to download.
4. If confirmed, the new `.exe` is downloaded and launched automatically, then the old instance closes.

### Configuration

The GitHub repository is set in `src/utils/constants.py`:

```python
REPO_URL = "TheRaven815/NavisToolClient"   # format: "owner/repo"
UPDATE_FILENAME = "NavisToolClient_Update.exe"
```

Releases must follow **semantic versioning** (e.g. `v1.0.2`) and attach the installer `.exe` as a release asset.

---

## 📋 Requirements

```
PySide6 >= 6.6
requests >= 2.31
```

See `requirements.txt` for pinned versions used during development.

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

### 👨‍💻 Developed by
**Enes Eliağır**  
[github.com/TheRaven815](https://github.com/TheRaven815)
