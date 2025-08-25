# Github Release Checker

This simple project runs a check to see if a starred Github repository has had a new release in the time since the script was last run.
The system will emit a HTTP POST call to a webhook that can be specified. The payload is in the following JSON form:

```json
{
    "title": "📢 GitHub Starred Repo Updates",
    "message": "'Repository Name' has a new release",
    "url": "Changelog URL"
}
```

## Prerequisites

### Install required packages
```bash
pip install -r requirements.txt
```

### Get the environment ready
1. Copy the ```.env.example``` file and name it ```.env```
2. Log into your Github account
3. Go to Settings - Developer Settings - Personal Access Tokens - Fine Grained Tokens
4. Create a new token and add it to the .env file
5. Add your webhook URL to the .env file

## Run
```bash
python main.py
```