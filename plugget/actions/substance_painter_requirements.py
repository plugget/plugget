"""
A Plugget action to pip install Python dependencies from requirements.txt for 3ds Max.
"""

from plugget.actions._requirements import RequirementsAction
from plugget.actions._utils import get_my_documents


class _Action(RequirementsAction):
    env_var = "SUBSTANCE_PAINTER"
    # interpreter = get_interpreter_path()  # TODO
    target = get_my_documents() / "Adobe" / "Adobe Substance 3D Painter" / "python" / "modules"


install = _Action.install
uninstall = _Action.uninstall
__all__ = ["install", "uninstall"]
