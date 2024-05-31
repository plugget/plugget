import logging
import os
from pathlib import Path
import importlib.metadata


def try_except(func):
    # decorator to catch errors in functions
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"error in '{func}': \n'{e}'")
    return wrapper


def get_my_documents() -> Path:
    # todo support other OS
    user_dir = Path(os.environ.get("USERPROFILE"))  # e.g. 'C:\\Users\\hannes'
    user_dir = user_dir.resolve()
    one_drive_docs = user_dir / "OneDrive" / "Documents"
    if one_drive_docs.exists():
        path = one_drive_docs
    else:
        path = user_dir / "Documents"

    logging.debug("my documents path:", path)
    return path
    # todo are there other locations for documents?


def is_package_installed(package_name):
    try:
        importlib.metadata.version(package_name)
        return True
    except importlib.metadata.PackageNotFoundError:
        return False


def clash_import_name(name):
    """check there isn't a py module with the same name as our addon"""
    try:
        module = __import__(name)
        file = module.__file__  # can be None
        if file and Path(file).exists():  # Path crashes if file is none
            logging.warning(f"Failed to install addon {name}, a py module with same name exists")
            return True
    except ImportError:
        pass
    return False
