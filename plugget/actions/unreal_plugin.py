import unreal
from pathlib import Path
import shutil
import os


def project_plugins_dir():
    project_path = unreal.Paths.project_plugins_dir()
    project_path = unreal.Paths.convert_relative_path_to_full(project_path)
    return Path(project_path)


def install(package: "plugget.data.Package", max_folder=None, **kwargs) -> bool:
    plugin_dir = project_plugins_dir()

    # move it to target folder
    repo_paths = package.get_content(target_dir=plugin_dir / package.package_name)
    # todo cloning directly in plugin dir works since unreal recursively searches for plugins.
    #  but it's not the way it should be done.
    #  e.g. it will install 2 plugins, if 2 plugins are in same repo (e.g. blendertools repo from epic)

    # for sub_path in repo_paths:
    #     print("copying", sub_path, "to", plugin_dir)
    #
    #     sub_path = os.path.realpath(sub_path)
    #     plugin_dir = os.path.realpath(plugin_dir)
    #     shutil.copy(sub_path, plugin_dir)  # PermissionError install unreal
    # #     #PermissionError: [Errno 13] Permission denied: 'C:\\Users\\hanne\\AppData\\Local\\Temp\\plugget\\unreal\\VaRest\\latest\\VaRest'
    # #     # permis denied to source.
    #
    # # # check if files were copied: package.clone_dir / p
    # # if not (package.clone_dir / p).exists():
    # #     raise FileNotFoundError(f"expected file not found: '{p}'")
    #
    # # delete plugin_dir / "temp"
    # shutil.rmtree(plugin_dir / "temp", ignore_errors=True)

    # package.installed_paths |= {local_addons_dir / x.name for x in addon_paths}  # todo might want a dict later


def uninstall(package: "plugget.data.Package", **kwargs):

    # plugin_dir = project_plugins_dir()

    for p in package.installed_paths:
        p = Path(p)
        print("remove", p)
        # delete all paths,. p can be folder or file. force delete and children
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
        else:
            p.unlink(missing_ok=True)