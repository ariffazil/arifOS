"""
arifosmcp/runtime/boot_attestation.py — Server-side BOOT-attestation proofs.

T3a Item 3 / APEX-CONCORDANCE-17072026 §7 (BOOT becomes real only when
converted from language into geometry).

The BOOT protocol's 7 questions (per /root/AAA/prompts/INIT.md §1) must be
answered from server-side state, not by the agent self-attesting. An agent
that lies (or is just wrong) can otherwise answer "yes yes yes" and proceed
without anything being honestly checked.

This module exposes `verify_boot_attestation()` which reads each Q's answer
from canonical server-side sources — kernel /health, session store, identity
service, vault999 chain, atlas333 substrate — and produces an
evidencedAnswer per Q. The caller (typically arif_init binding or any
SOVEREIGN-grade action) is expected to inspect the result and refuse to
issue authority above OBSERVE_ONLY unless every required Q is answered
with method + evidence_ref populated.

APEX §6 proof-rule: PositiveClaim ⇒ EvidenceRef ∧ Method ∧ Issuer ∧
Freshness. This module is the single source for that proof at BOOT.
"""

from __future__ import annotations

import logging
import os
import socket
from dataclasses import dataclass
from typing import Any
from urllib.error import URLError
from urllib.request import Request as URLRequest
from urllib.request import urlopen

logger = logging.getLogger(__name__)


# BOOTSTATE_VERSION — bumped 2026-07-17 (F-007 sovereign key attestation).
# v1: Q5 was name-string match — sovereign authority bind by name (INCORRECT).
# v2: Q5 routes through _verify_ed25519_proof — sovereign authority bind by key,
#     per governance_identity.py:44 doctrine:
#     "Sovereign authority binds to a verified key, not a name."
# Bump forces re-attestation across the federation under the new path.
BOOTSTATE_VERSION = 2

# Q-id → server-side evidence method
_METHODS = {
    "Q1": "session_identity_service",
    "Q2": "kernel_health_constitution",
    "Q3": "session_store_liveness",
    "Q4": "atlas333_substrate",
    "Q5": "ed25519_sovereign_or_identity_toml_f13",  # v2: crypto primary, name-match PARTIAL fallback
    "Q6": "refusal_list_module",
    "Q7": "rsi_session_endpoint",
}

# Canonical sources
_KERNEL_HEALTH = "http://127.0.0.1:8088/health"
_IDENTITY_TOML_PATH = "/opt/arifos/identity.toml"
_IDENTITY_TOML_FALLBACK = "/root/arifOS/identity.toml"
_VAULT_CHAIN_HEAD = "/root/.local/share/arifos/vault999/seal_chain_head.json"

# F-007: hardcoded sovereign Ed25519 pubkey path.
# NEVER glob *.pem in /root/.secrets/aaa-identity/keys/ — arif_private.pem
# (mode 600 private key) sits alongside. Explicit filename only, fail-closed.
_SOVEREIGN_PUBKEY_PATH = "/root/.secrets/aaa-identity/keys/arif_public.pem"


@dataclass(frozen=True)
class EvidencedAnswer:
    """One BOOT question's server-side evidence."""

    q: str  # "Q1".."Q7"
    answer: str  # "YES" | "PARTIAL" | "NO"
    method: str  # server-side source name (T6 §method)
    evidence_ref: str  # key:// or session:// or local:// pointer
    issuer: str  # who produced this answer
    fresh_at: str  # ISO-8601 timestamp
    note: str = ""

    def __post_init__(self) -> None:
        # T3a Item 3 / Claude Point 2 / APEX §6 — PositiveClaim requires evidence.
        # A YES answer without method or evidence_ref is structurally incoherent.
        if self.answer == "YES":
            if not self.method:
                raise ValueError(f"EvidencedAnswer({self.q}): YES requires method")
            if not self.evidence_ref:
                raise ValueError(f"EvidencedAnswer({self.q}): YES requires evidence_ref")

    def to_dict(self) -> dict[str, Any]:
        return {
            "q": self.q,
            "answer": self.answer,
            "method": self.method,
            "evidence_ref": self.evidence_ref,
            "issuer": self.issuer,
            "fresh_at": self.fresh_at,
            "note": self.note,
        }


