"""
Plugget action to install dependencies from requirements.txt using pip.

PLUGGET_BLENDER_TARGET: env var to set target folder for pip install, if not set use user scripts folder from bpy
PLUGGET_BLENDER_INTERPRETER: env var to set python interpreter for pip install, defaults to sys.executable
"""

from pathlib import Path
import sys
import plugget.actions._utils as action_utils
import py_pip
import os


def setup_py_pip():
    py_pip.default_target_path = os.environ.get("PLUGGET_BLENDER_TARGET")
    if not py_pip.default_target_path:
        import bpy
        py_pip.default_target_path = str(Path(str(bpy.utils.script_path_user())) / "modules")

    # todo, startup script to add to site packages, else we cant support pth files.
    py_pip.python_interpreter = os.environ.get("PLUGGET_BLENDER_INTERPRETER") or sys.executable


def install(package: "plugget.data.Package", force=False, **kwargs):
    setup_py_pip()
    # TODO ideally use setup.py or pyproject.toml to install dependencies
    # if requirements.txt exists in self.repo_paths, install requirements
    for req_path in action_utils.iter_requirements_paths(package):
        py_pip.install(requirements=req_path, force=force, upgrade=True)


def uninstall(package: "plugget.data.Package", dependencies=False, **kwargs):
    # this method runs on uninstall, then the manifest is removed from installed packages
    # ideally uninstall removes files from a folder,

    if not dependencies:
        return

    setup_py_pip()

    # uninstall plugget_qt
    # we uninstall the dependencies (requirements)
    # TODO is there a chance we share requirements with another package?
    #  and uninstalling them breaks another package?

    for req_path in action_utils.iter_requirements_paths(package):
        print("requirements.txt found, uninstalling requirements")
        print("package.clone_dir / p", package.clone_dir / req_path)
        py_pip.uninstall(requirements=req_path, yes=True)
