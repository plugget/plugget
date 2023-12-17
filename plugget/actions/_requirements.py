"""
Abstract Plugget action to pip install Python dependencies from requirements.txt.
"""

import py_pip
import os
import logging
from pathlib import Path


def get_requirements_txt_paths(package: "plugget.data.Package", **kwargs) -> "list[Path]":
    """return a list of requirements.txt paths"""
    requirements_paths = []
    if not package.clone_dir.exists():
        logging.warning(f"package.clone_dir does not exist, plugget didn't fetch package content: '{package.clone_dir}'")
    # get the requirements.txt in the root of the repo
    if (package.clone_dir / "requirements.txt").exists():
        requirements_paths.append(package.clone_dir / "requirements.txt")
    # get requirements.txt paths defined by user in repo_paths
    if package.repo_paths:
        for p in package.repo_paths:
            if p.endswith("requirements.txt"):
                requirements_paths.append(package.clone_dir / p)
    return requirements_paths


def iter_requirements_paths(package: "plugget.data.Package") -> "Generator[Path]":
    """yield all requirements.txt paths"""
    req_paths = get_requirements_txt_paths(package)

    for req_path in req_paths:
        if req_path.exists():
            print(f"requirements.txt found: '{req_path}'")
            yield req_path
        else:
            logging.warning(f"expected requirements.txt not found: '{req_path}'")
    if not req_paths:
        print(f"no requirements.txt paths found")


# plugget gets requirements from requirements.txt, because the module is not packaged.
# if we can get requirements from setup.py or pyproject.toml, the module is packaged,
# and we don't need plugget. Keeping these methods for now, in case we need them later.

# def get_requirements_from_setup_py(path: "Path|str") -> "list[str]":
#     """
#     Get the requirements from a setup.py file
#     path: The path to the setup.py file
#
#     Warning: This method executes the setup.py file, so it should only be used on trusted files.
#     """
#     setup_info = {}
#     with open(str(path), "r") as file:
#         setup_code = file.read()
#     exec(setup_code, setup_info)
#     requirements = setup_info.get("install_requires", [])
#     return requirements


# def get_requirements_from_pyproject_toml(path: "Path|str") -> "list[str]":
#     """
#     Get the requirements from a pyproject.toml file
#     path: The path to the pyproject.toml file
#     """
#     import toml
#     with open(str(path), "r") as file:
#         pyproject_toml = toml.load(file)
#     requirements = pyproject_toml.get("project", {}).get("requires", [])
#     return requirements


class RequirementsAction:
    """
    interpreter: Path to interpreter to use for pip commands
    target: Path to target folder to install dependencies to
    env_var: app name to detect env-variables that override settings, e.g.MAYA -> PLUGGET_MAYA_INTERPRETER
    """

    interpreter = None
    target = None
    env_var = None

    @classmethod
    def setup_py_pip(cls):
        if not cls.interpreter:
            cls.interpreter = os.environ.get(f"PLUGGET_{cls.env_var}_INTERPRETER")
        if not cls.target:
            cls.target = os.environ.get(f"PLUGGET_{cls.env_var}_TARGET_MODULES")
        py_pip.default_target_path = cls.target
        py_pip.python_interpreter = cls.interpreter

    @classmethod
    def install(cls, package: "plugget.data.Package", force=False, requirements:list=None, *args, **kwargs):
        print("install requirements to target", cls.target)
        package.get_content(use_cached=True)
        cls.setup_py_pip()
        for req_path in iter_requirements_paths(package):
            print("requirements.txt found, installing: ", req_path)
            py_pip.install(requirements=req_path, force=force, upgrade=True)
            # TODO confirm install worked, atm any crash in py_pip is silently ignored
        requirements = requirements or []
        for name in requirements:
            print("installing extra requirement:", name)
            py_pip.install(package_name=name)

    @classmethod
    def uninstall(cls, package: "plugget.data.Package", dependencies=False, **kwargs):
        if not dependencies:
            return
        cls.setup_py_pip()
        for req_path in iter_requirements_paths(package):
            print("requirements.txt found, uninstalling requirements")
            print("package.clone_dir / p", package.clone_dir / req_path)
            py_pip.uninstall(requirements=req_path, yes=True)
            # TODO confirm uninstall worked
