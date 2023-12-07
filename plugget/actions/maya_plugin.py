import plugget.actions._copy_files
import plugget.actions._maya_utils


class _Action(plugget.actions._copy_files.CopyFiles):
    target_dir = plugget.actions._maya_utils.get_plugin_path()

    @classmethod
    def install(cls, package: "plugget.data.Package", **kwargs) -> bool:
        super().install(package, **kwargs)
        plugget.actions._maya_utils.enable_maya_plugins(package)

    @classmethod
    def uninstall(cls, package: "plugget.data.Package", **kwargs) -> bool:
        plugget.actions._maya_utils.disable_plugin(package)
        super().uninstall(package, **kwargs)

install = _Action.install
uninstall = _Action.uninstall
__all__ = ["install", "uninstall"]
