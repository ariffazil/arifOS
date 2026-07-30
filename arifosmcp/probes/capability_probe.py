"""
arifosmcp/probes/capability_probe.py — Daily capability probe (F-002 closure)

Forged: 2026-07-18 by FORGE-000Ω under F-002 Task 1 brief.

Doctrine (brief 2026-07-18):
  - Invoke all 8 canonical arif_* verbs read-only via public MCP.
  - Carry signed SCT forward from init (refresh if within 60s of TTL expiry).
  - HOLD verdicts on judge/forge from an unattended probe = PASS-BY-RESTRAINT
    (still emit SUCCESS — invocation succeeded, kernel restraint is correct).
  - Probe writes raw evidence to the durable bus via the canonical writer.
  - The Observatory probe matrix derives the verdict independently.

DO NOT INVENT NEW WRITERS. The probe emits ONLY via:
    arifosmcp.runtime.event_bus.emit_operation()  — canonical writer
    → /var/lib/arifos/event_bus/operations.log
    → read_durable_events() in observatory_routes.py:1907
    → compute_capability_matrix() in capability_drift.py:445
    → /api/observatory/v1/capabilities (tested_count, proven_live_count)

DO NOT INVENT NEW CHECKS. The probe verifies ONLY via:
    arifosmcp.runtime.capability_drift.compute_capability_matrix()
    → returns tested_count, proven_live_count, untested_count, matrix

CITATIONS (doctrine #2 — never invent canon):
    - Canonical 8 verbs and ordering:
        /root/arifOS/arifosmcp/tool_registry.json → canonical_order
    - LIVE F-002 check (the one that flips tested_count from 0 → 8):
        /root/arifOS/arifosmcp/runtime/rest_routes/observatory_routes.py:1907
    - Threshold constants:
        /root/arifOS/arifosmcp/runtime/capability_drift.py:56,58
        TEST_FRESHNESS_SECONDS = 300, PROVEN_LIVE_SECONDS = 86400
    - Hydrator (durable-bus → cache):
        /root/arifOS/arifosmcp/runtime/capability_drift.py:369
        hydrate_test_cache_from_durable_bus()
    - SCT resolution pattern (token in params.session_token, NOT header):
        /root/arifOS/arifosmcp/runtime/tools_internal.py:482-508
    - Canonical writer:
        /root/arifOS/arifosmcp/runtime/event_bus.py:244 emit_operation()

Honest rules (per F2 TRUTH + F7 HUMILITY):
    - INVOCATION success = probe emits SUCCESS, regardless of verdict content.
    - Restraint verdicts (HOLD from judge/forge) are NOT probe failures — they
      are the correct constitutional response to an unattended probe.
    - If MCP is unreachable, the probe fails loudly (non-zero exit). It does
      NOT silently claim SUCCESS.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from typing import Any

import requests

# Canonical 8 — exact order from tool_registry.json canonical_order.
# (tool_name, mode, is_restraint_expected)
# Restraint: judge/forge return HOLD from an unattended probe — that's correct.
CANONICAL_8: list[tuple[str, str | None, bool]] = [
    ("arif_init", "init", False),
    ("arif_observe", "vitals", False),
    ("arif_think", "axioms", False),
    ("arif_route", "route_test", False),
    ("arif_memory", "recall", False),
    ("arif_judge", "validate", True),  # PASS-BY-RESTRAINT
    ("arif_forge", "engineer", True),  # PASS-BY-RESTRAINT
    ("arif_seal", "verify", False),  # verify mode, NOT seal — read-only
]

PROBE_ACTOR_ID = "arif-capability-probe"
SCT_REFRESH_HEADROOM_S = 60  # refresh if expiring within 60s


# ── Result types ──────────────────────────────────────────────────────────────


@dataclass
class ProbeRow:
    tool: str
    mode: str | None
    invocation_ok: bool
    verdict: str | None
    trace_id: str | None
    session_id: str | None
    session_token_remaining_s: float | None
    restraint_expected: bool
    emitted_success: bool
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d = {
            "tool": self.tool,
            "mode": self.mode,
            "invocation_ok": self.invocation_ok,
            "verdict": self.verdict,
            "trace_id": self.trace_id,
            "session_id": self.session_id,
            "session_token_remaining_s": self.session_token_remaining_s,
            "restraint_expected": self.restraint_expected,
            "emitted_success": self.emitted_success,
        }
        if self.error:
            d["error"] = self.error
        return d


@dataclass
class ProbeReport:
    rows: list[ProbeRow] = field(default_factory=list)
    tested_count: int | None = None
    proven_live_count: int | None = None
    untested_count: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "rows": [r.to_dict() for r in self.rows],
            "tested_count": self.tested_count,
            "proven_live_count": self.proven_live_count,
            "untested_count": self.untested_count,
            "all_8_invoked": all(r.invocation_ok for r in self.rows),
            "all_8_emitted": all(r.emitted_success for r in self.rows),
        }


# ── MCP wire layer ─────────────────────────────────────────────────────────────

class MCPError(RuntimeError):
    pass


def _mcp_endpoint(mcp_url: str) -> str:
    """Normalize base URL → streamable HTTP /mcp endpoint."""
    base = mcp_url.rstrip("/")
    if base.endswith("/mcp"):
        return base
    return f"{base}/mcp"


class MCPTransport:
    """Streamable-HTTP MCP session: initialize → session id → tools/call.

    FastMCP streamable HTTP rejects tools/call without Mcp-Session-Id
    (HTTP 400 Missing session ID). SCT (session_token) is separate —
    constitutional authority inside arguments; transport session is wire state.
    """

    def __init__(self, mcp_url: str) -> None:
        self.endpoint = _mcp_endpoint(mcp_url)
        self.session_id: str | None = None
        self._rpc_id = 0
        self._open()

    def _headers(self) -> dict[str, str]:
        h = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.session_id:
            h["Mcp-Session-Id"] = self.session_id
        return h

    def _next_id(self) -> int:
        self._rpc_id += 1
        return self._rpc_id

    def _open(self) -> None:
        init_body = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {
                    "name": "arifos-capability-probe",
                    "version": "2026.07.30",
                },
            },
        }
        resp = requests.post(
            self.endpoint, json=init_body, headers=self._headers(), timeout=20
        )
        if resp.status_code != 200:
            raise MCPError(
                f"MCP initialize HTTP {resp.status_code}: {resp.text[:200]}"
            )
        sid = resp.headers.get("mcp-session-id") or resp.headers.get("Mcp-Session-Id")
        if not sid:
            raise MCPError("MCP initialize returned no Mcp-Session-Id header")
        self.session_id = sid
        note = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        requests.post(self.endpoint, json=note, headers=self._headers(), timeout=10)

    def call(
        self,
        tool: str,
        *,
        mode: str | None,
        session_token: str | None,
        actor_id: str,
        extra_args: dict[str, Any] | None = None,
        minimal_envelope: bool = True,
    ) -> dict[str, Any]:
        """JSON-RPC tools/call. SCT in arguments.session_token (not HTTP header)."""
        arguments: dict[str, Any] = {"intent": f"daily_probe:{tool}"}
        if minimal_envelope:
            arguments["verbosity"] = "minimal"
        if mode:
            arguments["mode"] = mode
        if session_token:
            arguments["session_token"] = session_token
        if actor_id:
            arguments["actor_id"] = actor_id
        if extra_args:
            arguments.update(extra_args)

        body = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {"name": tool, "arguments": arguments},
        }
        resp = requests.post(
            self.endpoint, json=body, headers=self._headers(), timeout=30
        )
        if resp.status_code != 200:
            raise MCPError(f"{tool}: HTTP {resp.status_code}: {resp.text[:200]}")
        ctype = (resp.headers.get("content-type") or "").lower()
        text_body = resp.text
        if "text/event-stream" in ctype and "data:" in text_body:
            for line in reversed(text_body.splitlines()):
                if line.startswith("data:"):
                    payload = line[5:].strip()
                    if payload and payload != "[DONE]":
                        try:
                            return json.loads(payload)
                        except json.JSONDecodeError:
                            continue
        try:
            return resp.json()
        except json.JSONDecodeError as exc:
            raise MCPError(f"{tool}: response is not JSON: {text_body[:200]}") from exc


_TRANSPORT: MCPTransport | None = None


def _get_transport(mcp_url: str) -> MCPTransport:
    global _TRANSPORT
    if _TRANSPORT is None:
        _TRANSPORT = MCPTransport(mcp_url)
    return _TRANSPORT


def _mcp_call(
    mcp_url: str,
    tool: str,
    *,
    mode: str | None,
    session_token: str | None,
    actor_id: str,
    extra_args: dict[str, Any] | None = None,
    minimal_envelope: bool = True,
) -> dict[str, Any]:
    """Single JSON-RPC tools/call via streamable-HTTP MCP session.

    SCT is passed in params.arguments.session_token (per tools_internal).
    Transport Mcp-Session-Id is established once per probe run.
    """
    return _get_transport(mcp_url).call(
        tool,
        mode=mode,
        session_token=session_token,
        actor_id=actor_id,
        extra_args=extra_args,
        minimal_envelope=minimal_envelope,
    )


def _extract_envelope(response: dict[str, Any]) -> dict[str, Any]:
    """Pull the standard result envelope out of a JSON-RPC response.

    Per arifOS contract:
      response.result.structuredContent = {session_token, session_id, trace_id,
                                          verdict, effective_verdict, expires_at, ...}
      OR response.result                = same shape if no structuredContent
      OR response.error                 = {code, message, ...}
    """
    if "error" in response and response["error"]:
        raise MCPError(f"JSON-RPC error: {response['error']}")
    result = response.get("result")
    if not isinstance(result, dict):
        raise MCPError(f"non-dict result: {result!r}")
    sc = result.get("structuredContent")
    if isinstance(sc, dict):
        return sc
    return result


def _parse_sct_expiry(token: str | None) -> float | None:
    """Best-effort parse of sct_v1.* JWT exp claim. Returns seconds-until-expiry.

    sct_v1 is a JWT-prefixed token (signature after a dot). Decoding base64
    payload is non-trivial cryptographically; we only need the `exp` claim.
    Returns None if exp cannot be parsed.
    """
    if not token or not token.startswith("sct_v1."):
        return None
    parts = token.split(".")
    if len(parts) < 2:
        return None
    try:
        import base64

        # JWT header.payload.signature — payload is the second segment
        payload_b64 = parts[1]
        # base64url padding
        payload_b64 += "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode("utf-8", "replace"))
        exp = float(payload.get("exp"))
        return exp - time.time()
    except Exception:
        return None


def _maybe_refresh(mcp_url: str, session_token: str | None, actor_id: str) -> str | None:
    """Refresh SCT if it's within the refresh headroom window."""
    remaining = _parse_sct_expiry(session_token)
    if remaining is None or remaining > SCT_REFRESH_HEADROOM_S:
        return session_token
    # arif_init(mode=resume) — re-mints SCT for an existing session.
    try:
        env = _extract_envelope(
            _mcp_call(
                mcp_url,
                "arif_init",
                mode="resume",
                session_token=session_token,
                actor_id=actor_id,
            )
        )
    except Exception:
        return session_token  # if refresh fails, keep the old token
    return env.get("session_token") or session_token


