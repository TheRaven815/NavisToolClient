import requests
from PySide6.QtCore import QObject, Signal, Slot

class DownloadWorker(QObject):
    """File download worker"""
    progress = Signal(int, int, int)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, url: str, save_path: str):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self._is_running = True

    @Slot()
    def run(self):
        try:
            response = requests.get(self.url, stream=True, timeout=30)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            with open(self.save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if not self._is_running:
                        self.error.emit("Download canceled by user.")
                        return
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            progress_percentage = int((downloaded_size / total_size) * 100)
                            self.progress.emit(progress_percentage, downloaded_size, total_size)
            if self._is_running:
                self.progress.emit(100, total_size, total_size)
                self.finished.emit(self.save_path)
        except requests.exceptions.RequestException as e:
            self.error.emit(f"Download failed: {e}")
        except Exception as e:
            self.error.emit(f"File writing error: {e}")

    def stop(self):
        self._is_running = False