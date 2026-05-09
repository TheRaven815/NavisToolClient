import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame,
    QScrollArea, QMessageBox, QSizePolicy
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
        self.setMinimumHeight(44)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 5, 6, 5)
        layout.setSpacing(4)

        # ---- Name + status ----
        name_col = QVBoxLayout()
        name_col.setSpacing(1)
        name_col.setContentsMargins(0, 0, 0, 0)
        name_col.setAlignment(Qt.AlignVCenter)

        name_color = self.colors['warning'] if is_debug else self.colors['text_bright']
        name_lbl = QLabel(display_name)
        name_lbl.setToolTip(display_name)
        name_lbl.setMinimumWidth(150)
        name_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        name_lbl.setStyleSheet(
            f"font-size: {'11px' if is_debug else '12px'}; font-weight: 500; color: {name_color}; background: transparent;"
        )
        name_col.addWidget(name_lbl)

        if is_installed:
            status_lbl = QLabel("Installed")
            status_lbl.setStyleSheet(
                f"font-size: 10px; font-weight: 500; color: {self.colors['success']}; background: transparent;"
            )
        else:
            status_lbl = QLabel("Not Installed")
            status_lbl.setStyleSheet(
                f"font-size: 10px; color: {self.colors['text_dim']}; background: transparent;"
            )
        name_col.addWidget(status_lbl)

        layout.addLayout(name_col, 1)
        layout.setAlignment(name_col, Qt.AlignVCenter)

        # ---- Action buttons ----
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(3)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setAlignment(Qt.AlignVCenter)

        if is_installed:
            btn_uninstall = QPushButton("Uninstall")
            btn_uninstall.setObjectName("DangerBtn")
            btn_uninstall.setCursor(Qt.PointingHandCursor)
            btn_uninstall.setFixedSize(66, 28)
            btn_uninstall.clicked.connect(lambda: self.on_uninstall(self.version_id))
            btn_layout.addWidget(btn_uninstall, 0, Qt.AlignVCenter)

        btn_deploy = QPushButton("Deploy")
        btn_deploy.setObjectName("SmallPrimaryBtn")
        btn_deploy.setCursor(Qt.PointingHandCursor)
        btn_deploy.setFixedSize(62, 28)
        btn_deploy.clicked.connect(lambda: self.on_deploy(self.version_id))
        btn_layout.addWidget(btn_deploy, 0, Qt.AlignVCenter)

        layout.addLayout(btn_layout)
        layout.setAlignment(btn_layout, Qt.AlignVCenter)

        # VSCode-like row styling: compact, subtle and list-oriented.
        bg = self.colors['list_item']
        hover_bg = self.colors['list_hover']
        border = self.colors['success_border'] if is_installed else (
            self.colors['warning_border'] if is_debug else self.colors['border']
        )
        accent_line = self.colors['success'] if is_installed else (
            self.colors['warning'] if is_debug else self.colors['text_dim']
        )

        self.setObjectName("VersionRow")
        self.setStyleSheet(f"""
            QWidget#VersionRow {{
                background-color: {bg};
                border: 1px solid {border};
                border-left: 3px solid {accent_line};
                border-radius: 4px;
            }}
            QWidget#VersionRow:hover {{
                background-color: {hover_bg};
                border-color: {self.colors['accent']};
            }}
            QWidget#VersionRow QLabel {{
                border: none;
                background: transparent;
            }}
        """)


