from pathlib import Path
import os
import tempfile


sources = [
    "https://github.com/hannesdelbeke/plugget-pkgs.git",
]

TEMP_PLUGGET = Path(tempfile.gettempdir()) / "plugget"

# plugget folder in user's appdata
PLUGGET_DIR = Path(os.getenv("APPDATA")) / "plugget"
INSTALLED_DIR = PLUGGET_DIR / "installed"

INSTALLED_DIR.mkdir(exist_ok=True, parents=True)