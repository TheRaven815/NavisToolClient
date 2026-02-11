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

    def deploy_plugin(self, version):
        plugin_name = self.config.get("plugin_name", "NewPlugin")
        source_folder_name = self.config.get("source_folder_name", plugin_name)
        version_prefix = self.config.get("version_folder_prefix", "Navis")
        
        # Local source path: {source_folder_name}/{version_prefix}{version}
        source_dir = os.path.join(os.getcwd(), source_folder_name, f"{version_prefix}{version}")
        
        if not os.path.exists(source_dir):
            return False, f"Source directory not found: {source_dir}"

        target_template = self.config.get("target_base_path")
        target_dir = target_template.format(version=version)
        plugin_target_dir = os.path.join(target_dir, plugin_name)

        try:
            # 1. Clear target directory if it exists
            if os.path.exists(plugin_target_dir):
                shutil.rmtree(plugin_target_dir)
            
            # 2. Create fresh target directory
            os.makedirs(plugin_target_dir)
            
            # 3. Copy all files from source to target
            files_to_copy = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]
            
            if not files_to_copy:
                return False, f"No files found in source: {source_dir}"

            for file_name in files_to_copy:
                shutil.copy2(os.path.join(source_dir, file_name), plugin_target_dir)
                
            return True, f"Successfully deployed {len(files_to_copy)} files to Navisworks {version}"
        except Exception as e:
            return False, f"Error during deployment to {version}: {str(e)}"
