"""
Plugget is a plugin-manager for various applications.
"""

from pathlib import Path
import importlib
import os
import subprocess
import json


sources = [
    "https://github.com/hannesdelbeke/plugget-pkgs.git",
]

TEMP_PLUGGET = Path(os.getenv("TEMP")) / "plugget"

def rmdir(path):
    # delete folder on windows
    if os.path.exists(path):
        # remove folder and all content
        os.system(f"rmdir /s /q {path}")


class Plugin(object):
    def __init__(self, app=None, name=None, id=None, version=None, description=None, author=None, repo_url=None, license=None, tags=None, dependencies=None, subdir=None):
        self.app = app

        self.name = name  # displayname
        self.id = id or name # unique id  # todo for now same as name
        self.version = version
        # description = ""
        # author = ""
        self.repo_url = repo_url
        # license = ""
        # tags = []
        # dependencies = []
        self.subdir = subdir


    @property
    def clone_dir(self):
        """return the path we clone to on install e.g C:/Users/username/AppData/Local/Temp/plugget/bqt/0.1.0"""
        print(self.app, self.id, self.version)
        return TEMP_PLUGGET / self.app / self.id / self.version

    # @property
    # def clone_dir_shell(self):
    #     """return the path we clone to on install e.g C:/Users/username/AppData/Local/Temp/plugget/bqt/0.1.0"""
    #     return str(self.clone_dir.as_posix()).replace("C:", "/c/")

    # @property
    # def subdir(self):
    #     """return the subdirectory of the repo, defined by '?Path=' in the URL e.g bqt"""
    #     split = self.repo_url.split("?Path=")
    #     if len(split) > 1:
    #         return split[1]
    #     else:
    #         return None

    @classmethod
    def from_json(cls, json_path):
        with open(json_path, "r") as f:
            json_data = json.load(f)

        app = Path(json_path).parent.parent.name  # e.g. blender/bqt/0.1.0.json -> blender
        version = Path(json_path).stem  # e.g. blender/bqt/0.1.0.json -> 0.1.0
        return cls(**json_data, app=app, version=version)

    def _clone_repo(self):
        # clone package repo to temp folder


        rmdir(self.clone_dir)

        # todo sparse checkout
        # mkdir <repo>
        # cd <repo>
        # git init
        # git remote add -f origin <url>

#         if self.subdir:
#             command = f"""
# mkdir "{self.clone_dir}"
# cd "{self.clone_dir}"
# git init "{self.clone_dir}"
# git remote add -f origin "{self.repo_url}"
# git pull origin master
#             """
# # git config core.sparseCheckout true
# # echo {self.subdir} > .git/info/sparse-checkout
#
#             print(command)
#
#             result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if self.subdir:
            subprocess.run(
                ["git", "clone", "--depth", "1", "--progress", self.repo_url, str(self.clone_dir)])

            # delete .git folder
            rmdir(self.clone_dir / ".git")
#
#             command = \
#             f"""
#             mkdir "{self.clone_dir}"
#             cd "{self.clone_dir}"
#             git init "{self.clone_dir}"
#             git remote add -f origin "{self.repo_url}"
#             git config core.sparseCheckout true
#             echo "{self.subdir}" > .git/info/sparse-checkout
#             git pull --depth=1"
#             """
# # f"git pull origin {self.branch} --depth=1 --single-branch"
#             print(command)
#             ret = subprocess.run(command, capture_output=True, shell=True)

            # confirm folder was created
            if not self.clone_dir.exists():
                raise Exception(f"Failed to clone repo to {self.clone_dir}")

            print("SUBDIR" , self.clone_dir / self.subdir)
            return self.clone_dir / self.subdir
        else:
            # clone repo
            subprocess.run(
                ["git", "clone", "--depth", "1", "--single-branch", "--progress", self.repo_url, str(self.clone_dir)])

            # delete .git folder
            rmdir(self.clone_dir / ".git")

            # app_dir = Path("C:/Users/hanne/OneDrive/Documents/repos/plugget-pkgs") / "blender"
            return self.clone_dir


def _clone_manifest_repo():
    # if repo doesn't exist, clone it
    source_dirs = []
    for source_url in sources:

        source_name = source_url.split("/")[-1].split(".")[0]
        print(source_name)

        source_dir = TEMP_PLUGGET / source_name

        print("remove dir")
        rmdir(source_dir)  # todo catch if this failed

        # check if dir exists
        if source_dir.exists():
            raise Exception(f"Failed to remove source_dir {source_dir}")

        # print(source_dir)
        # if not source_dir.exists():
        print("clone repo")
        subprocess.run(["git", "clone", "--depth", "1", "--progress", source_url, str(source_dir)])
         # todo single branch
        # # if repo exists, pull it
        # else:
        #
        #     source_dir_shell = source_dir.as_posix().replace("\\", "/").replace("C:", "/c")
        #     print(source_dir_shell)
        #     command = f"cd {source_dir_shell}; " \
        #               "git pull"
        #
        #
        #     ret = subprocess.run(command, capture_output=True, shell=True)
        #
        #     print("command \n", command)
        #
        #
        #     # subprocess.run(["git", "pull", "--depth", "1", "--single-branch", "--progress", source_url, str(source_dir)])
        source_dirs.append(source_dir)
    return source_dirs


def _add_repo(repo_url):
    sources.append(repo_url)
    # TODO save to config file

def _detect_app():
    # detect application

    dcc = 'blender'
    module = importlib.import_module(f"plugget.apps.{dcc}")

    pass

def get_app_module():
    # detect application

    dcc = 'blender'
    module = importlib.import_module(f"plugget.apps.{dcc}")
    return module


def search_iter(name=None):
    """search if package is in sources"""

    source_dirs = _clone_manifest_repo()

    for source_dir in source_dirs:
        print("source_dir", source_dir)
        for plugin_manifest in source_dir.rglob("*.json"):
            print("plugin_manifest", plugin_manifest)
            source_name = plugin_manifest.parent.name
            if name is None or name.lower() in source_name.lower():
                # todo yield plugin object
                # l;oad json
                plugin = Plugin.from_json(plugin_manifest)

                yield plugin_manifest



def list():
    """list installed packages"""

    # detect plugins from dcc,
    #   detect dcc
    #   load dcc plugin

    module = get_app_module()
    module.installed_plugins()


def install(name):
    """install package"""
    # get package from package repo
    # copy package to blender package folder
    module = get_app_module()

    packages = []
    for package in search_iter(name):
        packages.append(package)

        if len(packages) > 1:
            print(f"Multiple packages found for {name}")
            return

    if len(packages) == 0:
        print(f"Package {name} not found")
        return

    plugin = Plugin.from_json(packages[0])
    repo_path = plugin._clone_repo()
    # get latest version from plugin
    module.install_plugin(repo_path)

    # enable
    module.enable_plugin(plugin.name)


def uninstall(name):

    module = get_app_module()
    module.uninstall_plugin(name)


def update():

    # get list of isntalled (not enabled) plugins.
    # check them for updates (plugget and app update if supported)

    pass


# open pacakge manager
def list():
    """list installed packages"""

    # detect plugins from dcc,
    #   detect dcc
    #   load dcc plugin

    module = get_app_module()
    return module.installed_plugins()


# aliases
upgrade = update