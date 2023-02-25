"""
Plugget is a plugin-manager for various applications.
"""
import importlib
import logging
import subprocess
import datetime

from plugget.utils import rmdir
from plugget.data import Plugin
from plugget import settings


def _plugin_name_from_manifest(manifest_name):
    # get plugin_name from manifest
    if manifest_name:
        print("provided manifest, searching for plugin")
        plugin = search(manifest_name, verbose=False)[0]
        print("found plugin name from manifest", plugin.plugin_name)
        plugin_name = plugin.plugin_name

        return plugin_name


def _clone_manifest_repo(source_url):
    source_name = source_url.split("/")[-1].split(".")[0]
    source_dir = settings.TEMP_PLUGGET / source_name

    # CACHING: check when repo was last updated
    if (source_dir / "_LAST_UPDATED").exists():
        with open(source_dir / "_LAST_UPDATED", "r") as f:
            last_updated = datetime.datetime.strptime(f.read(), "%Y-%m-%d %H:%M:%S")
        if last_updated > datetime.datetime.now() - datetime.timedelta(days=1):
            print("using cached manifest repo, last updated less than a day ago")
            return source_dir

    rmdir(source_dir)  # todo catch if this failed

    # check if dir exists
    if source_dir.exists():
        raise Exception(f"Failed to remove source_dir {source_dir}")

    # clone repo
    subprocess.run(["git", "clone", "--depth", "1", "--progress", source_url, str(source_dir)])

    # CACHING: make a file inside named _LAST_UPDATED with the current date
    with open(source_dir / "_LAST_UPDATED", "w") as f:
        f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    return source_dir


def _clone_manifest_repos():
    # if repo doesn't exist, clone it
    source_dirs = []
    for source_url in settings.sources:
        source_dir = _clone_manifest_repo(source_url)
        source_dirs.append(source_dir)
    return source_dirs

def _add_repo(repo_url):
    settings.sources.append(repo_url)
    # TODO save to config file


def _detect_app():
    # detect application

    dcc = 'blender'
    module = importlib.import_module(f"plugget.apps.{dcc}")

    pass


def _get_app_module():
    # detect application
    dcc = 'blender'
    module = importlib.import_module(f"plugget.apps.{dcc}")
    return module


def _search_iter(name=None):  # todo can we merge with search?
    """
    search if package is in sources
    if name is None, return all packages
    """
    source_dirs = _clone_manifest_repos()
    for source_dir in source_dirs:
        for plugin_manifest in source_dir.rglob("*.json"):
            source_name = plugin_manifest.parent.name
            if name is None or name.lower() in source_name.lower():
                yield Plugin.from_json(plugin_manifest)


def search(name=None, verbose=True):
    plugins = [x for x in _search_iter(name)]
    if verbose:
        print(f"{len(plugins)} plugins found in repo:")
        print(f"{'-' * 20}")
        for plugin in plugins:
            print(f"{plugin}")
    return plugins


# # we overwrite build in type list here, carefull when using list in this module!
# open package manager
def list(enabled=False, disabled=False, verbose=True):  # , source=None):
    """
    list all installed packages by default
    :param enabled: list enabled packages only if True
    :param disabled: list disabled packages only if True
    TODO :param source: list packages from specific source only if set
    """

    module = _get_app_module()

    if enabled:
        plugins = module.enabled_plugins()
    elif disabled:
        plugins = module.disabled_plugins()
    else:  # list all installed
        plugins = module.installed_plugins()

    if verbose:
        print(f"{len(plugins)} installed plugins")
        print(f"{'-' * 20}")
        for plugin in plugins:
            print(f"{plugin}")

    return plugins


#    plugin_name = plugin_name or plugin_name_from_manifest(manifest_name)
def install(manifest_name, enable=True):
    """
    install package
    :param name: name of the manifest folder in the manifest repo
    :param enable: enable plugin after install
    """
    # get package from package repo
    # copy package to blender package folder
    module = _get_app_module()

    plugin = search(manifest_name, verbose=False)[0]
    if not plugin:
        print("Package not found, cancelling install")
        return

    # before install, check if plugin is already installed
    if module.is_installed(plugin.plugin_name):
        logging.warning(f"Plugin {plugin.plugin_name} is already installed, skipping install")
        return

    repo_path = plugin._clone_repo()  # we install the plugin with the repo name, not the manifest name!

    # get latest version from plugin
    module.install_plugin(repo_path)

    if enable:
        module.enable_plugin(plugin.plugin_name)


def uninstall(manifest_name=None, plugin_name=None):
    """
    uninstall package
    :param name: name of the manifest folder in the manifest repo
    """
    # todo, a user might expect to do install(pluginname") instead of install("manifestname"),
    #  since this would also work with non plugget plugins
    #  check repos for (matching) manifest, uninstall? vs check local isntalled plugins, uninstall. much easier but name is diff from install

    plugin_name = plugin_name or _plugin_name_from_manifest(manifest_name)
    module = _get_app_module()
    module.uninstall_plugin(plugin_name)


# todo this is a plugin command, exposed to plugget. maybe we want to do this for all commands?
def disable(manifest_name=None, plugin_name=None):
    """
    disable package
    :param name: name of the manifest folder in the manifest repo
    """
    plugin_name = plugin_name or _plugin_name_from_manifest(manifest_name)
    module = _get_app_module()
    module.disable_plugin(plugin_name)


def enable(manifest_name=None, plugin_name=None):
    """
    enable package
    :param name: name of the manifest folder in the manifest repo
    """
    plugin_name = plugin_name or _plugin_name_from_manifest(manifest_name)
    module = _get_app_module()
    module.enable_plugin(plugin_name)


# def update(manifest_name=None, plugin_name=None, all=False):
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


def open_install_dir():
    module = _get_app_module()
    module.open_install_dir()


# aliases
# upgrade = update





