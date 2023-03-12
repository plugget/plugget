"""
this action copies all (repo_paths) files to the macroscript folder
"""
import pymxs
from pymxs import runtime as rt
import shutil
from pathlib import Path


def install(package: "plugget.data.Package", **kwargs) -> bool:
    # get macroscript folder
    macro_folder_path = rt.getDir(rt.name('userMacros'))  #"#userMacros")

    # move it to folder
    repo_path = package.get_content()[0]
    sub_paths = package.repo_paths or [p.relative_to(repo_path) for p in repo_path.glob("*")]
    for sub_path in sub_paths:
        sub_path = repo_path / sub_path
        # rename file to end in .mcr
        if sub_path.is_file() and sub_path.suffix != ".mcr":
            sub_path.rename(sub_path.with_suffix(".mcr"))
        # copy files (and folders) to the macroscript folder
        shutil.copy(sub_path, macro_folder_path)

    # refresh macroscript folder to load the new macros in max
    pymxs.runtime.macros.load(macro_folder_path)


def uninstall(package: "plugget.data.Package", **kwargs):
    # get plugin name from manifest
    pass