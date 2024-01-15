"""
Configure plugget settings & manifest sources
e.g. constant paths & setting methods for plugget

these can then be saved to the user-settings in a json file, and automatically reload on startup
"""

from pathlib import Path
import os
import tempfile
import json
import logging
import importlib.resources


# paths
TEMP_PLUGGET = Path(tempfile.gettempdir()) / "plugget"
PLUGGET_DIR = Path(os.getenv("APPDATA")) / "plugget"  # todo expose PLUGGET_DIR to env var so it can be changed
INSTALLED_DIR = PLUGGET_DIR / "installed"
INSTALLED_DIR.mkdir(exist_ok=True, parents=True)
USER_SETTINGS_PATH = PLUGGET_DIR / "settings_plugget.json"

try:
    with importlib.resources.path('plugget.resources', 'config.json') as p:
        DEFAULT_PLUGGET_SETTINGS_PATH = Path(p).resolve()
except Exception as e:
    logging.error("failed to get default settings path", e)
    DEFAULT_PLUGGET_SETTINGS_PATH = Path()

# get settings for the actions etc, requires unique name for each action
# todo support duplicates of the same settings for each app (blender, blender2, maya, etc)
# actions request plugget for their settings
# plugget manages & saves the settings and returns them


registered_settings_paths = set([DEFAULT_PLUGGET_SETTINGS_PATH, USER_SETTINGS_PATH])
sources: set = set()  # set to avoid duplicate entries


def _load_json_settings(path: Path) -> dict:

    if not path.exists():
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except json.decoder.JSONDecodeError:
        return {}


def load_registered_settings() -> dict:
    """Load the registered settings configs"""
    settings = {}
    for path in registered_settings_paths:
        path = Path(path)
        if not path.exists():
            logging.warning(f"settings file not found: '{path}'")
            continue
        data = _load_json_settings(USER_SETTINGS_PATH)
        settings.update(data)
    return settings


def load_plugget_settings():
    """load all plugget settings (default, user)"""
    global sources
    settings_data = load_registered_settings()
    sources = set(settings_data.get("sources", []))


def save_user_settings(settings):
    """save user settings to json file in USER_SETTINGS_PATH"""
    with open(USER_SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=4)
        logging.debug("saved settings:", USER_SETTINGS_PATH)


load_plugget_settings()
