from utils.telegram import send_telegram_message

async def handle_push(payload):
    repo = payload.get("repository", {}).get("full_name", "Unknown Repo")
    pusher = payload.get("pusher", {}).get("name", "Unknown User")
    commits = payload.get("commits", [])
    branch = payload.get("ref", "").split("/")[-1] or "unknown-branch"
    
    commit_count = len(commits)
    commit_messages = "\n".join([
        f"- [`{c.get('id', '')[:7]}`]({c.get('url', '')}) {c.get('message', '').strip()}"
        for c in commits
    ]) or "- Tidak ada commit terdeteksi"

    push_time = ""
    if commits:
        push_time = commits[-1].get("timestamp", "").replace("T", " ").replace("Z", " UTC")

    message = (
        f"🚀 *Push to* `{repo}`\n"
        f"🔀 *Branch:* `{branch}`\n"
        f"👤 By: *{pusher}*\n"
    )
    if push_time:
        message += f"🕒 *Time:* {push_time}\n"

    message += (
        f"\n*Total Commit:* {commit_count}\n\n"
        f"🔧 Commit Details:\n"
        f"{commit_messages}"
    )

    await send_telegram_message(message)
