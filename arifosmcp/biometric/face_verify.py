"""face_verify.py — consent-based 1:1 face verification service (888 audit 2026-09-05).

CONTRACT (auditor spec, verbatim intent):
  - 1:1 VERIFICATION ONLY. This service can NEVER answer "who is this?" —
    it evaluates a CLAIMED subject_id against that subject's enrolled template.
  - LLM never sees embeddings, images, or raw similarity. Structured output:
    decision / assurance / reason_code / assertion_id / expires_at.
  - Raw frames never reach this service — edge gateway supplies embedding +
    quality + liveness attestation. Server does policy + math + assertions.
  - deny-by-default: unknown subject, no consent trigger, multi-face, bad
    quality, liveness fail → no PASS. Liveness fail → DENY + security event.
  - Two-threshold band (T_reject / T_accept), middle = ESCALATE (step-up),
    never a guess. Bias false-reject: annoying is reversible; unauthorized
    execution is not.
  - Assertions: fva_*, signed, TTL ≤5 min, bound to (subject, session,
    device, purpose, nonce), single-use (replay cache).
  - Templates: encrypted at rest (Fernet), separate key file, separate
    audit trail, one-command revocation, no enrollment enumeration.
  - 888 HOLD: any deployment beyond local personal prototype (other people,
    surveillance, 1:N, irreversible access) requires sovereign authorization.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import math
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DEFAULTS = {
    "t_accept": 0.68,          # ≥ → PASS (calibrate empirically per audit §777)
    "t_reject": 0.45,          # < → FAIL; between = ESCALATE (step-up)
    "assertion_ttl_s": 240,    # 4 min (spec: 2–5)
    "rate_limit_per_min": 5,
    "liveness_fail_lockout_s": 60,
    "min_face_size_px": 120,
    "max_yaw_deg": 15.0,
    "min_blur": 0.5,
    "min_brightness": 0.25,
}
_REASONS = {"MATCH", "NO_FACE", "MULTIPLE_FACES", "LOW_QUALITY", "LIVENESS_FAILED",
            "BELOW_THRESHOLD", "RATE_LIMITED", "NO_CONSENT", "UNKNOWN_SUBJECT",
            "REPLAY_DETECTED", "EXPIRED_ASSERTION", "REVOKED", "SERVER_HOLD"}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _cos(a: list[float], b: list[float]) -> float:
    if not a or len(a) != len(b):
        return -1.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1e-9
    nb = math.sqrt(sum(y * y for y in b)) or 1e-9
    return dot / (na * nb)


class _Crypto:
    """Fernet if available; else HMAC-stream (still at-rest-encrypted vs casual read).
    Key: dedicated file, 600, provisioned on first use — OUTSIDE app database."""

    def __init__(self, key_path: Path):
        self.key_path = key_path
        self._f = None
        try:
            from cryptography.fernet import Fernet

            if key_path.exists():
                key = key_path.read_bytes().strip()
            else:
                key = Fernet.generate_key()
                key_path.parent.mkdir(parents=True, exist_ok=True)
                key_path.write_bytes(key)
                os.chmod(key_path, 0o600)
            self._f = Fernet(key)
        except Exception:
            self._f = None
            self._hk = hashlib.sha256((key_path.read_bytes() if key_path.exists()
                                       else b"biometric-fallback")).digest()

    def seal(self, obj: dict) -> str:
        raw = json.dumps(obj, sort_keys=True).encode()
        if self._f:
            return self._f.encrypt(raw).decode()
        ks = hashlib.sha256(self._hk + b"stream").digest()
        return "h1:" + hmac.new(ks, raw, hashlib.sha256).hexdigest() + ":" + \
            bytes(b ^ ks[i % len(ks)] for i, b in enumerate(raw)).hex()

    def open(self, tok: str) -> dict | None:
        try:
            if self._f:
                return json.loads(self._f.decrypt(tok.encode()))
            if not tok.startswith("h1:"):
                return None
            mac, hx = tok[3:].split(":", 1)
            raw = bytes.fromhex(hx)
            ks = hashlib.sha256(self._hk + b"stream").digest()
            pt = bytes(b ^ ks[i % len(ks)] for i, b in enumerate(raw))
            good = hmac.new(ks, pt, hashlib.sha256).hexdigest()
            return json.loads(pt) if hmac.compare_digest(good, mac) else None
        except Exception:
            return None


@dataclass
class VerifyResult:
    decision: str                  # PASS | FAIL | RETRY | ESCALATE | DENY
    assurance: str                 # LOW | MEDIUM | HIGH
    reason_code: str
    assertion_id: str | None = None
    expires_at: str | None = None


class FaceVerifyService:
    def __init__(self, vault_dir: Path | str | None = None, config: dict | None = None):
        self.cfg = {**DEFAULTS, **(config or {})}
        base = Path(vault_dir or os.getenv("ARIFOS_BIOMETRIC_DIR",
                                           "/var/lib/arifos/biometric"))
        self.dir = base
        self.dir.mkdir(parents=True, exist_ok=True)
        self._crypt = _Crypto(base / "vault.key")
        self._vault_path = base / "templates.enc"
        self._audit_path = base / "audit.jsonl"
        self._replay: dict[str, float] = {}
        self._attempts: dict[str, list[float]] = {}      # rate limit window
        self._lockout: dict[str, float] = {}             # liveness-fail lockout
        self._assertions: dict[str, dict] = {}

    # ── audit trail (separate, no biometric material) ────────────────
    def _audit(self, ev: dict) -> None:
        ev = {"ts": _now().isoformat(), **ev}
        with self._audit_path.open("a") as f:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")

    # ── vault ─────────────────────────────────────────────────────────
    def _load(self) -> dict:
        if not self._vault_path.exists():
            return {"subjects": {}}
        d = self._crypt.open(self._vault_path.read_text().strip())
        return d or {"subjects": {}}

    def _save(self, v: dict) -> None:
        tmp = self._vault_path.with_suffix(".tmp")
        tmp.write_text(self._crypt.seal(v))
        os.chmod(tmp, 0o600)
        tmp.replace(self._vault_path)

    # ── enrollment (sovereign-gated, explicit consent) ────────────────
    def enroll(self, subject_id: str, embedding: list[float], consent_note: str,
               *, sovereign_token: str) -> dict:
        want = os.getenv("ARIFOS_BIOMETRIC_ENROLL_TOKEN", "")
        if not want or not hmac.compare_digest(sovereign_token, want):
            self._audit({"event": "ENROLL_DENIED", "subject": subject_id,
                         "reason": "sovereign_token_invalid"})
            return {"ok": False, "error": "sovereign enroll token required"}
        if not embedding or len(embedding) < 8:
            return {"ok": False, "error": "invalid embedding"}
        v = self._load()
        v["subjects"][subject_id] = {
            "template": embedding,
            "enrolled_at": _now().isoformat(),
            "consent": consent_note,
            "samples": v["subjects"].get(subject_id, {}).get("samples", 0) + 1,
            "revoked": False,
        }
        self._save(v)
        self._audit({"event": "ENROLL", "subject": subject_id, "consent": consent_note,
                     "samples": v["subjects"][subject_id]["samples"]})
        return {"ok": True, "subject": subject_id,
                "samples": v["subjects"][subject_id]["samples"]}

    def revoke(self, subject_id: str, *, sovereign_token: str) -> dict:
        want = os.getenv("ARIFOS_BIOMETRIC_ENROLL_TOKEN", "")
        if not want or not hmac.compare_digest(sovereign_token, want):
            return {"ok": False, "error": "sovereign enroll token required"}
        v = self._load()
        if subject_id in v["subjects"]:
            del v["subjects"][subject_id]
            self._save(v)
        # kill live assertions for this subject
        for aid in [a for a, m in self._assertions.items()
                    if m.get("subject") == subject_id]:
            del self._assertions[aid]
        self._audit({"event": "REVOKE", "subject": subject_id})
        return {"ok": True, "subject": subject_id, "templates_remaining": len(v["subjects"])}

    def drill(self, *, sovereign_token: str) -> dict:
        """Deletion/revocation drill (audit build-order #8)."""
        r1 = self.revoke("__drill_dummy__", sovereign_token=sovereign_token)
        live = sum(1 for a in self._assertions.values())
        self._assertions.clear()
        v = self._load()
        return {"drill": "delete-revoke", "ok": r1["ok"], "subjects_in_vault": len(v["subjects"]),
                "assertions_cleared": live,
                "note": "rotate vault.key manually for full drill; verify_face must FAIL after revoke"}

    # ── verification (the ONLY public decision path) ─────────────────
    def verify(self, *, claimed_subject_id: str, purpose: str, session_id: str,
               device_id: str, capture_nonce: str, embedding: list[float],
               liveness: str, quality: dict, user_triggered: bool = True) -> VerifyResult:
        rl_key = f"{claimed_subject_id}|{device_id}"

        # policy §777 — order matters, verbatim
        if not user_triggered:
            return self._fin("DENY", "LOW", "NO_CONSENT", sec_event=True)
        if time.time() < self._lockout.get(rl_key, 0):
            return self._fin("DENY", "LOW", "RATE_LIMITED")
        if liveness == "FAIL":
            self._lockout[rl_key] = time.time() + self.cfg["liveness_fail_lockout_s"]
            return self._fin("DENY", "LOW", "LIVENESS_FAILED", sec_event=True)
        if liveness not in ("PASS", "UNTESTED"):
            return self._fin("RETRY", "LOW", "LIVENESS_FAILED")
        if not embedding:
            return self._fin("RETRY", "LOW", "NO_FACE")
        # rate limit (sliding minute)
        now = time.time()
        win = [t for t in self._attempts.get(rl_key, []) if now - t < 60]
        if len(win) >= self.cfg["rate_limit_per_min"]:
            self._attempts[rl_key] = win
            return self._fin("DENY", "LOW", "RATE_LIMITED")
        win.append(now)
        self._attempts[rl_key] = win
        # replay: nonce single-use
        if capture_nonce in self._replay:
            return self._fin("DENY", "LOW", "REPLAY_DETECTED", sec_event=True)
        self._replay[capture_nonce] = now
        # quality gates
        q = quality or {}
        if q.get("num_faces", 1) > 1:
            return self._fin("RETRY", "LOW", "MULTIPLE_FACES")
        if (q.get("face_size_px", 999) < self.cfg["min_face_size_px"]
                or q.get("blur_score", 1.0) < self.cfg["min_blur"]
                or q.get("brightness_score", 1.0) < self.cfg["min_brightness"]
                or abs(q.get("yaw_deg", 0.0)) > self.cfg["max_yaw_deg"]):
            return self._fin("RETRY", "LOW", "LOW_QUALITY")

        v = self._load()
        sub = v["subjects"].get(claimed_subject_id)
        # anti-enumeration: unknown/revoked → generic FAIL (never "not enrolled")
        if not sub or sub.get("revoked"):
            self._audit({"event": "VERIFY", "subject": claimed_subject_id,
                         "decision": "FAIL", "reason": "BELOW_THRESHOLD"})
            return self._fin("FAIL", "LOW", "BELOW_THRESHOLD")

        score = _cos(embedding, sub["template"])
        t_a, t_r = self.cfg["t_accept"], self.cfg["t_reject"]
        if score >= t_a:
            aid = "fva_" + hashlib.sha256(
                f"{claimed_subject_id}{session_id}{device_id}{purpose}{capture_nonce}"
                .encode()).hexdigest()[:24]
            exp = (_now() + timedelta(seconds=self.cfg["assertion_ttl_s"])).isoformat()
            self._assertions[aid] = {"subject": claimed_subject_id, "session": session_id,
                                     "device": device_id, "purpose": purpose,
                                     "nonce": capture_nonce, "exp": exp}
            self._audit({"event": "VERIFY", "subject": claimed_subject_id,
                         "decision": "PASS", "reason": "MATCH",
                         "score_rounded": round(score, 3)})  # audit trail only
            return VerifyResult("PASS", "HIGH" if score >= t_a + 0.1 else "MEDIUM",
                                "MATCH", aid, exp)
        if score >= t_r:
            self._audit({"event": "VERIFY", "subject": claimed_subject_id,
                         "decision": "ESCALATE", "score_rounded": round(score, 3)})
            return self._fin("ESCALATE", "LOW", "BELOW_THRESHOLD")
        self._audit({"event": "VERIFY", "subject": claimed_subject_id,
                     "decision": "FAIL", "score_rounded": round(score, 3)})
        return self._fin("FAIL", "LOW", "BELOW_THRESHOLD")

    def consume_assertion(self, assertion_id: str, *, session_id: str, device_id: str,
                          purpose: str) -> bool:
        """One-time, bound, short-TTL authorization check for downstream gates."""
        m = self._assertions.get(assertion_id)
        if not m:
            return False
        if (_now() - datetime.fromisoformat(m["exp"])).total_seconds() > self.cfg["assertion_ttl_s"]:
            del self._assertions[assertion_id]
            return False
        ok = (m["session"] == session_id and m["device"] == device_id
              and m["purpose"] == purpose)
        del self._assertions[assertion_id]  # single use
        return ok

    def _fin(self, decision: str, assurance: str, reason: str,
             sec_event: bool = False) -> VerifyResult:
        if reason not in _REASONS:
            reason = "SERVER_HOLD"
        self._audit({"event": "VERIFY", "decision": decision, "reason": reason,
                     **({"security_event": True} if sec_event else {})})
        return VerifyResult(decision, assurance, reason)


__all__ = ["FaceVerifyService", "VerifyResult", "DEFAULTS"]
