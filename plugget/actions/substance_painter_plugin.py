import plugget.actions._copy_files
from plugget.actions._utils import get_my_documents


class _Action(plugget.actions._copy_files.CopyFiles):
    target_dir = get_my_documents() / "Adobe" / "Adobe Substance 3D Painter" / "python" / "plugins"

    @classmethod
    def install(cls, package: "plugget.data.Package", **kwargs) -> bool:
        super().install(package, **kwargs)


install = _Action.install
uninstall = _Action.uninstall
__all__ = ["install", "uninstall"]
