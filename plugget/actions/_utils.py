from pathlib import Path
import logging


def get_requirements(package: "plugget.data.Package", **kwargs) -> list[Path]:
    """return a list of requirements.txt paths"""
    requirements_paths = []
    if (package.clone_dir / "requirements.txt").exists():
        requirements_paths.append(package.clone_dir / "requirements.txt")
    if package.repo_paths:
        for p in package.repo_paths:
            if p.endswith("requirements.txt"):
                requirements_paths.append(package.clone_dir / p)
    return requirements_paths


def iter_requirements(package: "plugget.data.Package"):
    for req_path in get_requirements(package):
        if req_path.exists():
            yield req_path
        else:
            logging.warning(f"expected requirements.txt not found: '{req_path}'")
