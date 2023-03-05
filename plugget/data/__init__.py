from pathlib import Path
import subprocess
import json
import logging
from plugget.utils import rmdir
from plugget import settings


class Plugin(object):
    # change representation when printed
    def __repr__(self):
        return f"Plugin({self.name} {self.version})"

    def __init__(self, app=None, name=None, display_name=None, plugin_name=None, id=None, version=None,
                 description=None, author=None, repo_url=None, package_url=None, license=None, tags=None,
                 dependencies=None, repo_paths=None, docs_url=None, package_name=None, manifest_path=None, **kwargs):
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
            logging.warning("unused kwargs on Plugin init:", kwargs)

        # attributes derived from the manifest path
        self._app = app
        self._package_name = package_name
        self._version = version
        # stores a reference where the config was loaded from, and sets app, package_name, version
        self.manifest_path = Path(manifest_path)

        # manifest settings
        self.repo_url = repo_url  # set before plugin name
        self.package_url = package_url  # set before plugin name
        self.plugin_name = plugin_name or self.default_plugin_name()
        self.name = name or self.plugin_name
        # self.id = id or plugin_name  # unique id  # todo for now same as name
        self.docs_url = None
        # description = ""
        # author = ""
        # license = ""
        # tags = []
        # dependencies = []
        self.repo_paths = repo_paths

    @property
    def app(self):
        return self._app

    @app.setter
    def app(self, value):
        self._app = value

    @property
    def package_name(self):
        return self._package_name

    @manifest_name.setter
    def package_name(self, value):
        self._package_name = value

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = value

    @property
    def manifest_path(self):
        return self._manifest_path

    @manifest_path.setter
    def manifest_path(self, value):
        # expects a path from the folder structure: app_name/package_name/version.json
        self._manifest_path = Path(value)
        self.version = self._manifest_path.stem
        self.app = self._manifest_path.parent.parent.name  # todo change this to be more robust
        self.package_name = self._manifest_path.parent.name

    def default_plugin_name(self):
        """
        use the repo name as the default plugin name
        e.g. https://github.com/SavMartin/TexTools-Blender -> TexTools-Blender
        """
        if self.package_url:
            return self.package_url.rsplit("/", 1)[1].split(".")[0]
        else:
            return self.repo_url.rsplit("/", 1)[1].split(".")[0]

    @property
    def clone_dir(self):
        """return the path we clone to on install e.g C:/Users/username/AppData/Local/Temp/plugget/bqt/0.1.0"""
        return settings.TEMP_PLUGGET / self.app / self.plugin_name / self.version / self.plugin_name

    @classmethod
    def from_json(cls, json_path):
        """create a plugin from a json file"""
        manifest_path = Path(json_path)

        with open(json_path, "r") as f:
            json_data = json.load(f)

        # todo this is a bit hacky, currently assumes you install from the plugget repo
        app = manifest_path.parent.parent.name  # e.g. blender/bqt/0.1.0.json -> blender

        # manifest_name = manifest_path.parent.name  # e.g. blender/bqt/0.1.0.json -> bqt
        version = manifest_path.stem  # e.g. blender/bqt/0.1.0.json -> 0.1.0
        return cls(**json_data, app=app, version=version, manifest_path=manifest_path)  #manifest_name=manifest_name

    def get_content(self) -> list[Path]:
        """download the plugin content from the repo, and return the paths to the files"""
        return self._clone_repo()

    def _clone_repo(self) -> list[Path]:
        # clone package repo to temp folder
        rmdir(self.clone_dir)

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
            subprocess.run(
                ["git", "clone", "--depth", "1", "--single-branch", "--progress", self.repo_url, str(self.clone_dir)])

            # delete .git folder
            rmdir(self.clone_dir / ".git")

            # app_dir = Path("C:/Users/hanne/OneDrive/Documents/repos/plugget-pkgs") / "blender"
            return [self.clone_dir]
