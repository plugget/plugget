"""
unreal utils
by default installs to project, not engine
"""
from pathlib import Path
import unreal


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


def get_plugin_path() -> Path:
    return project_plugins_dir()


def project_plugins_dir():
    project_path = unreal.Paths.project_plugins_dir()
    project_path = unreal.Paths.convert_relative_path_to_full(project_path)
    return Path(project_path)
