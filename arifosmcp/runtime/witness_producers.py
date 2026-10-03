"""Real tri-witness producers for F3 TRI-WITNESS.

Follow-up to SCAR-OBS-GREENWASH (2026-10-03). F3 was published as 0.9299 for
months from three hardcoded numbers — `3*(0.42*0.99*0.99)**(1/3)/2.40`. This
module replaces that with legs that must each have an external referent.

Contract: a leg returns ``(value | None, evidence)``. **None is a result, not a
failure.** The coherence is a normalised geometric mean, so it is undefined when
any leg is unmeasured; the caller must then leave F3 `unmeasured` rather than
substitute a placeholder. Inventing a leg is exactly the defect this replaces.

Legs
----
earth
    Declared organ ports from the canonical topology SOT
    (``/root/AAA/federation/organs.yaml``, ``components[].mcp_port`` +
    ``components[].interfaces``), TCP-probed. External to the kernel by
    construction: a process either accepts a connection or it does not.
ai
    ``/var/lib/arifos/observatory/capability-test-cache.json`` — a record of
    actual tool invocations written by ``record_test_result``, with ``last_pass``
    and ``last_invocation_at``. Counted only while fresh, so a stale pass cannot
    keep paying rent.
human
    **No instrument exists.** Measured 2026-10-03: zero human actors across
    94,999 rows of ``/root/VAULT999/outcomes.jsonl`` (actor_id is None or
    "anonymous") and 106,055 rows of ``/var/lib/arifflow/receipts.jsonl`` (25
    distinct actors, all machine: A-FORGE, grok-build, hermes-asi,
    codex-startup, 333-agi, ...); no ``actor_class`` field exists in either
    ledger. This leg therefore returns None and names the gap. When a real
    human-witness ledger lands at one of ``HUMAN_WITNESS_SOURCES``, F3 lights up
    with no further code change.
"""

from __future__ import annotations

import json
import os
import socket
import time
from typing import Any

ORGANS_SOT = "/root/AAA/federation/organs.yaml"
CAPABILITY_TEST_CACHE = "/var/lib/arifos/observatory/capability-test-cache.json"

# Where a real human-witness signal would be read from. Neither exists as of
# 2026-10-03; they are declared so the leg becomes measurable without a code
# change, and so "no instrument" is a checked fact rather than an assumption.
HUMAN_WITNESS_SOURCES = (
    "/var/lib/arifos/human_witness.jsonl",
    "/var/lib/arifflow/human_witness.jsonl",
)

HUMAN_LEG_GAP = (
    "NO_INSTRUMENT: measured 2026-10-03 — 0 human actors in 94999 rows of "
    "VAULT999/outcomes.jsonl (actor_id None|anonymous) and 106055 rows of "
    "arifflow/receipts.jsonl (25 distinct actors, all machine); no actor_class "
    "field in either ledger"
)

DEFAULT_PROBE_TIMEOUT = 0.6
DEFAULT_FRESH_SECONDS = 86400


def _declared_organ_ports() -> list[tuple[str, int]]:
    """Return (organ_id, port) pairs declared by the topology SOT."""
    import yaml  # local import: only this producer needs YAML

    with open(ORGANS_SOT) as fh:
        doc = yaml.safe_load(fh) or {}
    out: list[tuple[str, int]] = []
    for comp in doc.get("components") or []:
        if not isinstance(comp, dict):
            continue
        oid = str(comp.get("id") or "unknown")
        port = comp.get("mcp_port")
        if isinstance(port, int) and port > 0:
            out.append((oid, port))
        for iface in comp.get("interfaces") or []:
            if isinstance(iface, dict):
                p = iface.get("port")
                if isinstance(p, int) and p > 0:
                    out.append((oid, p))
    # de-duplicate, preserve order
    seen: set[tuple[str, int]] = set()
    return [x for x in out if not (x in seen or seen.add(x))]


def probe_earth_witness(
    timeout: float = DEFAULT_PROBE_TIMEOUT, host: str = "127.0.0.1"
) -> tuple[float | None, str]:
    """Fraction of SOT-declared organ ports that accept a TCP connection."""
    try:
        targets = _declared_organ_ports()
    except Exception as exc:  # unreadable/absent SOT is "cannot witness"
        return None, f"organs_sot_unreadable: {type(exc).__name__}: {exc}"
    if not targets:
        return None, "organs_sot_declares_no_probeable_ports"

    up: list[str] = []
    down: list[str] = []
    for oid, port in targets:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                up.append(f"{oid}:{port}")
        except OSError:
            down.append(f"{oid}:{port}")
    value = round(len(up) / len(targets), 4)
    return value, (
        f"tcp_probe {len(up)}/{len(targets)} declared organ ports up"
        + (f"; down={','.join(down[:6])}" if down else "")
    )


