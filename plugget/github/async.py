import aiohttp
import asyncio
import logging


async def get_repo_stars_async(repo_url, username=None):
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
    if username:
        headers["Authorization"] = f"token {username}"

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                repo_data = await response.json()
                return repo_data["stargazers_count"]
            else:
                response.raise_for_status()


async def get_star_counts(urls):
    results = {}
    for url in urls:
        results[url] = await get_repo_stars_async(url)
    return results


def get_star_counts_sync(urls):
    """
    Get the number of stars for a list of GitHub repositories.

    >>> urls = ["https://github.com/openai/triton", "https://github.com/openai/gpt-3"]
    >>> star_counts = get_star_counts_sync(urls)
    >>> print(star_counts) # doctest: +ELLIPSIS
    {'https://github.com/openai/triton': ..., 'https://github.com/openai/gpt-3': ...}
    (...) represent the current number of stars for each repository.
    """
    return asyncio.run(get_star_counts(urls))


