import logging
import shutil
from pathlib import Path


class CopyFiles:
    def __init__(self, **kwargs):
        self.target_dir = None

    def install(self, package: "plugget.data.Package", **kwargs) -> bool:

        # validate input
        if kwargs:
            logging.warning(f"unsupported kwargs passed to install: {kwargs}")
        if not self.target_dir:
            raise ValueError("target_dir not set")

        # move it to target folder
        repo_paths = package.get_content()
        for sub_path in repo_paths:
            # copy files (and folders) to the target folder
            print("copying", sub_path, "to", self.target_dir)
            new_path = shutil.copy(sub_path, self.target_dir)

            # confirm files were copied
            if not new_path.exists():
                raise FileNotFoundError(f"expected file not found: '{sub_path}'")

            # save installed paths
            package.installed_paths.add(new_path)  # todo might want a dict later

        # TODO on fail, cleanup files already copied over, reset package.installed_paths

        return True

    @staticmethod
    def uninstall(package: "plugget.data.Package", **kwargs):
        # validate input
        if kwargs:
            logging.warning(f"unsupported kwargs passed to uninstall: {kwargs}")

        # delete all installed paths
        for p in package.installed_paths:
            p = Path(p)

            print("remove", p)
            # delete all paths,. p can be folder or file. force delete and children
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
            else:
                p.unlink(missing_ok=True)

            # todo check if remove worked. if file in use (e.g. Qt.dll) it might fail.

        return True
