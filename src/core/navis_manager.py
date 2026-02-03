import os
import shutil
import glob

class NavisManager:
    def __init__(self, config_manager):
        self.config = config_manager

    def detect_installed_versions(self):
        installed_versions = []
        base_path_template = self.config.get("target_base_path")
        versions = self.config.get("navis_versions", [])
        
        for version in versions:
            # Check if the folder for this version exists
            check_path = f"C:/Program Files/Autodesk/Navisworks Manage {version}"
            if os.path.exists(check_path):
                installed_versions.append(version)
        return installed_versions

    def deploy_plugin(self, version, source_files, plugin_name=None):
        if not plugin_name:
            plugin_name = self.config.get("plugin_name", "NewPlugin")
            
        target_template = self.config.get("target_base_path")
        target_dir = target_template.format(version=version)
        plugin_target_dir = os.path.join(target_dir, plugin_name)

        try:
            if not os.path.exists(plugin_target_dir):
                os.makedirs(plugin_target_dir)
            
            for file_path in source_files:
                if os.path.isfile(file_path):
                    shutil.copy2(file_path, plugin_target_dir)
            return True, f"Successfully deployed to Navisworks {version}"
        except Exception as e:
            return False, str(e)
