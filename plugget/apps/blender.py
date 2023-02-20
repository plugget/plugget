import bpy
import addon_utils
from pathlib import Path
import shutil


# TODO uninstal/remove vs deactivate/disable


def installed_plugins():
    """return list of installed plugins"""
    # TODO get list of installed plugins
    return bpy.context.preferences.addons.keys()


def available_plugins():
    for mod in addon_utils.modules():
        print(mod.bl_info.get("name"))
        # print(mod.bl_info)


def disable_plugin(name):
    bpy.ops.preferences.addon_disable(module=name)

def enable_plugin(name):
    bpy.ops.preferences.addon_enable(module=name)

def install_plugin(plugin_path: Path, force=False, enable=True):
    # If the “overwrite” parameter is True, the add-on will be reinstalled, even if it has not been previously removed.

    local_script_dir = bpy.utils.script_path_user()
    local_addons_dir = Path(local_script_dir) / "addons"
    # copy plugin_path to local_addons_dir
    new_plugin_path = local_addons_dir / plugin_path.name
    # # create dir if not exists
    # if not new_plugin_path.exists():
    #     new_plugin_path.mkdir(parents=True)

    print(new_plugin_path, plugin_path)
    shutil.move(str(plugin_path), str(new_plugin_path.parent))  # todo permission error

    # get user path from bpy



    # bpy.ops.preferences.addon_install(filepath=path, overwrite=force)
    # if enable:
    #     enable_plugin(name)

def uninstall_plugin(name):
    bpy.ops.preferences.addon_remove(module=name)