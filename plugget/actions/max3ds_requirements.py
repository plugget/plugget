"""
A Plugget action to pip install Python dependencies from requirements.txt for 3ds Max.
"""

from plugget.actions._requirements import RequirementsAction
from plugget.actions._max3ds_utils import _get_interpreter_path, get_site_packages


class _Action(RequirementsAction):
    env_var = "MAX"
    interpreter = _get_interpreter_path()
    target = get_site_packages()


install = _Action.install
uninstall = _Action.uninstall
__all__ = ["install", "uninstall"]
