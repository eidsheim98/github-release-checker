import requests
import os
import json
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Config
CACHE_FILE = "release_cache.json"
API_URL = "https://api.github.com"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Load GitHub token
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("Please set the GITHUB_TOKEN environment variable.")
if not WEBHOOK_URL:
    raise ValueError("Please set the WEBHOOK_URL environment variable.")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_starred_repositories():
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
    url = f"{API_URL}/repos/{owner}/{repo}/releases/latest"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 404:
        return None
    elif response.status_code != 200:
        raise Exception(f"Failed to get release for {owner}/{repo}: {response.status_code} {response.text}")
    return response.json()

def send_webhook(message, url):
    """Send updates to the webhook as JSON."""
    payload = {
        "title": "📢 GitHub Starred Repo Updates",
        "message": message,
        "url": url
    }
    try:
        r = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        if r.status_code not in (200, 204):
            print(f"⚠️ Webhook returned status {r.status_code}: {r.text}")
        else:
            print("✅ Webhook sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send webhook: {e}")

def check_updates():
    cache = load_cache()
    starred_repos = get_starred_repositories()
    print(f"Found {len(starred_repos)} starred repositories.\n")

    updated_cache = {}
    updates = []

    for repo in starred_repos:
        owner = repo["owner"]["login"]
        name = repo["name"]
        full_name = f"{owner}/{name}"

        release = get_latest_release(owner, name)
        if release:
            tag_name = release["tag_name"]
            published_at = release["published_at"]

            if full_name in cache:
                if cache[full_name] != tag_name:
                    print(f"🔔 Update available for {full_name}: {cache[full_name]} → {tag_name}")
                    updates.append({
                        "name": full_name,
                        "old_version": cache[full_name],
                        "new_version": tag_name,
                        "published_at": published_at,
                        "url": release["html_url"]
                    })
                else:
                    print(f"{full_name} is up to date ({tag_name})")
            else:
                print(f"📌 Tracking new repo {full_name} with version {tag_name}")

            updated_cache[full_name] = tag_name
        else:
            print(f"{full_name} → No releases found.")
            if full_name in cache:
                updated_cache[full_name] = cache[full_name]

    # Save updated cache
    save_cache(updated_cache)

    # Send webhook only if there are updates
    if updates:
        for update in updates:
            message = update["name"] + " has a new release"
            send_webhook(message, update["url"])
    else:
        print("No updates found.")

if __name__ == "__main__":
    check_updates()
