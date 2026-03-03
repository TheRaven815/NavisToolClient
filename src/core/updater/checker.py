import requests
from packaging.version import parse as parse_version
from PySide6.QtCore import QObject, Signal, Slot
from src.utils.constants import ASSET_EXTENSION

class GitHubVersionChecker(QObject):
    """Optimized version checker for startup"""
    finished = Signal(bool, str)

    def __init__(self, current_version: str, repo_url: str):
        super().__init__()
        self.api_url = f"https://api.github.com/repos/{repo_url}/releases/latest"
        self.current_version = current_version

    @Slot()
    def run(self):
        try:
            response = requests.get(self.api_url, timeout=10)
            data = response.json()
            latest_version = data.get("tag_name", "0.0.0").lstrip('v')
            is_available = parse_version(latest_version) > parse_version(self.current_version)
            self.finished.emit(is_available, latest_version)
        except Exception:
            self.finished.emit(False, "")

class UpdateWorker(QObject):
    """Update checker worker for manual check"""
    result_ready = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, current_version: str, repo_url: str):
        super().__init__()
        self.current_version = current_version
        self.repo_url = repo_url
        self.api_url = f"https://api.github.com/repos/{self.repo_url}/releases/latest"

    @Slot()
    def run(self):
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            latest_version_str = data["tag_name"].lstrip('v')
            if parse_version(latest_version_str) > parse_version(self.current_version):
                download_url = None
                for asset in data.get("assets", []):
                    if asset["name"].endswith(ASSET_EXTENSION):
                        download_url = asset["browser_download_url"]
                        break
                if not download_url:
                    self.error_occurred.emit(f"No asset with the '{ASSET_EXTENSION}' extension found in the new release.")
                    return
                result = {
                    "update_available": True,
                    "latest_version": data["tag_name"],
                    "release_notes": data["body"],
                    "download_url": download_url
                }
            else:
                result = {"update_available": False}
            self.result_ready.emit(result)
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit(f"Network error: Could not check for updates.\n{e}")
        except Exception as e:
            self.error_occurred.emit(f"An unexpected error occurred: {e}")