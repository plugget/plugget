import bpy
import addon_utils


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
    bpy.ops.wm.addon_disable(module=name)

def enable_plugin(name):
    bpy.ops.wm.addon_enable(module=name)

def install_plugin(path, force=False, enable=True):
    # If the “overwrite” parameter is True, the add-on will be reinstalled, even if it has not been previously removed.
    bpy.ops.wm.addon_install(filepath=path, overwrite=force)
    if enable:
        enable_plugin(name)

def uninstall_plugin(name):
    bpy.ops.wm.addon_remove(module=name)