"""
A Plugget action to pip install Python dependencies from requirements.txt for 3ds Max.
"""

from plugget.actions._requirements import RequirementsAction
from plugget.actions._maya_utils import get_user_scripts_dir, get_interpreter_path


class _Action(RequirementsAction):
    env_var = "MAYA"
    interpreter = str(get_interpreter_path())
    target = str(get_user_scripts_dir())


install = _Action.install
uninstall = _Action.uninstall
__all__ = ["install", "uninstall"]
