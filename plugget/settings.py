"""
Configure plugget settings & manifest sources
e.g. constant paths & setting methods for plugget
"""

from pathlib import Path
import os
import tempfile
import json
import logging
import importlib.resources


# paths
TEMP_PLUGGET = Path(tempfile.gettempdir()) / "plugget"
PLUGGET_DIR = Path(os.getenv("APPDATA")) / "plugget"
INSTALLED_DIR = PLUGGET_DIR / "installed"
# PLUGGET_SETTINGS = PLUGGET_DIR / "settings.json"
# todo expose PLUGGET_DIR to env var so it can be changed
INSTALLED_DIR.mkdir(exist_ok=True, parents=True)


# get settings for the actions etc, requires unique name for each action
# todo support duplicates of the same settings for each app (blender, blender2, maya, etc)
# actions request plugget for their settings
# plugget manages & saves the settings and returns them

def _settings_name(name):
    return PLUGGET_DIR / f"settings_{name}.json"


def load_settings(name) -> dict:
    """Load the settings configs in PLUGGET_DIR (user) and plugget/resources (default)"""
    user_settings_path = _settings_name(name)
    user_settings = _load_json_settings(user_settings_path)

    # plugget settings
    path = importlib.resources.path('plugget.resources', 'config.json')
    plugget_settings = _load_json_settings(path)

    # combine settings
    settings = plugget_settings
    settings.update(user_settings)
    return settings


def _load_json_settings(path: Path) -> dict:

    if not path.exists():
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except json.decoder.JSONDecodeError:
        return {}


def save_settings(name, settings):
    with open(_settings_name(name), "w") as f:
        json.dump(settings, f, indent=4)
        logging.debug("saved settings:", _settings_name(name))


def add_source(source):
    """source: a git URL or path to local manifest-folder"""
    sources.add(source)
    save_settings("plugget", {"sources": list(sources)})


def remove_source(source):
    sources.remove(source)
    save_settings("plugget", {"sources": list(sources)})  # todo combine all these save settings lines


# def list_sources():
#     return sources


# todo in settings we need a add_repo, remove_repo, list_repos.
# todo cleanup simple way of loading
settings_data = load_settings("plugget")
sources: set = set(settings_data.get("sources", []))
save_settings("plugget", {"sources": list(sources)})
