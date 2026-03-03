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
        # Balanced Dark Slate Palette
        self.colors = {
            "bg": "#1c1c1e",
            "card": "#2c2c2e",
            "accent": "#0a84ff",
            "accent_hover": "#409cff",
            "text": "#ffffff",
            "text_dim": "#a1a1a6",
            "border": "#3a3a3c"
        }

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['bg']};
            }}
            QWidget {{
                color: {self.colors['text']};
                font-family: 'Segoe UI', Arial;
            }}
            QFrame#Card {{
                background-color: {self.colors['card']};
                border: 1px solid {self.colors['border']};
                border-radius: 8px;
            }}
            QLabel#Title {{
                font-size: 18px;
                font-weight: 600;
                color: white;
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
                background-color: #3a3a3c;
                border-radius: 6px;
                padding: 6px 10px;
                margin-bottom: 4px;
                font-size: 12px;
            }}
            QListWidget::item:selected {{
                background-color: {self.colors['accent']};
                color: white;
            }}
            QListWidget::item:hover:!selected {{
                background-color: #48484a;
            }}
            QPushButton#PrimaryBtn {{
                background-color: {self.colors['accent']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton#PrimaryBtn:hover {{
                background-color: {self.colors['accent_hover']};
            }}
            QPushButton#GhostBtn {{
                background-color: transparent;
                color: {self.colors['text_dim']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 3px 8px;
                font-size: 10px;
            }}
            QPushButton#GhostBtn:hover {{
                background-color: #3a3a3c;
                color: white;
            }}
            QStatusBar {{
                background-color: {self.colors['bg']};
                color: {self.colors['text_dim']};
                font-size: 10px;
            }}
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 10)
        main_layout.setSpacing(0)

        # --- Header ---
        plugin_name = self.config.get("plugin_name", "Navisworks")
        title = QLabel(f"{plugin_name} Deployer")
        title.setObjectName("Title")
        main_layout.addWidget(title)
        
        subtitle = QLabel("Plugin management and deployment tool")
        subtitle.setObjectName("Subtitle")
        main_layout.addWidget(subtitle)
        main_layout.addSpacing(10)

        # --- Detection Card ---
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(10)

        section_header = QHBoxLayout()
        section_label = QLabel("Available Versions")
        section_label.setObjectName("SectionTitle")
        section_header.addWidget(section_label, 0, Qt.AlignVCenter)
        section_header.addStretch()
        
        refresh_label = QLabel("AUTO-DETECTED")
        refresh_label.setFixedHeight(16) # Fix height to prevent stretching
        refresh_label.setStyleSheet(f"""
            color: {self.colors['accent']}; 
            font-size: 8px; 
            font-weight: bold; 
            border: 1px solid {self.colors['accent']}; 
            border-radius: 3px; 
            padding: 1px 4px;
        """)
        section_header.addWidget(refresh_label, 0, Qt.AlignVCenter)
        
        card_layout.addLayout(section_header)

        self.version_list = QListWidget()
        self.version_list.setSelectionMode(QListWidget.MultiSelection)
        self.version_list.setFixedHeight(160)
        card_layout.addWidget(self.version_list)
        
        main_layout.addWidget(card)
        main_layout.addSpacing(15)

        # --- Action Section ---
        self.btn_deploy = QPushButton(f"Deploy to Selected Versions")
        self.btn_deploy.setObjectName("PrimaryBtn")
        self.btn_deploy.setCursor(Qt.PointingHandCursor)
        self.btn_deploy.clicked.connect(self.deploy_plugins)
        
        # Add shadow to primary button
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 132, 255, 60))
        shadow.setOffset(0, 3)
        self.btn_deploy.setGraphicsEffect(shadow)
        
        main_layout.addWidget(self.btn_deploy)
        
        # This push the footer to the bottom while keeping upper elements tight
        main_layout.addStretch()

        # --- Footer ---
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 10, 0, 5)
        
        version_label = QLabel(f"Version {self.current_version}")
        version_label.setStyleSheet(f"color: {self.colors['text_dim']}; font-size: 10px;")
        footer_layout.addWidget(version_label)
        
        footer_layout.addStretch()
        
        self.btn_update = QPushButton("Check for Updates")
        self.btn_update.setObjectName("GhostBtn")
        self.btn_update.setCursor(Qt.PointingHandCursor)
        self.btn_update.clicked.connect(self.check_updates)
        footer_layout.addWidget(self.btn_update)
        
        main_layout.addLayout(footer_layout)

        # Setup Status Bar
        self.setStatusBar(QStatusBar())

    def check_updates(self):
        self.btn_deploy.setEnabled(False)
        self.statusBar().showMessage("Güncellemeler denetleniyor...")
        
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
        self.statusBar().showMessage("")
        
        if result.get("update_available"):
            msg = f"Yeni Versiyon: {result['latest_version']}\n\nNotlar:\n{result['release_notes']}\n\nŞimdi indirip güncellemek istiyor musunuz?"
            reply = QMessageBox.question(self, "Güncelleme Mevcut", msg, QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.start_download(result["download_url"])
        else:
            QMessageBox.information(self, "Güncel", "Uygulamanız zaten güncel!")

    def on_update_error(self, error):
        self.btn_deploy.setEnabled(True)
        self.statusBar().showMessage("")
        QMessageBox.warning(self, "Hata", f"Güncelleme kontrolü başarısız: {error}")

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
        self.statusBar().showMessage(f"İndiriliyor: %{percent} ({downloaded/1024/1024:.1f}MB / {total/1024/1024:.1f}MB)")

    def on_download_finished(self, path):
        self.btn_deploy.setEnabled(True)
        self.statusBar().showMessage("İndirme tamamlandı!")
        
        QMessageBox.information(self, "Başarılı", "Güncelleme indirildi. Uygulama kapatılacak ve yeni versiyon başlatılacak.")
        
        try:
            import subprocess
            subprocess.Popen([path], shell=True)
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Yeni versiyon başlatılamadı: {e}")

    def on_download_error(self, error):
        self.btn_deploy.setEnabled(True)
        self.statusBar().showMessage("")
        QMessageBox.critical(self, "Hata", f"İndirme hatası: {error}")

    def load_installed_versions(self):
        self.version_list.clear()
        versions = self.navis.detect_installed_versions()
        for v in versions:
            item = QListWidgetItem(f"Navisworks Manage {v}")
            item.setData(Qt.UserRole, v)
            item.setSelected(True)
            self.version_list.addItem(item)
        
        if not versions:
            empty_item = QListWidgetItem("No Navisworks detected")
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
