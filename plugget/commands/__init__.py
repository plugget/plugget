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


def _clone_manifest_repo(source_url) -> "pathlib.Path":
    """Clone git repo containing plugget manifests, from a git URL"""
    source_name = source_url.split("/")[-1].split(".")[0]
    source_dir = settings.TEMP_PLUGGET / source_name

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
    subprocess.run(["git", "clone", "--depth", "1", "--progress", source_url, str(source_dir)])
    # todo check if command errored / catch exception
    # todo check if clone was successful

    # CACHING: make a file inside named _LAST_UPDATED with the current date
    source_dir.mkdir(parents=True, exist_ok=True)
    with open(source_dir / "_LAST_UPDATED", "w") as f:
        f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    return source_dir


def _clone_manifest_repos():
    """
    clone the manifest repos that are registered, defaults to ['github.com/hannesdelbeke/plugget-pkgs']
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
                source_dir = _clone_manifest_repo(source_url)
                
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


def _manifest_repo_app_paths(app):
    """get the default app paths from all registered manifest repos"""
    # assume default search if we didn't get any search_paths
    app = _detect_app_id() if not app else app  # e.g. blender
    search_paths = _clone_manifest_repos()
    if app and app != 'all':
        search_paths = [search_path / app for search_path in search_paths]
    return search_paths


def search(name=None, app=None, verbose=True, version=None, search_paths=None) -> PackagesMeta:
    """
    Search if package is in sources
    :param name: pacakge name to search in manifest repo, return all packages if not set
    :param app: app name to search in, return all apps if not set
    :param verbose: print results if True
    search_paths: list of pathlib.Path objects to search in,
                defaults to temp path of clone for all registered manifest repos
    """
    # search a folder with the format: app/app-hash/package/manifest-version.json, e.g.:
    # Blender/8e3c1114/io_xray/1.2.3.json

    # todo atm packagemeta populates it's versions from the folder structure
    #  which means that if we create it from the installed folder in appdata,
    #  it wont include all versions from the local manifest repo in appdata

    # todo curr returns package and version
    #  return package meta. latest, name, author, description
    #  search will return all package names, and then plugin needs to read all versions from this package name.
    #  ideally i can do .versions

    manifest_paths = _discover_manifest_paths(name=name, search_paths=search_paths, app=app)
    meta_packages = _create_packages(manifest_paths)
    if verbose:
        _print_search_results(meta_packages)
    return meta_packages


def _create_packages(manifest_paths):
    # create packages from manifests
    packages_metas = {}
    for manifest_path in manifest_paths:
        meta = packages_metas.get(manifest_path) or PackagesMeta()
        packages_metas[manifest_path] = meta
        meta.packages.append(Package.from_json(manifest_path))
    package_collections = packages_metas.values()
    return package_collections


def _discover_manifest_paths(name=None, search_paths=None, app=None):
    app = _detect_app_id() if not app else app
    search_paths = search_paths or _manifest_repo_app_paths(app)

    manifest_paths = []  # get the manifests
    for app_path in search_paths:  # iter app folders
        package_dirs = [package_dir for package_dir in app_path.iterdir() if package_dir.is_dir()]
        for package_dir in package_dirs:  # iter package folders
            for manifest_path in package_dir.glob("*.json"):  # iter manifests
                source_name = package_dir.name  # this checks for manifest name, not name in package todo
                if name is None or name.lower() in source_name.lower():  # todo we search manifest file name, instead of name in the package
                    manifest_paths.append(manifest_path)
    return manifest_paths


# # WARNING we overwrite build in type list here, careful when using list in this module!
# todo do we need list, or can this be merged w search?
def list(package_name:str = None, enabled=False, disabled=False, verbose=True, app=None):  # , source=None):
    """
    List all installed packages
    if run from an app, only list the apps installed packages, with option to list all app installed packages

    :param enabled: list enabled packages only if True
    :param disabled: list disabled packages only if True
    TODO :param source: list packages from specific source only if set
    """

    # todo setting an app name wont work externally since hash will be different.

    import plugget.data.package
    app_hash = plugget.data.package.hash_current_app()    # e.g. 8e3c1114
    app = _detect_app_id() if not app else app            # e.g. blender
    source_dir = settings.INSTALLED_DIR / app / app_hash  # e.g. ...\AppData\Roaming\plugget\installed\blender\8e3c1114
    results = search(name=package_name, app=app, verbose=verbose, search_paths=[source_dir])
    return results


def install(package_name, enable=True, app=None, version=None, **kwargs):
    """
    Install package
    :param name: name of the manifest folder in the manifest repo
    :param enable: enable plugin after install
    """
    # todo
    #  get package (manifest)
    #  check if package is already installed
    #  install package, by running action(s) from manifest
    #  save manifest to installed packages dir

    # copy package to blender package folder
    # module = _get_app_module()

    # get package manifest from package repo
    result = search(name=package_name, app=app, verbose=False, version=version)
    if not result:
        logging.warning(f"Package {package_name} not found, failed install")
        return

    meta_collection = result[0]
    package = meta_collection.get_version(version) or meta_collection.latest

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

    package = list(package_name, verbose=False)[0]
    if not package:
        logging.warning("Package not found, cancelling install")
        return

    package.uninstall(dependencies=dependencies, **kwargs)


def info(package_name=None, verbose=True):
    """
    Show info about package
    :param name: name of the manifest folder in the manifest repo
    """

    packages = list(package_name, verbose=False) or search(package_name, verbose=False)
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