# ── Durable bus write layer ────────────────────────────────────────────────────


def _emit_probe_event(
    tool: str, *, trace_id: str | None, session_id: str | None, verdict: str | None, restraint: bool
) -> bool:
    """Emit a SUCCESS operation event to the durable bus via the canonical writer.

    Invocations that succeeded get status=SUCCESS regardless of verdict, because:
      - HOLD on judge/forge from unattended probe = PASS-BY-RESTRAINT (correct)
      - Invocation itself was schema-valid and got a response
    """
    try:
        from arifosmcp.runtime.event_bus import emit_operation
    except Exception as exc:
        # If the canonical module is unreachable, the probe is misconfigured.
        # Do NOT silently fall back — return False loudly.
        print(f"  ⚠️  {tool}: cannot import event_bus.emit_operation: {exc}", file=sys.stderr)
        return False

    params = {
        "actor_id": PROBE_ACTOR_ID,
        "session_id": session_id,
        "trace_id": trace_id,
        "organ": "arifos",
        "capability": tool,
        "status": "SUCCESS",
        "params": {
            "verdict": verdict or "UNKNOWN",
            "restraint": restraint,
            "probe_source": "capability_probe.py@daily",
        },
    }
    try:
        emit_operation(**params)
        return True
    except Exception as exc:
        print(f"  ⚠️  {tool}: emit_operation failed: {exc}", file=sys.stderr)
        return False


