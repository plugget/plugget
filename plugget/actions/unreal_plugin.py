import unreal
from pathlib import Path
import shutil


def project_plugins_dir():
    project_path = unreal.Paths.project_plugins_dir()
    project_path = unreal.Paths.convert_relative_path_to_full(project_path)
    return Path(project_path)


def install(package: "plugget.data.Package", max_folder=None, **kwargs) -> bool:
    plugin_dir = project_plugins_dir()

    # move it to target folder
    repo_paths = package.get_content()
    for sub_path in repo_paths:
        print("copying", sub_path, "to", plugin_dir)
        shutil.copy(sub_path, plugin_dir)


def uninstall(package: "plugget.data.Package", **kwargs):

    plugin_dir = project_plugins_dir()

    for sub_path in package.repo_paths:
        sub_path = Path(sub_path)

        # delete files (and folders) from the plugin folder
        sub_path = plugin_dir / sub_path
        print("deleting", sub_path, "from", plugin_dir)
        if sub_path.is_file():
            sub_path.unlink()
        else:
            sub_path.rmdir()