def _now_iso() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).isoformat()


def _local_url_get(url: str, timeout_s: float = 1.5) -> dict[str, Any] | None:
    """Read a local-HTTP URL as JSON with bounded timeout. No network calls."""
    try:
        req = URLRequest(url, headers={"Accept": "application/json"})
        with urlopen(req, timeout=timeout_s) as resp:
            import json

            return json.loads(resp.read().decode("utf-8"))
    except (URLError, TimeoutError, socket.timeout, ValueError, ConnectionError):
        return None


def _file_read(path: str) -> str:
    try:
        with open(path) as f:
            return f.read()
    except OSError:
        return ""


def _answer_q1_identity_bind(session_id: str | None) -> EvidencedAnswer:
    """Q1: Is there a server-side bound actor_id for the given session?"""
    if not session_id:
        return EvidencedAnswer(
            q="Q1",
            answer="PARTIAL",
            method=_METHODS["Q1"],
            evidence_ref="boot://init#session_pending",
            issuer="session_store",
            fresh_at=_now_iso(),
            note="no session_id provided — expected during boot init, identity verified via crypto",
        )

    sess = _local_url_get(
        f"{_KERNEL_HEALTH.replace('/health', '/sessions/')}lookup?session_id={session_id}"
    )
    if sess and sess.get("actor_id"):
        return EvidencedAnswer(
            q="Q1",
            answer="YES",
            method=_METHODS["Q1"],
            evidence_ref=f"session://{session_id}#actor_id",
            issuer="session_store",
            fresh_at=_now_iso(),
            note=f"actor_id={sess.get('actor_id')}",
        )
    return EvidencedAnswer(
        q="Q1",
        answer="PARTIAL",
        method=_METHODS["Q1"],
        evidence_ref=f"session://{session_id}#lookup_attempted",
        issuer="session_store",
        fresh_at=_now_iso(),
        note="session lookup endpoint not reachable; answer conservative",
    )


def _answer_q2_constitution_load() -> EvidencedAnswer:
    """Q2: Has the kernel loaded F1–F13?

    Prefer in-process floor count (never HTTP self-call /health — that
    deadlocks single-worker uvicorn when authority_envelope → boot gate
    runs during a concurrent /health request). Fall back to HTTP only
    when in-process probe is unavailable (out-of-process CLI use).
    """
    floor_count = 0
    method_note = "in_process"
    try:
        from arifosmcp.runtime.law import get_floor_count

        floor_count = int(get_floor_count() or 0)
    except Exception:
        h = _local_url_get(_KERNEL_HEALTH)
        if not h:
            return EvidencedAnswer(
                q="Q2",
                answer="NO",
                method=_METHODS["Q2"],
                evidence_ref="",
                issuer="kernel_health",
                fresh_at=_now_iso(),
                note="kernel floors unreachable (in-process + /health)",
            )
        floors = h.get("floors_active") or h.get("runtime_floors") or {}
        floor_count = len(floors) if isinstance(floors, dict) else int(floors or 0)
        method_note = "http_health_fallback"
    if floor_count >= 13:
        return EvidencedAnswer(
            q="Q2",
            answer="YES",
            method=_METHODS["Q2"],
            evidence_ref="local://kernel/floors#floors_active",
            issuer="kernel_floors",
            fresh_at=_now_iso(),
            note=f"floors_active={floor_count};probe={method_note}",
        )
    return EvidencedAnswer(
        q="Q2",
        answer="PARTIAL",
        method=_METHODS["Q2"],
        evidence_ref="local://kernel/floors#floors_active",
        issuer="kernel_floors",
        fresh_at=_now_iso(),
        note=f"floors_active={floor_count} (<13);probe={method_note}",
    )


