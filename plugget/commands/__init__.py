"""
The core commands for Plugget. See plugget.help() for more info
"""

import logging
import subprocess
import datetime
import pprint
import os

from plugget._utils import rmdir
from plugget.data import Package, PackagesMeta
from plugget import settings

from pathlib import Path


# define which methods can be imported with import *
__all__ = [
    "search",
    "list",
    "install",
    "uninstall",
    "info",
    "open_installed_dir",
    "help",
]


# plugget / cache
# plugget / installed / blender / io_xray.


# def _plugin_name_from_manifest(package_name):
#     # todo rename plugin name to resource name
#     # get plugin_name from manifest
#     if package_name:
#         print("provided manifest, searching for plugin")
#         package = search(package_name, verbose=False)[0]
#         print("found plugin name from manifest", package.package_name)
#         plugin_name = package.plugin_name
#
#         return plugin_name


def _clone_manifest_repo(source_url, use_cache=False) -> "pathlib.Path":
    """Clone git repo containing plugget manifests, from a git URL"""
    source_name = source_url.split("/")[-1].split(".")[0]
    source_dir = settings.TEMP_PLUGGET / source_name

    if use_cache:
        return source_dir

    # by default disable caching for now, it hinders debugging
    # great for instant search results though
    if os.environ.get('PLUGGET_USE_CACHE') == 1:
        # CACHING: check when repo was last updated
        if (source_dir / "_LAST_UPDATED").exists():
            with open(source_dir / "_LAST_UPDATED", "r") as f:
                last_updated = datetime.datetime.strptime(f.read(), "%Y-%m-%d %H:%M:%S")
            if last_updated > datetime.datetime.now() - datetime.timedelta(days=1):
                print("using cached manifest repo, last updated less than a day ago")
                return source_dir

    # remove old manifest repo
    rmdir(source_dir)  # todo catch if this failed
    # check if dir exists
    if source_dir.exists():
        raise Exception(f"Failed to remove source_dir {source_dir}")

    # clone repo
    commands = ["git", "clone", "--depth", "1", "--progress", source_url, str(source_dir)]
    process = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = process.communicate()

    try:
        for line in stdout.splitlines():
            low_line = line.lower()
            if low_line.startswith(b"error") or low_line.startswith(b"fatal"):
                logging.error(line)
            elif low_line.startswith(b"warning"):
                logging.warning(line)
            else:
                logging.debug(line)
        if stderr:
            for line in stderr.splitlines():
                logging.error(line)
    except Ellipsis as e:
        logging.error("Failed to log git clone output, likely decode issue")
        logging.error(e)

    # todo check if command errored / catch exception
    # todo check if clone was successful

    # CACHING: make a file inside named _LAST_UPDATED with the current date
    source_dir.mkdir(parents=True, exist_ok=True)
    with open(source_dir / "_LAST_UPDATED", "w") as f:
        f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    return source_dir


def _clone_manifest_repos(use_cache=False):
    """
    clone the manifest repos that are registered, defaults to ['github.com/plugget/plugget-pkgs']
    """
    # if repo doesn't exist, clone it
    source_dirs = []
    for source_url in settings.sources:
        
            # first check if path is a local path
            source_dir = Path(source_url)

            exists = False
            try:
                exists = source_dir.exists()
            except OSError as e:
                # source_dir.exists triggers OSError if it's a git URL (in older versions of python?)
                pass

            if not exists:  # todo fix this naive impicit approach
                # else assume it's a git URL
                # we then clone the repo to a temp folder, and save the path in source_dir
                source_dir = _clone_manifest_repo(source_url, use_cache=use_cache)
                
            source_dirs.append(source_dir)

    return source_dirs


def _detect_app_id():
    try:
        import detect_app
        app = None
        if not app:
            app_found = detect_app.detect_app()
            return app_found.id if app_found else None
    except:
        None


def _print_search_results(packages):
    print(f"{len(packages)} packages found in repo:")
    print(f"{'-' * 20}")
    for package_name in packages:
        print(f"{package_name}")


