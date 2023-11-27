"""
Plugget action to install dependencies from requirements.txt using pip.

PLUGGET_BLENDER_TARGET_MODULES: env var to set pip install target dir, else use blender user modules dir
PLUGGET_BLENDER_INTERPRETER: env var to set python interpreter for pip install, defaults to sys.executable
"""

from pathlib import Path
import sys
from plugget.actions._requirements import RequirementsAction
import os


def _get_modules_target_path():
    default_target_path = os.environ.get("PLUGGET_BLENDER_TARGET_MODULES")
    if not default_target_path:
        import bpy
        default_target_path = str(Path(str(bpy.utils.script_path_user())) / "modules")
    return default_target_path


class _Action(RequirementsAction):
    env_var = "BLENDER"
    interpreter = sys.executable
    target = _get_modules_target_path()


install = _Action.install
uninstall = _Action.uninstall
__all__ = ["install", "uninstall"]