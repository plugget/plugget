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
        plugget.actions.unreal_utils.enable_plugin(package, enable=False)
        super().uninstall(package, **kwargs)


install = _Action.install
uninstall = _Action.uninstall
__all__ = ["install", "uninstall"]





# def project_plugins_dir():
#     project_path = unreal.Paths.project_plugins_dir()
#     project_path = unreal.Paths.convert_relative_path_to_full(project_path)
#     return Path(project_path)
#
#
# def install(package: "plugget.data.Package", max_folder=None, **kwargs) -> bool:
#     plugin_dir = project_plugins_dir()
#
#     # move it to target folder
#     print(f"installing the unreal plugin '{package.package_name}' to '{plugin_dir / package.package_name}'")
#     # todo clean up this hack,
#     #  where we use get content to directly download to the plugin folder instead of a temp folder, and move it
#     repo_paths = package.get_content(target_dir=plugin_dir / package.package_name, use_cached=False)
#     # todo cloning directly in plugin dir works since unreal recursively searches for plugins.
#     #  but it's not the way it should be done.
#     #  this would install 2 plugins, if 2 plugins are in same repo
#     #  (e.g. the blendertools github repo from epic contains multiple uplugins)
#
#     # enable on install
#     # search for uplugin files in the plugin folder
#     for uplugin in (plugin_dir / package.package_name).rglob("*.uplugin"):
#         plugin_dir = Path(uplugin).parent
#         py_path = plugin_dir / "Content" / "Python"
#         sys.path.append(str(py_path))  # add to python path
#         startup_script = py_path / "init_unreal.py"
#         if startup_script.exists():
#             print("running plugin startup code", startup_script)
#             exec(startup_script.read_text())
#
#     # for sub_path in repo_paths:
#     #     print("copying", sub_path, "to", plugin_dir)
#     #
#     #     sub_path = os.path.realpath(sub_path)
#     #     plugin_dir = os.path.realpath(plugin_dir)
#     #     shutil.copy(sub_path, plugin_dir)  # PermissionError install unreal
#     # #     #PermissionError: [Errno 13] Permission denied: 'C:\\Users\\hanne\\AppData\\Local\\Temp\\plugget\\unreal\\VaRest\\latest\\VaRest'
#     # #     # permis denied to source.
#     #
#     # # # check if files were copied: package.clone_dir / p
#     # # if not (package.clone_dir / p).exists():
#     # #     raise FileNotFoundError(f"expected file not found: '{p}'")
#     #
#     # # delete plugin_dir / "temp"
#     # shutil.rmtree(plugin_dir / "temp", ignore_errors=True)
#
#     # package.installed_paths |= {local_addons_dir / x.name for x in addon_paths}  # todo might want a dict later
#
#
# def uninstall(package: "plugget.data.Package", **kwargs):
#
#     # plugin_dir = project_plugins_dir()
#
#     for p in package.installed_paths:
#         p = Path(p)
#         print("remove", p)
#         # delete all paths,. p can be folder or file. force delete and children
#         if p.is_dir():
#             shutil.rmtree(p, ignore_errors=True)
#         else:
#             p.unlink(missing_ok=True)