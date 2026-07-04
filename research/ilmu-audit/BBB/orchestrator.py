#!/usr/bin/env python3
"""
BBB Red Team Orchestrator
=========================
Sovereign: Muhammad Arif bin Fazil (F13 SOVEREIGN)
Mission: Full codebreaker red team of ILMU API (YTL AI Labs).
All raw requests/responses captured to /root/BBB/raw/transcripts.json
Methodology reference: aisingapore/sea-guard
"""

import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import urllib.request
import urllib.error

# Load ILMU credentials
ILMU_BASE = os.environ.get("ILMU_BASE_URL", "https://api.ilmu.ai/v1")
ILMU_KEY = os.environ.get("ILMU_API_KEY")
if not ILMU_KEY:
    print("FATAL: ILMU_API_KEY not in env", file=sys.stderr)
    sys.exit(1)

OUT_DIR = Path("/root/BBB")
RAW_DIR = OUT_DIR / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Single growing transcript log (so partial runs survive crashes)
LOG_PATH = RAW_DIR / "transcripts.jsonl"


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def call_ilmu(
    model: str,
    messages: list,
    *,
    max_tokens: int = 800,
    temperature: float = 0.0,
    timeout: int = 60,
) -> dict:
    """Call ILMU chat completions, return full receipt dict."""
    url = f"{ILMU_BASE}/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    req = urllib.request.Request(  # type: ignore[arg-type]
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {ILMU_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read().decode("utf-8", errors="replace")
    except Exception as e:
        status = -1
        body = f"EXCEPTION: {type(e).__name__}: {e}"
    t1 = time.time()
    receipt = {
        "ts": now_iso(),
        "ts_unix": int(time.time()),
        "model": model,
        "endpoint": "/chat/completions",
        "request": payload,
        "status": status,
        "latency_ms": int((t1 - t0) * 1000),
        "raw_response": body,
    }
    # Parse JSON if possible
    try:
        parsed: dict = json.loads(body)
        receipt["parsed"] = parsed
        if "choices" in parsed and parsed["choices"]:
            choice = parsed["choices"][0]
            if "message" in choice:
                receipt["assistant_content"] = choice["message"].get("content", "")
            receipt["finish_reason"] = choice.get("finish_reason")
        receipt["usage"] = parsed.get("usage")
    except Exception:
        pass
    return receipt


def log(receipt: dict):
    """Append a single receipt to the JSONL log."""
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(receipt, ensure_ascii=False) + "\n")


def probe(
    phase: str,
    probe_id: str,
    model: str,
    prompt: str,
    *,
    system: str = None,
    max_tokens: int = 800,
    temperature: float = 0.0,
) -> dict:
    """Run a single probe and log the receipt. Returns the receipt."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    receipt = call_ilmu(model, messages, max_tokens=max_tokens, temperature=temperature)
    receipt["phase"] = phase
    receipt["probe_id"] = probe_id
    log(receipt)
    # Console summary
    content = receipt.get("assistant_content", receipt.get("raw_response", "")[:200])
    print(
        f"  [{phase}/{probe_id}] {model} status={receipt['status']} "
        f"latency={receipt['latency_ms']}ms"
    )
    print(f"    → {content[:300]}")
    return receipt


if __name__ == "__main__":
    # Test that import works
    print(f"ILMU base: {ILMU_BASE}")
    print(f"ILMU key: {ILMU_KEY[:10]}...{ILMU_KEY[-4:]}")
    print(f"Log: {LOG_PATH}")
