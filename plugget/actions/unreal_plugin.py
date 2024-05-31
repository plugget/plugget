import sys

import unreal
from pathlib import Path
import shutil


import plugget.actions._copy_files
import plugget.actions.unreal_utils


class _Action(plugget.actions._copy_files.CopyFiles):
    target_dir = plugget.actions.unreal_utils.get_plugin_path()

    @classmethod
    def install(cls, package: "plugget.data.Package", **kwargs) -> bool:
        super().install(package, **kwargs)
        plugget.actions.unreal_utils.enable_plugin(package.package_name)
        plugin_path = plugget.actions.unreal_utils.project_plugins_dir() / package.package_name
        plugget.actions.unreal_utils.exec_plugin_startup_code(plugin_path)

    @classmethod
    def uninstall(cls, package: "plugget.data.Package", **kwargs) -> bool:
        plugget.actions.unreal_utils.enable_plugin(package.package_name, enable=False)
        super().uninstall(package, **kwargs)


install = _Action.install
uninstall = _Action.uninstall
__all__ = ["install", "uninstall"]