def _get_app_paths(search_paths, app=None):  # todo make it clear this also clones
    """get the default app paths from all registered manifest repos"""
    app = app or _detect_app_id()  # e.g. blender
    if app and app != 'all':
        search_paths = [search_path / app for search_path in search_paths]
    return search_paths


def search(name=None, app=None, verbose=True, version=None, use_cache=False, installed=False) -> "typing.List[PackagesMeta]":
    """
    Search if package is in sources
    :param name: pacakge name to search in manifest repo, return all packages if not set
    :param app: app name to search in, return all apps if not set
    :param verbose: print results if True
    search_paths: list of pathlib.Path objects to search in,
                defaults to temp path of clone for all registered manifest repos
    installed: filter results to only installed packages
    use_cache: don't re-clone the manifest repos, use cached version
    """
    # search a folder with the format: app/app-hash/package/manifest-version.json, e.g.:
    # Blender/8e3c1114/io_xray/1.2.3.json

    if installed:
        use_cache = True
    
    # clone
    search_paths = _clone_manifest_repos(use_cache=use_cache)
    search_paths = _get_app_paths(search_paths=search_paths, app=app)

    manifest_paths = _discover_manifest_paths(name=name, search_paths=search_paths)
    manifest_dirs = {manifest_path.parent for manifest_path in manifest_paths}
    meta_packages = [PackagesMeta(manifests_dir=manifest_dir) for manifest_dir in manifest_dirs]  # todo move to PackagesMeta, create from manifest_dir
    if installed:
        meta_packages = [x for x in meta_packages if x.installed_package]
    if verbose:
        _print_search_results(meta_packages)
    return meta_packages


def _discover_manifest_paths(search_paths, name=None):
    """search for manifest files"""
    manifest_paths = []  # get the manifests
    for app_path in search_paths:  # iter app folders
        print("app_path", app_path)
        if not app_path.exists(): # or not app_path.is_dir() or app_path.name.startswith("."):
            continue
        package_dirs = [package_dir for package_dir in app_path.iterdir() if package_dir.is_dir()]
        for package_dir in package_dirs:  # iter package folders
            if not package_dir.exists():
                continue
            for manifest_path in package_dir.glob("*.json"):  # iter manifests
                source_name = package_dir.name  # this checks for manifest name, not name in package todo
                if name is None or name.lower() in source_name.lower():  # todo we search manifest file name, instead of name in the package
                    manifest_paths.append(manifest_path)
    return manifest_paths


# # # WARNING we overwrite build in type list here, careful when using list in this module!
# todo remove this list
#  and update all dependent projects. plugget qt, plugget blender, ....
def list(package_name: str = None, enabled=False, disabled=False, verbose=True, app=None) -> PackagesMeta:  # , source=None):
    """List all installed packages"""
    logging.warning("list is deprecated, use search instead")
    return search(name=package_name, app=app, verbose=verbose, installed=True)


def install(package_name, enable=True, app=None, version=None, **kwargs):
    """
    Install package
    :param name: name of the manifest folder in the manifest repo
    :param enable: enable plugin after install
    """
    #  get package (manifest)
    #  check if package is already installed
    #  install package, by running action(s) from manifest
    #  save manifest to installed packages dir

    # todo this search clones the repo. (pure optimization, low priority)
    #  we should check first if we already have this version installed.
    #  if yes dont install unless force

    packages = search(name=package_name, app=app, verbose=False, version=version)
    if not packages:
        logging.warning(f"Package {package_name} not found, failed install")
        return

    meta_package: PackagesMeta = packages[0]
    package: Package = meta_package.get_version(version) or meta_package.latest

    if not package:
        logging.warning("Package not found, cancelling install")
        return

    package.install(enable=enable, **kwargs)
    # uninstall if unsuccessful?


def uninstall(package_name=None, dependencies=False, **kwargs):
    """
    Uninstall package
    :param name: name of the manifest folder in the manifest repo
    """
    # todo, a user might expect to do install(pluginname") instead of install("manifestname"),
    #  since this would also work with non plugget plugins
    #  check repos for (matching) manifest, uninstall? vs check local isntalled plugins, uninstall. much easier but name is diff from install

    # plugin_name = plugin_name or _plugin_name_from_manifest(package_name)
    # module = _get_app_module()  # todo remove
    # module.uninstall_plugin(plugin_name)

    packages = search(package_name, verbose=False, installed=True)

    if not packages:
        logging.warning("Package not found, cancelling install")
        return

    for package in packages:
        package.uninstall(dependencies=dependencies, **kwargs)


