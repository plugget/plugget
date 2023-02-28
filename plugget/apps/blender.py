import bpy
import addon_utils
from pathlib import Path
import shutil
import logging


"""
Blender plugins are named addons
addons in Blender are folders of scripts, and can be enabled/disabled
"""


def is_installed(name):
    """check if plugin is installed, use plugin_name from manifest, checking folder name in addons"""
    local_script_dir = bpy.utils.script_path_user()
    local_addons_dir = Path(local_script_dir) / "addons"
    return (local_addons_dir / name).exists()


def installed_plugins():
    """return list of installed plugins"""
    # Blender names returned are from the operator, but plugin_name in the manifest refers to the blender folder name
    # todo ideally we return a name thats useable in the pluggest install commands
    return [mod.bl_info.get("name") for mod in addon_utils.modules()]


def enabled_plugins() -> list[str]:
    """return list of enabled plugins"""
    # Blender names returned are from the operator, but plugin_name in the manifest refers to the blender folder name
    # todo ideally we return a name thats useable in the pluggest install commands
    return bpy.context.preferences.addons.keys()


def disabled_plugins() -> list[str]:
    """return list of disabled plugins"""
    # Blender names returned are from the operator, but plugin_name in the manifest refers to the blender folder name
    # todo ideally we return a name thats useable in the pluggest install commands
    return [p for p in installed_plugins() if p not in enabled_plugins()]


def disable_plugin(name):
    """disable plugin by name"""
    bpy.ops.preferences.addon_disable(module=name)


def enable_plugin(name):
    """enable plugin by name"""
    bpy.ops.preferences.addon_enable(module=name)


def install_plugin(plugin_paths: list[Path]) -> bool:  # todo , force=False, enable=True):
    """install plugin from path"""
    # If the “overwrite” parameter is True, the add-on will be reinstalled, even if it has not been previously removed.

    # manifest is named io_xray
    # but subdir is io_scene_xray
    # resulting in clashes. we cant just rename the subdir, might break code inside.
    # so we need to track the "name" with plugin_name in the manifest

    # todo fix only support 1 plugin
    plugin_path = plugin_paths[0]
    if len(plugin_paths) > 1:
        raise NotImplemented("Only 1 plugin can be installed at a time for now")

    local_script_dir = bpy.utils.script_path_user()
    local_addons_dir = Path(local_script_dir) / "addons"
    new_plugin_path = local_addons_dir / plugin_path.name
    shutil.move(str(plugin_path), str(new_plugin_path.parent))  # copy plugin_path to local_addons_dir

    # check if plugin folder was copied, by checking if any files are in new_plugin_path
    if not any(new_plugin_path.iterdir()):
        logging.warning(f"Failed to install plugin {plugin_path.name}")
        return False
    else:
        return True


def uninstall_plugin(name):
    """uninstall plugin by name"""
    if not name:
        logging.warning("No plugin name given")
        return
    bpy.ops.preferences.addon_remove(module=name)


def open_install_dir():
    """Open the directory where plugins are installed"""
    local_script_dir = bpy.utils.script_path_user()
    local_addons_dir = Path(local_script_dir) / "addons"
    bpy.ops.wm.path_open(filepath=str(local_addons_dir))
