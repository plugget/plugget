from pathlib import Path
import logging
import shutil
import bpy


def default_plugin_name(package_url, repo_url):
    """
    use the repo name as the default plugin name
    e.g. https://github.com/SavMartin/TexTools-Blender -> TexTools-Blender
    """
    if package_url:
        return package_url.rsplit("/", 1)[1].split(".")[0]
    else:
        return repo_url.rsplit("/", 1)[1].split(".")[0]


def __clash_import_name(name):
    """check there isn't a py module with the same name as our addon"""
    try:
        __import__(name)
        logging.warning(f"Failed to install addon {name}, a py module with same name exists")
        return True
    except ImportError:
        return False

def __make_modules_importable(addon_path):
    """
    if addon_path is a folder containing python files,
    ensure the folder has an __init__.py, so it imports correctly in Blender
    """
    if addon_path.is_dir():
        if not any(addon_path.rglob("*.py")):
            return
        addon_path.joinpath("__init__.py").touch(exist_ok=True)


def install(package: "plugget.data.Package", force=False, enable=True, **kwargs) -> bool:  # todo , force=False, enable=True):
    # If the “force” parameter is True, the add-on will be reinstalled, even if it has not been previously removed.

    # foldername and addon (operator) name are different!
    # operator name is tracked in plugin_name in manifest

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
    for addon_path in addon_paths:

        if __clash_import_name(addon_path.name):
            continue

        new_addon_path = local_addons_dir / addon_path.name
        __make_modules_importable(addon_path)  # todo do we still need this? 
        # new_addon_path.mkdir(parents=True, exist_ok=True)
        shutil.move(str(addon_path), str(local_addons_dir))

        # todo clean up empty folders

        # check if plugin folder was copied, by checking if any files are in new_plugin_path
        if not any(new_addon_path.iterdir()):
            logging.warning(f"Failed to install plugin {addon_path.name}")
            return False

    if enable:
        addon_name = package.plugin_name or default_plugin_name(package.package_url, package.repo_url)
        if not addon_name:
            raise ValueError(f"No plugin name found for package '{package.package_name}'")
        bpy.ops.preferences.addon_enable(module=addon_name)

    return True


def uninstall(package: "plugget.data.Package", **kwargs):
    """uninstall plugin by name"""
    # todo make plugin name an action kwarg
    plugin_name = package.plugin_name or default_plugin_name(package.package_url, package.repo_url)
    bpy.ops.preferences.addon_remove(module=plugin_name)
    print("PLUGGET uninstalled plugin_name ", plugin_name)
