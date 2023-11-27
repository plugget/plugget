"""
A Plugget action to pip install Python dependencies from requirements.txt for 3ds Max.
"""

import site
from pathlib import Path
import sys
from plugget.actions._requirements import RequirementsAction
import os


def _get_interpreter_path():
    # return "python"  # TODO hack since code below is buggy
    windows_python = Path(sys.executable).parent / "Python" / "python.exe"  # TODO support other OS
    return windows_python


def get_site_packages():
    # get env var APPDATA that contains 'C:\\Users\\hanne\\AppData\\Roaming\
    # todo support other OS
    roaming = os.environ.get("APPDATA")
    for path in sys.path:
        # get current python version in roaming
        if path.startswith(roaming):
            return path
            # 'C:\\Users\\hanne\\AppData\\Roaming\\Python\\Python39\\site-packages'
    # todo this path is not in site packages, might be a problem for pth files


class _Action(RequirementsAction):
    env_var = "MAX"
    interpreter = _get_interpreter_path()
    target = get_site_packages()

install = _Action.install
uninstall = _Action.uninstall
__all__ = ["install", "uninstall"]