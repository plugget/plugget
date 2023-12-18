import plugget.actions._copy_files
from plugget.actions._utils import get_my_documents
from pathlib import Path
import importlib


class _Action(plugget.actions._copy_files.CopyFiles):
    target_dir = get_my_documents() / "Adobe" / "Adobe Substance 3D Painter" / "python" / "plugins"

    @classmethod
    def install(cls, package: "plugget.data.Package", **kwargs) -> bool:
        result = super().install(package, **kwargs)

        # todo refresh plugins in substance painter
        import substance_painter_plugins

        # substance_painter_plugins.update_sys_path()

        # Start the Plugin if it wasn't already: (.py name)
        for plugin_path in package.installed_paths:
            plugin_name = Path(plugin_path).stem

            plugin = importlib.import_module(plugin_name)
            if not substance_painter_plugins.is_plugin_started(plugin):
                substance_painter_plugins.start_plugin(plugin_name)

        return result

install = _Action.install
uninstall = _Action.uninstall
__all__ = ["install", "uninstall"]
