"""
util functions for Plugget
"""

import os


def rmdir(path):
    # logging.debug(f"rmdir {path}")
    # delete folder on windows
    if os.path.exists(path):
        # remove folder and all content
        os.system(f"rmdir /s /q {path}")


def install_dependencies(app=None):
    """
    this allows us to drag and drop plugget in the pythonpath, then run:
        import plugget
        plugget.install_dependencies(app="maya")
    """
    import plugget

    p = plugget.Package(app=app)  # create a fake package
    requirement_action = p.actions_args_kwargs[0][0]  # get the pip install action with target paths setup for the app
    requirement_action.install(package=None, requirements=["py-pip", "detect-app", "requests"])  # install dependencies

