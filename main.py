from fastapi import FastAPI, Request
import requests

app = FastAPI()

DISCORD_WEBHOOK = 'https://discord.com/api/webhooks/1412808374713581578/Bd6HgJsex1RqlLM-G8S18S15hEtanFZjhLAW6uEeuyuH7VxRGhvryHM9_3nDOO_TO-i1'

@app.post("/github-webhook")
async def github_webhook(request: Request):
    event = request.headers.get("X-GitHub-Event")
    payload = await request.json()

    if event == "push":
        repo = payload.get("repository", {}).get("name")
        branch = payload.get("ref", "").split("/")[-1]
        pusher = payload.get("pusher", {}).get("name")
        commits = payload.get("commits", [])

        message = f'📌 **{pusher}** pushed to **{repo}/{branch}**\n'

        for commit in commits:
            msg = commit.get("message")
            sha = commit.get("id")[:7]
            url = commit.get("url")
            message += f'- [{sha}] {msg} ({url})\n'

        requests.post(DISCORD_WEBHOOK, json={"content": message})

    elif event == "create":
        repo = payload.get("repository", {}).get("name")
        ref_type = payload.get("ref_type")
        ref = payload.get("ref")
        sender = payload.get("sender", {}).get("login")

        message = f'✨ **{sender}** created a new {ref_type}: **{ref}** in {repo}'
        requests.post(DISCORD_WEBHOOK, json={"content": message})

    return {"status": "ok"}
