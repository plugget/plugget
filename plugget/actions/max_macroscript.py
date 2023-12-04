"""
this action copies all (repo_paths) files to the macroscript folder
"""
import logging

import pymxs
from pymxs import runtime as rt
import shutil
from pathlib import Path


def install(package: "plugget.data.Package", max_folder=None, **kwargs) -> bool:
    # get macroscript target folder
    macro_folder_path = rt.getDir(rt.name('userMacros'))  # todo expose to kwarg

    # move it to target folder
    repo_paths = package.get_content()
    for sub_path in repo_paths:
        # sub_path = repo_path / sub_path
        # rename file to end in .mcr
        if sub_path.is_file() and sub_path.suffix != ".mcr":
            new_path = sub_path.with_suffix(".mcr")
            sub_path = sub_path.rename(new_path)
            logging.warning(f"renamed {sub_path} to {new_path}")

        if not sub_path.is_file():
            logging.warning(f"skipping: expected file, got folder: '{sub_path}'")
            continue

        # copy files (and folders) to the macroscript folder
        print("copying", sub_path, "to", macro_folder_path)
        shutil.copy(sub_path, macro_folder_path)

    # refresh macroscript folder to load the new macros in max
    pymxs.runtime.macros.load(macro_folder_path)


def uninstall(package: "plugget.data.Package", **kwargs):
    for p in package.installed_paths:
        p = Path(p)

        print("remove", p)
        # delete all paths,. p can be folder or file. force delete and children
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
        else:
            p.unlink(missing_ok=True)

        # todo check if remove worked. if file in use (e.g. Qt.dll) it might fail.

    # refresh macroscript folder to unload the uninstalled macros in max
    # pymxs.runtime.macros.load(macro_folder_path)
    # todo this doesn't unload the macro, so it will still be available untill we restart max

# todo commands
# def run():
#     #macros.run <category_string> <name_string>
#     rt.macros.run("Plugget", "test")