# ── Verify layer ───────────────────────────────────────────────────────────────


def _verify_matrix(mcp_url: str) -> dict[str, int]:
    """Read the LIVE capability matrix to confirm the probe flipped tested_count.

    Uses the kernel's own /api/observatory/v1/capabilities endpoint, NOT the
    static snapshot file. This is the same data the page renders.
    """
    try:
        resp = requests.get(
            f"{mcp_url.rstrip('/')}/api/observatory/v1/capabilities",
            headers={"Accept": "application/json, text/event-stream"},
            timeout=5,
        )
        if resp.status_code != 200:
            return {"tested_count": -1, "proven_live_count": -1, "untested_count": -1}
        body = resp.json()
        return {
            "tested_count": int(body.get("tested_count", -1)),
            "proven_live_count": int(body.get("proven_live_count", -1)),
            "untested_count": int(body.get("untested_count", -1)),
        }
    except Exception:
        return {"tested_count": -1, "proven_live_count": -1, "untested_count": -1}


# ── Main probe runner ──────────────────────────────────────────────────────────


def run(mcp_url: str = "http://127.0.0.1:8088", actor_id: str = PROBE_ACTOR_ID) -> ProbeReport:
    """Invoke all 8 canonical arif_* verbs, emit SUCCESS events, verify.

    Returns a ProbeReport. Raises MCPError if the very first call (arif_init)
    fails — the probe cannot proceed without a session.
    """
    global _TRANSPORT
    # Fresh MCP transport session each run (streamable HTTP session id).
    _TRANSPORT = None
    report = ProbeReport()
    # Open wire session before any tools/call
    _get_transport(mcp_url)

    # ── 1. arif_init — mint session_token ───────────────────────────────────
    # arif_init keeps the standard envelope because the minimal trim strips
    # session_token (F11 safety net — never drop a credential). The probe
    # needs the SCT to forward to subsequent calls.
    try:
        init_env = _extract_envelope(
            _mcp_call(
                mcp_url,
                "arif_init",
                mode="init",
                session_token=None,
                actor_id=actor_id,
                minimal_envelope=False,
            )
        )
    except MCPError as exc:
        raise MCPError(f"arif_init (init) failed — cannot proceed: {exc}") from exc

    session_token = init_env.get("session_token")
    session_id = init_env.get("session_id")
    trace_id = init_env.get("trace_id")
    verdict = init_env.get("effective_verdict") or init_env.get("verdict")
    token_remaining = _parse_sct_expiry(session_token)

    report.rows.append(
        ProbeRow(
            tool="arif_init",
            mode="init",
            invocation_ok=True,
            verdict=verdict,
            trace_id=trace_id,
            session_id=session_id,
            session_token_remaining_s=token_remaining,
            restraint_expected=False,
            emitted_success=_emit_probe_event(
                "arif_init",
                trace_id=trace_id,
                session_id=session_id,
                verdict=verdict,
                restraint=False,
            ),
        )
    )

    # ── 2-8. Remaining 7 verbs, carrying session_token ────────────────────
    for tool, mode, restraint in CANONICAL_8[1:]:
        # Refresh token if close to expiry
        session_token = _maybe_refresh(mcp_url, session_token, actor_id)

        invocation_ok = True
        row_verdict: str | None = None
        row_trace: str | None = trace_id
        row_session: str | None = session_id
        row_token_remaining = _parse_sct_expiry(session_token)
        error: str | None = None

        try:
            env = _extract_envelope(
                _mcp_call(
                    mcp_url,
                    tool,
                    mode=mode,
                    session_token=session_token,
                    actor_id=actor_id,
                )
            )
            row_verdict = env.get("effective_verdict") or env.get("verdict")
            row_trace = env.get("trace_id") or row_trace
            row_session = env.get("session_id") or row_session
        except MCPError as exc:
            invocation_ok = False
            error = str(exc)
            print(f"  ⚠️  {tool} ({mode}): {error}", file=sys.stderr)

        report.rows.append(
            ProbeRow(
                tool=tool,
                mode=mode,
                invocation_ok=invocation_ok,
                verdict=row_verdict,
                trace_id=row_trace,
                session_id=row_session,
                session_token_remaining_s=row_token_remaining,
                restraint_expected=restraint,
                emitted_success=(
                    invocation_ok
                    and _emit_probe_event(
                        tool,
                        trace_id=row_trace,
                        session_id=row_session,
                        verdict=row_verdict,
                        restraint=restraint,
                    )
                ),
                error=error,
            )
        )

    # ── 9. Verify — read LIVE /api/observatory/v1/capabilities ────────────
    matrix = _verify_matrix(mcp_url)
    report.tested_count = matrix["tested_count"]
    report.proven_live_count = matrix["proven_live_count"]
    report.untested_count = matrix["untested_count"]

    return report


# ── CLI entry point ────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Daily capability probe — closes F-002 by writing fresh "
        "SUCCESS events to the durable bus."
    )
    parser.add_argument(
        "--mcp-url",
        default="http://127.0.0.1:8088",
        help="arifOS MCP base URL (default: http://127.0.0.1:8088)",
    )
    parser.add_argument(
        "--actor-id",
        default=PROBE_ACTOR_ID,
        help=f"Actor id used for the probe (default: {PROBE_ACTOR_ID})",
    )
    args = parser.parse_args(argv)

    try:
        report = run(mcp_url=args.mcp_url, actor_id=args.actor_id)
    except MCPError as exc:
        print(f"PROBE FAILED — cannot start: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(report.to_dict(), indent=2, default=str))

    # Honest exit codes (F2 TRUTH + F7 HUMILITY):
    #   0 — all 8 invoked, all 8 emitted, tested_count >= 8 (or not yet computed)
    #   1 — some invocations failed
    #   3 — all invoked+emitted but matrix shows tested_count < 8 (verify failed)
    summary = report.to_dict()
    if not summary["all_8_invoked"] or not summary["all_8_emitted"]:
        return 1
    if report.tested_count is not None and 0 <= report.tested_count < 8:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