# ---------------------------------------------------------------------------
# Footer Status Proxy
# ---------------------------------------------------------------------------
class FooterStatusProxy:
    """Small status-bar compatible wrapper that writes messages into a QLabel."""

    def __init__(self, label: QLabel):
        self.label = label

    def showMessage(self, message: str, timeout: int = 0):
        self.label.setText(message)
        if timeout > 0:
            QTimer.singleShot(timeout, self.clearMessage)

    def clearMessage(self):
        self.label.clear()

    def currentMessage(self) -> str:
        return self.label.text()


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

        self._refresh_timer = None
        self._refresh_frame = 0
        self._refresh_frames = ("Refreshing", "Refreshing.", "Refreshing..", "Refreshing...")

        self.setWindowTitle("Navisworks Tool Client")
        self.setMinimumSize(430, 455)
        self.resize(445, 455)

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
            "bg":             "#1e1e1e",
            "sidebar":        "#252526",
            "card":           "#252526",
            "list_item":      "#252526",
            "list_hover":     "#2a2d2e",
            "accent":         "#007acc",
            "accent_dark":    "#0e639c",
            "accent_hover":   "#1177bb",
            "success":        "#4ec9b0",
            "success_border": "#2f6f5f",
            "danger":         "#f14c4c",
            "danger_hover":   "#ff6b6b",
            "text":           "#cccccc",
            "text_bright":    "#ffffff",
            "text_dim":       "#858585",
            "border":         "#3c3c3c",
            "warning":        "#d7ba7d",
            "warning_border": "#7c6f3e",
            "status_bg":      "#007acc",
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
                background-color: {self.colors['card']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
            }}
            QLabel#AppTitle {{
                font-size: 20px;
                font-weight: 600;
                color: {self.colors['text_bright']};
            }}
            QLabel#AppSubtitle {{
                font-size: 12px;
                color: {self.colors['text_dim']};
            }}
            QLabel#VersionBadge {{
                background-color: #2d2d30;
                color: #9cdcfe;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 11px;
                font-weight: 600;
            }}
            QLabel#SectionTitle {{
                font-size: 11px;
                font-weight: 600;
                color: {self.colors['text']};
                letter-spacing: 0.8px;
            }}
            QPushButton {{
                min-height: 26px;
                text-align: center;
            }}
            QPushButton#PrimaryBtn {{
                background-color: {self.colors['accent_dark']};
                color: #ffffff;
                border: 1px solid {self.colors['accent']};
                border-radius: 4px;
                padding: 0 8px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton#PrimaryBtn:hover {{
                background-color: {self.colors['accent_hover']};
            }}
            QPushButton#PrimaryBtn:pressed {{
                background-color: #094771;
            }}
            QPushButton#PrimaryBtn:disabled {{
                background-color: #2d2d30;
                border-color: #3c3c3c;
                color: #6f6f6f;
            }}
            QPushButton#SmallPrimaryBtn {{
                background-color: transparent;
                color: #9cdcfe;
                border: 1px solid {self.colors['accent_dark']};
                border-radius: 4px;
                padding: 0 7px;
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton#SmallPrimaryBtn:hover {{
                background-color: #0e639c;
                border-color: {self.colors['accent']};
                color: #ffffff;
            }}
            QPushButton#SmallPrimaryBtn:pressed {{
                background-color: #094771;
            }}
            QPushButton#DangerBtn {{
                background-color: transparent;
                color: {self.colors['danger']};
                border: 1px solid #8f3f3f;
                border-radius: 4px;
                padding: 0 7px;
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton#DangerBtn:hover {{
                background-color: #5a1d1d;
                border-color: {self.colors['danger']};
                color: #ffffff;
            }}
            QPushButton#DangerBtn:pressed {{
                background-color: #451717;
            }}
            QPushButton#GhostBtn {{
                background-color: #2d2d30;
                color: {self.colors['text']};
                border: 1px solid {self.colors['border']};
                border-radius: 4px;
                padding: 0 7px;
                font-size: 12px;
            }}
            QPushButton#GhostBtn:hover {{
                background-color: #37373d;
                border-color: #5a5a5a;
                color: {self.colors['text_bright']};
            }}
            QPushButton#GhostBtn:pressed {{
                background-color: #252526;
            }}
            QPushButton#GhostBtn:disabled {{
                background-color: #253241;
                border-color: {self.colors['accent_dark']};
                color: #9cdcfe;
            }}
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 2px 0;
            }}
            QScrollBar::handle:vertical {{
                background: #424242;
                border-radius: 4px;
                min-height: 28px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #5a5a5a;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QLabel#FooterStatus {{
                color: {self.colors['text']};
                font-size: 11px;
                font-weight: 500;
                background: transparent;
                padding: 0 8px;
                min-height: 20px;
                max-height: 22px;
            }}
        """)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(10, 12, 10, 2)
        root.setSpacing(0)

        # ================================================================
        # HEADER
        # ================================================================
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(6)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        plugin_name = self.config.get("plugin_name", "Plugin")
        title_lbl = QLabel(f"{plugin_name} Deployer")
        title_lbl.setObjectName("AppTitle")
        title_lbl.setToolTip(title_lbl.text())
        title_lbl.setMinimumWidth(220)
        title_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        title_col.addWidget(title_lbl)
        title_col.setAlignment(Qt.AlignVCenter)

        sub_lbl = QLabel("Plugin deployment console")
        sub_lbl.setObjectName("AppSubtitle")
        title_col.addWidget(sub_lbl)

        header.addLayout(title_col, 1)

        # Version pill
        ver_pill = QLabel(f"v{self.current_version}")
        ver_pill.setObjectName("VersionBadge")
        ver_pill.setAlignment(Qt.AlignCenter)
        ver_pill.setFixedSize(48, 38)
        header.addWidget(ver_pill, 0, Qt.AlignVCenter)

        root.addLayout(header)
        root.addSpacing(12)

        # ================================================================
        # VERSION LIST CARD
        # ================================================================
        version_card = QFrame()
        version_card.setObjectName("Card")
        card_layout = QVBoxLayout(version_card)
        card_layout.setContentsMargins(7, 9, 7, 10)
        card_layout.setSpacing(8)

        # Card header row
        card_header = QHBoxLayout()
        card_header.setContentsMargins(0, 0, 0, 0)
        card_header.setSpacing(6)
        sec_title = QLabel("DETECTED TARGETS")
        sec_title.setObjectName("SectionTitle")
        card_header.addWidget(sec_title, 0, Qt.AlignVCenter)
        card_header.addStretch()

        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setObjectName("GhostBtn")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setFixedSize(74, 30)
        self.btn_refresh.clicked.connect(self._refresh_with_animation)
        card_header.addWidget(self.btn_refresh, 0, Qt.AlignVCenter)
        card_layout.addLayout(card_header)

        # Divider line
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("color: #3c3c3c; background-color: #3c3c3c; border: none; max-height: 1px;")
        card_layout.addWidget(divider)

        # Scroll area for version rows
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(214)

        self.rows_container = QWidget()
        self.rows_container.setStyleSheet("background: transparent;")
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        self.rows_layout.setSpacing(4)
        self.rows_layout.addStretch()

        scroll.setWidget(self.rows_container)
        card_layout.addWidget(scroll)

        root.addWidget(version_card)
        root.addSpacing(8)

        # ================================================================
        # DEPLOY ALL BUTTON
        # ================================================================
        self.btn_deploy_all = QPushButton("Deploy to All")
        self.btn_deploy_all.setObjectName("PrimaryBtn")
        self.btn_deploy_all.setCursor(Qt.PointingHandCursor)
        self.btn_deploy_all.setFixedHeight(35)
        self.btn_deploy_all.clicked.connect(self.deploy_all)
        root.addWidget(self.btn_deploy_all)

        root.addSpacing(4)

        # ================================================================
        # FOOTER
        # ================================================================
        footer = QHBoxLayout()
        footer.setContentsMargins(0, 5, 0, 0)
        footer.setSpacing(6)

        plugin_owner = self.config.get("plugin_owner", "Unknown")
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("FooterStatus")
        self.status_label.setToolTip(f"Plugin Owner: {plugin_owner}")
        self.status_label.setMinimumWidth(120)
        self.status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        footer.addWidget(self.status_label, 1, Qt.AlignVCenter)
        self._status_bar = FooterStatusProxy(self.status_label)

        self.btn_update = QPushButton("Updates")
        self.btn_update.setObjectName("GhostBtn")
        self.btn_update.setCursor(Qt.PointingHandCursor)
        self.btn_update.setFixedSize(78, 30)
        self.btn_update.clicked.connect(self.check_updates)
        footer.addWidget(self.btn_update, 0, Qt.AlignVCenter)

        root.addLayout(footer)
        self.statusBar().showMessage("Ready")

    # ------------------------------------------------------------------
    def statusBar(self):
        return self._status_bar

    # ------------------------------------------------------------------
    def _refresh_with_animation(self):
        """Show a polished loading state on Refresh, then reload targets."""
        if self._refresh_timer and self._refresh_timer.isActive():
            return

        self._refresh_frame = 0
        self.btn_refresh.setEnabled(False)
        self.btn_refresh.setCursor(Qt.BusyCursor)
        self.statusBar().showMessage("Refreshing detected targets…")

        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(90)
        self._refresh_timer.timeout.connect(self._tick_refresh_animation)
        self._refresh_timer.start()
        self._tick_refresh_animation()

        QTimer.singleShot(650, self._finish_refresh_animation)

    def _tick_refresh_animation(self):
        frame = self._refresh_frames[self._refresh_frame % len(self._refresh_frames)]
        self.btn_refresh.setText(frame)
        self._refresh_frame += 1

    def _finish_refresh_animation(self):
        if self._refresh_timer:
            self._refresh_timer.stop()

        self.load_installed_versions()
        self.btn_refresh.setText("Refresh")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setEnabled(True)

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
                f"color: {self.colors['text_dim']}; font-size: 12px; padding: 18px;"
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
                self.rows_layout.insertWidget(self.rows_layout.count() - 1, row)

                if idx < len(versions) - 1:
                    sep = QFrame()
                    sep.setFrameShape(QFrame.HLine)
                    sep.setStyleSheet("border: none; background-color: #323232; max-height: 1px; min-height: 1px;")
                    self.rows_layout.insertWidget(self.rows_layout.count() - 1, sep)

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
