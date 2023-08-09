"""
util functions used by plugget, avoid using if possible
"""
import os


def rmdir(path):
    # logging.debug(f"rmdir {path}")
    # delete folder on windows
    if os.path.exists(path):
        # remove folder and all content
        os.system(f"rmdir /s /q {path}")
