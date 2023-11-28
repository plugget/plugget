"""
Abstract Plugget action to pip install Python dependencies from requirements.txt.
"""

import plugget.actions._utils as action_utils
import py_pip
import os


class RequirementsAction:
    interpreter = None
    target = None
    env_var = None

    @classmethod
    def setup_py_pip(cls):
        if not cls.interpreter:
            cls.interpreter = os.environ.get(f"PLUGGET_{cls.env_var}_INTERPRETER")
        if not cls.target:
            cls.target = os.environ.get(f"PLUGGET_{cls.env_var}_TARGET_MODULES")
        py_pip.default_target_path = cls.target
        py_pip.python_interpreter = cls.interpreter

    @classmethod
    def install(cls, package: "plugget.data.Package", force=False, **kwargs):
        print("install requirements to target", cls.target)
        package.get_content(use_cached=True)
        cls.setup_py_pip()
        for req_path in action_utils.iter_requirements_paths(package):
            print("requirements.txt found, installing: ", req_path)
            py_pip.install(requirements=req_path, force=force, upgrade=True)
            # TODO confirm install worked, atm any crash in py_pip is silently ignored

    @classmethod
    def uninstall(cls, package: "plugget.data.Package", dependencies=False, **kwargs):
        if not dependencies:
            return
        cls.setup_py_pip()
        for req_path in action_utils.iter_requirements_paths(package):
            print("requirements.txt found, uninstalling requirements")
            print("package.clone_dir / p", package.clone_dir / req_path)
            py_pip.uninstall(requirements=req_path, yes=True)
            # TODO confirm uninstall worked
