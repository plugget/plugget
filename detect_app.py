"""
Detect which app the python interpreter is running in. use detect_app()
"""

import types
import contextlib
from typing import Optional
import logging
import importlib


def attempt_import(module_name: str) -> Optional[types.ModuleType]:
    """attempt to import a module, return True if it succeeded"""
    with contextlib.suppress(ImportError):
        importlib.import_module(module_name)
        return True
    return False


class App:
    id: str  # id follows python module name conventions, name should not start with int, useinstead of spaces
    _name: str
    action: callable  # if returns True, the app is detected

    @classmethod
    def get_name(cls):
        return cls.id.replace("_", " ").title() if not cls._name else cls._name


class Blender(App):
    id = "blender"
    action = lambda: attempt_import("bpy")


class Fusion(App):
    id = "fusion"
    action = lambda: attempt_import("adsk.fusion")


class Houdini(App):
    id = "houdini"
    action = lambda: attempt_import("hou")


class SubstancePainter(App):
    id = "substance_painter"
    action = lambda: attempt_import("substance_painter")


class Krita(App):
    id = "krita"
    action = lambda: attempt_import("krita")


class Marmoset(App):
    id = "marmoset"
    action = lambda: attempt_import("mset")


class Maya(App):
    id = "maya"
    action = lambda: attempt_import("maya")


class Max3ds(App):
    id = "max3ds"
    _name = "3ds Max"
    action = lambda: attempt_import("pymxs")


class MotionBuilder(App):
    id = "motion_builder"
    action = lambda: attempt_import("pyfbsdk")


class Nuke(App):
    id = "nuke"
    action = lambda: attempt_import("nuke")


class Softimage(App):
    id = "softimage"
    action = lambda: attempt_import("PySoftimage")


class SubstanceDesigner(App):
    id = "substance_designer"
    action = lambda: attempt_import("pysbs")


class Unreal(App):
    id = "unreal"
    action = lambda: attempt_import("unreal")


# try keep alphabetically
apps = [
    Blender,
    Fusion,
    Houdini,
    Krita,
    MotionBuilder,
    Marmoset,
    Maya,
    Max3ds,
    Nuke,
    SubstancePainter,
    SubstanceDesigner,
    Softimage,
    Unreal,
]


def detect_app() -> Optional[App]:
    """
    detect which app is currently running
    """
    for app in apps:
        if app.action():
            logging.debug(f"app detected {app.id}")
            return app

