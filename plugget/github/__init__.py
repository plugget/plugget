from plugget import settings
import requests
import json


# todo make this a plugin based setup. so we can add github, gitlab, ...


def get_starred_repos(username=None):
    """
    gGt starred repos from github

    Returns:
    a list of dicts, with full_name as key, and value user/my-repo
    """
    # todo cache?
    username = username or settings.GITHUB_USER

    # token = prefs.github_token

    # headers = {
    #     "Authorization": f"token {token}"
    # }

    url = f"https://api.github.com/users/{username}/starred"

    try:
        response = requests.get(url)  # , headers=headers)
        if response.ok:
            favorites = json.loads(response.text)
            return favorites
            print(favorites)
            for favorite in favorites:
                print(favorite["full_name"])
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")


def is_starred(repo_url, username=None):
    """
    check if repo is starred
    """
    favorites = get_starred_repos(username=username)
    for favorite in favorites:
        if favorite["full_name"] in repo_url:
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