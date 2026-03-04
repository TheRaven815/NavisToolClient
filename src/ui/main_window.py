import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QListWidget, QListWidgetItem, 
                             QMessageBox, QFrame, QGraphicsDropShadowEffect, QStatusBar)
from PySide6.QtCore import Qt, QThread, QSize
from PySide6.QtGui import QColor, QFont, QIcon

from src.core.navis_manager import NavisManager
from src.utils.config_manager import ConfigManager
from src.core.updater.checker import UpdateWorker
from src.core.updater.downloader import DownloadWorker
from src.utils.constants import REPO_URL, UPDATE_FILENAME

class MainWindow(QMainWindow):
    def __init__(self, version):
        super().__init__()
        self.current_version = version
        self.config = ConfigManager()
        self.navis = NavisManager(self.config)
        
        self.update_thread = None
        self.download_thread = None
        
        self.setWindowTitle("Navisworks Tool Client")
        self.setMinimumSize(500, 450)
        self.init_ui()
        self.load_installed_versions()

    def init_ui(self):
        # VS Code Inspired Palette
        self.colors = {
            "bg": "#1e1e1e",
            "sidebar": "#252526",
            "card": "#2d2d2d",
            "accent": "#007acc",
            "accent_hover": "#1f8ad2",
            "text": "#cccccc",
            "text_bright": "#ffffff",
            "text_dim": "#858585",
            "border": "#3c3c3c",
            "warning": "#cca700"
        }

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['bg']};
            }}
            QWidget {{
                color: {self.colors['text']};
                font-family: 'Segoe UI', Inter, Arial;
            }}
            QFrame#Card {{
                background-color: {self.colors['sidebar']};
                border: 1px solid {self.colors['border']};
                border-radius: 4px;
            }}
            QLabel#Title {{
                font-size: 15px;
                font-weight: 600;
                color: {self.colors['text_bright']};
            }}
            QLabel#Subtitle {{
                font-size: 11px;
                color: {self.colors['text_dim']};
            }}
            QLabel#SectionTitle {{
                font-size: 10px;
                font-weight: 700;
                color: {self.colors['text_dim']};
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                background-color: transparent;
                border-radius: 3px;
                padding: 4px 8px;
                margin-bottom: 1px;
                font-size: 12px;
            }}
            QListWidget::item:selected {{
                background-color: #37373d;
                color: {self.colors['text_bright']};
                border: 1px solid {self.colors['accent']};
            }}
            QListWidget::item:hover:!selected {{
                background-color: #2a2d2e;
            }}
            QPushButton#PrimaryBtn {{
                background-color: {self.colors['accent']};
                color: white;
                border: none;
                border-radius: 3px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton#PrimaryBtn:hover {{
                background-color: {self.colors['accent_hover']};
            }}
            QPushButton#GhostBtn {{
                background-color: #3a3d41;
                color: {self.colors['text_bright']};
                border: none;
                border-radius: 3px;
                padding: 4px 10px;
                font-size: 11px;
            }}
            QPushButton#GhostBtn:hover {{
                background-color: #45494e;
            }}
            QStatusBar {{
                background-color: {self.colors['accent']};
                color: white;
                font-size: 11px;
            }}
            QStatusBar::item {{
                border: none;
            }}
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 8)
        main_layout.setSpacing(0)

        # --- Header ---
        header_layout = QVBoxLayout()
        plugin_name = self.config.get("plugin_name", "Navisworks")
        title = QLabel(f"{plugin_name} Deployer")
        title.setObjectName("Title")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Plugin Management Console")
        subtitle.setObjectName("Subtitle")
        header_layout.addWidget(subtitle)
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(12)

        # --- Detection Card ---
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(8, 8, 8, 8)
        card_layout.setSpacing(8)

        section_label = QLabel("Available Targets")
        section_label.setObjectName("SectionTitle")
        card_layout.addWidget(section_label)

        self.version_list = QListWidget()
        self.version_list.setSelectionMode(QListWidget.MultiSelection)
        self.version_list.setFixedHeight(180)
        card_layout.addWidget(self.version_list)
        
        main_layout.addWidget(card)
        main_layout.addSpacing(12)

        # --- Action Section ---
        self.btn_deploy = QPushButton(f"Deploy to Selected")
        self.btn_deploy.setObjectName("PrimaryBtn")
        self.btn_deploy.setCursor(Qt.PointingHandCursor)
        self.btn_deploy.clicked.connect(self.deploy_plugins)
        
        main_layout.addWidget(self.btn_deploy)
        
        main_layout.addStretch()

        # --- Footer ---
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 8, 0, 0)
        
        version_label = QLabel(f"v{self.current_version}")
        version_label.setStyleSheet(f"color: {self.colors['text_dim']}; font-size: 10px;")
        footer_layout.addWidget(version_label)
        
        footer_layout.addStretch()
        
        # Attribution
        attr_label = QLabel("Coded by Enes Eliağır")
        attr_label.setStyleSheet(f"color: {self.colors['text_dim']}; font-size: 10px;")
        footer_layout.addWidget(attr_label)
        
        footer_layout.addStretch()
        
        self.btn_update = QPushButton("Check for Updates")
        self.btn_update.setObjectName("GhostBtn")
        self.btn_update.setCursor(Qt.PointingHandCursor)
        self.btn_update.clicked.connect(self.check_updates)
        footer_layout.addWidget(self.btn_update)
        
        main_layout.addLayout(footer_layout)

        # Setup Status Bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")

    def check_updates(self):
        self.btn_deploy.setEnabled(False)
        self.statusBar().showMessage("🔍 Checking for updates...")
        
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
        self.btn_deploy.setEnabled(True)
        self.statusBar().showMessage("Ready.")
        
        if result.get("update_available"):
            msg = f"A new version is available: {result['latest_version']}\n\nNotes:\n{result['release_notes']}\n\nDo you want to download and update now?"
            reply = QMessageBox.question(self, "Update Available", msg, QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.start_download(result["download_url"])
        else:
            QMessageBox.information(self, "Up to Date", "Your application is already up to date!")

    def on_update_error(self, error):
        self.btn_deploy.setEnabled(True)
        self.statusBar().showMessage("Update check failed.")
        QMessageBox.warning(self, "Error", f"Update check failed: {error}")

    def start_download(self, url):
        save_path = os.path.join(os.getcwd(), UPDATE_FILENAME)
        
        self.download_thread = QThread()
        self.download_worker = DownloadWorker(url, save_path)
        self.download_worker.moveToThread(self.download_thread)
        
        self.download_thread.started.connect(self.download_worker.run)
        self.download_worker.progress.connect(self.on_download_progress)
        self.download_worker.finished.connect(self.on_download_finished)
        self.download_worker.error.connect(self.on_download_error)
        
        self.btn_deploy.setEnabled(False)
        self.download_thread.start()

    def on_download_progress(self, percent, downloaded, total):
        self.statusBar().showMessage(f"📥 Downloading: {percent}% ({downloaded/1024/1024:.1f}MB / {total/1024/1024:.1f}MB)")

    def on_download_finished(self, path):
        self.btn_deploy.setEnabled(True)
        self.statusBar().showMessage("Download complete!")
        
        QMessageBox.information(self, "Success", "Update downloaded. The application will close and start the new version.")
        
        try:
            import subprocess
            subprocess.Popen([path], shell=True)
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start new version: {e}")

    def on_download_error(self, error):
        self.btn_deploy.setEnabled(True)
        self.statusBar().showMessage("Download failed.")
        QMessageBox.critical(self, "Error", f"Download error: {error}")

    def load_installed_versions(self):
        self.version_list.clear()
        versions = self.navis.detect_installed_versions()
        for v in versions:
            if v == "DEBUG":
                item = QListWidgetItem(f"🛠️ LOCAL DEBUG (Target: ./DEBUG_PLUGINS)")
                item.setForeground(QColor(self.colors['warning']))
            else:
                item = QListWidgetItem(f"🏗️ Navisworks Manage {v}")
            
            item.setData(Qt.UserRole, v)
            item.setSelected(True)
            self.version_list.addItem(item)
        
        if not versions:
            empty_item = QListWidgetItem("❌ No Navisworks detected")
            empty_item.setFlags(Qt.NoItemFlags)
            self.version_list.addItem(empty_item)

    def deploy_plugins(self):
        selected_items = self.version_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select at least one Navisworks version.")
            return
        
        success_count = 0
        details = []

        for item in selected_items:
            version = item.data(Qt.UserRole)
            if not version: continue
            
            success, msg = self.navis.deploy_plugin(version)
            if success:
                success_count += 1
                details.append(f"✅ {msg}")
            else:
                details.append(f"❌ {msg}")

        if success_count > 0:
            QMessageBox.information(self, "Deployment Complete", "\n".join(details))
        else:
            QMessageBox.critical(self, "Deployment Failed", "\n".join(details))
