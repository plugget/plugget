"""
A Plugget action to pip install Python dependencies from requirements.txt for 3ds Max.
"""

import site
from pathlib import Path
import sys
from plugget.actions._requirements import RequirementsAction


def _get_interpreter_path():
    windows_python = Path(sys.executable).parent / "Python" / "python.exe"  # TODO support other OS
    return windows_python


class _Action(RequirementsAction):
    env_var = "MAX"
    interpreter = _get_interpreter_path()
    target = site.getsitepackages()[0]


install = _Action.install
uninstall = _Action.uninstall
__all__ = ["install", "uninstall"]