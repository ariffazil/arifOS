import os
import time
import requests
import json
from datetime import datetime, timezone

TOKEN = os.getenv('NOTIFIER_TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('NOTIFIER_TELEGRAM_CHAT_ID')
VAULT_URL = os.getenv('VAULT_URL', 'http://vault999:8100/seals')

def send_telegram(text):
    if not TOKEN or not CHAT_ID:
        print('[Notifier] Telegram not configured.')
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        payload = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "Markdown"
        }
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[Notifier] Telegram Error: {e}")

def monitor_vault():
    print(f"[Notifier] Starting monitor for {VAULT_URL}")
    last_seal_id = None
    while True:
        try:
            r = requests.get(f"{VAULT_URL}?limit=1", timeout=5)
            if r.status_code == 200:
                data = r.json()
                records = data.get('records', [])
                if records:
                    latest = records[0]
                    if last_seal_id is None:
                        last_seal_id = latest['id']
                    elif latest['id'] != last_seal_id:
                        last_seal_id = latest['id']
                        msg = f"🔔 *arifOS SEAL DETECTED*\n\n"
                        msg += f"*Action:* `{latest['action']}`\n"
                        msg += f"*Verdict:* `{latest['verdict']}`\n"
                        msg += f"*Hash:* `{latest['seal_hash'][:16]}...`"
                        send_telegram(msg)
        except Exception as e:
            print(f"[Notifier] Monitor Error: {e}")
        time.sleep(15)

if __name__ == '__main__':
    send_telegram("🚀 *arifOS Notifier Active* — Sovereignty voice restored.")
    monitor_vault()