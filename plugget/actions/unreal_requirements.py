import os
import sys
import subprocess


import os
import sys
import subprocess
import logging
from pathlib import Path
import importlib
import unreal
import plugget.actions._requirements as action_utils


# def project_plugins_dir():
#     project_path = unreal.Paths.project_plugins_dir()
#     project_path = unreal.Paths.convert_relative_path_to_full(project_path)
#     return Path(project_path)


def project_site_dir():
    content_path = unreal.Paths.project_content_dir()  # '../../../Users/USER/MyProject/Content/'
    content_path = unreal.Paths.convert_relative_path_to_full(content_path)  # 'C:/Users/USER/MyProject/Content/'
    return Path(content_path) / r"Python\Lib\site-packages"  # 'C:/Users/USER/MyProject/Content/Python/Lib/site-packages'


# todo unify, copied from krita_pip


project_site_dir = project_site_dir()
# python_version = "{}.{}".format(sys.version_info.major, sys.version_info.minor)


def install(package: "plugget.data.Package", **kwargs):
    print("check for requirements")

    for p in action_utils.get_requirements_txt_paths(package):
        if p.exists():
            print("requirements.txt found, installing requirements")
            # todo python -m pip with unreal py interpreter
            subprocess.run(["pip", "install", "-r", package.clone_dir / p, '-t', project_site_dir, "--no-user"])
        else:
            logging.warning(f"expected requirements.txt not found: '{p}'")
    importlib.invalidate_caches()

    # # check if files were copied: package.clone_dir / p
    # if not (package.clone_dir / p).exists():
    #     raise FileNotFoundError(f"expected file not found: '{p}'")


# def install(package: "plugget.data.Package", **kwargs):
#     # Use the Python executable to run the pip install command
#     args = [get_python(), "-m", "pip", "install", name, "-t", path]
#     subprocess.check_call(args)
#
#
# def uninstall(package: "plugget.data.Package", dependencies=False, **kwargs):
#     # Use the Python executable to run the pip uninstall command
#     if not dependencies:
#         return
#     args = [get_python(), "-m", "pip", "uninstall", name, "-t", path]
#     subprocess.check_call(args)


def uninstall(package: "plugget.data.Package", dependencies=False, **kwargs):
    # this method runs on uninstall, then the manifest is removed from installed packages
    # ideally uninstall removes files from a folder,

    if not dependencies:
        return

    for p in action_utils.get_requirements_txt_paths(package):
        if p.exists():
            print("requirements.txt found, uninstalling requirements")
            print("package.clone_dir / p", package.clone_dir / p)
            subprocess.run(["pip", "uninstall", "-r", package.clone_dir / p, "-y"])
        else:
            logging.warning(f"expected requirements.txt not found: '{p}'")
    importlib.invalidate_caches()

