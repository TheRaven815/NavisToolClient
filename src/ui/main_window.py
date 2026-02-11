from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QListWidget, 
                             QListWidgetItem, QMessageBox, QFrame)
from PySide6.QtCore import Qt
from src.core.navis_manager import NavisManager
from src.utils.config_manager import ConfigManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.navis = NavisManager(self.config)
        
        self.setWindowTitle("Navisworks Tool Client")
        self.setMinimumSize(450, 480)
        self.init_ui()
        self.load_installed_versions()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 15, 20, 10)

        # Style - Minimalist Dark Theme
        self.setStyleSheet("""
            QMainWindow { 
                background-color: #0c0c0c; 
            }
            QWidget {
                color: #e1e1e1;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel { 
                color: #e1e1e1; 
                font-size: 13px; 
                font-weight: 500;
            }
            QPushButton { 
                background-color: #2c2c2e; 
                color: #e1e1e1; 
                border: 1px solid #3a3a3c;
                border-radius: 6px; 
                padding: 8px 16px; 
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover { 
                background-color: #3a3a3c; 
            }
            QPushButton:pressed {
                background-color: #1c1c1e;
            }
            QPushButton#primary {
                background-color: #007aff;
                border-color: #007aff;
                color: white;
            }
            QPushButton#primary:hover {
                background-color: #0063cc;
            }
            QPushButton#secondary { 
                background-color: transparent; 
                border: 1px solid #3a3a3c;
                color: #e1e1e1; 
            }
            QPushButton#secondary:hover { 
                background-color: #2c2c2e; 
            }
            QListWidget { 
                background-color: #1c1c1e; 
                border: 1px solid #3a3a3c; 
                border-radius: 8px; 
                padding: 5px;
                color: #e1e1e1;
                outline: none;
            }
            QListWidget::item {
                padding: 4px 8px;
                border-radius: 4px;
                margin-bottom: 1px;
                font-size: 12px;
            }
            QListWidget::item:selected {
                background-color: #007aff;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #2c2c2e;
            }
            QFrame#separator {
                background-color: #3a3a3c;
                max-height: 1px;
            }
            QMessageBox {
                background-color: #1c1c1e;
            }
            QMessageBox QLabel {
                color: #e1e1e1;
            }
            QMessageBox QPushButton {
                min-width: 80px;
            }
        """)

        # Header Section (Title + Version Label)
        header_layout = QVBoxLayout()
        header_layout.setSpacing(2)
        
        plugin_name = self.config.get("plugin_name", "Navisworks")
        self.setWindowTitle(f"{plugin_name} Deployer")
        
        title = QLabel(f"{plugin_name} Deployer")
        title.setStyleSheet("font-size: 16px; color: #ffffff; font-weight: 600; margin: 0;")
        header_layout.addWidget(title)

        version_desc = QLabel("Detected Navisworks Versions")
        version_desc.setStyleSheet("color: #8e8e93; font-size: 11px; font-weight: normal; margin: 0;")
        header_layout.addWidget(version_desc)
        
        layout.addLayout(header_layout)
        self.version_list = QListWidget()
        self.version_list.setSelectionMode(QListWidget.MultiSelection)
        self.version_list.setFixedHeight(120)  # Make list more compact
        layout.addWidget(self.version_list)

        # Status Info Section
        status_layout = QVBoxLayout()
        status_layout.setSpacing(5)
        
        plugin_name = self.config.get("plugin_name", "NavisIFCExport")
        source_folder = self.config.get("source_folder_name", plugin_name)
        
        info_label = QLabel(f"Deployment Source: ./{source_folder}/")
        info_label.setStyleSheet("color: #8e8e93; font-size: 11px; font-weight: normal;")
        status_layout.addWidget(info_label)
        
        layout.addLayout(status_layout)

        # Deploy Button
        layout.addSpacing(5)
        self.btn_deploy = QPushButton(f"Deploy {plugin_name} to Selected Versions")
        self.btn_deploy.setObjectName("primary")
        self.btn_deploy.clicked.connect(self.deploy_plugins)
        layout.addWidget(self.btn_deploy)

        # Separator
        layout.addSpacing(10)
        line = QFrame()
        line.setObjectName("separator")
        line.setStyleSheet("background-color: #2c2c2e; max-height: 1px; border: none;")
        layout.addWidget(line)

        # Footer / Update Section
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(5, 5, 5, 5)
        
        version_info = QWidget()
        version_vbox = QVBoxLayout(version_info)
        version_vbox.setContentsMargins(0, 0, 0, 0)
        version_vbox.setSpacing(2)
        
        v_title = QLabel("SYSTEM STATUS")
        v_title.setStyleSheet("color: #48484a; font-size: 9px; font-weight: bold; text-transform: uppercase;")
        version_vbox.addWidget(v_title)
        
        v_num = QLabel("Version 1.0.1 - Stable")
        v_num.setStyleSheet("color: #8e8e93; font-size: 10px;")
        version_vbox.addWidget(v_num)
        
        footer_layout.addWidget(version_info)
        footer_layout.addStretch()
        
        btn_update = QPushButton("Check for Updates")
        btn_update.setCursor(Qt.PointingHandCursor)
        btn_update.setStyleSheet("""
            QPushButton { 
                background-color: #1c1c1e; 
                border: 1px solid #3a3a3c;
                border-radius: 4px;
                color: #e1e1e1; 
                font-size: 10px; 
                padding: 4px 10px;
            }
            QPushButton:hover { background-color: #2c2c2e; border-color: #007aff; }
        """)
        btn_update.clicked.connect(self.check_updates)
        footer_layout.addWidget(btn_update)
        layout.addLayout(footer_layout)

    def check_updates(self):
        QMessageBox.information(self, "Update", "Checking for updates... (Already up to date)")

    def load_installed_versions(self):
        versions = self.navis.detect_installed_versions()
        for v in versions:
            item = QListWidgetItem(f"Navisworks Manage {v}")
            item.setData(Qt.UserRole, v)
            # Pre-select installed versions by default
            item.setSelected(True)
            self.version_list.addItem(item)
        
        if not versions:
            self.version_list.addItem("No Navisworks installations found")

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
