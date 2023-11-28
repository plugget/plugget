"""
A Plugget action to pip install Python dependencies from requirements.txt for 3ds Max.
"""

import os
import sys
from pathlib import Path
from plugget.actions._requirements import RequirementsAction


def _get_interpreter_path() -> Path:
    # TODO support other OS, see
    #  https://help.autodesk.com/view/MAYAUL/2023/ENU/?guid=GUID-D64ACA64-2566-42B3-BE0F-BCE843A1702F
    windows_python = Path(sys.executable).parent / "mayapy.exe"
    return windows_python


def _get_user_scripts_dir() -> Path:
    MAYA_APP_DIR: str = os.environ.get("MAYA_APP_DIR")  # env var set by maya on startup
    MAYA_VERSION: str = os.environ.get("PLUGGET_MAYA_VERSION")
    maya_version = MAYA_VERSION
    if not maya_version:
        import maya.cmds as cmds
        maya_version = cmds.about(version=True)
    return Path(MAYA_APP_DIR) / maya_version / "scripts"


class _Action(RequirementsAction):
    env_var = "MAYA"
    interpreter = _get_interpreter_path()
    target = _get_user_scripts_dir()


install = _Action.install
uninstall = _Action.uninstall
__all__ = ["install", "uninstall"]


