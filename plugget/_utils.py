"""
util functions for Plugget
"""

import os


DEPENDENCIES = ["plugget", "py-pip", "detect-app", "requests"]


def rmdir(path):
    # logging.debug(f"rmdir {path}")
    # delete folder on windows
    if os.path.exists(path):
        # remove folder and all content
        os.system(f"rmdir /s /q {path}")


def install_plugget_dependencies(app=None):
    install_pypi(modules=DEPENDENCIES, app=app)


def install_pypi(modules: "list[str]", app=None):
    """
    to simplify setup for non-technical users and avoid a complex pip install,
    users can copy-paste plugget in a pythonpath folder,
    then install the dependencies with the following code:

    import plugget._utils
    plugget._utils.install_dependencies(app="maya")

    this assumes the pip module is installed already
    """
    # todo freezes in maya 2026
    import plugget

    try:
        import detect_app
        app = detect_app.detect_app()
    except ImportError:
        pass

    p = plugget.Package(app=app)  # create a fake package
    requirement_action = p.actions_args_kwargs[0][0]  # get the pip install action with target paths setup for the app
    requirement_action.install(package=None, requirements=modules)  # install dependencies
    # todo this could be cleaner


def update_plugget():
    """
    update plugget and its dependencies, e.g.:

    import plugget._utils
    plugget._utils.update_plugget()
    """
    import py_pip
    import plugget
    import detect_app

    # set the correct target path and python interpreter for the app
    # todo this could be cleaner
    app = detect_app.detect_app()
    p = plugget.Package(app=app)  # create a fake package
    requirement_action = p.actions_args_kwargs[0][0]  # get the pip install action with target paths setup for the app
    py_pip.default_target_path = requirement_action.target
    py_pip.python_interpreter = requirement_action.interpreter

    # upgrade plugget and its dependencies
    for dep in DEPENDENCIES:
        py_pip.install(package_name=dep, upgrade=True)


def download_github_repo(repo_url, target_dir, branch=None):
    import requests
    import zipfile
    import io

    branch = branch or "main"

    # download the zip file from the repository URL
    if repo_url.endswith('/'):
        repo_url = repo_url[:-1]
    api_url = f"{repo_url}/archive/refs/heads/{branch}.zip"

    # Send a request to the URL
    response = requests.get(api_url)
    if response.status_code == 200:
        print(f"Successfully downloaded {api_url}")
    else:
        raise Exception(f"Failed to download {api_url}: {response.status_code}")

    # Extract the content of the zip file to the temporary directory
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        zip_file.extractall(path=target_dir)
        print(f"Repository extracted to temporary directory {target_dir}")
