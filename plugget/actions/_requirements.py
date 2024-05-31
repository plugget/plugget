"""
Abstract Plugget action to pip install Python dependencies from requirements.txt.
"""
from plugget.actions._utils import is_package_installed

try:
    import py_pip
except ImportError:
    # import vendored version, this allows us to install plugget without dependencies
    # we can then use plugget to update it's own dependencies
    # TODO add instructions
    from plugget.vendor import py_pip

import os
import logging
from pathlib import Path
import plugget.actions._utils


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
        print(f"no requirements.txt paths found in '{package.clone_dir}'")


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


# todo move to pypip
def iter_packages_in_requirements(path: "str|Path"):
    data = Path(path).read_text().splitlines()
    for line in data:
        line = line.strip()
        if line.startswith("#"):  # skip comments
            continue
        yield line


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
    def install(cls, package: "plugget.data.Package", force=False, requirements: list = None, *args, **kwargs):
        print("install requirements to target", cls.target)
        cls.setup_py_pip()

        requirements = requirements or []

        if package:
            package.get_content(use_cached=True)
            for req_path in iter_requirements_paths(package):
                print("requirements.txt found: ", req_path)
                for package_name in iter_packages_in_requirements(req_path):
                    requirements.append(package_name)

        if not (requirements or package):
            logging.warning("no package provided to RequirementsAction.install method")

        for name in requirements:
            try:
                print(f"installing '{name}' from requirements.txt")
                stdout, error = py_pip.install(package_name=package_name, force=force, upgrade=True)
                print(stdout.decode())
            except Exception as e:
                # this can happen if a package is in use, e.g. PySide
                # check if package is already installed, if yes we can pass this
                if plugget.actions._utils.is_package_installed(package_name):
                    print(f"Error on install package '{package_name}', but is already installed")
                else:  # if not we error
                    logging.error(f"failed to install package '{package_name}'")
                    raise Exception(e)

    @classmethod
    def uninstall(cls, package: "plugget.data.Package", dependencies=False, **kwargs):
        return

        # if not dependencies:
        #     return
        # cls.setup_py_pip()
        # for req_path in iter_requirements_paths(package):
        #     print("requirements.txt found, uninstalling requirements")
        #     print("package.clone_dir / p", package.clone_dir / req_path)
        #     py_pip.uninstall(requirements=req_path, yes=True)
        #     # TODO confirm uninstall worked
