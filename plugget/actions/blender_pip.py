import logging
import subprocess
from pathlib import Path
import bpy
import importlib
import os
import sys


def run_command(cmd):
    """Run a command in a subprocess and print the output to the console."""

    # Start the command with Popen
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Loop over the output of the command
    while True:
        output = process.stdout.readline()
        if output == b'' and process.poll() is not None:
            break
        if output:
            print(output.strip().decode('utf-8'))

    # Get the output of the command
    stdout, stderr = process.communicate()

    # Print the output to the Blender console
    print(stdout.decode('utf-8'))
    print(stderr.decode('utf-8'))


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
                cmd = [sys.executable, '-m', 'pip', "install", "--upgrade", 
                "-r", str(package.clone_dir / p), 
                '-t', str(blender_user_site_packages), "--no-user"]
                print(cmd)
                subprocess.run(cmd)
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
            cmd = [sys.executable, '-m', 'pip', "uninstall", "-r", package.clone_dir / p, "-y"]
            print(cmd)
            subprocess.run(cmd)
        else:
            logging.warning(f"expected requirements.txt not found: '{p}'")

    importlib.invalidate_caches()



