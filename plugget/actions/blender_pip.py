import logging
import subprocess
from pathlib import Path
import bpy
import importlib
import os
import sys


def prep_pythonpath():
    # copy the sys.paths to PYTHONPATH to pass to subprocess, for pip to use
    paths = os.environ.get("PYTHONPATH", "").split(os.pathsep)
    new_paths = [p for p in sys.path if p not in paths]
    paths += new_paths
    joined_paths = os.pathsep.join(paths)
    if joined_paths:
        os.environ["PYTHONPATH"] = joined_paths


def get_requirements(package: "plugget.data.Package", **kwargs) -> list[Path]:
    # if requirements.txt exists in self.repo_paths, install requirements
    requirements_paths = []
    if (package.clone_dir / "requirements.txt").exists():
        requirements_paths.append(package.clone_dir / "requirements.txt")
    if package.repo_paths:
        for p in package.repo_paths:
            if p.endswith("requirements.txt"):
                requirements_paths.append(package.clone_dir / p)
    return requirements_paths


# todo share pip functions
def install(package: "plugget.data.Package", **kwargs):
    prep_pythonpath()

    blender_user_site_packages = Path(str(bpy.utils.script_path_user())) / "modules"  # appdata
    blender_user_site_packages.mkdir(exist_ok=True, parents=True)

    for p in get_requirements(package):
        if p.exists():
            print("requirements.txt found, installing requirements")
            # todo blender pip
            try:
                # todo python -m pip
                subprocess.run(
                    ["pip", "install", "--upgrade", "-r", package.clone_dir / p, '-t', blender_user_site_packages,
                     "--no-user"])
            except subprocess.CalledProcessError as e:
                logging.error(e.output)
        else:
            logging.warning(f"expected requirements.txt not found: '{p}'")
    importlib.invalidate_caches()


def uninstall(package: "plugget.data.Package", dependencies=False, **kwargs):
    # this method runs on uninstall, then the manifest is removed from installed packages
    # ideally uninstall removes files from a folder,

    if not dependencies:
        return

    prep_pythonpath()

    blender_user_site_packages = Path(str(bpy.utils.script_path_user())) / "modules"  # appdata

    for p in get_requirements(package):
        if p.exists():
            print("requirements.txt found, uninstalling requirements")
            print("package.clone_dir / p", package.clone_dir / p)
            subprocess.run(["pip", "uninstall", "-r", package.clone_dir / p, "-y"])
        else:
            logging.warning(f"expected requirements.txt not found: '{p}'")

    importlib.invalidate_caches()



