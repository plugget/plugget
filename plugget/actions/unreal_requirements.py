from plugget.actions._requirements import RequirementsAction
from plugget.actions.unreal_utils import _get_interpreter_path, get_site_packages


class _Action(RequirementsAction):
    env_var = "UNREAL"
    interpreter = _get_interpreter_path()
    target = get_site_packages()


install = _Action.install
uninstall = _Action.uninstall
__all__ = ["install", "uninstall"]
