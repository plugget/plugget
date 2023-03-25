from pathlib import Path
import subprocess
import json
import logging
from plugget.utils import rmdir
from plugget import settings
import importlib
import shutil


# app plugin / addon: a plugin for a specific app
# (plugget) package, a wrapper for distributing files, e.g. plugin (zip or repo), icon packs, ...
# (plugget) package manifest: a json file with the data to get the correct (plugget) package
# manifest repo: a repo containing (plugget) package manifests

# the content of a package: plugin or resource

class Package(object):
    """
    manifest & package wrapper
    """

    def __repr__(self):
        return f"Package({self.package_name} {self.version})"

    def __init__(self, app=None, name=None, display_name=None, plugin_name=None, id=None, version=None,
                 description=None, author=None, repo_url=None, package_url=None, license=None, tags=None,
                 dependencies=None, repo_paths=None, docs_url=None, package_name=None, manifest_path=None,
                 actions=None, installed_paths=None, **kwargs):
        """
        :param app: the application this plugin is for e.g. blender

        :param name: the name of the plugin e.g. bqt (currently same as display_name)
        :param display_name: the display name of the plugin e.g. BQT (not used)

        :param plugin_name: the (unique) name of the plugin used by the app e.g. bqt
        :param id: the unique id of the plugin e.g. bqt (not used)

        :param repo_paths: a list containing the subdirectory of the repo where the plugin is located, this becomes pluginname in blender, can contain multiple paths or files

        :param version: the version of the plugin e.g. 0.1.0, derived from manifest name


        """
        if kwargs:
            logging.warning("unused kwargs on Package init:", kwargs)

        # attributes derived from the manifest path
        self.app = app  # set from app folder containing the manifest, todo currently is app name, swap to app object
        self.package_name = package_name  # set from folder name containing the manifests
        self.version = version  # set from manifest name
        self.manifest_path = Path(manifest_path)  # set before _set_data_from_manifest_path()
        self._set_data_from_manifest_path()  # populate above attributes to their default values

        # manifest settings
        self.repo_url = repo_url  # set before plugin name
        self.repo_paths: "list[str]" = repo_paths  # subdir(s)
        self.package_url = package_url  # set before self.plugin_name
         # self.name = name #or self.plugin_name
        self.docs_url = None
        self._actions = actions  # todo default app action
        self.dependencies = dependencies or []  # todo
        # self.id = id or plugin_name  # unique id  # todo for now same as name
        # description = ""
        # author = ""
        # license = ""
        # tags = []
        # dependencies = []

        self.installed_paths = set() if installed_paths is None else set(installed_paths)   # list of files cloned locally

    # @property
    # def app(self):
    #     return self._app
    #
    # @app.setter
    # def app(self, value):
    #     self._app = value
    #
    # @property
    # def package_name(self):
    #     return self._package_name
    #
    # @package_name.setter
    # def package_name(self, value):
    #     self._package_name = value
    #
    # @property
    # def version(self):
    #     return self._version
    #
    # @version.setter
    # def version(self, value):
    #     self._version = value

    @property
    def manifest_path(self):
        return self._manifest_path

    @manifest_path.setter
    def manifest_path(self, value):
        # expects a path from the folder structure: app_name/package_name/version.json
        self._manifest_path = Path(value)

    def _set_data_from_manifest_path(self):
        """set app_name, package_name, version from the manifest path"""
        self.version = self.version or self._manifest_path.stem
        self.app = self.app or self._manifest_path.parent.parent.name  # todo change this to be more robust
        self.package_name = self.package_name or self._manifest_path.parent.name

    @property
    def clone_dir(self):
        """return the path we clone to on install e.g C:/Users/username/AppData/Local/Temp/plugget/bqt/0.1.0"""
        return settings.TEMP_PLUGGET / self.app / self.package_name / self.version / self.package_name

    @property
    def is_installed(self):
        """a plugin is installed, if the manifest is in the installed packages folder"""
        return (settings.INSTALLED_DIR / self.app / self.package_name / f"{self.version}.json").exists()

    @property
    def default_actions(self):
        """get the default action for the app"""
        DefaultActions = {
            "blender": ["blender_addon", "blender_pip"],
            "max": ["max_macroscript"],  # todo pip
            "krita": ["krita_plugin", "krita_pip"],
            # "maya": "maya_module",
        }
        return DefaultActions.get(self.app)

    @property
    def actions(self):
        """
        get the action for the plugin, used for install, uninstall
        if the manifest doesn't specify an action, get the default action for the app
        """
        # get install action from manifest,
        actions_raw = self._actions or self.default_actions
        actions = []
        for action in actions_raw:
            # if action is a string, it's the name of the action
            if isinstance(action, str):
                module = importlib.import_module("plugget.actions")
                action_module = None
                for file in Path(module.__path__[0]).glob("*.py"):
                    if file.stem == action:  # todo action name
                        action_module = importlib.import_module(f"plugget.actions.{file.stem}")
                        action = action_module
                        break
                if not action_module:
                    raise Exception(f"action {action} not found")

            # if action is a module, it's the action itself
            # elif inspect.ismodule(self._action):
            # else:
            #     action = self._action

            actions.append(action)

        return actions

    @classmethod
    def from_json(cls, json_path):
        """create a plugin from a json file"""
        manifest_path = Path(json_path)

        with open(json_path, "r") as f:
            json_data = json.load(f)

        # todo this is a bit hacky, currently assumes you install from the plugget repo
        app = manifest_path.parent.parent.name  # e.g. blender/bqt/0.1.0.json -> blender

        # package_name = manifest_path.parent.name  # e.g. blender/bqt/0.1.0.json -> bqt
        version = manifest_path.stem  # e.g. blender/bqt/0.1.0.json -> 0.1.0
        json_data.setdefault("app", app)
        json_data.setdefault("version", version)
        json_data.setdefault("manifest_path", manifest_path)
        return cls(**json_data)  #package_name=package_name

    def to_dict(self, empty_keys=False):
        """
        convert the package to a dict, e.g. used for manifest files
        :param empty_keys: if True, include keys with None values
        """
        output = {'app': self.app,
                  'package_name': self.package_name,
                  'version': self.version,
                  'repo_url': self.repo_url,
                  'repo_paths': self.repo_paths,
                  'package_url': self.package_url,
                  'docs_url': self.docs_url,
                  'actions': self._actions,
                  'dependencies': self.dependencies,
                  'installed_paths': [str(x) for x in self.installed_paths]
                  }
        if not empty_keys:
            empty_keys = [k for k, v in output.items() if not v]
            for key in empty_keys:
                del output[key]
        return output

    def to_json(self, json_path):
        """save the plugin to a json file"""

        output = self.to_dict()
        Path(json_path).parent.mkdir(exist_ok=True, parents=True)
        with open(json_path, "w") as f:
            json.dump(output, f, indent=4)

    def get_content(self) -> "list[Path]":
        """download the plugin content from the repo, and return the paths to the files"""
        return self._clone_repo()

    def _clone_repo(self) -> "list[Path]":
        """
        returns either the files in repo (sparse) or the folder containing the repo
        """
        # clone package repo to temp folder
        rmdir(self.clone_dir)

        print("cloning", self.repo_url, "to", self.clone_dir)
        # todo sparse checkout, support multiple entries in self.repo_paths
        if self.repo_paths:
            # logging.debug(f"cloning {self.repo_url} to {self.clone_dir}")
            subprocess.run(["git", "clone", "--depth", "1", "--progress", self.repo_url, str(self.clone_dir)])

            # delete .git folder
            rmdir(self.clone_dir / ".git")

            # confirm folder was created
            if not self.clone_dir.exists():
                raise Exception(f"Failed to clone repo to {self.clone_dir}")

            return [self.clone_dir / p for p in self.repo_paths]
        else:
            # clone repo
            subprocess.run(["git", "clone", "--depth", "1", "--progress", self.repo_url, str(self.clone_dir)])

            # delete .git folder
            rmdir(self.clone_dir / ".git")

            # app_dir = Path("C:/Users/hanne/OneDrive/Documents/repos/plugget-pkgs") / "blender"
            return [self.clone_dir]

    def install(self, force=False, *args, **kwargs):
        from plugget import commands

        if self.is_installed and not force:
            raise Exception(f"{self.package_name} is already installed")
        for action in self.actions:
            # action install implicitly adds to self.install_paths
            action.install(self, *args, force=force, **kwargs)

        i = 0
        for d in self.dependencies:
            i += 1

            package = None

            # if dependency is a string, it's a package name, e.g. "blender:my-exporter",
            if isinstance(d, str):
                result = d.split(":")
                if len(result) == 1:
                    # if no app is specified, use the same app as the current package
                    package_name = result[0]
                    app_name = self.app
                elif len(result) == 2:
                    app_name, package_name = result
                else:
                    raise Exception(f"expected only 1 ':', got {len(result)-1}. Invalid dependency: {d}")
                package = commands.search(package_name)[0]  # app=app_name, also support python app dependencies

            # if dependency is a dict, it's a package object, e.g. {"name": "my-exporter", "app": "blender"}
            elif isinstance(d, dict):
                # overwrite attrs set in _set_data_from_manifest_path
                d.setdefault("manifest_path", self.manifest_path)
                d.setdefault("app", self.app)
                d.setdefault("version", self.version)
                d.setdefault("package_name", f"{self.package_name}_dependency_{i}")
                package = Package(**d)

            package.install(force=force, *args, **kwargs)

        # # if requirements.txt exists in self.repo_paths, install requirements
        # requirements_paths = []
        # if (self.clone_dir / "requirements.txt").exists():
        #     requirements_paths.append(self.clone_dir / "requirements.txt")
        # if self.repo_paths:
        #     for p in self.repo_paths:
        #         if p.endswith("requirements.txt"):
        #             requirements_paths.append(self.clone_dir / p)
        # for p in requirements_paths:
        #     if p.exists():
        #         print("requirements.txt found, installing requirements")
        #         subprocess.run(["pip", "install", "-r", self.clone_dir / p])
        #     else:
        #         logging.warning(f"expected requirements.txt not found: '{p}'")

        # copy manifest to installed packages dir
        # todo check if install was successful
        manifest_path = settings.INSTALLED_DIR / self.app / self.package_name / self.manifest_path.name
        self.to_json(manifest_path)

    def uninstall(self, dependencies=False, **kwargs):
        for action in self.actions:
            action.uninstall(self, dependencies=False, **kwargs)

        # todo uninstall dependencies
        # todo move pip action to dependencies

        # remove manifest from installed packages dir
        # todo check if uninstall was successful
        install_dir = settings.INSTALLED_DIR / self.app / self.package_name  # / plugin.manifest_path.name
        shutil.rmtree(install_dir, ignore_errors=True)

