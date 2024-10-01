import sys

import unreal
from pathlib import Path
import shutil


import plugget.actions._copy_files
import plugget.actions.unreal_utils as unreal_utils


class _Action(plugget.actions._copy_files.CopyFiles):
    target_dir = unreal_utils.get_plugins_path()

    @classmethod
    def install(cls, package: "plugget.data.Package", **kwargs) -> bool:
        super().install(package, **kwargs)
        # todo currently installs to
        #  - plugins/package-name/PluginName
        #  but should install to
        #  - plugins/PluginName
        # TODO current solution is a bit hacky, cleanup
        package_path = unreal_utils.project_plugins_dir() / package.package_name

        for plugin_name in unreal_utils.find_plugin_names(package_path):
            unreal_utils.enable_plugin(plugin_name)
            # plugin_path = unreal_utils.project_plugins_dir() / plugin_name
            unreal_utils.exec_plugin_startup_code(package_path)

    @classmethod
    def uninstall(cls, package: "plugget.data.Package", **kwargs) -> bool:
        unreal_utils.enable_plugin(package.package_name, enable=False)
        super().uninstall(package, **kwargs)


install = _Action.install
uninstall = _Action.uninstall
__all__ = ["install", "uninstall"]
