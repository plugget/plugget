"""
this action copies all (repo_paths) files to the macroscript folder
"""
import pymxs
from pymxs import runtime as rt
import shutil
from pathlib import Path


def install(package: "plugget.data.Package", **kwargs) -> bool:
    # get macroscript folder
    macro_folder_path = rt.getDir(rt.name('userMacros'))

    # move it to folder
    repo_paths = package.get_content()
    for sub_path in repo_paths:
        # sub_path = repo_path / sub_path
        # rename file to end in .mcr
        if sub_path.is_file() and sub_path.suffix != ".mcr":
            new_path = sub_path.with_suffix(".mcr")
            sub_path = sub_path.rename(new_path)
        # copy files (and folders) to the macroscript folder
        print("copying", sub_path, "to", macro_folder_path)
        shutil.copy(sub_path, macro_folder_path)

    # refresh macroscript folder to load the new macros in max
    pymxs.runtime.macros.load(macro_folder_path)


def uninstall(package: "plugget.data.Package", **kwargs):

    # get macroscript folder
    macro_folder_path = rt.getDir(rt.name('userMacros'))

    for sub_path in package.repo_paths:
        sub_path = Path(sub_path)
        if sub_path.suffix != ".mcr":
            sub_path = sub_path.with_suffix(".mcr")
        # delete files (and folders) from the macroscript folder
        sub_path = macro_folder_path / sub_path
        print("deleting", sub_path, "from", macro_folder_path)
        if sub_path.is_file():
            sub_path.unlink()
        else:
            sub_path.rmdir()

    # refresh macroscript folder to unload the uninstalled macros in max
    # pymxs.runtime.macros.load(macro_folder_path)
    # todo this doesn't unload the macro, so it will still be available untill we restart max

# def run():
#     #macros.run <category_string> <name_string>
#     rt.macros.run("Plugget", "test")
