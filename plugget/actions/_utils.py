from pathlib import Path


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