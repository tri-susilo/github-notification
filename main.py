from fastapi import FastAPI, Request, Header
from dotenv import load_dotenv
import httpx
import os

load_dotenv(override=True)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_THREAD_ID = int(os.getenv("TELEGRAM_THREAD_ID", 0)) 

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

app = FastAPI()

async def send_telegram_message(text: str):
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "message_thread_id": TELEGRAM_THREAD_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(TELEGRAM_API_URL, json=payload)
            print("Telegram Status:", response.status_code)
            print("Telegram Response:", response.text)
        except Exception as e:
            print("Telegram Error:", str(e))

@app.post("/github-webhook")
async def github_webhook(request: Request, x_github_event: str = Header(None)):
    payload = await request.json()

    if x_github_event == "push":
        repo = payload["repository"]["full_name"]
        pusher = payload["pusher"]["name"]
        commits = payload.get("commits", [])
        commit_messages = "\n".join([f"- [{c['id'][:7]}]({c['url']}) {c['message']}" for c in commits])
        message = f"?? *Push Event* on `{repo}` by *{pusher}*\n{commit_messages}"
        await send_telegram_message(message)

    elif x_github_event == "pull_request":
        pr = payload["pull_request"]
        action = payload["action"]
        repo = payload["repository"]["full_name"]
        message = (
            f"?? *PR {action.capitalize()}* in `{repo}`\n"
            f"*#{pr['number']} {pr['title']}*\n"
            f"?? {pr['html_url']}"
        )
        await send_telegram_message(message)

    elif x_github_event == "issues":
        issue = payload["issue"]
        action = payload["action"]
        repo = payload["repository"]["full_name"]
        message = (
            f"?? *Issue {action.capitalize()}* in `{repo}`\n"
            f"*#{issue['number']} {issue['title']}*\n"
            f"?? {issue['html_url']}"
        )
        await send_telegram_message(message)

    elif x_github_event == "deployment":
        repo = payload["repository"]["full_name"]
        environment = payload["deployment"].get("environment", "unknown")
        creator = payload["deployment"]["creator"]["login"]
        message = (
            f"?? *Deployment Started* in `{repo}`\n"
            f"?? Environment: `{environment}`\n"
            f"?? By: {creator}"
        )
        await send_telegram_message(message)

    else:
        # Optional: log unhandled events
        await send_telegram_message(f"?? Unhandled event `{x_github_event}` received.")

    return {"status": "ok"}
