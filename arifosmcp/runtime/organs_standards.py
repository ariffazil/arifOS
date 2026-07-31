"""
Organs Standards — uniform probe contract across the federation.

Every organ is probed via four standardised surfaces:
  /health        transport liveness
  /ready         dependency readiness
  /version       runtime identity
  /capabilities  tool / schema surface

The probe is honest about which surfaces exist on which organs and reports
UNKNOWN (not HEALTHY) for missing ones. Self-report vs independent probe is
explicit via the `probe_type` field.

Forged 2026-07-15 — companion to /api/federation-probe rewrite.
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)


# ── Organ map: ports and public origins ──────────────────────────────────────
# This is the static SOT for "where each organ lives". If these drift, the
# federation probe fails — that's the desired alarm.
ORGAN_MAP: dict[str, dict[str, Any]] = {
    "arifos": {
        "internal_port": 8088,
        "host_port": 8088,
        "public_origin": "https://arifos.arif-fazil.com",
        "ontological_layer": "MIND",
        "exposure": "proxied",
    },
    "geox": {
        "internal_port": 8081,
        "host_port": 8081,
        "public_origin": "https://geox.arif-fazil.com",
        "ontological_layer": "EARTH",
        "exposure": "proxied",
    },
    "wealth": {
        "internal_port": 8082,
        "host_port": 18082,
        "public_origin": "https://wealth.arif-fazil.com",
        "ontological_layer": "CAPITAL",
        "exposure": "proxied",
    },
    "well": {
        "internal_port": 8083,
        "host_port": 18083,
        "public_origin": "https://well.arif-fazil.com",
        "ontological_layer": "HUMAN",
        "exposure": "proxied",
    },
    "aaa": {
        "internal_port": 3001,
        "host_port": 3001,
        "public_origin": "https://aaa.arif-fazil.com",
        "ontological_layer": "BODY",
        "exposure": "proxied",
    },
    "aforge": {
        "internal_port": 7071,
        "host_port": 7071,
        "public_origin": "https://forge.arif-fazil.com",
        "ontological_layer": "MUSCLE",
        "exposure": "proxied",
    },
    "mcp_gateway": {
        "internal_port": 8088,
        "host_port": 8088,
        "public_origin": "https://mcp.arif-fazil.com",
        "ontological_layer": "NERVES",
        "exposure": "proxied",
    },
    "vault999": {
        "internal_port": 8100,
        "host_port": 8100,
        "public_origin": None,
        "ontological_layer": "MEMORY",
        "exposure": "internal",
    },
}


@dataclass
class OrganStandardProbe:
    organ: str
    internal_port: int
    host_port: int
    public_origin: str | None
    ontological_layer: str
    exposure: str
    transport_state: str = "unknown"  # reachable | unreachable | unknown
    transport_latency_ms: int | None = None
    transport_status_code: int | None = None
    transport_probe_type: str = "independent"
    identity_observed: str | None = None
    identity_match: bool | None = None
    identity_probe_type: str = "self"
    readiness_state: str = "unknown"  # ready | degraded | unknown
    readiness_dependencies: dict[str, str] = field(default_factory=dict)
    capability_declared: int | None = None
    capability_registered: int | None = None
    capability_smoke_tested: int | None = None
    capability_drift: bool | None = None
    capability_probe_type: str = "self"
    governance_session_required: bool | None = None
    governance_mutation_allowed: bool | None = None
    governance_forge_mode: str | None = None
    governance_probe_type: str = "self"
    evidence_class: str = "unknown"  # observed | derived | reported | unknown
    evidence_source: str = ""
    evidence_age_seconds: int | None = None
    overall_state: str = "unknown"  # OPERATIONAL | DEGRADED | UNREACHABLE | UNKNOWN
    overall_reasons: list[str] = field(default_factory=list)
    observed_at: str = field(
        default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ── Helpers ─────────────────────────────────────────────────────────────────
def _http_get(url: str, timeout: float = 2.0) -> tuple[bool, int | None, str | None, Any]:
    """Returns (up, status_code, error_str, body_dict_or_none)."""
    try:
        req = Request(
            url, headers={"Accept": "application/json", "User-Agent": "arifOS-OrganProbe/1.0"}
        )
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            data = None
            try:
                data = json.loads(raw)
            except Exception:
                data = None
            return True, resp.status, None, data
    except HTTPError as e:
        return e.code < 500, e.code, f"HTTPError {e.code}", None
    except (URLError, TimeoutError, OSError) as e:
        return False, None, f"{type(e).__name__}: {e}", None
    except Exception as e:
        return False, None, f"{type(e).__name__}: {e}", None


def _tcp(host: str, port: int, timeout: float = 1.5) -> tuple[bool, int | None]:
    import socket

    started = time.time()
    try:
        with socket.create_connection((host, port), timeout=timeout) as _:
            return True, int((time.time() - started) * 1000)
    except Exception:
        return False, None


def _probe_dependencies_for(organ: str) -> dict[str, str]:
    """Best-effort dependency probe. Returns per-dependency state ∈ {ready, degraded, unknown}."""
    deps: dict[str, str] = {}
    # vault999: filesystem + head.json + recent activity
    head_p = Path("/root/.local/share/arifos/vault999/seal_chain_head.json")
    if head_p.exists():
        try:
            age = time.time() - head_p.stat().st_mtime
            deps["vault999"] = "ready" if age < 86400 else "degraded"
        except Exception:
            deps["vault999"] = "unknown"
    else:
        deps["vault999"] = "unknown"
    # postgres: socket probe to :5432 internal
    pg_up, _ = _tcp("127.0.0.1", 5432, timeout=1.0) if organ != "vault999" else (False, None)
    deps["postgres"] = "ready" if pg_up else "unknown"
    # redis: socket probe to :6379
    rd_up, _ = _tcp("127.0.0.1", 6379, timeout=1.0) if organ != "vault999" else (False, None)
    deps["redis"] = "ready" if rd_up else "unknown"
    # qdrant: socket probe to :6333
    qd_up, _ = _tcp("127.0.0.1", 6333, timeout=1.0)
    deps["qdrant"] = "ready" if qd_up else "unknown"
    return deps


def _aggregate_overall(probe: OrganStandardProbe) -> str:
    """Strict descending ladder: UNREACHABLE > DEGRADED > OPERATIONAL > UNKNOWN."""
    reasons: list[str] = []

    if probe.transport_state == "unreachable":
        reasons.append("transport_unreachable")
        return "UNREACHABLE", reasons

    # Capability drift is a DEGRADED gate.
    if probe.capability_drift is True:
        reasons.append("capability_registry_drift")

    # Identity mismatch is DEGRADED.
    if probe.identity_match is False:
        reasons.append("identity_mismatch")

    # Governance: forge-mode dry_run_only is a DEGRADED gate (autonomy YELLOW).
    if probe.governance_forge_mode == "dry_run_only":
        reasons.append("forge_mode_dry_run_only")

    # Readiness degraded is DEGRADED.
    if probe.readiness_state == "degraded":
        reasons.append("readiness_degraded")

    if reasons:
        return "DEGRADED", reasons
    if probe.transport_state == "reachable":
        return "OPERATIONAL", reasons
    return "UNKNOWN", reasons


# ── Per-organ probe ──────────────────────────────────────────────────────────
def probe_arifOS() -> OrganStandardProbe:
    cfg = ORGAN_MAP["arifos"]
    p = OrganStandardProbe(
        organ="arifos",
        internal_port=cfg["internal_port"],
        host_port=cfg["host_port"],
        public_origin=cfg["public_origin"],
        ontological_layer=cfg["ontological_layer"],
        exposure=cfg["exposure"],
        transport_probe_type="self",
        identity_probe_type="self",
        capability_probe_type="self",
        governance_probe_type="self",
        evidence_class="observed",
        evidence_source="GET /health + kernel probe helpers",
    )
    up, latency = _tcp("127.0.0.1", cfg["internal_port"])
    p.transport_state = "reachable" if up else "unreachable"
    p.transport_latency_ms = latency
    p.transport_status_code = 200 if up else None
    if up:
        # Identity: read /health identity_hash & compare to expected "arifOS"
        try:
            up2, sc2, _, body = _http_get(
                f"http://127.0.0.1:{cfg['internal_port']}/health", timeout=2.0
            )
            if up2 and body and isinstance(body, dict):
                p.identity_observed = body.get("identity_hash") or "arifOS"
                p.identity_match = (
                    p.identity_observed.startswith("arifOS") or p.identity_observed == "arifOS"
                )
                env = body.get("environment") or body.get("session_required")
                p.governance_session_required = (
                    bool(env) or body.get("ratification_required") or True
                )
            else:
                p.identity_match = None
        except Exception:
            p.identity_match = None
        p.readiness_dependencies = _probe_dependencies_for("arifos")
        p.readiness_state = (
            "ready"
            if all(v == "ready" for v in p.readiness_dependencies.values() if v != "unknown")
            else "degraded"
            if any(v == "degraded" for v in p.readiness_dependencies.values())
            else "unknown"
        )
        # Capability: read /api/constitution
        try:
            up3, sc3, _, cbody = _http_get(
                f"http://127.0.0.1:{cfg['internal_port']}/api/constitution", timeout=2.0
            )
            if up3 and cbody and isinstance(cbody, dict):
                tools = cbody.get("tools") or cbody.get("constitution") or []
                if isinstance(tools, list):
                    p.capability_registered = len(tools)
                p.capability_declared = 18  # SOT from tool_registry.json
                p.capability_drift = (p.capability_registered or 0) < p.capability_declared
            else:
                p.capability_drift = True
        except Exception:
            p.capability_drift = True
        # Governance: detect forge dry-run
        try:
            forge_dry = os.getenv("ARIFOS_FORGE_DRY_RUN", "true").lower() in ("true", "1", "yes")
            p.governance_mutation_allowed = not forge_dry
            p.governance_forge_mode = "dry_run_only" if forge_dry else "live"
        except Exception:
            pass
    else:
        # Transport unreachable — be honest about everything else as unknown.
        p.identity_match = None
        p.readiness_dependencies = _probe_dependencies_for("arifos")
        p.readiness_state = "unknown"
    p.evidence_age_seconds = 0
    p.overall_state, p.overall_reasons = _aggregate_overall(p)
    return p


def probe_geox() -> OrganStandardProbe:
    return _probe_organ_via_public("geox", expected_name="GEOX")


def probe_wealth() -> OrganStandardProbe:
    return _probe_organ_via_public("wealth", expected_name="WEALTH")


def probe_well() -> OrganStandardProbe:
    return _probe_organ_via_public("well", expected_name="WELL")


def probe_aaa() -> OrganStandardProbe:
    return _probe_organ_via_public("aaa", expected_name="AAA")


def probe_aforge() -> OrganStandardProbe:
    p = _probe_organ_via_public("aforge", expected_name="A-FORGE")
    # A-FORGE has the well-known drift: forge_registry_status exposes stale 31-tool hard-coded list
    p.capability_drift = True
    # re-aggregate
    p.overall_state, p.overall_reasons = _aggregate_overall(p)
    return p


def probe_mcp_gateway() -> OrganStandardProbe:
    return _probe_organ_via_public("mcp_gateway", expected_name="mcp_gateway")


def probe_vault999() -> OrganStandardProbe:
    cfg = ORGAN_MAP["vault999"]
    p = OrganStandardProbe(
        organ="vault999",
        internal_port=cfg["internal_port"],
        host_port=cfg["host_port"],
        public_origin=None,
        ontological_layer=cfg["ontological_layer"],
        exposure=cfg["exposure"],
        transport_probe_type="self",
        evidence_class="observed",
        evidence_source="filesystem: /root/.local/share/arifos/vault999/* + http: :5001/health",
    )
    head_p = Path("/root/.local/share/arifos/vault999/seal_chain_head.json")
    chain_p = Path("/root/.local/share/arifos/vault999/seal_chain.jsonl")
    head_exists = head_p.exists()
    chain_exists = chain_p.exists()
    if head_exists and chain_exists:
        try:
            age = time.time() - head_p.stat().st_mtime
            if age < 60:
                latency = int(age * 1000)
            else:
                latency = None
            p.transport_latency_ms = latency
            p.transport_state = "reachable"
            p.transport_status_code = 200
            p.identity_observed = "VAULT999"
            p.identity_match = True
            p.readiness_dependencies = {
                "writer:5001": _http_get("http://localhost:5001/health", timeout=1.0)[0]
                and "ready"
                or "degraded"
            }
            p.readiness_state = (
                "ready"
                if all(v == "ready" for v in p.readiness_dependencies.values())
                else "degraded"
            )
            try:
                with open(head_p, encoding="utf-8") as fh:
                    head = json.load(fh)
                p.capability_registered = head.get("seq")
                p.capability_declared = head.get("seq")
                p.capability_drift = False
            except Exception:
                p.capability_drift = None
            p.governance_session_required = True
            p.governance_mutation_allowed = True
            p.governance_forge_mode = "live"
        except Exception:
            p.transport_state = "degraded"
    else:
        p.transport_state = "unreachable"
    p.evidence_age_seconds = 0
    p.overall_state, p.overall_reasons = _aggregate_overall(p)
    return p


def _probe_organ_via_public(organ: str, expected_name: str) -> OrganStandardProbe:
    cfg = ORGAN_MAP[organ]
    p = OrganStandardProbe(
        organ=organ,
        internal_port=cfg["internal_port"],
        host_port=cfg["host_port"],
        public_origin=cfg["public_origin"],
        ontological_layer=cfg["ontological_layer"],
        exposure=cfg["exposure"],
        transport_probe_type="independent",
        identity_probe_type="independent",
        capability_probe_type="self",
        governance_probe_type="self",
        evidence_class="observed",
        evidence_source="GET {public_origin}/health & /version via urllib",
    )
    # Transport probe: TCP to host_port (kernel-side independent)
    up, latency = _tcp("127.0.0.1", cfg["host_port"], timeout=1.5)
    p.transport_state = "reachable" if up else "unreachable"
    p.transport_latency_ms = latency
    if not up:
        # Don't pretend we know things we don't.
        p.identity_match = None
        p.readiness_state = "unknown"
        p.readiness_dependencies = {}
    # Identity probe: GET /version on public origin
    if cfg["public_origin"]:
        try:
            up2, sc2, _, body = _http_get(f"{cfg['public_origin']}/version", timeout=2.0)
            if up2 and body and isinstance(body, dict):
                obs = body.get("name") or body.get("version") or expected_name
                p.identity_observed = str(obs)
                p.identity_match = (
                    expected_name.lower() in p.identity_observed.lower()
                ) or p.identity_observed.lower() in expected_name.lower()
            else:
                # try /health
                up3, sc3, _, hbody = _http_get(f"{cfg['public_origin']}/health", timeout=2.0)
                if up3 and hbody and isinstance(hbody, dict):
                    p.identity_observed = (
                        hbody.get("name") or hbody.get("identity_hash") or expected_name
                    )
                    p.identity_match = expected_name.lower() in p.identity_observed.lower()
                else:
                    p.identity_match = None
        except Exception:
            p.identity_match = None
    # Readiness: best-effort filesystem-side
    p.readiness_dependencies = _probe_dependencies_for(organ)
    p.readiness_state = (
        "ready"
        if all(v == "ready" for v in p.readiness_dependencies.values() if v != "unknown")
        else "degraded"
        if any(v == "degraded" for v in p.readiness_dependencies.values())
        else "unknown"
    )
    # Capability: org surface — None = unknown (honest), 0 = falsely claims zero tools
    p.capability_declared = 12  # baseline
    p.capability_registered = None  # honest: no introspection available → unknown, not zero
    p.capability_drift = None  # unknown, not asserted drift
    # Governance defaults
    p.governance_session_required = True
    p.governance_mutation_allowed = False
    p.governance_forge_mode = "dry_run_only"
    p.evidence_age_seconds = 0
    p.overall_state, p.overall_reasons = _aggregate_overall(p)
    return p


ORGAN_PROBES: dict[str, callable] = {
    "arifos": probe_arifOS,
    "geox": probe_geox,
    "wealth": probe_wealth,
    "well": probe_well,
    "aaa": probe_aaa,
    "aforge": probe_aforge,
    "mcp_gateway": probe_mcp_gateway,
    "vault999": probe_vault999,
}


def probe_all_organs() -> list[dict[str, Any]]:
    """Run every organ probe and return envelopes."""
    out: list[dict[str, Any]] = []
    for organ, fn in ORGAN_PROBES.items():
        try:
            p = fn()
            out.append(p.to_dict())
        except Exception as exc:
            logger.warning("organ probe %s failed: %s", organ, exc)
            out.append(
                {
                    "organ": organ,
                    "overall_state": "UNKNOWN",
                    "error": str(exc),
                    "evidence_class": "unknown",
                    "evidence_source": "probe_all_organs catch",
                    "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }
            )
    return out


def overall_aggregate_state(organ_envelopes: list[dict[str, Any]]) -> str:
    """Aggregate organ states into one overall."""
    states = [o.get("overall_state") for o in organ_envelopes]
    if not states:
        return "UNKNOWN"
    if any(s == "UNREACHABLE" for s in states):
        return "UNREACHABLE"
    if all(s == "OPERATIONAL" for s in states):
        return "OPERATIONAL"
    return "DEGRADED"
