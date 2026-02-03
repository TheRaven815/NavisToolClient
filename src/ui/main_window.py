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
        self.setMinimumSize(500, 600)
        self.init_ui()
        self.load_installed_versions()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Style
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f5f7; }
            QLabel { color: #333; font-size: 14px; font-weight: bold; }
            QPushButton { 
                background-color: #007aff; 
                color: white; 
                border-radius: 8px; 
                padding: 10px; 
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #0063cc; }
            QPushButton#secondary { background-color: #e5e5ea; color: #333; }
            QPushButton#secondary:hover { background-color: #d1d1d6; }
            QListWidget { 
                background-color: white; 
                border: 1px solid #d1d1d6; 
                border-radius: 8px; 
                padding: 5px;
            }
            QFrame#card {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e5e5ea;
            }
        """)

        # Title
        title = QLabel("Navisworks Plugin Deployer")
        title.setStyleSheet("font-size: 24px; color: #1d1d1f; margin-bottom: 10px;")
        layout.addWidget(title)

        # Version Selection
        layout.addWidget(QLabel("Detected Navisworks Versions"))
        self.version_list = QListWidget()
        self.version_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.version_list)

        # Source Files
        layout.addWidget(QLabel("Plugin Files (DLLs)"))
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No files selected")
        self.file_label.setStyleSheet("font-weight: normal; color: #666;")
        file_layout.addWidget(self.file_label)
        
        btn_select = QPushButton("Select Files")
        btn_select.setObjectName("secondary")
        btn_select.clicked.connect(self.select_files)
        file_layout.addWidget(btn_select)
        layout.addLayout(file_layout)

        # Deploy Button
        self.btn_deploy = QPushButton("Deploy to Selected Versions")
        self.btn_deploy.setFixedHeight(50)
        self.btn_deploy.clicked.connect(self.deploy_plugins)
        layout.addWidget(self.btn_deploy)

        self.selected_files = []

    def load_installed_versions(self):
        versions = self.navis.detect_installed_versions()
        for v in versions:
            item = QListWidgetItem(f"Navisworks Manage {v}")
            item.setData(Qt.UserRole, v)
            self.version_list.addItem(item)
        
        if not versions:
            self.version_list.addItem("No Navisworks installations found")

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select DLL Files", "", "DLL Files (*.dll);;All Files (*)"
        )
        if files:
            self.selected_files = files
            self.file_label.setText(f"{len(files)} files selected")

    def deploy_plugins(self):
        selected_items = self.version_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select at least one Navisworks version.")
            return
        
        if not self.selected_files:
            QMessageBox.warning(self, "Warning", "Please select plugin files to deploy.")
            return

        success_count = 0
        errors = []

        for item in selected_items:
            version = item.data(Qt.UserRole)
            success, msg = self.navis.deploy_plugin(version, self.selected_files)
            if success:
                success_count += 1
            else:
                errors.append(f"Version {version}: {msg}")

        if success_count > 0:
            QMessageBox.information(self, "Success", f"Deployed to {success_count} versions.")
        
        if errors:
            QMessageBox.critical(self, "Error", "\n".join(errors))
