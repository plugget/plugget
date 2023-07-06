import logging
import subprocess


def install(package: "plugget.data.Package", **kwargs):

    # if requirements.txt exists in self.repo_paths, install requirements
    requirements_paths = []
    if (package.clone_dir / "requirements.txt").exists():
        requirements_paths.append(package.clone_dir / "requirements.txt")
    if package.repo_paths:
        for p in package.repo_paths:
            if p.endswith("requirements.txt"):
                requirements_paths.append(package.clone_dir / p)
    for p in requirements_paths:
        if p.exists():
            print("requirements.txt found, installing requirements")
            subprocess.run(["pip", "install", "-r", package.clone_dir / p])
        else:
            logging.warning(f"expected requirements.txt not found: '{p}'")


    # ideally install moves files to a folder
    pass


def uninstall(package: "plugget.data.Package", **kwargs):
    # this method runs on uninstall, then the manifest is removed from installed packages
    # ideally uninstall removes files from a folder,
    pass



