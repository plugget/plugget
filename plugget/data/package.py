from pathlib import Path
import subprocess
import json
import logging
from plugget._utils import rmdir
from plugget import settings
import importlib
import shutil
import sys
import hashlib
import zlib


# app plugin / addon: a plugin for a specific app
# (plugget) package, a wrapper for distributing files, e.g. plugin (zip or repo), icon packs, ...
# (plugget) package manifest: a json file with the data to get the correct (plugget) package
# manifest repo: a repo containing (plugget) package manifests

# the content of a package: plugin or resource

class Package(object):
    """
    Manifest & package wrapper
    """

    def __repr__(self):
        return f"Package({self.package_name} {self.version})"

    def __init__(self, app=None, name=None, display_name=None, plugin_name=None, id=None, version=None,
                 description=None, author=None, repo_url=None, package_url=None, license=None, tags=None,
                 dependencies=None, repo_paths=None, docs_url=None, package_name=None, manifest_path=None,
                 actions=None, installed_paths=None, repo_SHA=None, repo_tag=None, packages_meta=None, **kwargs):
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
            logging.warning("Unused kwargs on Package init: '{kwargs}'")

        # attributes derived from the manifest path
        self.app = app  # set from app folder containing the manifest, todo currently is app name, swap to app object
        self.package_name = package_name  # set from folder name containing the manifests
        self.version = version  # set from manifest name

        self._manifest_path: "Path|None" = None  # path to the manifest file in the plugget package repo
        if manifest_path:
            self.manifest_path = Path(manifest_path)  # set before _set_data_from_manifest_path()
            self._set_data_from_manifest_path()  # populate above attributes to their default values

        # manifest settings
        self.repo_url = repo_url  # set before plugin name
        self.repo_paths: "list[str]" = repo_paths  # subdir(s)
        self.repo_SHA = repo_SHA
        self.repo_tag = repo_tag
        self.package_url = package_url  # set before self.plugin_name
         # self.name = name #or self.plugin_name
        self.docs_url = docs_url
        self._actions = actions  # todo default app action
        self.dependencies = dependencies or []  # todo
        # self.id = id or plugin_name  # unique id  # todo for now same as name
        description = ""
        # author = ""
        # license = ""
        # tags = []

        self.installed_paths: set = set() if installed_paths is None else set(installed_paths)   # list of files cloned locally
        self._starred = None
        self._stars = None
        self._clone_dir = None
        self._content_paths = []  # used for caching, to prevent cloning multiple times
        self.packages_meta = packages_meta or None  # optional backlink to the packages meta object # todo make it not optional?

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
        """path to the package manifest, in the temp plugget repo"""
        return self._manifest_path

    @manifest_path.setter
    def manifest_path(self, value):
        # expects a path from the folder structure: app_name/(optional hash/)package_name/version.json
        if value:
            self._manifest_path = Path(value)
        else:
            self._manifest_path = None

    def _set_data_from_manifest_path(self):
        """set app_name, package_name, version from the manifest path"""
        self.version = self.version or self._manifest_path.stem
        self.app = self.app or self._manifest_path.parent.parent.name  # todo change this to be more robust
        self.package_name = self.package_name or self._manifest_path.parent.name

    @property
    def clone_dir(self):  # keep in sync with package_install_dir
        """return the path we clone to on install e.g C:/Users/username/AppData/Local/Temp/plugget/bqt/0.1.0"""
        if not self._clone_dir:
            # todo atm we calc hash for current app
            #  lets save this path instead, so we can load this data from outside the app
            self._clone_dir = settings.TEMP_PLUGGET / self.app / hash_current_app() / self.package_name / self.version / self.package_name
        return self._clone_dir

    @property
    def package_install_dir(self):  # keep in sync with clone_dir
        dir_to_install_to = settings.INSTALLED_DIR / self.app / hash_current_app() / self.package_name
        installed_dir = None

        # if we haven't installed this package yet, return the default install dir
        # if we have installed this package, the install dir is saved in the manifest
        # we return the saved install dir, so we dont need to calc the hash.
        # so the package data can be loaded from outside the app

        return settings.INSTALLED_DIR / self.app / hash_current_app() / self.package_name
        # todo hash_current_app, only works for current app

    @property
    def is_installed(self):
        """a plugin is installed, if the manifest is in the installed packages folder"""

        # if INSTALLED DIR in manifest path
        # installed_manifest_path = self.manifest_path
        # if self.installed_manifest_path and self.installed_manifest_path.exists():
        #     return True

        # backward compatible when self.installed_manifest_path didnt exist
        # else:
        return (self.package_install_dir / f"{self.version}.json").exists()

    @property
    def default_actions(self):
        """get the default action for the app"""
        # to prevent install bugs, ensure the dependencies install before the main plugin/addon
        # so order pip-install actions (requirements) in the list before addon-install actions,
        DefaultActions = {
            "blender": ["blender_requirements", "blender_addon"],
            "max3ds": ["max3ds_requirements", "max3ds_macroscript"],
            "maya": ["maya_requirements", "maya_plugin"],
            "krita": ["krita_requirements", "krita_plugin"],
            "unreal": ["unreal_requirements", "unreal_plugin"],
            "substance_painter": ["substance_painter_requirements", "substance_painter_plugin"],
        }
        actions = DefaultActions.get(self.app)
        if not actions:
            raise Exception(f"no default action for app '{self.app}'")
        return actions

    def get_stars(self) -> int:
        """get the number of stars on the repo"""
        import plugget.github
        if self._stars is None:
            self._stars =plugget.github.get_repo_stars(self.repo_url)
        return self._stars

    def is_starred(self) -> bool:
        """get the number of stars on the repo"""

        import plugget.github
        if self._starred is None:
            self._starred = plugget.github.is_starred(self.repo_url)
        return self._starred

    @property
    def actions_args_kwargs(self) -> "list[tuple[types.ModuleType, list, dict]]":
        """
        Get the plugin's actions & it's action settings, used for install, uninstall.
        If the manifest doesn't specify an action, get the default action for the app
        """
        """
        "actions": [
            "action_1_name",
            ("action_2_name", {"action_2_kwarg": "value"})
            ]
        """
        # get install action from manifest,w
        actions_raw = self._actions or self.default_actions
        actions: list = []
        action: "str | list | types.ModuleType" = None
        for action in actions_raw:
            action_name: str = ""
            action_args: list = []
            action_kwargs: dict = {}
            action_module: "types.ModuleType" = None

            if isinstance(action, list):
                action_name = action[0]
                action_args = action[1]
                action_kwargs = action[2]

            if isinstance(action, dict):
                action_name = action["name"]
                action_args = action.get("args", [])
                action_kwargs = action.get("kwargs", {})

            if isinstance(action, str):
                action_name = action

            # get module from action name
            if action_name:
                package = importlib.import_module("plugget.actions")

                # little bit hacky, needed since path could be a path or _NamespacePath
                path: "List[str]|_frozen_importlib_external._NamespacePath" = package.__path__
                if not isinstance(path, str):
                    # assume _NamespacePath
                    path: "list[str]" = path._path
                path = path[0]

                for file in Path(path).glob("*.py"):
                    if file.stem == action_name:
                        action_module = importlib.import_module(f"plugget.actions.{file.stem}")
                        break
                if not action_module:
                    raise Exception(f"action '{action}' not found by name")

            # if action is a module, it's the action itself
            # if inspect.ismodule(self._action):
            # if isinstance(action, type(importlib)):  # check if action is of type module
            #     print("action is module", action, type(action), type(importlib))
            #     action_module = action

            if not action_module:
                raise Exception(f"action '{action}' not found")

            actions.append((action_module, action_args, action_kwargs))
        return actions

    @classmethod
    def from_json(cls, json_path) -> "plugget.data.package.Package":
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

    def to_dict(self, empty_keys=False) -> dict:
        """
        convert the package to a dict, e.g. used for manifest files
        :param empty_keys: if True, include keys with None values
        """
        output = {'app': self.app,
                  'package_name': self.package_name,
                  'version': self.version,
                  'repo_url': self.repo_url,
                  'repo_paths': self.repo_paths,
                  'self.repo_SHA': self.repo_SHA,
                  'package_url': self.package_url,
                  'docs_url': self.docs_url,
                  'actions': self._actions,
                  'dependencies': self.dependencies,
                  'installed_paths': [str(x) for x in self.installed_paths],
                  }

        if not empty_keys:
            empty_keys = [k for k, v in output.items() if not v]
            for key in empty_keys:
                del output[key]
        return output

    def to_json(self, json_path) -> None:
        """save the plugin to a json file"""

        output = self.to_dict()
        Path(json_path).parent.mkdir(exist_ok=True, parents=True)
        with open(json_path, "w") as f:
            json.dump(output, f, indent=4)

    def get_content(self, target_dir=None, use_cached=True) -> "list[Path]":
        """
        download the plugin content from the repo, and return the paths to the files
        target_dir: the folder to download the files to
        use_cached: if True, use the cached files if they exist
        """
        # this choosing what to do, could be a manager in an action
        # if zip file, download and extract
        # else clone repo
        if not use_cached or not self._content_paths:
            self._content_paths = self._clone_repo(target_dir=target_dir)
        return self._content_paths
        # todo instead of clone can we download the files directly?
        # cant clone to non empty folder, so we need to move files instead. but unreal had permission issues with that

    def _clone_repo(self, target_dir=None) -> "list[Path]":
        """
        returns either the files in repo (sparse) or the folder containing the repo
        """

        target_dir = target_dir or self.clone_dir
        self._clone_dir = target_dir
        # todo save target_dir in self.clone_dir ?

        # clone package repo to temp folder
        rmdir(target_dir)

        logging.info(f"cloning '{self.repo_url}' to '{target_dir}'")
        # todo sparse checkout, support multiple entries in self.repo_paths

        # logging.debug(f"cloning {self.repo_url} to {target_dir}")
        # subprocess.run(["git", "clone", "--depth", "1", "--progress", self.repo_url, str(target_dir)])
        # todo this doesnt always print the error, see unreal plugget for example with errors

        # ensure target dir exists.
        target_dir.mkdir(exist_ok=True, parents=True)

        def run_log(command, cwd=None) -> int:
            logging.info("command: '{command}'")
            process = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout, stderr = process.communicate()
            try:
                if stdout:
                    logging.debug(stdout.decode())
                if stderr:
                    logging.error(stderr.decode())
            except Exception as e:
                logging.error("error printing stdout/stderr: '{e}'")
                logging.error("stdout: '{stdout}'")
            return process.returncode

        if self.repo_SHA:
            # todo check if repo_SHA is valid
            logging.info(["command to run repo_SHA:", ["git", "clone", "--depth", "1", "--progress", self.repo_url, str(target_dir)]])
            run_log(["git", "clone", "--depth", "1", "--progress", self.repo_url, str(target_dir)])
            run_log(["git", "fetch", "--depth", "1", "origin", self.repo_SHA], cwd=target_dir)
            run_log(["git", "checkout", self.repo_SHA], cwd=target_dir)
        elif self.repo_tag:
            # subprocess.run(["git", "checkout", f"tags/{self.repo_tag}"], cwd=target_dir)
            logging.info(["command to run repo_tag:", ["git", "clone", "--depth", "1", "--branch", self.repo_tag], target_dir])
            run_log(["git", "clone", "--depth", "1", "--branch", self.repo_tag,  "--progress", self.repo_url, str(target_dir)])
        else:
            logging.info(["command to run other:", ["git", "clone", "--depth", "1", "--progress", self.repo_url, str(target_dir)]])
            run_log(["git", "clone", "--depth", "1", "--progress", self.repo_url, str(target_dir)])

        # delete .git folder
        rmdir(target_dir / ".git")

        # check if target dir contains any files
        if not any(target_dir.iterdir()):
            raise Exception(f"Failed to clone repo to {target_dir}")

        if self.repo_paths:
            return [target_dir / p for p in self.repo_paths]
        else:
            return [target_dir]

    def install(self, force=False, *args, **kwargs) -> None:
        from plugget import commands

        # install should be handled by its parent the packages meta.
        # since atm we check is installed. not if other versions are installed
        self.packages_meta.uninstall(self.package_name)

        if self.is_installed and not force:
            logging.warning(f"{self.package_name} is already installed")
            return

        action: "types.ModuleType" = None
        for action, action_args, action_kwargs in self.actions_args_kwargs:
            # action install implicitly adds to self.install_paths
            action_kwargs.update(kwargs)  # add kwargs to action_kwargs
            action.install(self, *args, force=force, *action_args, **action_kwargs)

        i = 0
        for d in self.dependencies:
            i += 1

            package = None

            # if dependency is a string, it's a package name, e.g. "blender:my-exporter", or "my-exporter"
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

            # if the dependency is a dict, it's a package object, e.g. {"name": "my-exporter", "app": "blender"}
            # that's saved in the same manifest file
            elif isinstance(d, dict):
                # the dependency attrs are defined in the same manifest file, so we manually set them
                # this overwrites attrs set in _set_data_from_manifest_path
                d.setdefault("manifest_path", self.manifest_path)
                d.setdefault("app", self.app)
                d.setdefault("version", self.version)
                d.setdefault("package_name", f"{self.package_name}_dependency_{i}")
                package = Package(**d)

            package.install(force=force, *args, **kwargs)

        # save (slightly modified) manifest to installed packages dir
        # todo check if install was successful
        installed_manifest_path = self.package_install_dir / self.manifest_path.name
        self.to_json(installed_manifest_path)

    def uninstall(self, dependencies=False, **kwargs) -> None:
        for action, action_args, action_kwargs in self.actions_args_kwargs:
            action_kwargs.update(kwargs)
            action.uninstall(self, dependencies=dependencies, *action_args, **action_kwargs)

        # todo uninstall dependencies
        # todo move pip action to dependencies

        # remove manifest from installed packages dir
        # todo check if uninstall was successful
        shutil.rmtree(self.package_install_dir, ignore_errors=True)


def hash_current_app() -> str:
    """
    create unique hash from sys exec path
    """
    # todo ensure this doesnt change mid session
    #  error if it does

    sys_exec_path = sys.executable
    crc32_hash = zlib.crc32(sys_exec_path.encode())
    app_id = hex(crc32_hash & 0xFFFFFFFF)[2:]  # Convert to hex and remove the "0x" prefix
    return app_id


def update_app_ids_json(app_id, root_folder_path, ) -> None:
    """
    add to json file which hash is which path in root folder.
    """
    data = {}
    try:
        with open('app_versions.json', 'r') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        pass

    data[app_id] = root_folder_path

    with open('app_versions.json', 'w') as json_file:
        json.dump(data, json_file)