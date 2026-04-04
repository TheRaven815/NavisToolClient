import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame,
    QStatusBar, QScrollArea, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, QTimer
from PySide6.QtGui import QIcon

from src.core.navis_manager import NavisManager
from src.utils.config_manager import ConfigManager
from src.core.updater.checker import UpdateWorker
from src.core.updater.downloader import DownloadWorker
from src.utils.constants import REPO_URL, UPDATE_FILENAME


# ---------------------------------------------------------------------------
# Version Row Widget
# ---------------------------------------------------------------------------
class VersionRowWidget(QWidget):
    """A single Navisworks version row with install status and action buttons."""

    def __init__(self, version_id: str, display_name: str, is_installed: bool,
                 is_debug: bool, on_deploy, on_uninstall, colors: dict, parent=None):
        super().__init__(parent)
        self.version_id = version_id
        self.on_deploy = on_deploy
        self.on_uninstall = on_uninstall
        self.colors = colors

        self._build_ui(display_name, is_installed, is_debug)

    def _build_ui(self, display_name: str, is_installed: bool, is_debug: bool):
        self.setMinimumHeight(50)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 7, 12, 7)
        layout.setSpacing(10)

        # ---- Status dot ----
        dot = QLabel("●")
        dot.setFixedWidth(10)
        dot.setAlignment(Qt.AlignCenter)
        if is_installed:
            dot.setStyleSheet("color: #4ec994; font-size: 10px;")
        elif is_debug:
            dot.setStyleSheet(f"color: {self.colors['warning']}; font-size: 10px;")
        else:
            dot.setStyleSheet("color: #555; font-size: 10px;")
        layout.addWidget(dot)

        # ---- Icon ----
        icon_lbl = QLabel("🛠️" if is_debug else "🏗️")
        icon_lbl.setStyleSheet("font-size: 14px;")
        icon_lbl.setFixedWidth(22)
        layout.addWidget(icon_lbl)

        # ---- Name + status ----
        name_col = QVBoxLayout()
        name_col.setSpacing(4)
        name_col.setContentsMargins(0, 0, 0, 0)

        name_color = "#f0ab00" if is_debug else self.colors['text_bright']
        name_lbl = QLabel(display_name)
        name_lbl.setStyleSheet(
            f"font-size: 12px; font-weight: 600; color: {name_color}; background: transparent;"
        )
        name_col.addWidget(name_lbl)

        if is_installed:
            status_lbl = QLabel("● Installed")
            status_lbl.setStyleSheet(
                "font-size: 10px; font-weight: 600; color: #4ec994; background: transparent;"
            )
        else:
            status_lbl = QLabel("○ Not Installed")
            status_lbl.setStyleSheet(
                f"font-size: 10px; color: {self.colors['text_dim']}; background: transparent;"
            )
        name_col.addWidget(status_lbl)

        layout.addLayout(name_col)
        layout.addStretch()

        # ---- Action buttons ----
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        btn_layout.setContentsMargins(0, 0, 0, 0)

        if is_installed:
            btn_uninstall = QPushButton("Uninstall")
            btn_uninstall.setObjectName("DangerBtn")
            btn_uninstall.setCursor(Qt.PointingHandCursor)
            btn_uninstall.setFixedHeight(26)
            btn_uninstall.setMinimumWidth(70)
            btn_uninstall.clicked.connect(lambda: self.on_uninstall(self.version_id))
            btn_layout.addWidget(btn_uninstall)

        btn_deploy = QPushButton("Deploy")
        btn_deploy.setObjectName("SmallPrimaryBtn")
        btn_deploy.setCursor(Qt.PointingHandCursor)
        btn_deploy.setFixedHeight(26)
        btn_deploy.setMinimumWidth(62)
        btn_deploy.clicked.connect(lambda: self.on_deploy(self.version_id))
        btn_layout.addWidget(btn_deploy)

        layout.addLayout(btn_layout)

        # Row background styling
        bg = "#1e3a28" if is_installed else (
            "#2d2a1e" if is_debug else self.colors['card']
        )
        border = "#2d6b45" if is_installed else (
            "#5a4d1e" if is_debug else self.colors['border']
        )
        self.setStyleSheet(f"""
            VersionRowWidget {{
                background-color: {bg};
                border-radius: 8px;
                border: 1px solid {border};
            }}
        """)


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self, version):
        super().__init__()
        self.current_version = version
        self.config = ConfigManager()
        self.navis = NavisManager(self.config)

        self.update_thread = None
        self.download_thread = None

        self.setWindowTitle("Navisworks Tool Client")
        self.setMinimumSize(500, 400)

        self.set_app_icon()
        self.init_ui()
        self.load_installed_versions()

    # ------------------------------------------------------------------
    def set_app_icon(self):
        import sys
        icon_path = "icon.ico"
        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    # ------------------------------------------------------------------
    def init_ui(self):
        self.colors = {
            "bg":           "#1e1e2e",
            "sidebar":      "#252535",
            "card":         "#2a2a3e",
            "accent":       "#0078d4",
            "accent_hover": "#1a8fe0",
            "success":      "#4ec994",
            "danger":       "#e05252",
            "danger_hover": "#c94141",
            "text":         "#cdd6f4",
            "text_bright":  "#f2f2f2",
            "text_dim":     "#6c7086",
            "border":       "#383850",
            "warning":      "#cca700",
            "status_bg":    "#0e639c",
        }

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['bg']};
            }}
            QWidget {{
                color: {self.colors['text']};
                font-family: 'Segoe UI', Inter, Arial;
                font-size: 13px;
                background-color: transparent;
            }}
            QMainWindow > QWidget {{
                background-color: {self.colors['bg']};
            }}
            QFrame#Card {{
                background-color: {self.colors['sidebar']};
                border: 1px solid {self.colors['border']};
                border-radius: 10px;
            }}
            QLabel#AppTitle {{
                font-size: 20px;
                font-weight: 700;
                color: {self.colors['text_bright']};
            }}
            QLabel#AppSubtitle {{
                font-size: 12px;
                color: {self.colors['text_dim']};
            }}
            QLabel#SectionTitle {{
                font-size: 10px;
                font-weight: 700;
                color: {self.colors['text_dim']};
                letter-spacing: 1.2px;
            }}
            QPushButton#PrimaryBtn {{
                background-color: {self.colors['accent']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton#PrimaryBtn:hover {{
                background-color: {self.colors['accent_hover']};
            }}
            QPushButton#PrimaryBtn:disabled {{
                background-color: #2e4a63;
                color: #5a7a99;
            }}
            QPushButton#SmallPrimaryBtn {{
                background-color: {self.colors['accent']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 14px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton#SmallPrimaryBtn:hover {{
                background-color: {self.colors['accent_hover']};
            }}
            QPushButton#DangerBtn {{
                background-color: transparent;
                color: {self.colors['danger']};
                border: 1px solid {self.colors['danger']};
                border-radius: 5px;
                padding: 5px 14px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton#DangerBtn:hover {{
                background-color: {self.colors['danger']};
                color: white;
            }}
            QPushButton#GhostBtn {{
                background-color: transparent;
                color: {self.colors['text']};
                border: 1px solid {self.colors['border']};
                border-radius: 5px;
                padding: 5px 13px;
                font-size: 12px;
            }}
            QPushButton#GhostBtn:hover {{
                background-color: #2a2a2a;
                border-color: #555;
                color: {self.colors['text_bright']};
            }}
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: #444;
                border-radius: 3px;
                min-height: 24px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QStatusBar {{
                background-color: {self.colors['status_bg']};
                color: #e0e0e0;
                font-size: 12px;
                padding: 0 8px;
            }}
            QStatusBar::item {{
                border: none;
            }}
        """)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(14, 14, 14, 8)
        root.setSpacing(0)

        # ================================================================
        # HEADER
        # ================================================================
        header = QHBoxLayout()
        header.setSpacing(0)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        plugin_name = self.config.get("plugin_name", "Plugin")
        title_lbl = QLabel(f"{plugin_name} Deployer")
        title_lbl.setObjectName("AppTitle")
        title_col.addWidget(title_lbl)

        sub_lbl = QLabel("Navisworks Plugin Management Console")
        sub_lbl.setObjectName("AppSubtitle")
        title_col.addWidget(sub_lbl)

        header.addLayout(title_col)
        header.addStretch()

        # Version pill
        ver_pill = QLabel(f"v{self.current_version}")
        ver_pill.setStyleSheet(
            f"background-color: #0e3a5e; color: #4da6e8; "
            f"font-size: 11px; font-weight: 700; "
            f"border-radius: 10px; padding: 3px 10px;"
        )
        ver_pill.setAlignment(Qt.AlignCenter)
        header.addWidget(ver_pill)

        root.addLayout(header)
        root.addSpacing(12)

        # ================================================================
        # VERSION LIST CARD
        # ================================================================
        version_card = QFrame()
        version_card.setObjectName("Card")
        card_layout = QVBoxLayout(version_card)
        card_layout.setContentsMargins(12, 10, 12, 10)
        card_layout.setSpacing(8)

        # Card header row
        card_header = QHBoxLayout()
        sec_title = QLabel("DETECTED INSTALLATIONS")
        sec_title.setObjectName("SectionTitle")
        card_header.addWidget(sec_title)
        card_header.addStretch()

        self.btn_refresh = QPushButton("↻  Refresh")
        self.btn_refresh.setObjectName("GhostBtn")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setFixedHeight(26)
        self.btn_refresh.clicked.connect(self._refresh_with_animation)
        card_header.addWidget(self.btn_refresh)
        card_layout.addLayout(card_header)

        # Divider line
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet(f"color: {self.colors['border']}; background-color: {self.colors['border']}; border: none; max-height: 1px;")
        card_layout.addWidget(divider)

        # Scroll area for version rows
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(170)

        self.rows_container = QWidget()
        self.rows_container.setStyleSheet("background: transparent;")
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setContentsMargins(0, 2, 0, 2)
        self.rows_layout.setSpacing(5)
        self.rows_layout.addStretch()

        scroll.setWidget(self.rows_container)
        card_layout.addWidget(scroll)

        root.addWidget(version_card)
        root.addSpacing(10)

        # ================================================================
        # DEPLOY ALL BUTTON
        # ================================================================
        self.btn_deploy_all = QPushButton("⬆   Deploy Plugin to All Detected Versions")
        self.btn_deploy_all.setObjectName("PrimaryBtn")
        self.btn_deploy_all.setCursor(Qt.PointingHandCursor)
        self.btn_deploy_all.setMinimumHeight(38)
        self.btn_deploy_all.clicked.connect(self.deploy_all)
        root.addWidget(self.btn_deploy_all)

        root.addStretch()

        # ================================================================
        # FOOTER
        # ================================================================
        footer = QHBoxLayout()
        footer.setContentsMargins(0, 8, 0, 0)

        plugin_owner = self.config.get("plugin_owner", "Unknown")
        attr = QLabel(f"Plugin Owner: {plugin_owner}")
        attr.setStyleSheet(f"color: {self.colors['text_dim']}; font-size: 11px;")
        footer.addWidget(attr)

        footer.addStretch()

        self.btn_update = QPushButton("Check for Updates")
        self.btn_update.setObjectName("GhostBtn")
        self.btn_update.setCursor(Qt.PointingHandCursor)
        self.btn_update.clicked.connect(self.check_updates)
        footer.addWidget(self.btn_update)

        root.addLayout(footer)

        # Status Bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")

    # ------------------------------------------------------------------
    def _refresh_with_animation(self):
        """Briefly animate the Refresh button then reload the version list."""
        self.btn_refresh.setEnabled(False)
        frames = ["◐  Refreshing", "◓  Refreshing", "◑  Refreshing", "◒  Refreshing"]
        self._anim_frame = 0

        def _tick():
            self.btn_refresh.setText(frames[self._anim_frame % len(frames)])
            self._anim_frame += 1
            if self._anim_frame >= 8:   # ~400 ms total (8 × 50 ms)
                self._refresh_timer.stop()
                self.btn_refresh.setText("↻  Refresh")
                self.btn_refresh.setEnabled(True)
                self.load_installed_versions()

        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(50)
        self._refresh_timer.timeout.connect(_tick)
        self._refresh_timer.start()

    # ------------------------------------------------------------------
    def _clear_rows(self):
        while self.rows_layout.count() > 1:
            item = self.rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # ------------------------------------------------------------------
    def load_installed_versions(self):
        self._clear_rows()

        versions = self.navis.detect_installed_versions()

        if not versions:
            placeholder = QLabel("No Navisworks installation detected on this machine.")
            placeholder.setStyleSheet(
                f"color: {self.colors['text_dim']}; font-size: 13px; padding: 20px;"
            )
            placeholder.setAlignment(Qt.AlignCenter)
            self.rows_layout.insertWidget(0, placeholder)
        else:
            for idx, v in enumerate(versions):
                is_debug = (v == "DEBUG")
                display = "LOCAL DEBUG  →  ./DEBUG_PLUGINS" if is_debug else f"Navisworks Manage {v}"
                is_installed = self.navis.is_plugin_installed(v)

                row = VersionRowWidget(
                    version_id=v,
                    display_name=display,
                    is_installed=is_installed,
                    is_debug=is_debug,
                    on_deploy=self._deploy_single,
                    on_uninstall=self._uninstall_single,
                    colors=self.colors,
                )
                self.rows_layout.insertWidget(idx, row)

        self.statusBar().showMessage("Ready")

    # ------------------------------------------------------------------
    def _deploy_single(self, version_id: str):
        self.btn_deploy_all.setEnabled(False)
        label = "LOCAL DEBUG" if version_id == "DEBUG" else f"Navisworks {version_id}"
        self.statusBar().showMessage(f"Deploying to {label}…")

        success, msg = self.navis.deploy_plugin(version_id)
        if success:
            QMessageBox.information(self, "Deployment Complete", f"✅  {msg}")
        else:
            QMessageBox.critical(self, "Deployment Failed", f"❌  {msg}")

        self.btn_deploy_all.setEnabled(True)
        self.load_installed_versions()

    # ------------------------------------------------------------------
    def _uninstall_single(self, version_id: str):
        plugin_name = self.config.get("plugin_name", "Plugin")
        label = "LOCAL DEBUG" if version_id == "DEBUG" else f"Navisworks {version_id}"

        reply = QMessageBox.question(
            self,
            "Confirm Uninstall",
            f"Remove <b>{plugin_name}</b> from <b>{label}</b>?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        success, msg = self.navis.uninstall_plugin(version_id)
        if success:
            QMessageBox.information(self, "Uninstall Complete", f"✅  {msg}")
        else:
            QMessageBox.critical(self, "Uninstall Failed", f"❌  {msg}")

        self.load_installed_versions()

    # ------------------------------------------------------------------
    def deploy_all(self):
        versions = self.navis.detect_installed_versions()
        if not versions:
            QMessageBox.warning(self, "No Targets",
                                "No Navisworks installations detected.")
            return

        self.btn_deploy_all.setEnabled(False)
        self.statusBar().showMessage("Deploying to all detected versions…")

        success_count = 0
        details = []

        for v in versions:
            ok, msg = self.navis.deploy_plugin(v)
            if ok:
                success_count += 1
                details.append(f"✅  {msg}")
            else:
                details.append(f"❌  {msg}")

        self.btn_deploy_all.setEnabled(True)

        if success_count > 0:
            QMessageBox.information(self, "Deployment Complete", "\n".join(details))
        else:
            QMessageBox.critical(self, "Deployment Failed", "\n".join(details))

        self.load_installed_versions()

    # ------------------------------------------------------------------
    # Update flow
    # ------------------------------------------------------------------
    def check_updates(self):
        self.btn_deploy_all.setEnabled(False)
        self.statusBar().showMessage("Checking for updates…")

        self.update_thread = QThread()
        self.update_worker = UpdateWorker(self.current_version, REPO_URL)
        self.update_worker.moveToThread(self.update_thread)

        self.update_thread.started.connect(self.update_worker.run)
        self.update_worker.result_ready.connect(self.on_update_result)
        self.update_worker.error_occurred.connect(self.on_update_error)
        self.update_worker.result_ready.connect(self.update_thread.quit)
        self.update_worker.error_occurred.connect(self.update_thread.quit)

        self.update_thread.start()

    def on_update_result(self, result):
        self.btn_deploy_all.setEnabled(True)
        self.statusBar().showMessage("Ready")

        if result.get("update_available"):
            msg = (
                f"A new version is available: {result['latest_version']}\n\n"
                f"Release Notes:\n{result['release_notes']}\n\n"
                f"Download and install now?"
            )
            reply = QMessageBox.question(self, "Update Available", msg,
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.start_download(result["download_url"])
        else:
            QMessageBox.information(self, "Up to Date",
                                    "You are running the latest version.")

    def on_update_error(self, error):
        self.btn_deploy_all.setEnabled(True)
        self.statusBar().showMessage("Update check failed.")
        QMessageBox.warning(self, "Update Error",
                            f"Could not check for updates:\n{error}")

    def start_download(self, url):
        save_path = os.path.join(os.getcwd(), UPDATE_FILENAME)

        self.download_thread = QThread()
        self.download_worker = DownloadWorker(url, save_path)
        self.download_worker.moveToThread(self.download_thread)

        self.download_thread.started.connect(self.download_worker.run)
        self.download_worker.progress.connect(self.on_download_progress)
        self.download_worker.finished.connect(self.on_download_finished)
        self.download_worker.error.connect(self.on_download_error)

        self.btn_deploy_all.setEnabled(False)
        self.download_thread.start()

    def on_download_progress(self, percent, downloaded, total):
        self.statusBar().showMessage(
            f"Downloading update: {percent}%  "
            f"({downloaded / 1024 / 1024:.1f} MB / {total / 1024 / 1024:.1f} MB)"
        )

    def on_download_finished(self, path):
        self.btn_deploy_all.setEnabled(True)
        self.statusBar().showMessage("Download complete.")
        QMessageBox.information(
            self, "Download Complete",
            "Update downloaded. The application will now restart."
        )
        try:
            import subprocess
            subprocess.Popen([path], shell=True)
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Launch Error",
                                 f"Could not start new version:\n{e}")

    def on_download_error(self, error):
        self.btn_deploy_all.setEnabled(True)
        self.statusBar().showMessage("Download failed.")
        QMessageBox.critical(self, "Download Error", f"Download failed:\n{error}")
