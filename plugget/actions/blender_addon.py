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
        new_addon_path = local_addons_dir / addon_path.name
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
