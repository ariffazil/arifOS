"""
arifosmcp/runtime/webhook_intake.py — Constitutional Webhook Intake Valve
═══════════════════════════════════════════════════════════════════════════════

Server-side signed webhook receiver for arifOS governance.
External reality enters the system through this single controlled doorway.

Axiom: Webhook triggers OBSERVE. arifOS performs JUDGE. VAULT999 records SEAL.
       Webhook received ≠ SEAL. Webhook verified ≠ SEAL.
       Webhook adjudicated + evidence + authority intact = SEAL.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import re
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from typing import Any

from core.enforcement.auth_continuity import verify_auth_context_with_revocation

from arifosmcp.runtime.integrity import REQUIRED_POLICY_VERSION

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

WEBHOOK_SECRET = os.environ.get("ARIFOS_WEBHOOK_SECRET", "")
WEBHOOK_MAX_AGE_SECONDS = int(os.environ.get("ARIFOS_WEBHOOK_MAX_AGE", "300"))
WEBHOOK_RATE_LIMIT_WINDOW = int(os.environ.get("ARIFOS_WEBHOOK_RL_WINDOW", "300"))
WEBHOOK_RATE_LIMIT_MAX = int(os.environ.get("ARIFOS_WEBHOOK_RL_MAX", "10"))
APPROVAL_MAX_AGE_SECONDS = int(os.environ.get("ARIFOS_APPROVAL_MAX_AGE", "300"))
APPROVAL_REQUIRED_AUTH_METHODS = {"passkey", "webauthn"}

# Source allowlist: source_name → required header signature scheme
SOURCE_REGISTRY: dict[str, dict[str, Any]] = {
    "github": {
        "sig_header": "x-hub-signature-256",
        "sig_prefix": "sha256=",
        "event_header": "x-github-event",
        "delivery_header": "x-github-delivery",
        "secret_env": "ARIFOS_WEBHOOK_SECRET_GITHUB",
        "schema": "github_webhook",
    },
    "grafana": {
        "sig_header": "x-grafana-signature",
        "sig_prefix": "",
        "event_header": "x-grafana-alert",
        "delivery_header": "x-grafana-id",
        "secret_env": "ARIFOS_WEBHOOK_SECRET_GRAFANA",
        "schema": "grafana_alert",
    },
    "manual": {
        "sig_header": "x-arifos-signature",
        "sig_prefix": "sha256=",
        "event_header": "x-arifos-event",
        "delivery_header": "x-arifos-id",
        "secret_env": "ARIFOS_WEBHOOK_SECRET_MANUAL",
        "schema": "manual_trigger",
    },
}

# Runtime replay protection (in-memory; VAULT999 is canonical)
_seen_event_ids: set[str] = set()
_rate_limit_buckets: dict[str, list[float]] = {}
_seen_approval_nonces: set[str] = set()
_trace_approval_bindings: dict[str, str] = {}
_vault_ledger_lock = RLock()

# ═══════════════════════════════════════════════════════════════════════════════
# SIGNATURE & AUTH
# ═══════════════════════════════════════════════════════════════════════════════


def _get_secret(source: str) -> str:
    """Resolve webhook secret for a source."""
    reg = SOURCE_REGISTRY.get(source, {})
    env_key = reg.get("secret_env", "ARIFOS_WEBHOOK_SECRET")
    return os.environ.get(env_key, WEBHOOK_SECRET)


def _get_policy_version() -> str:
    policy_version = os.environ.get("ARIFOS_POLICY_VERSION", "").strip()
    return policy_version or REQUIRED_POLICY_VERSION


def _canonical_payload_hash(payload: dict[str, Any]) -> str:
    governed_payload = {key: value for key, value in payload.items() if key != "approval_artifact"}
    canonical = json.dumps(
        governed_payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


def _derive_event_id(source: str, headers: dict[str, str], payload_bytes: bytes) -> str:
    """Derive a stable idempotency key for webhook processing."""
    reg = SOURCE_REGISTRY.get(source, {})
    delivery_header = reg.get("delivery_header", "x-delivery-id")
    explicit = (
        headers.get(delivery_header.lower())
        or headers.get(delivery_header)
        or headers.get("x-idempotency-key")
        or headers.get("x-request-id")
    )
    if explicit:
        return f"{source}:{explicit}"
    digest = hashlib.sha256(payload_bytes).hexdigest()
    return f"{source}:{digest[:24]}"


def _trace_id_for_event(event_id: str) -> str:
    trace_hash = hashlib.sha256(event_id.encode()).hexdigest()[:12]
    return f"wh-{trace_hash}"


def _required_approval_scope(
    trace_id: str,
    event_id: str,
    payload_hash: str,
    policy_version: str,
    requested_action: str,
    auth_method: str | None = None,
    key_id: str | None = None,
    authority_level: str | None = None,
) -> set[str]:
    scope = {
        f"trace:{trace_id}",
        f"event:{event_id}",
        f"hash:{payload_hash}",
        f"policy:{policy_version}",
        f"action:{requested_action}",
    }
    if auth_method:
        scope.add(f"auth:{auth_method}")
    if key_id:
        scope.add(f"key:{key_id}")
    if authority_level:
        scope.add(f"authority:{authority_level}")
    return scope


def _allowed_approval_key_ids() -> set[str]:
    current = os.environ.get("ARIFOS_APPROVAL_KEY_ID", "arifos-approval-primary").strip()
    previous = os.environ.get("ARIFOS_APPROVAL_KEY_ID_PREVIOUS", "").strip()
    return {key_id for key_id in (current, previous) if key_id}


def _revoked_approval_key_ids() -> set[str]:
    raw = os.environ.get("ARIFOS_APPROVAL_KEY_IDS_REVOKED", "")
    return {item.strip() for item in raw.split(",") if item.strip()}


def _vault_path() -> Path:
    return Path(os.environ.get("VAULT999_PATH", "/root/VAULT999/outcomes.jsonl"))


def verify_signature(
    payload_bytes: bytes,
    signature: str | None,
    source: str = "github",
) -> bool:
    """Validate HMAC-SHA256 webhook signature."""
    secret = _get_secret(source)
    if not secret or not signature:
        return False

    reg = SOURCE_REGISTRY.get(source, {})
    prefix = reg.get("sig_prefix", "sha256=")

    if prefix and not signature.startswith(prefix):
        return False

    sig_body = signature[len(prefix) :] if prefix else signature
    expected = hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig_body)


# ═══════════════════════════════════════════════════════════════════════════════
# REPLAY PROTECTION
# ═══════════════════════════════════════════════════════════════════════════════


def is_replay(event_id: str) -> bool:
    """Check if event_id has been seen. Thread-safe in single-process; scale with Redis."""
    if event_id in _seen_event_ids:
        return True
    # Bound memory usage — crude but effective for single-process
    if len(_seen_event_ids) > 100_000:
        _seen_event_ids.clear()
    _seen_event_ids.add(event_id)
    return False


def check_timestamp_freshness(timestamp_iso: str, max_age: int = WEBHOOK_MAX_AGE_SECONDS) -> bool:
    """Reject stale webhooks to prevent replay of old events."""
    try:
        ts = datetime.fromisoformat(timestamp_iso.replace("Z", "+00:00"))
        age = (datetime.now(UTC) - ts).total_seconds()
        return 0 <= age <= max_age
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# RATE LIMITING
# ═══════════════════════════════════════════════════════════════════════════════


def check_rate_limit(client_key: str) -> tuple[bool, dict[str, Any]]:
    """Token-bucket style rate limit per client. Returns (allowed, metadata)."""
    now = time.time()
    window = WEBHOOK_RATE_LIMIT_WINDOW
    max_req = WEBHOOK_RATE_LIMIT_MAX

    bucket = _rate_limit_buckets.get(client_key, [])
    bucket = [t for t in bucket if (now - t) < window]
    _rate_limit_buckets[client_key] = bucket

    if len(bucket) >= max_req:
        oldest = bucket[0] if bucket else now
        reset_in = int(window - (now - oldest))
        return False, {"limit": max_req, "remaining": 0, "reset_in": reset_in}

    bucket.append(now)
    return True, {"limit": max_req, "remaining": max_req - len(bucket), "reset_in": window}


def _extract_approval_artifact(
    headers: dict[str, str], payload: dict[str, Any]
) -> tuple[dict[str, Any] | None, list[str]]:
    """Read approval artifact from headers or payload without trusting it yet."""
    raw_header = headers.get("x-arifos-approval") or headers.get("x-approval-artifact")
    if raw_header:
        try:
            artifact = json.loads(raw_header)
        except json.JSONDecodeError:
            return None, ["F11 AUTH: Approval artifact header is not valid JSON"]
        if not isinstance(artifact, dict):
            return None, ["F11 AUTH: Approval artifact header must decode to an object"]
        return artifact, []

    raw_payload = payload.get("approval_artifact")
    if raw_payload is None:
        return None, []
    if not isinstance(raw_payload, dict):
        return None, ["F11 AUTH: approval_artifact must be an object"]
    return raw_payload, []


def _approval_summary(
    status: str,
    *,
    actor: str = "unknown",
    auth_method: str | None = None,
    key_id: str | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "actor": actor,
        "auth_method": auth_method,
        "key_id": key_id,
        "reason": reason,
    }


def verify_approval_artifact(
    artifact: dict[str, Any] | None,
    *,
    trace_id: str,
    event_id: str,
    payload_hash: str,
    policy_version: str,
    requested_action: str,
) -> tuple[bool, dict[str, Any], list[str]]:
    """Verify a fresh, exact-bound human approval artifact for consequential actions."""
    if artifact is None:
        return False, _approval_summary("missing", reason="approval artifact missing"), []

    actor = _sanitize_actor(artifact.get("actor_id"))
    auth_method = str(artifact.get("auth_method", "")).strip().lower()
    key_id = str(artifact.get("key_id", "")).strip()
    authority_level = str(artifact.get("authority_level", "")).strip().lower()
    nonce = str(artifact.get("nonce", "")).strip()
    session_id = str(artifact.get("session_id", "")).strip()

    issues: list[str] = []

    if auth_method not in APPROVAL_REQUIRED_AUTH_METHODS:
        issues.append(
            "F11 AUTH: Approval artifact must use passkey or WebAuthn step-up authentication"
        )

    allowed_key_ids = _allowed_approval_key_ids()
    revoked_key_ids = _revoked_approval_key_ids()
    if not key_id:
        issues.append("F11 AUTH: Approval artifact missing key_id")
    elif key_id in revoked_key_ids:
        issues.append(f"F11 AUTH: Approval key '{key_id}' is revoked")
    elif key_id not in allowed_key_ids:
        issues.append(f"F11 AUTH: Approval key '{key_id}' is not active")

    if authority_level in {"", "anonymous"}:
        issues.append("F13 SOVEREIGNTY: Approval artifact lacks non-anonymous authority")

    if not nonce:
        issues.append("F12 INJECTION: Approval artifact missing nonce")
    elif nonce in _seen_approval_nonces:
        issues.append("F12 INJECTION: Approval nonce already used")

    if trace_id in _trace_approval_bindings:
        issues.append("F12 INJECTION: Trace already bound to an approval artifact")

    if not session_id:
        issues.append("F11 AUTH: Approval artifact missing session_id")
    else:
        ok, reason = verify_auth_context_with_revocation(session_id, artifact)
        if not ok:
            issues.append(f"F11 AUTH: Approval artifact rejected ({reason})")

    iat = artifact.get("iat")
    if not isinstance(iat, int):
        issues.append("F11 AUTH: Approval artifact missing integer iat")
    else:
        now = int(time.time())
        age = now - iat
        if iat > (now + 30):
            issues.append("F11 AUTH: Approval artifact issued in the future")
        elif age > APPROVAL_MAX_AGE_SECONDS:
            issues.append(
                f"F11 AUTH: Approval artifact stale ({age}s > {APPROVAL_MAX_AGE_SECONDS}s)"
            )

    if artifact.get("parent_signature") != payload_hash:
        issues.append("F2 TRUTH: Approval artifact does not match the event payload hash")

    approval_scope = {str(item) for item in artifact.get("approval_scope", [])}
    missing_scope = sorted(
        _required_approval_scope(
            trace_id=trace_id,
            event_id=event_id,
            payload_hash=payload_hash,
            policy_version=policy_version,
            requested_action=requested_action,
            auth_method=auth_method or None,
            key_id=key_id or None,
            authority_level=authority_level or None,
        )
        - approval_scope
    )
    if missing_scope:
        issues.append(
            "F4 CLARITY: Approval artifact missing required scope bindings: "
            + ", ".join(missing_scope)
        )

    if issues:
        return (
            False,
            _approval_summary(
                "rejected",
                actor=actor,
                auth_method=auth_method or None,
                key_id=key_id or None,
                reason=issues[0],
            ),
            issues,
        )

    _seen_approval_nonces.add(nonce)
    _trace_approval_bindings[trace_id] = nonce
    return (
        True,
        _approval_summary(
            "approved",
            actor=actor,
            auth_method=auth_method,
            key_id=key_id,
            reason="fresh human approval artifact verified",
        ),
        [],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMA VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════


def validate_github_payload(payload: dict[str, Any]) -> list[str]:
    """Validate GitHub webhook payload structure. Returns list of issue strings."""
    issues: list[str] = []
    if not isinstance(payload.get("repository"), dict):
        issues.append("F02 TRUTH: Missing repository object")
    else:
        repo = payload["repository"]
        if not repo.get("full_name"):
            issues.append("F02 TRUTH: Missing repository full_name")
        if not re.match(r"^[\w\-]+/[\w.\-]+$", repo.get("full_name", "")):
            issues.append("F02 TRUTH: Invalid repository full_name format")
    if "ref" not in payload and "action" not in payload:
        issues.append("F02 TRUTH: Missing ref or action")
    return issues


def validate_grafana_payload(payload: dict[str, Any]) -> list[str]:
    """Validate Grafana alert payload structure."""
    issues: list[str] = []
    if not payload.get("title"):
        issues.append("F02 TRUTH: Missing alert title")
    if payload.get("status") not in {"firing", "resolved", "no_data"}:
        issues.append("F02 TRUTH: Unknown alert status")
    return issues


def validate_manual_payload(payload: dict[str, Any]) -> list[str]:
    """Validate manual trigger payload structure."""
    issues: list[str] = []
    if not payload.get("actor"):
        issues.append("F11 AUTH: Manual trigger missing actor")
    if not payload.get("intent"):
        issues.append("F04 CLARITY: Manual trigger missing intent")
    allowed_intents = {"deploy_signal", "health_check", "audit_request", "sovereign_veto"}
    if payload.get("intent") not in allowed_intents:
        issues.append(f"F04 CLARITY: Intent must be one of {allowed_intents}")
    return issues


_SCHEMA_VALIDATORS = {
    "github_webhook": validate_github_payload,
    "grafana_alert": validate_grafana_payload,
    "manual_trigger": validate_manual_payload,
}


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTITUTIONAL ADJUDICATION
# ═══════════════════════════════════════════════════════════════════════════════


def adjudicate_event(
    source: str,
    event_type: str,
    payload: dict[str, Any],
    headers: dict[str, str],
    *,
    trace_id: str | None = None,
    policy_version: str | None = None,
    approval: dict[str, Any] | None = None,
    approval_issues: list[str] | None = None,
) -> dict[str, Any]:
    """
    Run constitutional floors against a webhook event.

    Returns adjudication result with verdict, trace_id, issues, and routing.
    Maximum auto-verdict: QUALIFY. Never auto-SEAL.
    """
    trace_id = trace_id or (
        f"wh-{datetime.now(UTC).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
    )
    policy_version = policy_version or _get_policy_version()
    issues: list[str] = []
    approval_summary = approval or _approval_summary("not_evaluated")

    # ── F11 AUTH: Source must be known ─────────────────────────────────
    if source not in SOURCE_REGISTRY:
        issues.append(f"F11 AUTH: Unknown source '{source}'")
        return _build_void(trace_id, issues, payload)

    reg = SOURCE_REGISTRY[source]

    # ── F02 TRUTH: Schema validation ───────────────────────────────────
    schema_name = reg.get("schema", "generic")
    validator = _SCHEMA_VALIDATORS.get(schema_name)
    if validator:
        schema_issues = validator(payload)
        issues.extend(schema_issues)

    # ── F02 TRUTH: Evidence refs must exist ────────────────────────────
    evidence = payload.get("evidence") or payload.get("repository")
    if source == "github" and not evidence:
        issues.append("F02 TRUTH: No repository context in GitHub payload")
    elif source == "grafana" and not payload.get("title"):
        issues.append("F02 TRUTH: No evidence context in Grafana payload")

    # ── F12 INJECTION: Sanitize actor identifier ───────────────────────
    actor = _derive_actor(source, payload)
    if not actor or actor == "unknown":
        issues.append("F12 INJECTION: Unidentifiable actor")

    # ── F01 AMANAH: Check for irreversible intent ──────────────────────
    intent = payload.get("intent", event_type)
    irreversible = _classify_reversibility(source, event_type, payload)
    if approval_issues:
        issues.extend(approval_issues)
    if irreversible == "IRREVERSIBLE" and approval_summary.get("status") != "approved":
        issues.append(
            "F01 AMANAH: Irreversible intent detected without fresh human approval artifact"
        )

    # ── F07 HUMILITY: Label confidence ─────────────────────────────────
    confidence = "HIGH" if not issues else "LOW"

    # ── Verdict derivation ─────────────────────────────────────────────
    # Webhooks NEVER auto-SEAL. Maximum is QUALIFY.
    if issues:
        verdict = "VOID" if any(i.startswith(("F11", "F12")) for i in issues) else "888-HOLD"
    else:
        verdict = "QUALIFY"

    return {
        "trace_id": trace_id,
        "verdict": verdict,
        "issues": issues,
        "source": source,
        "event_type": event_type,
        "actor": actor,
        "intent": intent,
        "reversibility": irreversible,
        "confidence": confidence,
        "timestamp": datetime.now(UTC).isoformat(),
        "policy_version": policy_version,
        "approval": approval_summary,
        "approval_status": approval_summary.get("status", "not_evaluated"),
        "seal_required": irreversible == "IRREVERSIBLE",
        "seal_authorized": False,
        "routing": _derive_routing(source, event_type, payload, verdict),
    }


def _build_void(trace_id: str, issues: list[str], payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "trace_id": trace_id,
        "verdict": "VOID",
        "issues": issues,
        "source": payload.get("source", "unknown"),
        "event_type": payload.get("event_type", "unknown"),
        "actor": "unknown",
        "intent": "unknown",
        "reversibility": "UNKNOWN",
        "confidence": "LOW",
        "timestamp": datetime.now(UTC).isoformat(),
        "routing": {"action": "reject", "target": None},
    }


def _derive_actor(source: str, payload: dict[str, Any]) -> str:
    """Extract and sanitize actor from payload based on source type."""
    if source == "github":
        raw = payload.get("pusher", {}).get("name") or payload.get("sender", {}).get("login")
    elif source == "grafana":
        raw = payload.get("actor") or "grafana_system"
    elif source == "manual":
        raw = payload.get("actor")
    else:
        raw = payload.get("actor", "unknown")
    return _sanitize_actor(raw)


def _sanitize_actor(raw: Any) -> str:
    """Sanitize actor identifier to prevent injection."""
    if not isinstance(raw, str):
        return "unknown"
    cleaned = re.sub(r"[^a-zA-Z0-9_\-\.]", "", raw)[:64]
    return cleaned or "unknown"


def _classify_reversibility(source: str, event_type: str, payload: dict[str, Any]) -> str:
    """Classify whether a webhook-triggered action is reversible."""
    irreversible_events = {
        ("github", "push"),
        ("github", "release"),
        ("manual", "deploy_signal"),
    }
    if (source, event_type) in irreversible_events:
        return "IRREVERSIBLE"
    return "REVERSIBLE"


def _derive_routing(
    source: str, event_type: str, payload: dict[str, Any], verdict: str
) -> dict[str, Any]:
    """Derive which canonical tool/route should handle this event."""
    if verdict == "VOID":
        return {"action": "reject", "target": None}

    routing_map = {
        ("github", "push"): {"action": "adjudicate", "target": "arif_forge_execute"},
        ("github", "release"): {"action": "adjudicate", "target": "arif_forge_execute"},
        ("grafana", "alert"): {"action": "adjudicate", "target": "arif_judge_deliberate"},
        ("manual", "deploy_signal"): {"action": "adjudicate", "target": "arif_forge_execute"},
        ("manual", "health_check"): {"action": "observe", "target": "arif_ops_measure"},
        ("manual", "audit_request"): {"action": "observe", "target": "arif_evidence_fetch"},
        ("manual", "sovereign_veto"): {"action": "veto", "target": "arif_judge_deliberate"},
    }
    return routing_map.get((source, event_type), {"action": "hold", "target": None})


def execute_routing(
    routing: dict[str, Any],
    event_context: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Execute the routed canonical tool for a QUALIFY verdict.
    Returns the tool result or None if execution is not permitted.
    """
    target = routing.get("target")
    if not target:
        return None

    candidate = event_context.get("candidate") or event_context.get("title") or "webhook_intake"
    actor_id = event_context.get("actor", "webhook_system")
    session_id = event_context.get("trace_id")

    try:
        if target == "arif_judge_deliberate":
            from arifosmcp.tools.judge import arif_judge_deliberate

            result = arif_judge_deliberate(
                mode="judge",
                candidate=candidate,
                session_id=session_id,
                actor_id=actor_id,
            )
            return {
                "tool": target,
                "executed": True,
                "verdict": getattr(result, "verdict", "UNKNOWN"),
                "status": getattr(result, "status", "UNKNOWN"),
            }
        elif target == "arif_ops_measure":
            from arifosmcp.tools.ops import arif_ops_measure

            result = arif_ops_measure(mode="vitals")
            return {
                "tool": target,
                "executed": True,
                "vitals": getattr(result, "__dict__", {}),
            }
        elif target == "arif_evidence_fetch":
            from arifosmcp.tools.evidence import arif_evidence_fetch

            result = arif_evidence_fetch(mode="search", query=candidate)
            return {
                "tool": target,
                "executed": True,
                "status": getattr(result, "status", "UNKNOWN"),
            }
        # arif_forge_execute is intentionally NOT auto-executed from webhooks
        # F01 AMANAH: forge requires explicit sovereign ack
        return {
            "tool": target,
            "executed": False,
            "reason": "F01 AMANAH: forge requires a fresh human approval artifact",
        }
    except Exception as e:
        logger.error(f"Webhook routing execution failed for {target}: {e}")
        return {"tool": target, "executed": False, "reason": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# VAULT999 INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════


def append_vault_record(record: dict[str, Any]) -> dict[str, Any]:
    """Append a hash-chained webhook audit record to VAULT999."""
    ledger_path = _vault_path()
    ledger_path.parent.mkdir(parents=True, exist_ok=True)

    with _vault_ledger_lock:
        prev_hash = "GENESIS"
        if ledger_path.exists():
            last_line = ""
            with ledger_path.open(encoding="utf-8") as handle:
                for line in handle:
                    if line.strip():
                        last_line = line.strip()
            if last_line:
                try:
                    last_record = json.loads(last_line)
                    prev_hash = str(last_record.get("payload_hash", "GENESIS"))
                except json.JSONDecodeError:
                    # Corrupt ledger tail — reset chain to GENESIS rather than fail
                    prev_hash = "GENESIS"

        chain_hash = hashlib.sha256(f"{record['payload_hash']}:{prev_hash}".encode()).hexdigest()[
            :16
        ]
        persisted = {
            **record,
            "entry_id": f"VAULT-{uuid.uuid4().hex[:12]}",
            "prev_hash": prev_hash,
            "chain_hash": chain_hash,
        }
        with ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(persisted, sort_keys=True) + "\n")
    return persisted


