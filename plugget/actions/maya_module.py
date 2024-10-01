import plugget.actions._copy_files
import plugget.actions._maya_utils


class _Action(plugget.actions._copy_files.CopyFiles):
    target_dir = plugget.actions._maya_utils.get_modules_path()

    @classmethod
    def install(cls, package: "plugget.data.Package", **kwargs) -> bool:
        super().install(package, **kwargs)

        # TODO if modules folder doesnt exist yet.
        #  will maya detect the module if we create it and copy to it?

        # todo enable plugins if any in the module
        # plugget.actions._maya_utils.enable_maya_plugins(package)

    @classmethod
    def uninstall(cls, package: "plugget.data.Package", **kwargs) -> bool:
        # todo disable plugins if any in the module
        # plugget.actions._maya_utils.disable_plugin(package)
        super().uninstall(package, **kwargs)

install = _Action.install
uninstall = _Action.uninstall
__all__ = ["install", "uninstall"]