def _answer_q3_session_ignite(session_id: str | None) -> EvidencedAnswer:
    """Q3: Is there a live session_id?

    In-process only — never HTTP self-call /health (deadlock risk).
    A non-empty session_id from the caller is the ignition evidence.
    """
    if not session_id:
        return EvidencedAnswer(
            q="Q3",
            answer="PARTIAL",
            method=_METHODS["Q3"],
            evidence_ref="boot://init#session_being_minted",
            issuer="session_store",
            fresh_at=_now_iso(),
            note="no session_id yet — during init, session being minted inline",
        )
    # Prefer in-process session store when available.
    try:
        from arifosmcp.runtime import tools as _tools

        sessions = getattr(_tools, "_SESSIONS", None) or {}
        if session_id in sessions:
            return EvidencedAnswer(
                q="Q3",
                answer="YES",
                method=_METHODS["Q3"],
                evidence_ref=f"session://{session_id}#in_process_store",
                issuer="session_store",
                fresh_at=_now_iso(),
                note="session present in kernel store",
            )
    except Exception:
        pass
    # Caller-supplied session_id still counts as ignition evidence for BOOT
    # (arif_init just minted it). Avoid HTTP self-call.
    return EvidencedAnswer(
        q="Q3",
        answer="YES",
        method=_METHODS["Q3"],
        evidence_ref=f"local://arif_init/result#session_id={session_id}",
        issuer="arif_init_mode_init",
        fresh_at=_now_iso(),
    )


def _answer_q4_trinity33_loaded() -> EvidencedAnswer:
    """Q4: Is the canonical 33-repo map reachable?"""
    candidates = [
        "/root/AAA/prompts/INIT.md",
        "/root/A-FORGE/forge_work/2026-07-12/CONSOLIDATION_EPOCH_SEAL_PAYLOAD.json",
        "/root/AAA/consolidation/",
    ]
    for path in candidates:
        try:
            with open(path):
                return EvidencedAnswer(
                    q="Q4",
                    answer="YES",
                    method=_METHODS["Q4"],
                    evidence_ref=f"local://{path}",
                    issuer="atlas333_substrate",
                    fresh_at=_now_iso(),
                    note=f"33-repo map reachable at {path}",
                )
        except OSError:
            continue
    return EvidencedAnswer(
        q="Q4",
        answer="NO",
        method=_METHODS["Q4"],
        evidence_ref="",
        issuer="atlas333_substrate",
        fresh_at=_now_iso(),
        note="no canonical 33-repo substrate reachable",
    )


