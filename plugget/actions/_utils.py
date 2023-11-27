from pathlib import Path
import logging


def get_requirements_txt_paths(package: "plugget.data.Package", **kwargs) -> list[Path]:
    """return a list of requirements.txt paths"""
    requirements_paths = []
    if (package.clone_dir / "requirements.txt").exists():
        requirements_paths.append(package.clone_dir / "requirements.txt")
    if package.repo_paths:
        for p in package.repo_paths:
            if p.endswith("requirements.txt"):
                requirements_paths.append(package.clone_dir / p)
    return requirements_paths


def iter_requirements_paths(package: "plugget.data.Package") -> "Generator[Path]":
    """yield all requirements.txt paths"""
    for req_path in get_requirements_txt_paths(package):
        if req_path.exists():
            yield req_path
        else:
            logging.warning(f"expected requirements.txt not found: '{req_path}'")


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

