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


def try_except(func):
    # decorator to catch errors in functions
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"error in '{func}': '{e}'")
    return wrapper