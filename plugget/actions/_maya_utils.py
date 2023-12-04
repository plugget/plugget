import os
from pathlib import Path


def get_plugin_path():
    """return the path to the plugin folder"""
    # todo support other OS
    documents = Path(os.environ.get("USERPROFILE")) / "Documents"
    maya_version = "2022"  # todo dynamic
    plugin_path = documents / "maya" / maya_version / "plug-ins"
    return plugin_path

