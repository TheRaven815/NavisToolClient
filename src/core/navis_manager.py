import os
import shutil

class NavisManager:
    def __init__(self, config_manager):
        self.config = config_manager
        # Enable DEBUG mode for testing phase
        self.DEBUG_MODE = True

    def detect_installed_versions(self):
        installed_versions = []
        base_path_template = self.config.get("target_base_path")
        versions = self.config.get("navis_versions", [])
        
        for version in versions:
            # Check if the folder for this version exists
            check_path = f"C:/Program Files/Autodesk/Navisworks Manage {version}"
            if os.path.exists(check_path):
                installed_versions.append(version)
        
        # Show "DEBUG" item in the list for testing
        if self.DEBUG_MODE:
            installed_versions.append("DEBUG")
            
        return installed_versions

    def deploy_plugin(self, version):
        plugin_name = self.config.get("plugin_name", "NewPlugin")
        source_folder_name = self.config.get("source_folder_name", plugin_name)
        version_prefix = self.config.get("version_folder_prefix", "Navis")
        
        # Use local folder for DEBUG version
        if version == "DEBUG":
            available_versions = self.config.get("navis_versions", ["2022"])
            test_version = available_versions[0]
            source_dir = os.path.join(os.getcwd(), source_folder_name, f"{version_prefix}{test_version}")
            target_dir = os.path.join(os.getcwd(), "DEBUG_PLUGINS")
            display_version = "LOCAL DEBUG"
        else:
            source_dir = os.path.join(os.getcwd(), source_folder_name, f"{version_prefix}{version}")
            target_template = self.config.get("target_base_path")
            target_dir = target_template.format(version=version)
            display_version = f"Navisworks {version}"

        if not os.path.exists(source_dir):
            return False, f"Source directory not found: {source_dir}"

        plugin_target_dir = os.path.join(target_dir, plugin_name)

        try:
            if os.path.exists(plugin_target_dir):
                shutil.rmtree(plugin_target_dir)
            
            os.makedirs(plugin_target_dir, exist_ok=True)
            
            files_to_copy = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]
            
            if not files_to_copy:
                return False, f"No files found in source: {source_dir}"

            for file_name in files_to_copy:
                shutil.copy2(os.path.join(source_dir, file_name), plugin_target_dir)
                
            return True, f"Successfully deployed {len(files_to_copy)} files to {display_version}."
        except Exception as e:
            return False, f"Error during deployment to {display_version}: {str(e)}"
