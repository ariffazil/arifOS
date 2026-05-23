#!/usr/bin/env python3
"""
arifOS Webhook Deploy Server
DITEMPA BUKAN DIBERI
"""

import os
import time
import hashlib
import hmac
import json
import threading
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import JSONResponse

# ── CONFIG ────────────────────────────────────────────────────────────
app = FastAPI(title="arifOS Webhook Deploy", version="2026.05.11")
ARIFOS_WEBHOOK_SECRET = os.environ.get("ARIFOS_WEBHOOK_SECRET", "")
ARIFOS_DEPLOY_SCRIPT = os.environ.get(
    "ARIFOS_DEPLOY_SCRIPT", "/root/arifOS/scripts/deploy_arifosmcp.sh"
)
ARIFOS_URL = os.environ.get("ARIFOS_URL", "http://127.0.0.1:8080")
VAULT999_URL = os.environ.get("VAULT999_URL", "http://127.0.0.1:8100")
RATE_LIMIT = {}
RATE_LIMIT_LOCK = threading.Lock()
START_TIME = time.time()


def verify_sig(body: bytes, sig: str, secret: str) -> bool:
    if not sig or not secret:
        return False
    expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig)


def rate_check(ip: str) -> bool:
    with RATE_LIMIT_LOCK:
        now = time.time()
        RATE_LIMIT.setdefault(ip, []).append(now)
        RATE_LIMIT[ip] = [t for t in RATE_LIMIT[ip] if now - t < 300]
        return len(RATE_LIMIT[ip]) <= 10


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "arifOS-webhook-deploy",
        "version": "2026.05.11",
        "last_deploy": None,
    }


@app.get("/status")
async def status():
    return {
        "service": "arifOS-webhook-deploy",
        "uptime": int(time.time() - START_TIME),
        "endpoints": ["/webhook/forge", "/webhook/github", "/health", "/status"],
    }


@app.post("/webhook/forge")
async def webhook_forge(request: Request, x_arifos_signature: str = Header(None)):
    """A-FORGE primary webhook receiver."""
    body = await request.body()
    ip = request.client.host if request.client else "unknown"

    if not ARIFOS_WEBHOOK_SECRET:
        raise HTTPException(500, "Webhook secret not configured")
    if not verify_sig(body, x_arifos_signature or "", ARIFOS_WEBHOOK_SECRET):
        return JSONResponse({"verdict": "VOID", "reason": "Invalid signature"}, status_code=403)
    if not rate_check(ip):
        return JSONResponse({"verdict": "HOLD", "reason": "Rate limited"}, status_code=429)

    try:
        payload = json.loads(body)
    except:
        payload = {}

    return {
        "verdict": "HOLD",
        "tool": "webhook_forge",
        "source": payload.get("source", "unknown"),
        "actor": payload.get("actor", "external"),
        "telemetry_score": 0.53,
        "vault_sealed": False,
        "message": "forge endpoint reached successfully",
    }


@app.post("/webhook/github")
async def github_webhook(request: Request, x_hub_signature_256: str = Header(None)):
    """GitHub webhook receiver."""
    body = await request.body()
    ip = request.client.host if request.client else "unknown"

    if not ARIFOS_WEBHOOK_SECRET:
        raise HTTPException(500, "Webhook secret not configured")
    if not verify_sig(body, x_hub_signature_256 or "", ARIFOS_WEBHOOK_SECRET):
        return JSONResponse({"verdict": "VOID", "reason": "Invalid signature"}, status_code=403)
    if not rate_check(ip):
        return JSONResponse({"verdict": "HOLD", "reason": "Rate limited"}, status_code=429)

    try:
        payload = json.loads(body)
    except:
        payload = {}

    event = request.headers.get("X-GitHub-Event", "unknown")
    delivery = request.headers.get("X-GitHub-Delivery", "unknown")
    repo = payload.get("repository", {}).get("full_name", "")
    branch = payload.get("ref", "").replace("refs/heads/", "")
    commit = payload.get("after", "")[:12]

    return {
        "status": "received",
        "event": event,
        "delivery": delivery,
        "repo": repo,
        "branch": branch,
        "commit": commit,
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("WEBHOOK_PORT", 8443))
    print(f"arifOS Webhook Deploy Server starting on port {port}")
    print(f"  Secret configured: {bool(ARIFOS_WEBHOOK_SECRET)}")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
