"""
unreal utils
by default installs to project, not engine
"""
from pathlib import Path
import unreal
import json
import sys


def _get_interpreter_path():
    # copied from https://github.com/hannesdelbeke/unreal-pip/blob/main/unreal_pip/__init__.py
    # todo can/should we use this as dependency?
    interpreter_path = Path(unreal.get_interpreter_executable_path())
    return interpreter_path


def get_site_packages() -> str:
    return project_site_dir()


def project_site_dir() -> Path:
    """
    Return the site-packages path for the current project
    Note: this folder might not exist
    """
    content_path = unreal.Paths.project_content_dir()  # '../../../Users/USER/MyProject/Content/'
    content_path = unreal.Paths.convert_relative_path_to_full(content_path)  # 'C:/Users/USER/MyProject/Content/'
    return Path(content_path) / r"Python\Lib\site-packages"  # 'C:/Users/USER/MyProject/Content/Python/Lib/site-packages'


def get_plugins_path() -> Path:
    return project_plugins_dir()


def project_plugins_dir():
    project_path = unreal.Paths.project_plugins_dir()
    project_path = unreal.Paths.convert_relative_path_to_full(project_path)
    return Path(project_path)


def load_project_file_json():
    uproject_path = unreal.Paths.get_project_file_path()
    with open(uproject_path, "r") as file:
        return json.load(file)


def save_project_file_json(data):
    uproject_path = unreal.Paths.get_project_file_path()
    with open(uproject_path, "w") as file:
        json.dump(data, file, indent=4)


def enable_plugin(name:str, enable:bool=True):
    if not isinstance(name, str):
        raise TypeError(f"expected str, got {type(name)}")

    uproject = load_project_file_json()
    plugins = uproject.get("Plugins", [])

    # check if name is already in plugins
    for plugin in plugins:
        if plugin["Name"] == name:
            plugin["Enabled"] = enable
            save_project_file_json(uproject)
            return
    # else add it
    plugins.append({"Name": name, "Enabled": enable})
    save_project_file_json(uproject)


def find_plugin_names(path: Path) -> "list[str]":
# search for uplugin files in the plugin folder
    return [uplugin.stem for uplugin in (path).rglob("*.uplugin")]


def exec_plugin_startup_code(path: Path):
    # search for uplugin files in the plugin folder
    for uplugin in (path).rglob("*.uplugin"):
        plugin_dir = Path(uplugin).parent
        py_path = plugin_dir / "Content" / "Python"
        sys.path.append(str(py_path))  # add to python path
        startup_script = py_path / "init_unreal.py"
        if startup_script.exists():
            print("running plugin startup code", startup_script)
            exec(startup_script.read_text())