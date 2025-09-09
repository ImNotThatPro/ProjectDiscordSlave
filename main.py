from fastapi import FastAPI, Request
import requests, os
import time 
app = FastAPI()

# --- Config ---
REPO_OWNER = "ImNotThatPro"     # 🔥 change this
REPO_NAME = "ProjectAIAudiobook"          # 🔥 change this
WEBHOOK_ID = 568654264           # from X-GitHub-Hook-ID header
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN_DISCORD_SLAVE_NGROK_AUTO_FETCH")

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1412808374713581578/Bd6HgJsex1RqlLM-G8S18S15hEtanFZjhLAW6uEeuyuH7VxRGhvryHM9_3nDOO_TO-i1"  # your existing one


def get_ngrok_url():
    try:
        tunnels = requests.get("http://127.0.0.1:4040/api/tunnels").json()
        for tunnel in tunnels["tunnels"]:
            if tunnel["proto"] == "https":
                return tunnel["public_url"]
    except Exception as e:
        print("❌ Failed to fetch ngrok URL:", e)
    return None


def update_github_webhook():
    ngrok_url = get_ngrok_url()
    if not ngrok_url: 
        print('NO ngrok url found ')
        return false 
    if not ngrok_url:
        print("⚠️ No ngrok URL found")
        return

    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/hooks/{WEBHOOK_ID}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    print("Loaded token?", bool(GITHUB_TOKEN))
    data = {
        "config": {
            "url": f"{ngrok_url}/github-webhook",
            "content_type": "json"
        }
    }

    r = requests.patch(api_url, json=data, headers=headers)
    if r.status_code == 200:
        print(f"✅ Webhook updated to {ngrok_url}/github-webhook")
    else:
        print(f"❌ Failed to update webhook: {r.status_code}", r.text)

@app.on_event("startup")
def startup_event():
    for i in range(5):
        if update_github_webhook():
            break
        time.sleep(2)

# --- Your existing webhook handler ---
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

#curl -X POST -H "Content-Type: application/json" \
#-d '{"content":"Hello from test"}' \
#<YOUR_DISCORD_WEBHOOK_URL>
