import hmac
import hashlib
import json
import requests

secret = "mySuperSecretToken"

body = {
    "ref": "refs/heads/main",
    "repository": {"full_name": "username/example-repo"},
    "pusher": {"name": "tri-susilo"},
    "commits": [
        {"id": "abc1234", "message": "fix bug login", "url": "https://github.com/username/example-repo/commit/abc1234", "timestamp": "2025-07-06T07:00:00Z"},
        {"id": "def5678", "message": "add telegram notif", "url": "https://github.com/username/example-repo/commit/def5678", "timestamp": "2025-07-06T07:05:00Z"}
    ]
}

# Compact JSON
payload_json = json.dumps(body, separators=(',', ':'), sort_keys=True)
payload_bytes = payload_json.encode()

# Generate Signature
signature = hmac.new(secret.encode(), msg=payload_bytes, digestmod=hashlib.sha256).hexdigest()

print(f"Signature: sha256={signature}")

# Kirim request ke FastAPI
headers = {
    "Content-Type": "application/json",
    "X-GitHub-Event": "push",
    "X-Hub-Signature-256": f"sha256={signature}"
}

response = requests.post("http://localhost:8000/github-webhook", headers=headers, data=payload_json)

print(response.status_code)
print(response.text)

#test