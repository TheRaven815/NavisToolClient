# 🚀 NavisToolClient

**NavisToolClient** is a modern, high-performance deployment and update client for Autodesk Navisworks plugins. Designed with a sleek, VS Code-inspired interface, it streamlines the lifecycle of your plugins from development to production deployment.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![UI](https://img.shields.io/badge/UI-PySide6-orange.svg)

## ✨ Features

- 🏗️ **Multi-Version Detection:** Automatically detects installed versions of Navisworks Manage (2022-2025).
- 🚀 **Seamless Deployment:** Deploys plugin files to the correct `ProgramData` directories with a single click.
- 🛠️ **Local Debug Mode:** Includes a dedicated testing target that deploys to a local `./DEBUG_PLUGINS` folder—no Navisworks installation required for testing.
- ✨ **Auto-Update System:** Built-in mechanism to check for and download new versions directly from GitHub releases.
- 🎨 **Pro UI/UX:** Compact, dark-themed interface inspired by modern code editors for a professional developer experience.
- 🌍 **English Interface:** Fully localized in English for global accessibility.

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/TheRaven815/NavisToolClient.git
   cd NavisToolClient
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python run.py
   ```

## ⚙️ Configuration

The application behavior is managed via `config.json`:

```json
{
    "plugin_name": "YourPluginName",
    "source_folder_name": "YourPluginSource",
    "version_folder_prefix": "Navis",
    "navis_versions": ["2022", "2023", "2024", "2025"],
    "target_base_path": "C:/ProgramData/Autodesk/Navisworks Manage {version}/Plugins"
}
```

## 🧪 Testing with Local Debug

If you don't have Navisworks installed or want to test deployment safely:
1. Enable `DEBUG_MODE` in `src/core/navis_manager.py`.
2. Select **🛠️ LOCAL DEBUG** in the targets list.
3. Click **Deploy Plugins**.
4. Check the `./DEBUG_PLUGINS` folder in the project directory for the results.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

### 👨‍💻 Developed by
**Enes Eliağır**
[GitHub Profile](https://github.com/TheRaven815)
