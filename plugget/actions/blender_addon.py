from pathlib import Path
import logging
import shutil
import bpy
import addon_utils


def __clash_import_name(name):
    """check there isn't a py module with the same name as our addon"""
    try:
        __import__(name)
        logging.warning(f"Failed to install addon {name}, a py module with same name exists")
        return True
    except ImportError:
        return False


def _get_all_addon_names() -> set[str]:
    bpy.ops.preferences.addon_refresh()
    return {a.__name__ for a in addon_utils.modules()}


def _enable_addons(names: set[str], enable=True):
    if not enable:
        return
    try:
        for addon_name in names:
            if not addon_name:
                raise ValueError(f"No plugin name found for package '{addon_name}', "
                                 f"maybe the addon failed to import or misses bl_info")
            bpy.ops.preferences.addon_enable(module=addon_name)
    except Exception as e:
        logging.warning(f"Failed to enable plugin '{addon_name}'")
        import traceback
        traceback.print_exc()


def install(package: "plugget.data.Package", force=False, enable=True, **kwargs) -> bool:  # todo , force=False, enable=True):
    # If the “force” parameter is True, the add-on will be reinstalled, even if it has not been previously removed.
    addon_names_before = _get_all_addon_names()
    _install_addon(package)
    addon_names_after = _get_all_addon_names()
    new_addons = addon_names_after - addon_names_before
    _enable_addons(new_addons, enable=enable)
    return True


def _install_addon(package):

    # if a repo has plugin in root. we get the repo files content
    # if the repo has plugin in subdir, that file lives in repo_paths

    addon_paths: list[Path] = package.get_content()  # get paths to plugin files in cloned repo
    # copy addons to local addons dir
    local_script_dir = bpy.utils.script_path_user()
    local_addons_dir = Path(local_script_dir) / "addons"
    # if force:
    #     from plugget.utils import rmdir
    #     rmdir(new_plugin_path)
    # shutil.move(str(plugin_path), str(new_plugin_path.parent), )  # copy plugin_path to local_addons_dir
    # todo filter repo paths
    print(f"copy files to {local_addons_dir}")
    for addon_path in addon_paths:
        print(addon_path)

        if __clash_import_name(addon_path.name):
            continue

        # new_addon_path.mkdir(parents=True, exist_ok=True)
        shutil.move(str(addon_path), str(local_addons_dir))

        # todo clean up empty folders

        # check if plugin folder was copied, by checking if any files are in new_plugin_path
        # new_addon_path = local_addons_dir / addon_path.name
        # if not any(new_addon_path.iterdir()):
        #     logging.warning(f"Failed to install plugin {addon_path.name}")
        #     return False

    package.installed_paths |= {local_addons_dir / x.name for x in addon_paths}  # todo might want a dict later


def uninstall(package: "plugget.data.Package", **kwargs):
    """uninstall plugin by name"""
    # todo make plugin name an action kwarg

    for p in package.installed_paths:
        p = Path(p)
        print("remove", p)
        # delete all paths,. p can be folder or file. force delete and children
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
        else:
            p.unlink(missing_ok=True)

    bpy.ops.preferences.addon_refresh()

    # bpy.ops.preferences.addon_remove(module=plugin_name)
    print("PLUGGET uninstalled plugin_name ", package.package_name)
