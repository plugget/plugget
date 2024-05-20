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
    to simplify setup for non-technical users and avoid a complex pip install,
    users can copy-paste plugget in a pythonpath folder,
    then install the dependencies with the following code:
        import plugget
        plugget.install_dependencies(app="maya")

    this assumes the pip module is installed already
    """
    # todo freezes in maya 2026

    import plugget

    p = plugget.Package(app=app)  # create a fake package
    requirement_action = p.actions_args_kwargs[0][0]  # get the pip install action with target paths setup for the app
    requirement_action.install(package=None, requirements=["py-pip", "detect-app", "requests"])  # install dependencies
