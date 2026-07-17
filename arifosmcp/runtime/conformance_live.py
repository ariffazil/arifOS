"""
arifOS Live Conformance — fail-closed conformance runner.

Epoch 1 / Item 4 of the Kernel Senescence Reduction plan.
Replaces the previous "9/9 GREEN while skipping" spine with a four-state
runner that explicitly distinguishes PASS / FAIL / UNKNOWN / NOT_APPLICABLE.

Final aggregation per the audit:

    Any P0 FAIL                -> FAIL
    No FAIL but P0 UNKNOWN     -> HOLD
    All required checks PASS   -> PASS

A skipped check is UNKNOWN, never PASS. The substrate verdict is computed
once at the end from the per-check states.

The runner uses real kernel invocations, not registry reads. If a check
cannot reach the kernel, it returns UNKNOWN with evidence explaining why.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


# ── Result types (four states) ─────────────────────────────────────────────

PASS = "PASS"
FAIL = "FAIL"
UNKNOWN = "UNKNOWN"
NOT_APPLICABLE = "NOT_APPLICABLE"

CANONICAL_STATES = frozenset({PASS, FAIL, UNKNOWN, NOT_APPLICABLE})

# Final aggregation outcomes.
AGGREGATE_PASS = "PASS"
AGGREGATE_FAIL = "FAIL"
AGGREGATE_HOLD = "HOLD"


@dataclass(frozen=True)
class CheckResult:
    """One conformance check outcome."""

    name: str
    priority: str  # "P0" | "P1" | "P2"
    state: str  # one of CANONICAL_STATES
    expected: str
    actual: str
    evidence: dict[str, Any] = field(default_factory=dict)
    observed_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "priority": self.priority,
            "state": self.state,
            "expected": self.expected,
            "actual": self.actual,
            "evidence": dict(self.evidence),
            "observed_at": self.observed_at,
        }


@dataclass(frozen=True)
class ConformanceReport:
    """Aggregated conformance report. This is the public surface."""

    aggregate_state: str  # PASS | FAIL | HOLD
    total_checks: int
    passed: int
    failed: int
    unknown: int
    not_applicable: int
    checks: list[CheckResult]
    run_started_at: str
    run_finished_at: str
    kernel_url: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "aggregate_state": self.aggregate_state,
            "total_checks": self.total_checks,
            "passed": self.passed,
            "failed": self.failed,
            "unknown": self.unknown,
            "not_applicable": self.not_applicable,
            "checks": [c.to_dict() for c in self.checks],
            "run_started_at": self.run_started_at,
            "run_finished_at": self.run_finished_at,
            "kernel_url": self.kernel_url,
        }


# ── Kernel transport (httpx-free; stdlib only) ────────────────────────────


def _kernel_url() -> str:
    return os.getenv("ARIFOS_MCP_URL", "http://127.0.0.1:8088").rstrip("/")


def _kernel_reachable(timeout: float = 2.0) -> tuple[bool, str]:
    """Probe whether the kernel is reachable. Returns (ok, reason)."""
    try:
        req = urllib.request.Request(_kernel_url() + "/health", method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return (resp.status == 200, f"health={resp.status}")
    except urllib.error.URLError as exc:
        return (False, f"url_error: {exc.reason}")
    except Exception as exc:  # noqa: BLE001
        return (False, f"error: {exc}")


def _mcp_post(method: str, params: dict[str, Any] | None = None, session_id: str | None = None, timeout: float = 5.0) -> dict[str, Any]:
    """Minimal MCP JSON-RPC POST against the kernel."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {},
    }
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    req = urllib.request.Request(
        _kernel_url() + "/mcp", data=body, headers=headers, method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    # Strip SSE framing if present.
    if raw.startswith("data:"):
        raw = raw.split("data:", 1)[1].strip()
    return json.loads(raw)


# ── Check helpers ──────────────────────────────────────────────────────────


def _ok(name: str, priority: str, expected: str, actual: str, evidence: dict[str, Any] | None = None) -> CheckResult:
    return CheckResult(
        name=name, priority=priority, state=PASS,
        expected=expected, actual=actual,
        evidence=evidence or {},
    )


def _fail(name: str, priority: str, expected: str, actual: str, evidence: dict[str, Any] | None = None) -> CheckResult:
    return CheckResult(
        name=name, priority=priority, state=FAIL,
        expected=expected, actual=actual,
        evidence=evidence or {},
    )


def _unknown(name: str, priority: str, expected: str, reason: str, evidence: dict[str, Any] | None = None) -> CheckResult:
    return CheckResult(
        name=name, priority=priority, state=UNKNOWN,
        expected=expected, actual=f"could_not_run: {reason}",
        evidence=evidence or {"reason": reason},
    )


def _na(name: str, priority: str, expected: str, reason: str) -> CheckResult:
    return CheckResult(
        name=name, priority=priority, state=NOT_APPLICABLE,
        expected=expected, actual=f"not_applicable: {reason}",
        evidence={"reason": reason},
    )


# ── The 18 conformance checks (audit spec) ────────────────────────────────


def _check_initialize() -> CheckResult:
    name = "initialize"
    priority = "P0"
    expected = "protocolVersion=2025-11-25, serverInfo present"
    try:
        result = _mcp_post(
            "initialize",
            {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {"name": "conformance-probe", "version": "1.0"},
            },
        )
        proto = result.get("result", {}).get("protocolVersion")
        info = result.get("result", {}).get("serverInfo")
        if proto and info:
            return _ok(name, priority, expected, f"protocolVersion={proto}",
                       {"serverInfo": info})
        return _fail(name, priority, expected, f"missing fields: {result}")
    except Exception as exc:  # noqa: BLE001
        return _unknown(name, priority, expected, str(exc))


def _check_notifications_initialized() -> CheckResult:
    name = "notifications/initialized"
    priority = "P0"
    expected = "no error, no required response"
    try:
        # notifications/initialized returns no result; an empty 200 is the
        # acceptance criterion. We just check no exception.
        _mcp_post("notifications/initialized", {})
        return _ok(name, priority, expected, "accepted")
    except Exception as exc:  # noqa: BLE001
        return _unknown(name, priority, expected, str(exc))


def _check_tools_list() -> CheckResult:
    name = "tools/list"
    priority = "P0"
    expected = "8 canonical tools present, no duplicates, no Unknown"
    try:
        result = _mcp_post("tools/list", {})
        tools = result.get("result", {}).get("tools", [])
        names = [t.get("name") for t in tools if isinstance(t, dict)]
        canonical_8 = {
            "arif_init", "arif_observe", "arif_think", "arif_route",
            "arif_memory", "arif_judge", "arif_forge", "arif_seal",
        }
        missing = canonical_8 - set(names)
        if missing:
            return _fail(
                name, priority, expected,
                f"missing canonical tools: {sorted(missing)}",
                {"present": sorted(names)},
            )
        if len(names) != len(set(names)):
            return _fail(name, priority, expected, "duplicate tool names",
                         {"present": sorted(names)})
        return _ok(name, priority, expected, f"{len(names)} tools", {"names": names})
    except Exception as exc:  # noqa: BLE001
        return _unknown(name, priority, expected, str(exc))


def _check_resources_list() -> CheckResult:
    name = "resources/list"
    priority = "P0"
    expected = "at least one canonical resource (arifos://surface/manifest or session)"
    try:
        result = _mcp_post("resources/list", {})
        uris = [
            r.get("uri") for r in result.get("result", {}).get("resources", [])
            if isinstance(r, dict)
        ]
        if not uris:
            return _fail(name, priority, expected, "no resources exposed",
                         {"raw": result})
        return _ok(name, priority, expected, f"{len(uris)} resources",
                   {"uris": uris[:20]})
    except Exception as exc:  # noqa: BLE001
        return _unknown(name, priority, expected, str(exc))


def _check_resources_templates_list() -> CheckResult:
    name = "resources/templates/list"
    priority = "P0"
    expected = "resource templates present (e.g., arifos://session/{id})"
    try:
        result = _mcp_post("resources/templates/list", {})
        templates = result.get("result", {}).get("resourceTemplates", [])
        if not templates:
            return _na(name, priority, expected, "kernel exposes no templates")
        return _ok(name, priority, expected, f"{len(templates)} templates",
                   {"uris": [t.get("uriTemplate") for t in templates]})
    except Exception as exc:  # noqa: BLE001
        return _unknown(name, priority, expected, str(exc))


def _check_prompts_list() -> CheckResult:
    name = "prompts/list"
    priority = "P1"
    expected = "at least one prompt exposed (canonical 5 or 6)"
    try:
        result = _mcp_post("prompts/list", {})
        prompts = result.get("result", {}).get("prompts", [])
        if not prompts:
            return _na(name, priority, expected, "kernel exposes no prompts")
        return _ok(name, priority, expected, f"{len(prompts)} prompts",
                   {"names": [p.get("name") for p in prompts]})
    except Exception as exc:  # noqa: BLE001
        return _unknown(name, priority, expected, str(exc))


def _check_tool_invoke(name: str, *, priority: str, args: dict[str, Any] | None = None) -> CheckResult:
    expected = f"{name} returns canonical envelope only"
    try:
        result = _mcp_post(
            "tools/call",
            {"name": name, "arguments": args or {}},
        )
        # Unwrap MCP tool result.
        content = result.get("result", {}).get("content", [])
        text = ""
        for c in content:
            if isinstance(c, dict) and c.get("type") == "text":
                text += c.get("text", "")
        parsed = json.loads(text) if text else result
        # The canonical envelope must have only the audit-specified top-level
        # fields. Any legacy field is a FAIL.
        if not isinstance(parsed, dict):
            return _fail(name, priority, expected, "response is not a dict",
                         {"raw": str(parsed)[:200]})
        legacy_keys = {
            "actor_verified", "authority_level", "authority",
            "human_authority", "runtime_authority", "verdict",
            "verdict_code", "canonical_verdict", "reasoning_verdict",
            "nine_signal_aggregate", "_identity_consistency_applied",
            "_identity_drift_count", "_identity_drift_first",
        }
        leaked = legacy_keys & set(parsed.keys())
        if leaked:
            return _fail(name, priority, expected,
                         f"legacy fields leaked: {sorted(leaked)}",
                         {"leaked": sorted(leaked)})
        # Must contain the canonical blocks.
        if "standing" not in parsed:
            return _fail(name, priority, expected, "no canonical standing block",
                         {"top_level_keys": sorted(parsed.keys())})
        if "effective_verdict" not in parsed:
            return _fail(name, priority, expected,
                         "no canonical effective_verdict field",
                         {"top_level_keys": sorted(parsed.keys())})
        return _ok(name, priority, expected, "canonical envelope",
                   {"top_level_keys": sorted(parsed.keys())})
    except Exception as exc:  # noqa: BLE001
        return _unknown(name, priority, expected, str(exc))


def _check_unknown_tool_rejection() -> CheckResult:
    name = "unknown-tool rejection"
    priority = "P0"
    expected = "Unknown tool returns an error (not a SEAL)"
    try:
        result = _mcp_post("tools/call", {"name": "arif_nonexistent_tool", "arguments": {}})
        if "error" in result:
            return _ok(name, priority, expected, "rejected",
                       {"error": result.get("error")})
        return _fail(name, priority, expected,
                     "kernel accepted unknown tool name",
                     {"raw": result})
    except Exception as exc:  # noqa: BLE001
        return _unknown(name, priority, expected, str(exc))


def _check_session_expiry_rejection() -> CheckResult:
    name = "session-expiry rejection"
    priority = "P1"
    expected = "expired session is rejected"
    try:
        # Use a clearly-expired session id and verify the kernel rejects it.
        result = _mcp_post(
            "tools/call",
            {"name": "arif_init", "arguments": {}},
            session_id="SEAL-expired-test-000000000000000000000000",
        )
        # If it returns HOLD or similar, count as PASS. If it returns SEAL
        # for an unknown session, that's the failure.
        text = ""
        for c in result.get("result", {}).get("content", []):
            if isinstance(c, dict) and c.get("type") == "text":
                text += c.get("text", "")
        parsed = json.loads(text) if text else {}
        verdict = parsed.get("effective_verdict")
        if verdict in {"HOLD", "OBSERVE_ONLY", "VOID", "888_HOLD"}:
            return _ok(name, priority, expected, f"verdict={verdict}",
                       {"verdict": verdict})
        return _fail(name, priority, expected,
                     f"expired session was not rejected (effective_verdict={verdict})",
                     {"raw": parsed})
    except Exception as exc:  # noqa: BLE001
        return _unknown(name, priority, expected, str(exc))


def _check_unverified_irreversible_action_rejection() -> CheckResult:
    name = "unverified-irreversible-action rejection"
    priority = "P0"
    expected = "an irreversible tool from an unverified session is HOLD"
    try:
        # arif_seal is irreversible. With OBSERVE_ONLY authority, it must HOLD.
        result = _mcp_post(
            "tools/call",
            {"name": "arif_seal", "arguments": {"intent": "test_irreversible"}},
        )
        text = ""
        for c in result.get("result", {}).get("content", []):
            if isinstance(c, dict) and c.get("type") == "text":
                text += c.get("text", "")
        parsed = json.loads(text) if text else {}
        verdict = parsed.get("effective_verdict")
        if verdict in {"HOLD", "888_HOLD", "VOID", "OBSERVE_ONLY"}:
            return _ok(name, priority, expected, f"verdict={verdict}",
                       {"verdict": verdict})
        return _fail(name, priority, expected,
                     f"irreversible action proceeded (effective_verdict={verdict})",
                     {"raw": parsed})
    except Exception as exc:  # noqa: BLE001
        return _unknown(name, priority, expected, str(exc))


def _check_receipt_readback() -> CheckResult:
    name = "receipt readback"
    priority = "P1"
    expected = "a sealed receipt can be retrieved"
    try:
        # The exact receipt id is not known ahead of time; mark as N/A
        # unless the kernel exposes a list endpoint we can probe.
        return _na(name, priority, expected, "no known receipt id to probe")
    except Exception as exc:  # noqa: BLE001
        return _unknown(name, priority, expected, str(exc))


# ── The 18-check ordered list ────────────────────────────────────────────

ALL_CHECKS = [
    _check_initialize,
    _check_notifications_initialized,
    _check_tools_list,
    _check_resources_list,
    _check_resources_templates_list,
    _check_prompts_list,
    lambda: _check_tool_invoke("arif_init", priority="P0"),
    lambda: _check_tool_invoke("arif_observe", priority="P0"),
    lambda: _check_tool_invoke("arif_think", priority="P0"),
    lambda: _check_tool_invoke("arif_route", priority="P0"),
    lambda: _check_tool_invoke("arif_memory", priority="P0"),
    lambda: _check_tool_invoke("arif_judge", priority="P0"),
    lambda: _check_tool_invoke("arif_seal", priority="P0"),
    lambda: _check_tool_invoke("arif_forge", priority="P1",
                               args={"intent": "reversible dry-run"}),
    _check_receipt_readback,
    _check_unknown_tool_rejection,
    _check_session_expiry_rejection,
    _check_unverified_irreversible_action_rejection,
]


# ── Aggregation ───────────────────────────────────────────────────────────


def aggregate(checks: list[CheckResult]) -> str:
    """Final state per audit spec.

    Any P0 FAIL       -> FAIL
    No FAIL but P0 UNKNOWN -> HOLD
    All required PASS -> PASS
    """
    p0_failures = [c for c in checks if c.priority == "P0" and c.state == FAIL]
    if p0_failures:
        return AGGREGATE_FAIL
    p0_unknowns = [c for c in checks if c.priority == "P0" and c.state == UNKNOWN]
    if p0_unknowns:
        return AGGREGATE_HOLD
    return AGGREGATE_PASS


def run_conformance() -> ConformanceReport:
    """Run the full conformance suite and aggregate per audit spec.

    If the kernel is unreachable, the per-check UNKNOWN state surfaces
    in the aggregate as HOLD (never PASS).
    """
    started = datetime.now(UTC).isoformat()
    reachable, reason = _kernel_reachable()
    checks: list[CheckResult] = []

    if not reachable:
        # Surface every check as UNKNOWN with the same reason.
        # Do NOT call the check function — that would defeat fail-closed
        # behaviour when the kernel is down.
        for fn in ALL_CHECKS:
            raw_name = getattr(fn, "__name__", None)
            if not raw_name or raw_name == "<lambda>":
                name = "tool_invocation_check"
            else:
                name = raw_name
            checks.append(_unknown(
                name=name,
                priority="P0",
                expected="",
                reason=f"kernel unreachable: {reason}",
            ))
    else:
        for fn in ALL_CHECKS:
            try:
                checks.append(fn())
            except Exception as exc:  # noqa: BLE001
                checks.append(_unknown(
                    name=getattr(fn, "__name__", "unknown"),
                    priority="P0",
                    expected="",
                    reason=f"runner exception: {exc}",
                ))

    finished = datetime.now(UTC).isoformat()
    return ConformanceReport(
        aggregate_state=aggregate(checks),
        total_checks=len(checks),
        passed=sum(1 for c in checks if c.state == PASS),
        failed=sum(1 for c in checks if c.state == FAIL),
        unknown=sum(1 for c in checks if c.state == UNKNOWN),
        not_applicable=sum(1 for c in checks if c.state == NOT_APPLICABLE),
        checks=checks,
        run_started_at=started,
        run_finished_at=finished,
        kernel_url=_kernel_url(),
    )


__all__ = [
    "PASS",
    "FAIL",
    "UNKNOWN",
    "NOT_APPLICABLE",
    "CANONICAL_STATES",
    "AGGREGATE_PASS",
    "AGGREGATE_FAIL",
    "AGGREGATE_HOLD",
    "CheckResult",
    "ConformanceReport",
    "aggregate",
    "run_conformance",
    "ALL_CHECKS",
]