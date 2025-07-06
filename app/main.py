import hmac
import hashlib
from fastapi import FastAPI, Request, Header, HTTPException
from dotenv import load_dotenv
import os
from app.events import push
from app.utils.telegram import send_telegram_message

load_dotenv(override=True)

app = FastAPI()

GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")


def verify_github_signature(secret, body: bytes, signature: str) -> bool:
    if not signature:
        return False
    try:
        sha_name, received_signature = signature.split("=")
    except ValueError:
        return False
    if sha_name != "sha256":
        return False

    mac = hmac.new(secret.encode(), msg=body, digestmod=hashlib.sha256)
    expected_signature = mac.hexdigest()

    return hmac.compare_digest(expected_signature, received_signature)



@app.post("/github-webhook")
async def github_webhook(request: Request, x_github_event: str = Header(None), x_hub_signature_256: str = Header(None)):
    body = await request.body()
    print("Body diterima:", body.decode())
    print("Signature header:", x_hub_signature_256)

    if not verify_github_signature(GITHUB_WEBHOOK_SECRET, body, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Invalid signature")

    # Parsing payload setelah verifikasi lolos
    try:
        payload = await request.json()
    except Exception:
        return {"status": "invalid json"}

    # Dispatch ke handler modular
    if x_github_event == "push":
        await push.handle_push(payload)
    elif x_github_event == "pull_request":
        await pr.handle_pr(payload)
    elif x_github_event == "issues":
        await issues.handle_issues(payload)
    elif x_github_event == "deployment":
        await deployment.handle_deployment(payload)
    else:
        await send_telegram_message(f"ℹ️ Unhandled event `{x_github_event}` received.")

    return {"status": "ok"}