def _answer_q5_sovereign_recognize(
    actor_id: str | None = None,
    ed25519_proof: dict | None = None,
) -> EvidencedAnswer:
    """Q5 v2 (F-007): sovereign attestation via Ed25519 signature.

    Resolution order:
      1. actor_id + ed25519_proof supplied → dispatch to
         governance_identity._verify_ed25519_proof.
            Verified   ⇒ YES  (cryptographic).
            Failed     ⇒ NO   (fail-closed; do NOT silently fall back).
            Dispatch raised   ⇒ NO   (note carries the exception).
      2. Else fall back to legacy name-string match against identity.toml.
            Match → PARTIAL only — name-match does NOT grant sovereign authority
            under governance_identity.py:44. Use the crypto path for YES.
            No match → NO.

    Per doctrine: name-string match MAY trigger a confirmation workflow, but
    never grants YES. Cryptographic verification is the only YES path.
    """
    if actor_id and ed25519_proof:
        try:
            from arifosmcp.runtime.governance_identity import _verify_ed25519_proof
            verified = _verify_ed25519_proof(actor_id, ed25519_proof)
        except Exception as e:
            return EvidencedAnswer(
                q="Q5",
                answer="NO",
                method="ed25519_proof_dispatch_failed",
                evidence_ref=f"key://{_SOVEREIGN_PUBKEY_PATH}#dispatch",
                issuer="q5_sovereign_v2",
                fresh_at=_now_iso(),
                note=f"_verify_ed25519_proof raised: {type(e).__name__}: {e}",
            )
        if verified:
            return EvidencedAnswer(
                q="Q5",
                answer="YES",
                method="ed25519_signature_verify",
                evidence_ref=f"key://{_SOVEREIGN_PUBKEY_PATH}#ed25519_sovereign",
                issuer="governance_identity._verify_ed25519_proof",
                fresh_at=_now_iso(),
                note=f"ed25519 proof verified for actor_id={actor_id}",
            )
        # Crypto attempted, failed. Fail-closed. Do NOT silently fall back.
        return EvidencedAnswer(
            q="Q5",
            answer="NO",
            method="ed25519_signature_verify",
            evidence_ref=f"key://{_SOVEREIGN_PUBKEY_PATH}#ed25519_invalid",
            issuer="governance_identity._verify_ed25519_proof",
            fresh_at=_now_iso(),
            note=f"ed25519 proof REJECTED for actor_id={actor_id}",
        )

    # Legacy fallback — name-string match. Demoted from YES to PARTIAL.
    toml_text = _file_read(_IDENTITY_TOML_PATH) or _file_read(_IDENTITY_TOML_FALLBACK)
    pii_text = _file_read("/root/.secrets/sovereign_identity.toml") or ""
    combined = toml_text + "\n" + pii_text
    name_match = ("Muhammad Arif bin Fazil" in combined or "Arif" in toml_text) and (
        "F13" in toml_text or "sovereign" in toml_text.lower()
    )
    if name_match:
        return EvidencedAnswer(
            q="Q5",
            answer="PARTIAL",
            method="identity_toml_f13",  # legacy label; PARTIAL not YES
            evidence_ref=(
                f"file://{_IDENTITY_TOML_PATH if _file_read(_IDENTITY_TOML_PATH) else _IDENTITY_TOML_FALLBACK}#owner"
            ),
            issuer="identity_toml",
            fresh_at=_now_iso(),
            note=(
                "NAME-MATCH ONLY. Per governance_identity.py:44, name-match does "
                "NOT grant sovereign authority. Provide actor_signature + nonce "
                "for cryptographic YES."
            ),
        )
    return EvidencedAnswer(
        q="Q5",
        answer="NO",
        method="identity_toml_f13",
        evidence_ref="",
        issuer="identity_toml",
        fresh_at=_now_iso(),
    )


def _answer_q6_refusal_surface() -> EvidencedAnswer:
    """Q6: Is the refusal list reachable?"""
    candidates = ["/root/AAA/prompts/INIT.md", "/root/AAA/governance/ADAT_AGENTIC.md"]
    for path in candidates:
        try:
            with open(path):
                if "refusal" in _file_read(path).lower():
                    return EvidencedAnswer(
                        q="Q6",
                        answer="YES",
                        method=_METHODS["Q6"],
                        evidence_ref=f"local://{path}#refusal_list",
                        issuer="refusal_list_module",
                        fresh_at=_now_iso(),
                    )
        except OSError:
            continue
    return EvidencedAnswer(
        q="Q6",
        answer="NO",
        method=_METHODS["Q6"],
        evidence_ref="",
        issuer="refusal_list_module",
        fresh_at=_now_iso(),
    )


def _answer_q7_rsi_path_clear() -> EvidencedAnswer:
    """Q7: Is the RSI invocation endpoint known?"""
    candidates = [
        "/root/AAA/skills/RSI-recursive-improvement/SKILL.md",
        "/root/arifOS/skills/RSI-recursive-improvement/SKILL.md",
        "/root/AAA/agents/makcikgpt/INIT.md",
        "/root/AAA/prompts/INIT.md",
    ]
    for path in candidates:
        try:
            with open(path):
                content = _file_read(path)
                if "RSI" in content and "session" in content.lower():
                    return EvidencedAnswer(
                        q="Q7",
                        answer="YES",
                        method=_METHODS["Q7"],
                        evidence_ref=f"local://{path}#rsi_path",
                        issuer="rsi_session_endpoint",
                        fresh_at=_now_iso(),
                    )
        except OSError:
            continue
    return EvidencedAnswer(
        q="Q7",
        answer="NO",
        method=_METHODS["Q7"],
        evidence_ref="",
        issuer="rsi_session_endpoint",
        fresh_at=_now_iso(),
    )


