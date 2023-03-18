import logging
import subprocess
from pathlib import Path
import bpy


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
    blender_user_site_packages = Path(str(bpy.utils.script_path_user())) / "modules"  # appdata

    for p in get_requirements(package):
        if p.exists():
            print("requirements.txt found, installing requirements")
            # todo blender pip
            subprocess.run(["pip", "install", "-r", package.clone_dir / p, '-t', blender_user_site_packages])
        else:
            logging.warning(f"expected requirements.txt not found: '{p}'")


def uninstall(package: "plugget.data.Package", dependencies=False, **kwargs):
    # this method runs on uninstall, then the manifest is removed from installed packages
    # ideally uninstall removes files from a folder,

    if not dependencies:
        return

    blender_user_site_packages = Path(str(bpy.utils.script_path_user())) / "modules"  # appdata

    for p in get_requirements(package):
        if p.exists():
            print("requirements.txt found, uninstalling requirements")
            print("package.clone_dir / p", package.clone_dir / p)
            subprocess.run(["pip", "uninstall", "-r", package.clone_dir / p, "-y"])
        else:
            logging.warning(f"expected requirements.txt not found: '{p}'")



