import plugget.actions._copy_files
from plugget.actions._max3ds_utils import get_plugin_path


class _Action(plugget.actions._copy_files.CopyFiles):
    target_dir = get_plugin_path()

    @classmethod
    def install(cls, package: "plugget.data.Package", **kwargs) -> bool:
        super().install(package, **kwargs)


install = _Action.install
uninstall = _Action.uninstall
__all__ = ["install", "uninstall"]
