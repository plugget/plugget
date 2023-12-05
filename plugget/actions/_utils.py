import logging
import sys
import os


def get_site_packages() -> str:
    # get env var APPDATA that contains 'C:\\Users\\hanne\\AppData\\Roaming\
    # todo support other OS
    roaming = os.environ.get("APPDATA")
    for path in sys.path:
        # get current python version in roaming
        if path.startswith(roaming):
            return path
            # 'C:\\Users\\hanne\\AppData\\Roaming\\Python\\Python39\\site-packages'
    # todo this path is not in site packages, might be a problem for pth files
from pathlib import Path


def try_except(func):
    # decorator to catch errors in functions
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"error in '{func}': '{e}'")
    return wrapper


def get_my_documents() -> Path:
    # todo support other OS
    user_dir = Path(os.environ.get("USERPROFILE"))  # e.g. 'C:\\Users\\hannes'
    # Windows auto resolves the path to the ondrive folder
    # one_drive_docs = user_dir / "OneDrive" / "Documents"
    # if one_drive_docs.exists():
    #     return one_drive_docs
    # else:
    return (user_dir / "Documents").resolve()
