from pathlib import Path
import os


sources = [
    "https://github.com/hannesdelbeke/plugget-pkgs.git",
]

TEMP_PLUGGET = Path(os.getenv("TEMP")) / "plugget"