# todo maybe move info to the package?
def info(package_name=None, verbose=True):
    """
    Show info about package
    :param name: name of the manifest folder in the manifest repo
    """

    packages: "typing.List[Package]" = search(package_name, verbose=False, installed=True)
    if not packages:
        logging.warning("Package not found")
        return
    if len(packages) > 1:
        logging.warning(f"Multiple packages found: {packages}")
        return
    package = packages[0]
    pprint.pp(package.to_dict())
    import plugget.github as github
    favorited = github.is_starred(package.repo_url)
    star_count = github.get_repo_stars(package.repo_url)
    print(f"starred by hannes: {favorited}, star-count ⭐:", star_count)


# # todo this is a plugin command, exposed to plugget. maybe we want to do this for all commands?
# def disable(package_name=None, plugin_name=None):
#     """
#     disable package
#     :param name: name of the manifest folder in the manifest repo
#     """
#     plugin_name = plugin_name or _plugin_name_from_manifest(package_name)
#     module = _get_app_module()  # todo remove
#     module.disable_plugin(plugin_name)
#
#
# def enable(package_name=None, plugin_name=None):
#     """
#     enable package
#     :param name: name of the manifest folder in the manifest repo
#     """
#     plugin_name = plugin_name or _plugin_name_from_manifest(package_name)
#     module = _get_app_module()  # todo remove
#     module.enable_plugin(plugin_name)


# def update(package_name=None, plugin_name=None, all=False):
#     """
#     update a plugin, identify by either:
#     TODO :param name: name of the manifest folder in the manifest repo
#     TODO :param plugin_name: name of the plugin in the app
#     TODO :param all: update all installed plugins if True
#     """
#
#     # get list of isntalled (not enabled) plugins.
#     # check them for updates (plugget and app update if supported)
#
#     pass


# def open_install_dir():
#     module = _get_app_module()  # todo remove
#     module.open_install_dir()


def open_installed_dir(*args, **kwargs):
    """Open the plugget manifests install folder in file explorer"""
    # todo currently copies json. but json is named after version
    #  this will clash between plugins with same version (but diff name)

    # start file explorer in installed dir
    os.startfile(settings.INSTALLED_DIR)


def help(object=None):
    """
    List all available commands

    object: object to print help for, if None, print help for this module
    """

    # try to print the docstring
    try:
        if object.__doc__:
            print(object.__doc__)
            print("")
    except:
        pass

    # get attributes
    if object:
        attr_names = [attr for attr in dir(object) if not attr.startswith("_")]
        attributes = [getattr(object, attr) for attr in attr_names]
    else:
        import plugget
        attr_names = [attr for attr in dir(plugget) if not attr.startswith("_")]
        attributes = [getattr(plugget, attr) for attr in attr_names]
    if not attributes:
        return

    # if no object provided, print plugget version
    if not object:
        from importlib.metadata import version
        plugget_version = version('plugget')
        print("Plugget is a package manager for app plugins & content")
        print(f"Plugget version: {plugget_version}")
        print()
        print("To find out more about a module or function, pass it to plugget.help()")
        print("e.g. >>> plugget.help(plugget.install)")
        print()

    # print attributes
    print("Available commands:")
    max_attr_name_length = max(len(attr_name) for attr_name in attr_names)
    for attr, attr_name in zip(attributes, attr_names):
        try:
            docstr_lines = attr.__doc__.split("\n")
            first_line_of_doc = docstr_lines[0] or docstr_lines[1]  # if first line is empty, use second line
            first_line_of_doc = first_line_of_doc.strip()  # remove leading and trailing whitespace
        except:
            first_line_of_doc = ""
        formatted_attr = attr_name.ljust(max_attr_name_length, ' ')  # add padding
        print(f"  {formatted_attr} {first_line_of_doc}")
