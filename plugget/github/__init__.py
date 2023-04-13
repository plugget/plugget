from plugget import settings

try:
    import requests
except ImportError:
    print("requests not installed, github info won't be available")
import json
import logging


settings_data = settings.load_settings("github")
# todo enforce required vs optional settings
settings_data.setdefault("GITHUB_USER", None)
settings_data.setdefault("GITHUB_TOKEN", None)
settings.save_settings("github", settings_data)

GITHUB_TOKEN = settings_data["GITHUB_TOKEN"]
GITHUB_USER = settings_data["GITHUB_USER"]


# todo make this a plugin based setup. so we can add github, gitlab, ...
# todo make requests optional, if it's not installed, use urllib


def get_starred_repos(username=None):
    """
    get starred repos from GitHub

    Returns:
    a list of dicts, with full_name as key, and value user/my-repo
    """
    # todo cache?
    username = username or GITHUB_USER
    token = GITHUB_TOKEN

    headers = {}
    headers["Authorization"] = f"token {token}"

    url = f"https://api.github.com/users/{username}/starred"

    try:
        response = requests.get(url, headers=headers)
        if response.ok:
            favorites = json.loads(response.text)
            return favorites
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    return []


def is_starred(repo_url, username=None):
    """
    check if repo is starred
    """
    favorites = get_starred_repos(username=username)
    for favorite in favorites:
        if repo_url and favorite["full_name"] in repo_url:
            return True
    return False


def get_repo_stars(repo_url, username=None):
    """
    get number of stars for repo
    """

    """
    Get the number of stars for a GitHub repository.

    :param repo_url: The URL of the repository.
    :param username: Optional username to use for authentication.
    :return: The number of stars for the repository.
    """

    if not repo_url:
        logging.error("No repository URL provided to get_repo_stars")
        return 0

    # Split the repo URL into its components
    parts = repo_url.strip("/").split("/")
    if len(parts) < 2:
        raise ValueError("Invalid repository URL")

    # Construct the API URL
    api_url = f"https://api.github.com/repos/{parts[-2]}/{parts[-1]}"

    # Add authentication if a username is provided
    headers = {}
    # if username:
    #     headers["Authorization"] = f"token {username}"

    # Make the API request
    response = requests.get(api_url, headers=headers)
    if response.ok:
        repo_data = response.json()
        return repo_data["stargazers_count"]
    else:
        response.raise_for_status()