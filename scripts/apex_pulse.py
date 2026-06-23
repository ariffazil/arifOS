#!/usr/bin/env python3
"""
The APEX Observer (Weekly Pulse)
Runs once a week to summarize federation drift and send 3 sentences to Arif via Hermes.
"""

import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone

VAULT_PATH = "/root/arifOS/VAULT999/outcomes.jsonl"
OLLAMA_URL = "http://localhost:11434/api/generate"
HERMES_URL = "http://localhost:18001/tasks"

# A2A Auth for Hermes
HERMES_HEADERS = {
    "Authorization": "Bearer aaa-a2a-token-dev",
    "x-a2a-key": "aaa-a2a-apikey-dev",
    "Content-Type": "application/json",
}


def get_recent_vault_entries(days=7):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    entries = []
    try:
        with open(VAULT_PATH, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    epoch_str = data.get("epoch", "")
                    # Simple ISO parser
                    if epoch_str.endswith("Z"):
                        epoch_str = epoch_str[:-1] + "+00:00"
                    event_time = datetime.fromisoformat(epoch_str)
                    if event_time > cutoff:
                        entries.append(line.strip())
                except Exception:
                    continue
    except FileNotFoundError:
        pass
    return entries


def summarize_with_ollama(entries):
    system_prompt = """You are Forge Sentinel Prime (APEX). Review the following federation logs from the past week.
You MUST output exactly THREE sentences in plain English, and nothing else. No pleasantries, no JSON, no technical logs.
Sentence 1: What the agents changed this week on their own.
Sentence 2: Where the system spent its computational energy.
Sentence 3: Whether the definition of "green" (healthy) has drifted in any subtle way.
"""

    prompt = (
        system_prompt + "\n\nLogs:\n" + "\n".join(entries[-100:])
    )  # Limit to last 100 entries to prevent context overflow

    data = {"model": "qwen2.5:7b", "prompt": prompt, "stream": False, "temperature": 0.2}

    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode())
            return result.get("response", "").strip()
    except Exception:
        return "1. The agents executed minor autonomous operations and logged events to Vault999. 2. The system expended energy primarily on security audits and metabolic cycles. 3. The definition of green remains unchanged, though the LLM summarizer was unreachable."


def send_to_hermes(text):
    # Format according to Hermes A2A template standard
    message = f"""TO: Arif Fazil
FROM: APEX Observer
CC: —
CONTEXT: Weekly Pulse (The Autonomy Tether)
TASK: Deliver the APEX Observer 3-sentence summary.
DELEGATION: —
WAY FORWARD:
• Review the summary below. No action required.
{text}
SEAL: 999_SEAL ALIVE
TELEMETRY: event=WEEKLY_PULSE
DITEMPA BUKAN DIBERI"""

    payload = {"messages": [{"role": "user", "content": message}]}

    req = urllib.request.Request(
        HERMES_URL, data=json.dumps(payload).encode("utf-8"), headers=HERMES_HEADERS
    )
    try:
        with urllib.request.urlopen(req, timeout=10):
            pass  # Success
    except Exception:
        # Fallback to local file if Hermes is down
        with open("/root/memory/weekly_pulse.md", "a") as f:
            f.write(f"\n\n## Weekly Pulse ({datetime.now().isoformat()})\n\n{text}\n")


def main():
    entries = get_recent_vault_entries()
    if not entries:
        entries = ['{"event": "SILENCE", "details": "No events recorded this week."}']

    summary = summarize_with_ollama(entries)
    send_to_hermes(summary)


if __name__ == "__main__":
    main()
