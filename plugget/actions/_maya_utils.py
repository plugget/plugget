import os
import sys
from pathlib import Path
from plugget.actions._utils import try_except


def get_interpreter_path() -> Path:
    # TODO support other OS, see
    #  https://help.autodesk.com/view/MAYAUL/2023/ENU/?guid=GUID-D64ACA64-2566-42B3-BE0F-BCE843A1702F
    windows_python = Path(sys.executable).parent / "mayapy.exe"
    return windows_python


def get_user_scripts_dir() -> Path:
    """
    Return the user scripts dir for the current Maya version.
    """
    MAYA_APP_DIR: str = os.environ.get("MAYA_APP_DIR")  # env var set by maya on startup
    MAYA_VERSION: str = os.environ.get("PLUGGET_MAYA_VERSION")
    maya_version = MAYA_VERSION
    if not maya_version:
        maya_version = get_maya_version()
    return Path(MAYA_APP_DIR) / maya_version / "scripts"


def get_maya_version() -> str:
    import maya.cmds as cmds
    return cmds.about(version=True)


def get_plugin_path():
    """return the path to the plugin folder"""
    # todo support other OS
    documents = Path(os.environ.get("USERPROFILE")) / "Documents"
    maya_version = get_maya_version()
    plugin_path = documents / "maya" / maya_version / "plug-ins"
    return plugin_path


def enable_plugin(name, quiet=True):
    """enable a Maya plugin by name"""
    import maya.cmds as cmds
    cmds.loadPlugin(name, quiet=quiet)  # load the plugin
    cmds.pluginInfo(name, edit=True, autoload=True)  # set autoload on startup


def disable_plugin(name, quiet=True):
    """disable a Maya plugin by name"""
    import maya.cmds as cmds
    cmds.unloadPlugin(name, quiet=quiet)  # load the plugin
    cmds.pluginInfo(name, edit=True, autoload=False)  # set autoload on startup


@try_except  # make this optional for now, accept fail
def enable_maya_plugins(package: "plugget.data.Package"):
    """enable all plugins in the package"""
    # usually only 1 plugin per package
    for full_path in package.installed_paths:
        full_path = Path(full_path)
        if full_path.suffix == ".py":
            print("enabling plugin", full_path.name)
            enable_plugin(full_path.name)
