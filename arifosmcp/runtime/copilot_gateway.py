"""
arifosmcp/runtime/copilot_gateway.py — Copilot Governance Relay Gateway
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# CONFIG
ARIFOS_COPILOT_API_KEY = os.environ.get("ARIFOS_COPILOT_API_KEY", "")
ARIFOS_COPILOT_API_KEY_FILE = os.environ.get(
    "ARIFOS_COPILOT_API_KEY_FILE", "/run/secrets/arifos_copilot_api_key"
)
ARIFOS_VAULT_PATH = os.environ.get("ARIFOS_VAULT_PATH", "/var/lib/arifos/volumes/vault999")
ARIFOS_JUDGE_URL = os.environ.get("ARIFOS_JUDGE_URL", "http://arifosmcp:8080")
RATE_LIMIT_WINDOW = int(os.environ.get("ARIFOS_COPILOT_RL_WINDOW", "300"))
RATE_LIMIT_MAX = int(os.environ.get("ARIFOS_COPILOT_RL_MAX", "20"))


def _load_api_key() -> str:
    key = ARIFOS_COPILOT_API_KEY
    if key:
        return key
    try:
        p = Path(ARIFOS_COPILOT_API_KEY_FILE)
        if p.exists():
            return p.read_text().strip()
    except Exception:
        pass
    return ""


# RATE LIMITING
_rate_limit_buckets: dict[str, list[float]] = {}


def _check_rate_limit(client_key: str) -> tuple[bool, dict[str, Any]]:
    now = time.time()
    bucket = _rate_limit_buckets.get(client_key, [])
    bucket = [t for t in bucket if (now - t) < RATE_LIMIT_WINDOW]
    _rate_limit_buckets[client_key] = bucket
    if len(bucket) >= RATE_LIMIT_MAX:
        oldest = bucket[0] if bucket else now
        reset_in = int(RATE_LIMIT_WINDOW - (now - oldest))
        return False, {"limit": RATE_LIMIT_MAX, "remaining": 0, "reset_in": reset_in}
    bucket.append(now)
    return True, {
        "limit": RATE_LIMIT_MAX,
        "remaining": RATE_LIMIT_MAX - len(bucket),
        "reset_in": RATE_LIMIT_WINDOW,
    }


# PYDANTIC SCHEMAS
class CopilotIngestRequest(BaseModel):
    session_id: str
    actor_id: str = "ARIF"
    copilot_output: str
    trigger: str = "MANUAL"
    metadata: dict[str, Any] = Field(default_factory=dict)


class CopilotIngestResponse(BaseModel):
    session_id: str
    verdict: str
    floors_triggered: list[str] = Field(default_factory=list)
    reason: str
    confidence: float = Field(ge=0.0, le=1.0)
    audit_id: str
    blocked: bool
    copilot_payload_echo: dict[str, Any]
    judge_engine: str
    trace_id: str


# CANONICALISATION + HASHING
def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _canonical_hash(req: dict, resp: dict) -> str:
    return _sha256_hex(_canonical_json(req) + "|" + _canonical_json(resp))


# HOLD DETECTION
_HOLD_PATTERNS = [
    re.compile(r"status\s*[:\-]?\s*PAUSE", re.IGNORECASE),
    re.compile(r"status\s*[:\-]?\s*HOLD", re.IGNORECASE),
    re.compile(r"\bUNKNOWN\b", re.IGNORECASE),
    re.compile(r"insufficient evidence", re.IGNORECASE),
    re.compile(r"irreversible", re.IGNORECASE),
    re.compile(r"high.?impact", re.IGNORECASE),
    re.compile(r"888_?HOLD", re.IGNORECASE),
    re.compile(r"escalat", re.IGNORECASE),
    re.compile(r"do not proceed", re.IGNORECASE),
    re.compile(r"verdict\s*[:\-]?\s*HOLD", re.IGNORECASE),
    re.compile(r"verdict\s*[:\-]?\s*VOID", re.IGNORECASE),
]


def _detect_hold(text: str) -> tuple[bool, list[str]]:
    matched = [p.pattern for p in _HOLD_PATTERNS if p.search(text)]
    return bool(matched), matched


# MVP RULE ENGINE
def _mvp_rule_engine(
    copilot_output: str, session_id: str, actor_id: str
) -> tuple[str, list[str], str, float]:
    hold_detected, matched = _detect_hold(copilot_output)

    if any(
        k in copilot_output.lower()
        for k in ["irreversible", "delete", "drop table", "rm -rf", "destroy"]
        if " " in k or re.search(rf"\b{re.escape(k)}\b", copilot_output, re.IGNORECASE)
    ):
        return (
            "HOLD",
            ["F1"],
            "F1 AMANAH: Irreversible action signal — requires explicit sovereign consent",
            0.85,
        )

    _consciousness_patterns = [
        re.compile(r"\bi am\b", re.IGNORECASE),
        re.compile(r"\bi'm\b", re.IGNORECASE),
        re.compile(r"\bi think\b", re.IGNORECASE),
        re.compile(r"\bas an ai\b", re.IGNORECASE),
    ]
    _consciousness_found = any(p.search(copilot_output) for p in _consciousness_patterns)
    if _consciousness_found:
        if not re.search(r"\b(evidence|source|cited)\s*:", copilot_output, re.IGNORECASE):
            return (
                "VOID",
                ["F2"],
                "F2 TRUTH: Consciousness/self-reference claim without evidence discipline",
                0.90,
            )

    if hold_detected:
        if re.search(r"verdict\s*[:\-]?\s*VOID", copilot_output, re.IGNORECASE):
            return (
                "VOID",
                ["F2", "F7"],
                f"F2+F7: Copilot flagged VOID — {matched[0] if matched else 'unknown'}",
                0.92,
            )
        return (
            "HOLD",
            ["F7"],
            f"F7 HUMILITY: Copilot signaled uncertainty — {matched[0] if matched else 'UNKNOWN'}",
            0.88,
        )

    return (
        "PARTIAL",
        [],
        "MVP_RULE_ENGINE: Basic checks passed. Full 13-floor requires arifOS 888_JUDGE.",
        0.70,
    )


# JUDGE AVAILABILITY
_JUDGE_AVAILABLE: bool = False
_JUDGE_CHECKED: bool = False


def _is_judge_available() -> bool:
    global _JUDGE_AVAILABLE, _JUDGE_CHECKED
    if _JUDGE_CHECKED:
        return _JUDGE_AVAILABLE
    _JUDGE_CHECKED = True
    try:
        import urllib.request

        url = f"{ARIFOS_JUDGE_URL}/health"
        with urllib.request.urlopen(url, timeout=3) as resp:
            _JUDGE_AVAILABLE = resp.status == 200
    except Exception:
        _JUDGE_AVAILABLE = False
    return _JUDGE_AVAILABLE


def _call_arif_judge(
    copilot_output: str, session_id: str, actor_id: str
) -> tuple[str, list[str], str, float]:
    if not _is_judge_available():
        return _mvp_rule_engine(copilot_output, session_id, actor_id)

    try:
        import urllib.error
        import urllib.request

        payload = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "arif_judge",
                "params": {
                    "mode": "judge",
                    "candidate": copilot_output[:2000],
                    "session_id": session_id,
                    "actor_id": actor_id,
                },
                "id": 1,
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            f"{ARIFOS_JUDGE_URL}/mcp",
            data=payload,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
        r = result.get("result", result)
        verdict = r.get("verdict", "HOLD")
        floors = r.get("floors_triggered", r.get("floor_compliance", []))
        reason = r.get("reason", r.get("rationale", "arifOS 888_JUDGE returned verdict"))
        confidence = float(r.get("confidence", r.get("epistemic_snapshot", {}).get("omega_0", 0.5)))
        return verdict, floors, reason, confidence
    except Exception as exc:
        logger.warning(
            "[copilot_gateway] arifOS judge call failed: %s — falling back to MVP rule engine", exc
        )
        return _mvp_rule_engine(copilot_output, session_id, actor_id)


# VAULT999 LEDGER
def _write_vault_ledger(**kwargs) -> dict:
    vault_dir = Path(ARIFOS_VAULT_PATH)
    ledger_path = vault_dir / "copilot_judgments.jsonl"
    vault_dir.mkdir(parents=True, exist_ok=True)

    record = {
        "ts": time.time(),
        "event_type": "copilot_judgment",
        "session_id": kwargs["session_id"],
        "actor_id": kwargs["actor_id"],
        "verdict": kwargs["verdict"],
        "floors_triggered": kwargs["floors_triggered"],
        "confidence": round(kwargs["confidence"], 4),
        "reason": kwargs["reason"],
        "audit_id": kwargs["audit_id"],
        "trace_id": kwargs["trace_id"],
        "judge_engine": kwargs["judge_engine"],
        "blocked": kwargs["blocked"],
        "output_length": len(kwargs["copilot_output"]),
        "output_hash": _sha256_hex(kwargs["copilot_output"])[:16],
    }

    try:
        with open(ledger_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
        logger.info(
            "[copilot_gateway] VAULT999 wrote audit_id=%s verdict=%s session=%s",
            kwargs["audit_id"],
            kwargs["verdict"],
            kwargs["session_id"],
        )
    except Exception as exc:
        logger.error("[copilot_gateway] VAULT999 write failed: %s", exc)
        record["vault_write_error"] = str(exc)

    return record


# FASTAPI APP
app = FastAPI(
    title="arifOS Copilot Governance Gateway", version="1.0.0", docs_url="/docs", redoc_url="/redoc"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def _request_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", uuid.uuid4().hex[:12])
    request.state.request_id = request_id
    logger.info(
        json.dumps(
            {
                "event": "request",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
            }
        )
    )
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


_API_KEY_CACHE: str = ""


def _get_cached_api_key() -> str:
    global _API_KEY_CACHE
    if not _API_KEY_CACHE:
        _API_KEY_CACHE = _load_api_key()
    return _API_KEY_CACHE


async def _verify_api_key(request: Request) -> bool:
    key = _get_cached_api_key()
    if not key:
        logger.warning("[copilot_gateway] No API key configured — gateway unprotected!")
        return True
    return request.headers.get("X-API-Key", "") == key


# ENDPOINTS
@app.get("/health")
async def health_check():
    vault_dir = Path(ARIFOS_VAULT_PATH)
    vault_ok = "ok"
    try:
        vault_dir.mkdir(parents=True, exist_ok=True)
        test_file = vault_dir / ".health_write_test"
        test_file.touch()
        test_file.unlink()
    except Exception as e:
        vault_ok = f"error: {e}"

    return JSONResponse(
        status_code=200 if vault_ok == "ok" else 503,
        content={
            "status": "healthy" if vault_ok == "ok" else "degraded",
            "service": "arifOS Copilot Gateway",
            "version": "1.0.0",
            "checks": {
                "rate_limiter": "ok",
                "vault_writable": vault_ok,
                "judge_available": (
                    "ok" if _is_judge_available() else "unavailable (MVP rule engine)"
                ),
            },
        },
    )


@app.post("/copilot/ingest", response_model=CopilotIngestResponse)
async def copilot_ingest(request: Request, body: CopilotIngestRequest):
    request_id = getattr(request.state, "request_id", uuid.uuid4().hex[:12])

    if not await _verify_api_key(request):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing X-API-Key"
        )

    client_key = request.client.host if request.client else "unknown"
    allowed, rl_meta = _check_rate_limit(client_key)
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={
                "session_id": body.session_id,
                "verdict": "VOID",
                "floors_triggered": ["F5"],
                "reason": f"F5 PEACE: Rate limit exceeded. Reset in {rl_meta['reset_in']}s",
                "confidence": 1.0,
                "audit_id": "",
                "blocked": True,
                "copilot_payload_echo": {"session_id": body.session_id},
                "judge_engine": "rate_limiter",
                "trace_id": request_id,
            },
            headers={"X-Request-ID": request_id, "Retry-After": str(rl_meta["reset_in"])},
        )

    hold_detected, matched_patterns = _detect_hold(body.copilot_output)

    if hold_detected:
        verdict, floors, reason, confidence = _call_arif_judge(
            body.copilot_output, body.session_id, body.actor_id
        )
        reason = f"[HOLD signal: {matched_patterns[0]}] {reason}"
        if verdict not in ("VOID", "HOLD"):
            verdict = "HOLD"
    else:
        verdict, floors, reason, confidence = _call_arif_judge(
            body.copilot_output, body.session_id, body.actor_id
        )

    req_dict = body.model_dump()
    resp_dict = {
        "verdict": verdict,
        "floors_triggered": floors,
        "reason": reason,
        "confidence": confidence,
    }
    audit_id = f"sha256:{_canonical_hash(req_dict, resp_dict)}"
    blocked = verdict in ("HOLD", "VOID")
    judge_engine = "arifOS_888_JUDGE" if _is_judge_available() else "MVP_RULE_ENGINE"

    _write_vault_ledger(
        session_id=body.session_id,
        actor_id=body.actor_id,
        copilot_output=body.copilot_output,
        verdict=verdict,
        floors_triggered=floors,
        reason=reason,
        confidence=confidence,
        audit_id=audit_id,
        trace_id=request_id,
        judge_engine=judge_engine,
        blocked=blocked,
    )

    return CopilotIngestResponse(
        session_id=body.session_id,
        verdict=verdict,
        floors_triggered=floors,
        reason=reason,
        confidence=confidence,
        audit_id=audit_id,
        blocked=blocked,
        copilot_payload_echo={
            "session_id": body.session_id,
            "actor_id": body.actor_id,
            "trigger": body.trigger,
            "output_length": len(body.copilot_output),
            "hold_signal_detected": hold_detected,
        },
        judge_engine=judge_engine,
        trace_id=request_id,
    )


@app.post("/arifos/judge", response_model=CopilotIngestResponse)
async def arifos_judge_alias(request: Request, body: CopilotIngestRequest):
    return await copilot_ingest(request, body)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8090, log_level="info")  # nosec: required for Docker container
