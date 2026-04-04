import os
import shutil


class NavisManager:
    def __init__(self, config_manager):
        self.config = config_manager
        # Enable DEBUG mode for testing phase
        self.DEBUG_MODE = True

    def detect_installed_versions(self):
        installed_versions = []
        versions = self.config.get("navis_versions", [])
        
        for version in versions:
            # Check if Navisworks is installed on this machine
            check_path = f"C:/Program Files/Autodesk/Navisworks Manage {version}"
            if os.path.exists(check_path):
                installed_versions.append(version)
        
        # Show "DEBUG" item in the list for testing
        if self.DEBUG_MODE:
            installed_versions.append("DEBUG")
            
        return installed_versions

    def is_plugin_installed(self, version):
        """Check if the plugin is currently deployed for a given Navisworks version."""
        plugin_name = self.config.get("plugin_name", "NewPlugin")

        if version == "DEBUG":
            target_dir = os.path.join(os.getcwd(), "DEBUG_PLUGINS", plugin_name)
        else:
            target_template = self.config.get("target_base_path")
            target_dir = os.path.join(target_template.format(version=version), plugin_name)

        if not os.path.exists(target_dir):
            return False
        # Consider installed if folder exists and has at least one file
        try:
            files = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]
            return len(files) > 0
        except Exception:
            return False

    def _get_allowed_extensions(self):
        """Return normalized extension filters for plugin copy operation."""
        copy_extensions = self.config.get("copy_extensions", {})
        if not isinstance(copy_extensions, dict):
            return set()

        plugin_extensions = copy_extensions.get("plugin", [])
        if not isinstance(plugin_extensions, list):
            return set()

        normalized = set()
        for ext in plugin_extensions:
            if not isinstance(ext, str):
                continue
            ext = ext.strip().lower()
            if not ext:
                continue
            if not ext.startswith("."):
                ext = f".{ext}"
            normalized.add(ext)
        return normalized

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

            source_files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]

            if not source_files:
                return False, f"No files found in source: {source_dir}"

            allowed_extensions = self._get_allowed_extensions()
            if allowed_extensions:
                files_to_copy = [
                    file_name
                    for file_name in source_files
                    if os.path.splitext(file_name)[1].lower() in allowed_extensions
                ]
            else:
                files_to_copy = source_files

            if not files_to_copy:
                return False, (
                    f"No files matched configured plugin extensions in source: {source_dir}. "
                    f"Allowed: {', '.join(sorted(allowed_extensions))}"
                )

            for file_name in files_to_copy:
                shutil.copy2(os.path.join(source_dir, file_name), plugin_target_dir)

            return True, f"Successfully deployed {len(files_to_copy)} files to {display_version}."
        except Exception as e:
            return False, f"Error during deployment to {display_version}: {str(e)}"

    def uninstall_plugin(self, version):
        """Remove the plugin from the given Navisworks version target directory."""
        plugin_name = self.config.get("plugin_name", "NewPlugin")

        if version == "DEBUG":
            target_dir = os.path.join(os.getcwd(), "DEBUG_PLUGINS", plugin_name)
            display_version = "LOCAL DEBUG"
        else:
            target_template = self.config.get("target_base_path")
            target_dir = os.path.join(target_template.format(version=version), plugin_name)
            display_version = f"Navisworks {version}"

        if not os.path.exists(target_dir):
            return False, f"Plugin is not installed for {display_version}."

        try:
            shutil.rmtree(target_dir)
            return True, f"Plugin successfully removed from {display_version}."
        except Exception as e:
            return False, f"Error during uninstall from {display_version}: {str(e)}"