def probe_ai_witness(
    fresh_seconds: int = DEFAULT_FRESH_SECONDS,
    cache_path: str = CAPABILITY_TEST_CACHE,
) -> tuple[float | None, str]:
    """Fraction of recorded tool tests that passed while still fresh."""
    if not os.path.exists(cache_path):
        return None, f"capability_test_cache_absent: {cache_path}"
    try:
        with open(cache_path) as fh:
            cache = json.load(fh)
    except Exception as exc:
        return None, f"capability_test_cache_unreadable: {type(exc).__name__}: {exc}"
    if not isinstance(cache, dict) or not cache:
        return None, "capability_test_cache_empty"

    now = time.time()
    total = 0
    passed_fresh = 0
    stale = 0
    for name, rec in cache.items():
        if not isinstance(rec, dict):
            continue
        total += 1
        last = rec.get("last_invocation_at")
        age = (now - float(last)) if isinstance(last, (int, float)) else None
        if age is not None and age > fresh_seconds:
            stale += 1
            continue
        if rec.get("last_pass") is True:
            passed_fresh += 1
    if total == 0:
        return None, "capability_test_cache_has_no_tool_records"
    value = round(passed_fresh / total, 4)
    return value, (
        f"record_test_result {passed_fresh}/{total} tools passed within "
        f"{fresh_seconds}s ({stale} stale excluded)"
    )


def probe_human_witness(
    sources: tuple[str, ...] = HUMAN_WITNESS_SOURCES,
) -> tuple[float | None, str]:
    """Human-witness leg. Returns None until a real ledger exists.

    Deliberately cheap: this runs inside /health and must not scan 100k-line
    ledgers per request. It checks for a declared human-witness source and reads
    it if present; otherwise it reports the measured gap.
    """
    for path in sources:
        if not os.path.exists(path):
            continue
        try:
            rows = 0
            witnessed = 0
            with open(path) as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    rows += 1
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(rec, dict) and rec.get("human_witness") is True:
                        witnessed += 1
            if rows == 0:
                return None, f"human_witness_ledger_empty: {path}"
            return round(witnessed / rows, 4), f"human_witness_ledger {witnessed}/{rows} rows: {path}"
        except OSError as exc:
            return None, f"human_witness_ledger_unreadable: {type(exc).__name__}: {exc}"
    return None, HUMAN_LEG_GAP


def coherence(human: float | None, ai: float | None, earth: float | None) -> float | None:
    """Normalised geometric-mean tri-witness coherence, or None if incomplete.

    Same formula the kernel uses, so a measured F3 is comparable with history:
    ``3 * (h*a*e)**(1/3) / (h + a + e)``. Undefined when any leg is unmeasured
    (None) — never when a leg is merely zero, which is a real result.
    """
    if human is None or ai is None or earth is None:
        return None
    total = human + ai + earth
    if total <= 0:
        return 0.0
    return round(3.0 * ((human * ai * earth) ** (1.0 / 3.0)) / total, 4)


def collect_witness_legs() -> dict[str, Any]:
    """Measure all three legs and report them with provenance.

    Returns ``{"legs": {...}, "coherence": float|None, "measured": n, "total": 3,
    "complete": bool, "blocking_legs": [...]}``. The caller publishes this
    verbatim so an unmeasured leg is visible instead of being averaged away.
    """
    legs: dict[str, Any] = {}
    for name, probe in (
        ("human", probe_human_witness),
        ("ai", probe_ai_witness),
        ("earth", probe_earth_witness),
    ):
        try:
            value, evidence = probe()
        except Exception as exc:
            value, evidence = None, f"probe_raised: {type(exc).__name__}: {exc}"
        legs[name] = {
            "value": value,
            "state": "measured" if value is not None else "unmeasured",
            "evidence": evidence,
        }
    values = [legs[k]["value"] for k in ("human", "ai", "earth")]
    coh = coherence(*values)
    return {
        "legs": legs,
        "coherence": coh,
        "measured": sum(1 for v in values if v is not None),
        "total": 3,
        "complete": coh is not None,
        "blocking_legs": [k for k in ("human", "ai", "earth") if legs[k]["value"] is None],
    }


__all__ = [
    "ORGANS_SOT",
    "CAPABILITY_TEST_CACHE",
    "HUMAN_WITNESS_SOURCES",
    "HUMAN_LEG_GAP",
    "probe_earth_witness",
    "probe_ai_witness",
    "probe_human_witness",
    "coherence",
    "collect_witness_legs",
]