def build_vault_record(
    adjudication: dict[str, Any],
    raw_payload: dict[str, Any],
) -> dict[str, Any]:
    """Build a VAULT999-compatible record for a webhook intake event."""
    return {
        "ledger_type": "WEBHOOK_INTAKE",
        "trace_id": adjudication["trace_id"],
        "verdict": adjudication["verdict"],
        "source": adjudication["source"],
        "event_type": adjudication["event_type"],
        "event_id": adjudication.get("event_id"),
        "actor": adjudication["actor"],
        "intent": adjudication["intent"],
        "confidence": adjudication["confidence"],
        "reversibility": adjudication["reversibility"],
        "issues": adjudication["issues"],
        "routing": adjudication["routing"],
        "policy_version": adjudication.get("policy_version", _get_policy_version()),
        "approval_status": adjudication.get("approval_status", "not_evaluated"),
        "approval_actor": adjudication.get("approval", {}).get("actor"),
        "approval_auth_method": adjudication.get("approval", {}).get("auth_method"),
        "payload_hash": _canonical_payload_hash(raw_payload)[:16],
        "timestamp": adjudication["timestamp"],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════


def process_webhook(
    source: str,
    payload_bytes: bytes,
    headers: dict[str, str],
    client_key: str,
) -> dict[str, Any]:
    """
    Full constitutional pipeline for a webhook intake.

    1. Rate limit check
    2. Signature verification
    3. Replay protection
    4. Timestamp freshness
    5. Payload parsing
    6. Schema validation
    7. Constitutional adjudication
    8. Vault record generation

    Returns complete result dict.
    """
    now_iso = datetime.now(UTC).isoformat()
    event_id = _derive_event_id(source, headers, payload_bytes)
    trace_id = _trace_id_for_event(event_id)
    policy_version = _get_policy_version()

    # 1. Rate limit
    allowed, rl_meta = check_rate_limit(client_key)
    if not allowed:
        return {
            "trace_id": trace_id,
            "event_id": event_id,
            "verdict": "VOID",
            "issues": [f"F05 PEACE: Rate limit exceeded. Reset in {rl_meta['reset_in']}s"],
            "source": source,
            "event_type": headers.get("x-event-type", "unknown"),
            "policy_version": policy_version,
            "approval_status": "not_evaluated",
            "seal_required": False,
            "seal_authorized": False,
            "rate_limit": rl_meta,
            "timestamp": now_iso,
        }

    # 2. Signature
    reg = SOURCE_REGISTRY.get(source, {})
    sig_header = reg.get("sig_header", "x-signature")
    signature = headers.get(sig_header.lower()) or headers.get(sig_header)
    if not verify_signature(payload_bytes, signature, source):
        return {
            "trace_id": trace_id,
            "event_id": event_id,
            "verdict": "VOID",
            "issues": ["F11 AUTH: Signature verification failed"],
            "source": source,
            "event_type": headers.get("x-event-type", "unknown"),
            "policy_version": policy_version,
            "approval_status": "not_evaluated",
            "seal_required": False,
            "seal_authorized": False,
            "timestamp": now_iso,
        }

    # 3. Event ID / replay
    if is_replay(event_id):
        return {
            "trace_id": trace_id,
            "event_id": event_id,
            "verdict": "VOID",
            "issues": ["F12 INJECTION: Replay detected — event_id already processed"],
            "source": source,
            "event_type": headers.get("x-event-type", "unknown"),
            "policy_version": policy_version,
            "approval_status": "not_evaluated",
            "seal_required": False,
            "seal_authorized": False,
            "timestamp": now_iso,
        }

    # 4. Timestamp freshness (if present in payload)
    try:
        payload = json.loads(payload_bytes)
    except json.JSONDecodeError:
        return {
            "trace_id": trace_id,
            "event_id": event_id,
            "verdict": "VOID",
            "issues": ["F02 TRUTH: Invalid JSON payload"],
            "source": source,
            "event_type": headers.get("x-event-type", "unknown"),
            "policy_version": policy_version,
            "approval_status": "not_evaluated",
            "seal_required": False,
            "seal_authorized": False,
            "timestamp": now_iso,
        }

    ts = payload.get("timestamp") or payload.get("sent_at")
    if ts and not check_timestamp_freshness(ts):
        return {
            "trace_id": trace_id,
            "event_id": event_id,
            "verdict": "VOID",
            "issues": [f"F12 INJECTION: Stale webhook timestamp ({ts})"],
            "source": source,
            "event_type": headers.get("x-event-type", "unknown"),
            "policy_version": policy_version,
            "approval_status": "not_evaluated",
            "seal_required": False,
            "seal_authorized": False,
            "timestamp": now_iso,
        }

    # 5. Event type
    event_type = headers.get("x-event-type", "unknown")
    if not event_type or event_type == "unknown":
        event_type = payload.get("event_type", payload.get("action", "unknown"))

    payload_hash = _canonical_payload_hash(payload)
    approval_artifact, approval_parse_issues = _extract_approval_artifact(headers, payload)
    approval_required = _classify_reversibility(source, event_type, payload) == "IRREVERSIBLE"
    requested_action = f"{source}:{payload.get('intent', event_type)}"
    _, approval_summary, approval_issues = verify_approval_artifact(
        approval_artifact,
        trace_id=trace_id,
        event_id=event_id,
        payload_hash=payload_hash,
        policy_version=policy_version,
        requested_action=requested_action,
    )
    if (
        not approval_required
        and approval_artifact is None
        and not approval_parse_issues
        and approval_summary.get("status") == "missing"
    ):
        approval_summary = _approval_summary("not_required")
        approval_issues = []
    else:
        approval_issues = [*approval_parse_issues, *approval_issues]

    # 6–8. Adjudication + vault record
    adjudication = adjudicate_event(
        source,
        event_type,
        payload,
        headers,
        trace_id=trace_id,
        policy_version=policy_version,
        approval=approval_summary,
        approval_issues=approval_issues,
    )
    adjudication["event_id"] = event_id
    vault_record = build_vault_record(adjudication, payload)
    try:
        vault_record = append_vault_record(vault_record)
    except (OSError, ValueError) as exc:
        adjudication["issues"] = [
            *adjudication.get("issues", []),
            f"F11 AUDIT: Vault append failed ({exc})",
        ]
        if adjudication.get("verdict") != "VOID":
            adjudication["verdict"] = "888-HOLD"
        vault_record = {
            **vault_record,
            "entry_id": None,
            "prev_hash": None,
            "chain_hash": None,
            "vault_error": str(exc),
        }

    result = {
        **adjudication,
        "vault_record": vault_record,
        "rate_limit": rl_meta,
        "event_id": event_id,
        "policy_version": policy_version,
        "approval": approval_summary,
        "approval_status": approval_summary.get("status", "not_evaluated"),
        "seal_required": approval_required,
        "seal_authorized": False,
        "vault_entry_id": vault_record.get("entry_id"),
        "chain_hash": vault_record.get("chain_hash"),
        "observation_only": True,
    }

    # 9. Execute routing for QUALIFY verdicts (observation-only for forge)
    if adjudication.get("verdict") == "QUALIFY":
        execution = execute_routing(adjudication.get("routing", {}), result)
        if execution:
            result["execution"] = execution

    # 10. Emit sanitized event to Observatory SSE (fire-and-forget)
    try:
        from arifosmcp.runtime.event_bus import emit_event_sync

        emit_event_sync(result)
    except Exception:
        pass  # Event bus failure must not break webhook intake

    return result
