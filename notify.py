import os, requests

def notify_console(message: str):
    print("[ALERT]", message)

def notify_discord(message: str):
    url = os.getenv("DISCORD_WEBHOOK_URL")
    if not url:
        return
    try:
        requests.post(url, data={"content": message}, timeout=10)
    except Exception:
        pass
