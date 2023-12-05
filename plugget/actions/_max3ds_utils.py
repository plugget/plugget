
from pathlib import Path
import sys
import os


def _get_interpreter_path():
    # return "python"  # TODO hack since code below is buggy
    windows_python = Path(sys.executable).parent / "Python" / "python.exe"  # TODO support other OS
    return windows_python


def get_site_packages() -> str:
    """
    hacky way to get the site-packages path for the current python version
    return: (str) site-packages path, that is also in sys.path
    Your default Python env should then return the site-packages path for the current python version
    """
    # get env var APPDATA that contains 'C:\\Users\\hanne\\AppData\\Roaming\
    # todo support other OS
    roaming = os.environ.get("APPDATA")
    for path in sys.path:
        # get current python version in roaming
        if path.startswith(roaming):
            return path  # e.g. 'C:\\Users\\hanne\\AppData\\Roaming\\Python\\Python39\\site-packages'
    return ""
    # todo even though it's a site packages, this path is not in site packages in Max?,
    #  might be a problem for pth files


def get_plugin_path() -> Path:
    # https://help.autodesk.com/view/MAXDEV/2023/ENU/?guid=packaging_plugins
    return Path(os.environ.get("APPDATA")) / "Autodesk" / "ApplicationPlugins"
