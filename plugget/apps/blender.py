import bpy
import addon_utils
from pathlib import Path
import shutil
import logging


"""
Blender plugins are named addons
"""


def is_installed(name):
    """check if plugin is installed, use plugin_name from manifest, checking folder name in addons"""
    local_script_dir = bpy.utils.script_path_user()
    local_addons_dir = Path(local_script_dir) / "addons"
    print((local_addons_dir / name).exists())
    return (local_addons_dir / name).exists()


def installed_plugins():
    """return list of installed plugins"""
    # Blender names returned are from the operator, but plugin_name in the manifest refers to the blender folder name
    return [mod.bl_info.get("name") for mod in addon_utils.modules()]


def enabled_plugins() -> list[str]:
    """return list of enabled plugins"""
    # Blender names returned are from the operator, but plugin_name in the manifest refers to the blender folder name
    return bpy.context.preferences.addons.keys()


def disabled_plugins() -> list[str]:
    """return list of disabled plugins"""
    # Blender names returned are from the operator, but plugin_name in the manifest refers to the blender folder name
    return [p for p in installed_plugins() if p not in enabled_plugins()]


def disable_plugin(name):
    """disable plugin by name"""
    bpy.ops.preferences.addon_disable(module=name)


def enable_plugin(name):
    """enable plugin by name"""
    bpy.ops.preferences.addon_enable(module=name)


def install_plugin(plugin_path: Path) -> bool:  # todo , force=False, enable=True):
    """install plugin from path"""
    # If the “overwrite” parameter is True, the add-on will be reinstalled, even if it has not been previously removed.

    # manifest is named io_xray
    # but subdir is io_scene_xray
    # resulting in clashes. we cant just rename the subdir, might break code inside.
    # so we need to track the "name" with plugin_name in the manifest

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
