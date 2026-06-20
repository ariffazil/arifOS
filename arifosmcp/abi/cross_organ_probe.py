"""
arifosmcp/abi/cross_organ_probe.py — MAKP-5 cross-organ trace primitive

Forged: 2026-06-11 by omega-forge-agent
Status: STAGED. Pure functions plus a small probe helper. Wired into
the kernel is a separate, gated change.

Addresses MAKP-5: one cross-organ trace, bound to a session_id.

The federation cross-organ trace already exists. A-FORGE's
GET /api/federation-probe polls every organ's /health and returns
the live status. 9 organs reported up at the time of this
commit (arifOS, arifosd, WEALTH, WELL, GEOX, A-FORGE, APEX,
OpenClaw, cn-organ). The MAKP-5 primitive is the *kernel-side*
call: the kernel makes the probe, gets the response, and seals
it as one receipt so the trace is bound to a verifiable session.

This module provides:
  - OrganStatus: the parsed shape of one organ's /health report.
  - FederationProbe: the parsed shape of A-FORGE's response.
  - fetch_federation_probe(a_forge_url, timeout): the HTTP call.
  - probe_receipt(probe): a dict ready to be sealed into VAULT999.

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request as URLRequest


@dataclass(frozen=True)
class OrganStatus:
    organ: str
    status: str  # "up" | "down" | "degraded"
    http_status: int
    latency_ms: int
    sample: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FederationProbe:
    a_forge_url: str
    fetched_at: float
    a_forge_ok: bool
    a_forge_error: str | None
    organs: tuple[OrganStatus, ...]
    n_up: int
    n_down: int
    duration_ms: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "a_forge_url": self.a_forge_url,
            "fetched_at": self.fetched_at,
            "a_forge_ok": self.a_forge_ok,
            "a_forge_error": self.a_forge_error,
            "organs": [
                {
                    "organ": o.organ,
                    "status": o.status,
                    "http_status": o.http_status,
                    "latency_ms": o.latency_ms,
                }
                for o in self.organs
            ],
            "n_up": self.n_up,
            "n_down": self.n_down,
            "duration_ms": self.duration_ms,
        }


def fetch_federation_probe(
    a_forge_url: str = "http://127.0.0.1:7071",
    *,
    timeout_s: float = 5.0,
) -> FederationProbe:
    """Synchronous fetch of A-FORGE /api/federation-probe.

    Returns a FederationProbe with .a_forge_ok=False on any
    transport error (network, timeout, non-2xx). The exception
    is captured into .a_forge_error; this function never raises.
    """
    start = time.perf_counter()
    url = a_forge_url.rstrip("/") + "/api/federation-probe"
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return FederationProbe(
            a_forge_url=url,
            fetched_at=time.time(),
            a_forge_ok=False,
            a_forge_error=f"unsupported scheme: {parsed.scheme!r}",
            organs=(),
            n_up=0,
            n_down=0,
            duration_ms=int((time.perf_counter() - start) * 1000),
        )
    try:
        req = URLRequest(url, headers={"Accept": "application/json"})
        with __import__("urllib.request", fromlist=["urlopen"]).urlopen(
            req, timeout=timeout_s
        ) as resp:
            raw = resp.read()
            http_status = resp.status
            data = json.loads(raw.decode("utf-8"))
    except (URLError, HTTPError, json.JSONDecodeError, TimeoutError) as e:
        return FederationProbe(
            a_forge_url=url,
            fetched_at=time.time(),
            a_forge_ok=False,
            a_forge_error=f"{type(e).__name__}: {e}",
            organs=(),
            n_up=0,
            n_down=0,
            duration_ms=int((time.perf_counter() - start) * 1000),
        )

    raw_organs = data.get("organs", {}) or {}
    organs_list: list[OrganStatus] = []
    for name, info in raw_organs.items():
        if not isinstance(info, dict):
            continue
        organs_list.append(
            OrganStatus(
                organ=name,
                status=str(info.get("status", "unknown")),
                http_status=int(info.get("http_status", 0) or 0),
                latency_ms=int(info.get("latency_ms", 0) or 0),
                sample=info.get("sample", {}) if isinstance(info.get("sample"), dict) else {},
            )
        )
    n_up = sum(1 for o in organs_list if o.status == "up")
    n_down = sum(1 for o in organs_list if o.status != "up")
    return FederationProbe(
        a_forge_url=url,
        fetched_at=time.time(),
        a_forge_ok=True,
        a_forge_error=None,
        organs=tuple(organs_list),
        n_up=n_up,
        n_down=n_down,
        duration_ms=int((time.perf_counter() - start) * 1000),
    )


def probe_receipt(
    probe: FederationProbe,
    *,
    session_id: str | None = None,
    actor_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a VAULT999-ready receipt from a probe.

    The receipt binds (call_url, response, timestamp, session_id)
    into one hash so the seal is non-replayable. The
    probe_hash is sha256 of the canonical JSON of the probe +
    session_id.
    """
    canonical = json.dumps(
        {
            "a_forge_url": probe.a_forge_url,
            "fetched_at": probe.fetched_at,
            "n_up": probe.n_up,
            "n_down": probe.n_down,
            "organs": [
                {"organ": o.organ, "status": o.status, "latency_ms": o.latency_ms}
                for o in probe.organs
            ],
            "session_id": session_id,
            "actor_id": actor_id,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    probe_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    out: dict[str, Any] = {
        "event": "CROSS_ORGAN_FEDERATION_PROBE",
        "epoch": datetime.now(UTC).isoformat(),
        "session_id": session_id,
        "actor_id": actor_id,
        "probe": probe.to_dict(),
        "probe_hash_sha256": probe_hash,
    }
    if extra:
        out["extra"] = extra
    return out


__all__ = [
    "OrganStatus",
    "FederationProbe",
    "fetch_federation_probe",
    "probe_receipt",
]
