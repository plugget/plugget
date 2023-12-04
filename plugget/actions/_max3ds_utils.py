
from pathlib import Path
import sys
import os



def _get_interpreter_path():
    # return "python"  # TODO hack since code below is buggy
    windows_python = Path(sys.executable).parent / "Python" / "python.exe"  # TODO support other OS
    return windows_python