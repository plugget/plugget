"""
A Plugget action to pip install Python dependencies from requirements.txt for 3ds Max.
"""

from plugget.actions._requirements import RequirementsAction
from plugget.actions._utils import get_my_documents
from pathlib import Path
import sys


def get_interpreter_path():
    return Path(sys.executable).parent / "resources" / "pythonsdk" / "python.exe"


class _Action(RequirementsAction):
    env_var = "SUBSTANCE_PAINTER"
    interpreter = get_interpreter_path()
    target = get_my_documents() / "Adobe" / "Adobe Substance 3D Painter" / "python" / "modules"


install = _Action.install
uninstall = _Action.uninstall
__all__ = ["install", "uninstall"]
