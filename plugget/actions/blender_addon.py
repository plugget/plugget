from pathlib import Path
import logging
import shutil
import bpy  # todo make this optional, so we can run this from outside blender
from plugget._utils import rmdir
import addon_utils
import sys
from plugget.actions._utils import clash_import_name


# _target_path = os.environ.get("PLUGGET_BLENDER_TARGET_ADDONS")
# _interpreter_path = os.environ.get("PLUGGET_BLENDER_INTERPRETER")


def _get_all_addon_names() -> set[str]:
    bpy.ops.preferences.addon_refresh()
    return {a.__name__ for a in addon_utils.modules()}


def _enable_addons(names: set[str], enable=True):
    """
    Enable addons by name, only works when run from inside Blender
    """
    # todo support enabling addons from outside blender

    if not enable:
        return
    try:
        for addon_name in names:
            if not addon_name:
                raise ValueError(f"No plugin name found for package '{addon_name}', "
                                 f"maybe the addon failed to import or misses bl_info")
            addon_utils.enable(addon_name)

    except Exception as e:
        logging.warning(f"Failed to enable plugin '{addon_name}'")
        import traceback
        traceback.print_exc()


def install(package: "plugget.data.Package", force=False, enable=True, target=None, **kwargs) -> bool:  # todo , force=False, enable=True):
    # If the “force” parameter is True, the add-on will be reinstalled, even if it has not been previously removed.

    if kwargs:
        logging.warning(f"unsupported kwargs passed to blender_addon install: {kwargs}")

    # since we don't know the addon name, we use a hack.
    # by comparing all addon names before and after install, we can find the new addon name
    # then we enable the addon by name
    addon_names_before = _get_all_addon_names()

    _install_addon(package, force=force, target=target)

    addon_names_after = _get_all_addon_names()
    new_addons = addon_names_after - addon_names_before
    _enable_addons(new_addons, enable=enable)  # don't run this before dependencies are installed
    return True


def _install_addon(package, force=False, target=None):

    # if a repo has plugin in root. we get the repo files content
    # if the repo has plugin in subdir, that file lives in repo_paths

    addon_paths: list[Path] = package.get_content()  # get paths to plugin files in cloned repo

    local_addons_dir = target or Path(bpy.utils.script_path_user()) / "addons"

    # add to path if not yet in there. e.g. if first addon install ever.
    if local_addons_dir not in sys.path:
        sys.path.append(str(local_addons_dir))

    # copy addons to local addons dir
    # todo filter repo paths
    print(f"copy files to {local_addons_dir}")
    for addon_path in addon_paths:
        print(addon_path)

        if force:
            rmdir(local_addons_dir / addon_path.name)
        elif clash_import_name(addon_path.name):
            logging.warning(f"skipping addon install '{addon_path.name}', clashing py-module already imported")
            continue

        # if we don't do this the first addon install fails, because of how shutil move works.
        local_addons_dir.mkdir(parents=True, exist_ok=True)

        # check if folder exists already, e.g. if addon is disabled import check will let it pass
        if not force and (local_addons_dir / addon_path.name).exists():
            logging.warning(f"Addon '{addon_path.name}' already installed")
            continue
            
        # todo replace move with copytree, else we mess with the package's content cache
        shutil.move(str(addon_path), str(local_addons_dir))

        # todo clean up empty folders

        # check if plugin folder was copied, by checking if any files are in new_plugin_path
        # new_addon_path = local_addons_dir / addon_path.name
        # if not any(new_addon_path.iterdir()):
        #     logging.warning(f"Failed to install plugin {addon_path.name}")
        #     return False

    package.installed_paths |= {local_addons_dir / x.name for x in addon_paths}  # todo might want a dict later
    # todo support renaming the addon in the config file
    #  also delete renamed folder


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

    # todo disable addon

    bpy.ops.preferences.addon_refresh()

    # bpy.ops.preferences.addon_remove(module=plugin_name)
    print("PLUGGET uninstalled plugin_name ", package.package_name)
