"""
A Plugget action to pip install Python dependencies from requirements.txt for 3ds Max.
"""

import os
import sys
from pathlib import Path
from plugget.actions._requirements import RequirementsAction


def _get_interpreter_path():
    # TODO support other OS, see
    #  https://help.autodesk.com/view/MAYAUL/2023/ENU/?guid=GUID-D64ACA64-2566-42B3-BE0F-BCE843A1702F
    windows_python = Path(sys.executable).parent / "mayapy.exe"
    return windows_python


MAYA_APP_DIR = Path(os.environ.get("MAYA_APP_DIR"))
# import maya.cmds as cmds
# v = cmds.about(version=True)
target = MAYA_APP_DIR / "2024" / "scripts"


class _Action(RequirementsAction):
    env_var = "MAYA"
    interpreter = _get_interpreter_path()
    target = None  # todo, user documents / maya / version / ....


install = _Action.install
uninstall = _Action.uninstall
__all__ = ["install", "uninstall"]


