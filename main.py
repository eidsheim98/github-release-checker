import requests
import os
import json
from datetime import datetime

# Config
CACHE_FILE = "release_cache.json"
API_URL = "https://api.github.com"

# Load GitHub token from environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("Please set the GITHUB_TOKEN environment variable.")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def load_cache():
    """Load cached release data from a file."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(data):
    """Save release data to a file."""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_starred_repositories():
    """Fetch all starred repositories for the authenticated user."""
    repos = []
    page = 1

    while True:
        response = requests.get(f"{API_URL}/user/starred", headers=HEADERS, params={"per_page": 100, "page": page})
        if response.status_code != 200:
            raise Exception(f"Failed to get starred repos: {response.status_code} {response.text}")

        data = response.json()
        if not data:
            break

        repos.extend(data)
        page += 1

    return repos

def get_latest_release(owner, repo):
    """Fetch the latest release for a repository."""
    url = f"{API_URL}/repos/{owner}/{repo}/releases/latest"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 404:
        return None  # No releases for this repo
    elif response.status_code != 200:
        raise Exception(f"Failed to get release for {owner}/{repo}: {response.status_code} {response.text}")

    return response.json()

def main():
    cache = load_cache()
    starred_repos = get_starred_repositories()
    print(f"Found {len(starred_repos)} starred repositories.\n")

    updated_cache = {}
    for repo in starred_repos:
        owner = repo["owner"]["login"]
        name = repo["name"]
        full_name = f"{owner}/{name}"

        release = get_latest_release(owner, name)

        if release:
            tag_name = release["tag_name"]
            published_at = release["published_at"]

            # Compare with cache
            if full_name in cache:
                if cache[full_name] != tag_name:
                    print(f"🔔 Update available for {full_name}: {cache[full_name]} → {tag_name}")
                else:
                    print(f"{full_name} is up to date ({tag_name})")
            else:
                print(f"📌 Tracking new repo {full_name} with version {tag_name}")

            updated_cache[full_name] = tag_name
        else:
            print(f"{full_name} → No releases found.")
            # Keep previous entry if no releases
            if full_name in cache:
                updated_cache[full_name] = cache[full_name]

    save_cache(updated_cache)
    print("\n✅ Cache updated.")

if __name__ == "__main__":
    main()