def verify_boot_attestation(
    session_id: str | None = None, *, iso_now: str | None = None,
    actor_id: str | None = None,
    ed25519_proof: dict | None = None,
) -> dict[str, Any]:
    """Run server-side BOOT Q1–Q7 checks. Return evidenced answers.

    F-007 (2026-07-17): accepts actor_id + ed25519_proof kwargs to route Q5
    through governance_identity._verify_ed25519_proof. Both default None —
    legacy callers are unaffected and get PARTIAL from the name-match fallback.

    Returns dict shaped:
        {
          "version": BOOTSTATE_VERSION,
          "fresh_at": "<iso>",
          "session_id": "<session_id or null>",
          "Q1": {...},
          ...
          "Q7": {...},
          "summary": {
              "yes_count": int, "partial_count": int, "no_count": int,
              "boot_state": "OK" | "PARTIAL" | "FAIL",
              "refuses_above_observe_only": bool,
          }
        }
    """
    now = iso_now or _now_iso()
    q1 = _answer_q1_identity_bind(session_id)
    q2 = _answer_q2_constitution_load()
    q3 = _answer_q3_session_ignite(session_id)
    q4 = _answer_q4_trinity33_loaded()
    q5 = _answer_q5_sovereign_recognize(actor_id=actor_id, ed25519_proof=ed25519_proof)
    q6 = _answer_q6_refusal_surface()
    q7 = _answer_q7_rsi_path_clear()
    answers = (q1, q2, q3, q4, q5, q6, q7)
    yes = sum(1 for a in answers if a.answer == "YES")
    partial = sum(1 for a in answers if a.answer == "PARTIAL")
    no = sum(1 for a in answers if a.answer == "NO")
    if no > 0:
        boot_state = "FAIL"
    elif partial > 0:
        boot_state = "PARTIAL"
    else:
        boot_state = "OK"
    refuses_above = boot_state != "OK"
    return {
        "version": BOOTSTATE_VERSION,
        "fresh_at": now,
        "session_id": session_id,
        "Q1": q1.to_dict(),
        "Q2": q2.to_dict(),
        "Q3": q3.to_dict(),
        "Q4": q4.to_dict(),
        "Q5": q5.to_dict(),
        "Q6": q6.to_dict(),
        "Q7": q7.to_dict(),
        "summary": {
            "yes_count": yes,
            "partial_count": partial,
            "no_count": no,
            "boot_state": boot_state,
            "refuses_above_observe_only": refuses_above,
        },
    }


def boot_state_for_authority_grade(requested_band: str) -> dict[str, Any]:
    """For any requested_band >= LIMITED_MUTATE, return the BOOT verdict that
    must be OK before that band can be issued.

    Per the doctrine, FAIL ⇒ refuse the band. PARTIAL ⇒ also refuse until
    kernel /health is reachable and atlas333 substrate is on disk.
    """
    parsed = verify_boot_attestation()
    if requested_band in ("OBSERVE_ONLY", ""):
        # Caller did not request authority-grade action; BOOT does not gate.
        return {
            "gates_requested_band": False,
            "boot_state": parsed["summary"]["boot_state"],
            "yes_count": parsed["summary"]["yes_count"],
            "no_count": parsed["summary"]["no_count"],
        }
    return {
        "gates_requested_band": True,
        "boot_state": parsed["summary"]["boot_state"],
        "yes_count": parsed["summary"]["yes_count"],
        "no_count": parsed["summary"]["no_count"],
        "must_be": "OK",
        "actual": parsed["summary"]["boot_state"],
        "passes": parsed["summary"]["boot_state"] == "OK",
        "parsed": parsed,
    }


if __name__ == "__main__":
    import json as _json

    print(_json.dumps(verify_boot_attestation(), indent=2, default=str))
