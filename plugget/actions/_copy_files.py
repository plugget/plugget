import logging
import shutil
from pathlib import Path


class CopyFiles:
    target_dir: Path = None

    @classmethod
    def install(cls, package: "plugget.data.Package", **kwargs) -> bool:
        print ("installing", package)

        cls.target_dir = cls.target_dir.resolve()

        # validate input
        if kwargs:
            logging.warning(f"unsupported kwargs passed to install: {kwargs}")
        if not cls.target_dir:
            raise ValueError("target_dir not set")
        if not cls.target_dir.exists():
            logging.warning(f"target_dir not found, creating: '{cls.target_dir}'")
            cls.target_dir.mkdir(parents=True, exist_ok=True)

        # move it to target folder
        repo_paths = package.get_content()
        for sub_path in repo_paths:
            # copy files (and folders) to the target folder
            print("copying", sub_path, "to", cls.target_dir)

            target_path = cls.target_dir / sub_path.name  # can be folder or file
            if target_path.exists():
                logging.warning(f"file already exists, overwriting: '{target_path}'")
                if target_path.is_dir():
                    shutil.rmtree(target_path)
                else:  # file
                    target_path.unlink()

            # check file or folder
            if sub_path.is_dir():
                # todo this is a naive implementation, doesn't handle nested folders
                new_path = shutil.copytree(sub_path, cls.target_dir / sub_path.name)
            else:
                new_path = shutil.copy(sub_path, cls.target_dir)

            # confirm files were copied
            if not Path(new_path).exists():
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
            if p.exists():
                if p.is_dir():
                    shutil.rmtree(p, ignore_errors=True)
                else:  # file
                    p.unlink()

            # todo check if remove worked. if file in use (e.g. Qt.dll) it might fail.

        return True
