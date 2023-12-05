import logging
import os
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
