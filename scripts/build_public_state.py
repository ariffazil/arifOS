#!/usr/bin/env python3
"""Project arifos.public-state.v1 from Observatory snapshot + live /health.

Single public contract for MCP Gateway (action door) and Observatory (evidence room).
Never hand-maintain the same numbers in HTML.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

SNAPSHOT_LATEST = Path("/root/.arifos/observatory/snapshots/snapshot_latest.json")
OUT_RUNTIME = Path("/root/.arifos/observatory/public-state.json")
OUT_WEBROOT = Path("/var/www/html/arifos/public-state.json")
PROOF_JSON = Path("/var/www/html/mcp/proof/index.json")
MCP_HEALTH_URL = "http://127.0.0.1:8088/health"
ORGAN_PORTS = {
    "arifos": 8088,
    "geox": 8081,
    "wealth": 18082,
    "well": 18083,
    "aforge": 7071,
    "aaa": 3001,
}
ORGAN_META = {
    "arifos": {
        "label": "arifOS",
        "domain": "governance",
        "website": "https://arifos.arif-fazil.com/",
        "mcp": "https://mcp.arif-fazil.com/mcp",
        "evidence_url": "https://arifos.arif-fazil.com/#sec-identity",
    },
    "geox": {
        "label": "GEOX",
        "domain": "earth",
        "website": "https://geox.arif-fazil.com/",
        "mcp": "https://geox.arif-fazil.com/mcp",
        "evidence_url": "https://arifos.arif-fazil.com/#sec-organs",
    },
    "wealth": {
        "label": "WEALTH",
        "domain": "capital",
        "website": "https://wealth.arif-fazil.com/",
        "mcp": "https://wealth.arif-fazil.com/mcp",
        "evidence_url": "https://arifos.arif-fazil.com/#sec-organs",
    },
    "well": {
        "label": "WELL",
        "domain": "human-substrate",
        "website": "https://well.arif-fazil.com/",
        "mcp": "https://well.arif-fazil.com/mcp",
        "evidence_url": "https://arifos.arif-fazil.com/#sec-organs",
    },
    "aforge": {
        "label": "A-FORGE",
        "domain": "execution",
        "website": "https://forge.arif-fazil.com/",
        "mcp": "https://forge.arif-fazil.com/mcp",
        "evidence_url": "https://arifos.arif-fazil.com/#sec-organs",
    },
    "aaa": {
        "label": "AAA",
        "domain": "routing",
        "website": "https://aaa.arif-fazil.com/",
        "mcp": None,
        "evidence_url": "https://arifos.arif-fazil.com/#sec-organs",
    },
}


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def pf_value(field: Any) -> Any:
    if isinstance(field, dict) and "value" in field:
        return field.get("value")
    return field


def short_commit(value: Any, n: int = 7) -> str | None:
    if not value:
        return None
    s = str(value).strip()
    return s[:n] if s else None


def get_json(url: str, timeout: float = 3.0) -> dict[str, Any] | None:
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data if isinstance(data, dict) else None
    except Exception:
        return None


# ── Three-verdict probe (Prompt 2, sovereign directive 2026-07-18) ───────────
# Per sovereign: a probe that can't distinguish "I couldn't reach it" from
# "it doesn't exist" will eventually produce false green. So every URL probe
# must report one of:
#   PRESENT    — got a valid 2xx JSON response
#   ABSENT     — got a definitive negative response (404, 410, 451)
#   UNVERIFIED — probe failure (timeout, DNS, connection refused, decode error)
#
# get_json() above collapses everything to None — that's the bug. probe_url()
# preserves the verdict so callers can render honest UNVERIFIED instead of
# false ABSENT.
def probe_url(url: str, timeout: float = 3.0) -> dict[str, Any]:
    """Three-verdict probe. Returns dict with 'state' ∈ {PRESENT, ABSENT, UNVERIFIED}.

    Never raises — every exception is captured into UNVERIFIED so callers can
    render honestly without try/except.
    """
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if 200 <= resp.status < 300:
                try:
                    data = json.loads(resp.read().decode("utf-8"))
                    return {
                        "state": "PRESENT",
                        "data": data if isinstance(data, dict) else {},
                        "status_code": resp.status,
                    }
                except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                    return {
                        "state": "UNVERIFIED",
                        "reason": f"decode_failed:{type(exc).__name__}:{exc}",
                        "status_code": resp.status,
                    }
            # Non-2xx but got a response — distinguish ABSENT (definitive) from
            # UNVERIFIED (transient server error).
            return {
                "state": "ABSENT" if resp.status in (404, 410, 451) else "UNVERIFIED",
                "reason": f"http_{resp.status}",
                "status_code": resp.status,
            }
    except urllib.error.HTTPError as exc:
        # 404 / 410 / 451 = server says "no, definitively". Other 4xx/5xx
        # = server is up but in trouble; UNVERIFIED.
        return {
            "state": "ABSENT" if exc.code in (404, 410, 451) else "UNVERIFIED",
            "reason": f"http_{exc.code}",
            "status_code": exc.code,
        }
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
        return {
            "state": "UNVERIFIED",
            "reason": f"{type(exc).__name__}:{str(exc)[:80]}",
            "status_code": None,
        }


def get_health() -> dict[str, Any] | None:
    return get_json(MCP_HEALTH_URL, timeout=4.0)


def tool_count_from_payload(data: dict[str, Any] | None) -> int | None:
    if not data:
        return None
    for key in (
        "tools_exposed_via_mcp",
        "count",
        "tool_count",
        "public_tools",
        "stateless_tools",
        "callable_public",
        "canonical_tools_loaded",
        "tools_loaded",
    ):
        val = data.get(key)
        if isinstance(val, int):
            return val
    tools = data.get("tools")
    if isinstance(tools, list):
        return len(tools)
    return None


def probe_organ(organ_id: str) -> dict[str, Any]:
    """Probe an organ with three-verdict semantics.

    Per sovereign directive 2026-07-18: distinguish PRESENT (reachable +
    2xx JSON) from ABSENT (definitive negative response) from UNVERIFIED
    (probe failure). The legacy "UP / DOWN / UNKNOWN" model collapsed ABSENT
    and UNVERIFIED into the same UNKNOWN bucket — that's the bug.
    """
    meta = ORGAN_META.get(organ_id, {})
    port = ORGAN_PORTS.get(organ_id)

    if not port:
        # No port known for this organ — pure UNVERIFIED (we literally don't
        # know how to probe it).
        health_verdict = {
            "state": "UNVERIFIED",
            "reason": "no_port_configured",
            "status_code": None,
        }
        tools_verdict = {"state": "UNVERIFIED", "reason": "no_port_configured", "status_code": None}
    else:
        health_verdict = probe_url(f"http://127.0.0.1:{port}/health")
        tools_verdict = probe_url(f"http://127.0.0.1:{port}/tools")

    # Roll up: /health state determines transport
    transport = health_verdict["state"]
    health_data = health_verdict.get("data") if transport == "PRESENT" else None

    # Tools count: PRESENT tools → PRESENT health → fall back to health
    count = None
    if tools_verdict["state"] == "PRESENT":
        count = tool_count_from_payload(tools_verdict["data"])
    if count is None and health_data:
        count = tool_count_from_payload(health_data)

    # Prefer exposed public facade for arifOS
    if (
        organ_id == "arifos"
        and health_data
        and isinstance(health_data.get("tools_exposed_via_mcp"), int)
    ):
        count = health_data["tools_exposed_via_mcp"]

    # Identity state: 3-verdict (mirrors transport)
    if transport == "PRESENT":
        identity_state = (
            "VERIFIED"
            if health_data
            and (
                health_data.get("identity_hash")
                or health_data.get("identity")
                or health_data.get("substrate_manifest_hash")
            )
            else "PRESENT"
        )
    else:
        identity_state = transport  # ABSENT or UNVERIFIED

    release = None
    if health_data:
        release = (
            health_data.get("release_name")
            or health_data.get("version")
            or health_data.get("git_commit")
        )

    return {
        "organ": meta.get("label") or organ_id.upper(),
        "id": organ_id,
        "domain": meta.get("domain"),
        "transport": transport,  # PRESENT | ABSENT | UNVERIFIED
        "public_tools": count,
        "release": release,
        "identity_state": identity_state,
        "last_observed": now_iso(),
        "probe_reason": health_verdict.get("reason"),
        "probe_status_code": health_verdict.get("status_code"),
        "website": meta.get("website"),
        "mcp": meta.get("mcp"),
        "evidence_url": meta.get("evidence_url"),
    }


def load_snapshot(path: Path | None = None) -> dict[str, Any] | None:
    p = path or SNAPSHOT_LATEST
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def tool_surface_hash() -> str | None:
    if PROOF_JSON.exists():
        try:
            proof = json.loads(PROOF_JSON.read_text(encoding="utf-8"))
            tools = proof.get("tools") if isinstance(proof, dict) else None
            if isinstance(tools, dict) and tools.get("surface_hash"):
                return str(tools["surface_hash"])
        except Exception:
            pass
    return None


def project_public_state(
    snapshot: dict[str, Any] | None,
    health: dict[str, Any] | None,
    *,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Project arifos.public-state.v1 from Observatory snapshot + live /health.

    `extra` is an optional dict of additional fields (e.g. APEX scalars, FQ,
    identity hashes, drift log freshness) collected from independent live probes.
    All `extra` keys are merged at the top level of the returned payload under
    the same names — never silently overridden by the snapshot.
    """
    snap = snapshot or {}
    health = health or {}
    extra = extra or {}

    ri = snap.get("runtime_identity") if isinstance(snap.get("runtime_identity"), dict) else {}
    caps = snap.get("capabilities") if isinstance(snap.get("capabilities"), dict) else {}
    fed = snap.get("federation_edges") if isinstance(snap.get("federation_edges"), dict) else {}
    receipts = snap.get("receipts") if isinstance(snap.get("receipts"), dict) else {}
    gov = snap.get("governance") if isinstance(snap.get("governance"), dict) else {}
    findings_block = snap.get("findings") if isinstance(snap.get("findings"), dict) else {}
    findings = (
        findings_block.get("findings") if isinstance(findings_block.get("findings"), list) else []
    )
    sig = snap.get("signature") if isinstance(snap.get("signature"), dict) else {}
    auth = (
        snap.get("authority_dimensions")
        if isinstance(snap.get("authority_dimensions"), dict)
        else {}
    )

    source = short_commit(
        pf_value(ri.get("workspace_source_commit")) or pf_value(ri.get("source_commit")),
        40,
    )
    deployed = short_commit(pf_value(ri.get("deployed_commit")), 40)
    build = short_commit(pf_value(ri.get("build_commit")), 40)
    drift_obj = pf_value(ri.get("drift"))
    if isinstance(drift_obj, dict):
        alignment = str(drift_obj.get("source_vs_deployed") or "UNKNOWN")
    else:
        alignment = "UNKNOWN"
    workspace_dirty = pf_value(ri.get("workspace_dirty"))
    if source and deployed:
        commits_match = source.startswith(deployed) or deployed.startswith(source)
        alignment = "ALIGNED" if commits_match and workspace_dirty is False else "DRIFTED"

    release_name = health.get("release_name") or health.get("version") or "unknown"
    release_id = str(release_name).lstrip("v")

    exposed = caps.get("exposed_count")
    if exposed is None:
        exposed = health.get("tools_exposed_via_mcp")
    if exposed is None:
        exposed = health.get("tools_loaded")
    if exposed is None:
        exposed = 0
    proven = caps.get("proven_live_count")
    tested = caps.get("tested_count")
    public_tools = int(exposed) if exposed is not None else 0

    transport_ok = (health.get("status") in ("healthy", "ok", "up")) or bool(health)
    mcp_init = "PASS" if transport_ok else "FAIL"
    tools_list = "PASS" if public_tools == 8 else ("PARTIAL" if public_tools else "FAIL")

    floors_loaded = pf_value(gov.get("floors_loaded"))
    floors_passing = pf_value(gov.get("floors_passing"))
    floors_total = int(floors_loaded) if isinstance(floors_loaded, int) else 13
    floors_measured = int(floors_passing) if isinstance(floors_passing, int) else 0
    gov_state = (
        "UNKNOWN"
        if floors_passing is None
        else ("MEASURED" if floors_measured > 0 else "UNMEASURED")
    )

    reachable = int(fed.get("reachable") or 0)
    declared = int(fed.get("declared") or 0)
    probed = int(fed.get("probed") or 0)
    semantic = int(fed.get("semantic_proven") or 0)
    if probed and reachable == probed and semantic == probed:
        fed_state = "ALIGNED"
    elif probed and reachable == probed and semantic == 0:
        fed_state = "TRANSPORT_ONLY"
    elif reachable > 0:
        fed_state = "PARTIAL"
    else:
        fed_state = "UNKNOWN"

    canonical_status = pf_value(receipts.get("canonical_status"))
    historical_status = pf_value(receipts.get("historical_status"))
    verify = canonical_status == "HEALTHY" if canonical_status is not None else None
    if verify is None:
        verify = pf_value(receipts.get("chain_verified"))
    if verify is None:
        verify = pf_value(receipts.get("verify_path_alive"))
    if verify is None:
        verify = receipts.get("verify")
    replay = pf_value(receipts.get("replay_verified"))
    if replay is None:
        replay = pf_value(receipts.get("replay_path_alive"))
    if replay is None:
        replay = receipts.get("replay")
    if verify is True and replay is True and historical_status != "SCARRED":
        receipt_state = "PROVEN"
    elif verify is None and replay is None:
        receipt_state = "NOT_PROVEN"
    else:
        receipt_state = "PARTIAL"

    open_findings = [f for f in findings if isinstance(f, dict) and f.get("status") == "OPEN"]
    by_sev: dict[str, int] = {}
    for f in open_findings:
        sev = str(f.get("severity") or "LOW")
        by_sev[sev] = by_sev.get(sev, 0) + 1
    highest_hold = (
        "HIGH"
        if by_sev.get("HIGH")
        else "MEDIUM"
        if by_sev.get("MEDIUM")
        else "LOW"
        if by_sev.get("LOW")
        else "NONE"
    )

    # Plane vocabulary — never collapse to single HEALTHY
    planes = {
        "transport": "REACHABLE" if transport_ok else "UNREACHABLE",
        "readiness": "PARTIAL"
        if alignment == "DRIFTED" or open_findings
        else ("READY" if transport_ok else "NOT_READY"),
        "capability": (
            f"PROVEN · {proven if proven is not None else public_tools}/{public_tools or 8}"
            if (proven is not None and proven == public_tools and public_tools)
            else f"PARTIAL · {proven or 0}/{public_tools or 8}"
        ),
        "governance": "UNMEASURED" if gov_state in ("UNKNOWN", "UNMEASURED") else gov_state,
        "authorization": (
            f"{auth.get('access_tier') or 'PUBLIC'} / "
            f"{auth.get('session_standing') or 'OBSERVE_ONLY'}"
        ),
        "receipt": "UNPROVEN" if receipt_state == "NOT_PROVEN" else receipt_state,
        "constitutional": (
            "HOLD"
            if highest_hold in ("HIGH", "MEDIUM")
            else ("CLEAR" if highest_hold == "NONE" else "HOLD")
        ),
    }

    # Headline from worst material plane
    if planes["transport"] == "UNREACHABLE":
        headline = "GATEWAY UNREACHABLE"
    elif highest_hold == "HIGH":
        headline = "GATEWAY OPERATIONAL · GOVERNANCE HOLD"
    elif alignment == "DRIFTED":
        headline = "GATEWAY OPERATIONAL · DEPLOYMENT DRIFTED"
    elif planes["governance"] == "UNMEASURED" or receipt_state == "NOT_PROVEN":
        headline = "GATEWAY OPERATIONAL · PROOF PARTIAL"
    else:
        headline = "GATEWAY OPERATIONAL · EVIDENCE ALIGNED"

    payload_hash = None
    if isinstance(sig.get("value"), str) and len(sig["value"]) >= 8:
        payload_hash = sig["value"][:7]
    # prefer explicit payload_hash if present
    for key in ("payload_hash", "content_hash", "digest"):
        if sig.get(key):
            payload_hash = str(sig[key])[:12]
            break

    surface_hash = tool_surface_hash() or short_commit(
        (health.get("software_release") or {}).get("runtime_manifest_hash"), 16
    )

    release_url = f"https://arifos.arif-fazil.com/verify/release/{release_id}"
    connect_url = "https://mcp.arif-fazil.com/"
    snap_id = snap.get("snapshot_id") or "unknown"

    # Live organ rows — kill hand-written tool counts on organ sites.
    # Stable organ_id is enforced via stable_organ_id(); renderers and
    # downstream consumers can rely on exactly six keys: arifos | geox |
    # wealth | well | aforge | aaa.
    organs: dict[str, Any] = {}
    for organ_id in ("arifos", "geox", "wealth", "well", "aforge", "aaa"):
        try:
            row = probe_organ(organ_id)
        except Exception as exc:
            row = {
                "organ": organ_id.upper(),
                "id": organ_id,
                "transport": "UNKNOWN",
                "public_tools": None,
                "error": str(exc),
                "evidence_url": ORGAN_META.get(organ_id, {}).get("evidence_url"),
            }
        # Snapshot fallback for transport / tools counts
        snap_organs = snap.get("organs") if isinstance(snap.get("organs"), dict) else {}
        if row.get("public_tools") is None:
            so = snap_organs.get(organ_id)
            if isinstance(so, dict):
                for key in ("tools", "tool_count", "public_tools", "exposed_count"):
                    if isinstance(so.get(key), int):
                        row["public_tools"] = so[key]
                        break
        # Carry snapshot-derived confidence / evidence links through when probe
        # did not produce them, so each row always has the v1 envelope.
        if isinstance(snap_organs.get(organ_id), dict):
            row.setdefault("confidence", snap_organs[organ_id].get("confidence"))
            if snap_organs[organ_id].get("evidence_url"):
                row.setdefault("evidence_url", snap_organs[organ_id]["evidence_url"])
        organs[organ_id] = row

    # Apply the v1 organ-row normalizer; never mutate the original probe
    # dict in-place so re-probes between calls don't accumulate drift.
    # The loop key is the source-of-truth canonical id; the row's own fields
    # are validated through stable_organ_id() but never override the key.
    organs_normalized: dict[str, Any] = {}
    for canonical_id, raw_row in organs.items():
        normalized = normalize_organ_row(raw_row, canonical_id=canonical_id)
        # Only trust the canonical set to surface top-level dict keys; an
        # unknown organ_id from the probe is logged but not promoted.
        if normalized["organ_id"] in ORGAN_META:
            organs_normalized[normalized["organ_id"]] = normalized
        else:
            organs_normalized[canonical_id] = normalized

    # Normalize findings — upstream block can be list OR {findings: [...]} OR
    # anything else; normalize_findings always returns a list of v1 envelopes
    # with stable organ_ids.
    findings_block = snap.get("findings") if isinstance(snap.get("findings"), dict) else {}
    all_findings = (
        findings_block.get("findings") if isinstance(findings_block.get("findings"), list) else []
    )
    normalized_findings = normalize_findings(all_findings)
    open_normalized = [
        f for f in normalized_findings
        if isinstance(f, dict) and str(f.get("status", "")).upper() == "OPEN"
    ]
    # Recompute by_severity from the normalized list so summary fields agree
    # with the items the renderer will see.
    by_sev_normalized: dict[str, int] = {}
    for f in open_normalized:
        sev = str(f.get("severity") or "LOW")
        by_sev_normalized[sev] = by_sev_normalized.get(sev, 0) + 1
    highest_hold = (
        "HIGH"
        if by_sev_normalized.get("HIGH")
        else "MEDIUM"
        if by_sev_normalized.get("MEDIUM")
        else "LOW"
        if by_sev_normalized.get("LOW")
        else "NONE"
    )

    return {
        "schema": PUBLIC_STATE_SCHEMA,
        "schema_version": PUBLIC_STATE_SCHEMA,
        "schema_aliases": [PUBLIC_STATE_SCHEMA, PUBLIC_STATE_OBSERVATORY_V1_ALIAS],
        "evidence_class": PUBLIC_STATE_EVIDENCE_CLASS,
        "compatibility": {
            "observatory_v1_still_served": True,
            "observatory_v1_endpoint": "/api/observatory/v1/snapshot",
            "public_state_endpoint": "/api/public-state",
        },
        "generated_at": now_iso(),
        "headline": headline,
        "planes": planes,
        "organs": organs_normalized,
        "release": {
            "release_id": release_id,
            "release_name": release_name,
            "source_commit": short_commit(source, 7),
            "source_commit_full": source,
            "deployed_commit": short_commit(deployed, 7),
            "deployed_commit_full": deployed,
            "build_commit": short_commit(build, 7),
            "build_commit_full": build,
            "deployment_alignment": alignment,
            "verify_url": release_url,
            "connect_url": connect_url,
        },
        "mcp": {
            "endpoint": "https://mcp.arif-fazil.com/mcp",
            "transport": health.get("transport") or "streamable-http",
            "public_tools": public_tools,
            "proven_live": proven,
            "tested": tested,
            "tool_surface_hash": surface_hash,
            "initialize": mcp_init,
            "tools_list": tools_list,
            "health_status": health.get("status"),
        },
        # ── Capability matrix (T1.1): expose the snapshot's matrix so the
        # Observatory renderer can populate the drift table instead of
        # "0 matrix rows parsed". Additive — never overrides snapshot.
        "capabilities": {
            "declared_count": caps.get("declared_count"),
            "registered_count": caps.get("registered_count"),
            "exposed_count": caps.get("exposed_count"),
            "invocable_count": caps.get("invocable_count"),
            "tested_count": caps.get("tested_count"),
            "degraded_count": caps.get("degraded_count"),
            "callable_public": caps.get("callable_public"),
            "untested_count": caps.get("untested_count"),
            "matrix": caps.get("matrix") if isinstance(caps.get("matrix"), list) else [],
            "as_of": caps.get("as_of"),
            "semantics": caps.get("semantics") if isinstance(caps.get("semantics"), dict) else {},
        },
        # ── APEX scalars (T1.3): G, C_dark, W³, h, QDF from AAA live probe.
        # Independent of snapshot — fed by `extra` parameter from live AAA /health.
        "apex": {
            "G": extra.get("apex_G"),
            "C_dark": extra.get("apex_C_dark"),
            "W3": extra.get("apex_W3"),
            "h": extra.get("apex_h"),
            "QDF": extra.get("apex_QDF"),
            "source": extra.get("apex_source", "aaa:3001/health"),
            "observed_at": extra.get("apex_observed_at"),
        },
        # ── arifFLOW FQ (T1.3): FLOW quotient + verdict, size-bounded.
        "ariflow": {
            "fq_quotient": extra.get("ariflow_fq_quotient"),
            "fq_verdict": extra.get("ariflow_fq_verdict"),
            "execute_count": extra.get("arifflow_execute_count"),
            "verify_count": extra.get("ariflow_verify_count"),
            "receipts": extra.get("arifflow_receipts"),
            "uptime_ms": extra.get("ariflow_uptime_ms"),
            "source": extra.get("ariflow_source", "ariflow:7073/health"),
            "observed_at": extra.get("ariflow_observed_at"),
        },
        # ── Identity hashes per organ (T1.3): trust chain links.
        "identity_hashes": {
            "arifos": extra.get("identity_arifos"),
            "geox": extra.get("identity_geox"),
            "wealth": extra.get("identity_wealth"),
            "well": extra.get("identity_well"),
            "aforge": extra.get("identity_aforge"),
            "aaa": extra.get("identity_aaa"),
            "ariflow": extra.get("identity_ariflow"),
            "observed_at": extra.get("identity_observed_at"),
        },
        # ── Drift log freshness (T1.3): the actual age of the last drfit check.
        "drift_log_freshness": {
            "last_check_at": extra.get("drift_last_check_at"),
            "overall_status": extra.get("drift_overall_status"),
            "age_seconds": extra.get("drift_age_seconds"),
            "source": extra.get("drift_source", "/root/.local/share/arifos/vault999/drift_log.jsonl"),
        },
        # ── Chain integrity (T1.5): sanitized card from /seal/verify.
        # Sensitive fields (ledger_path, failure_classes) are operator-only.
        "chain_integrity": {
            "entries": extra.get("chain_entries"),
            "canonical_entries": extra.get("chain_canonical_entries"),
            "historical_entries": extra.get("chain_historical_entries"),
            "corrupt_lines": extra.get("chain_corrupt_lines"),
            "gap_count": extra.get("chain_gap_count"),
            "verified": extra.get("chain_verified"),
            "head_hash": extra.get("chain_head_hash"),
            "head_seq": extra.get("chain_head_seq"),
            "observed_at": extra.get("chain_observed_at"),
            "source": extra.get("chain_source", "/api/observatory/v1/seal/verify"),
        },
        # ── Kernel canonical verdict (T1.6): the actual nine-signal verdict
        # (BELUM_SAH / SYUBHAH / SABAR / SEAL / HOLD) — never the parser's
        # 'UNKNOWN' fallback, which would render as false-green HOLD.
        "canonical_verdict": {
            "state": extra.get("kernel_verdict_state", "UNKNOWN"),
            "native": extra.get("kernel_verdict_native", "BELUM_SAH"),
            "native_en": extra.get("kernel_verdict_native_en", "UNAUTHENTICATED"),
            "failed_floors": extra.get("kernel_failed_floors", []),
            "reason": extra.get("kernel_verdict_reason"),
            "next_safe_action": extra.get("kernel_next_safe_action"),
            "observed_at": extra.get("kernel_observed_at"),
            "source": extra.get("kernel_source", "arif_observe"),
        },
        "governance": {
            "state": gov_state,
            "floors_measured": floors_measured,
            "floors_total": floors_total,
            "floors_loaded": floors_loaded,
            "verdict": pf_value(gov.get("verdict")),
            "floors": gov.get("floors") if isinstance(gov.get("floors"), dict) else {},
            "verdict_decomposition": (
                gov.get("verdict_decomposition")
                if isinstance(gov.get("verdict_decomposition"), dict)
                else {}
            ),
        },
        "federation": {
            "declared": declared,
            "probed": probed,
            "reachable": reachable,
            "semantic_proven": semantic,
            "transport_edges": f"{reachable}/{probed or declared or 11}",
            "semantic_edges": f"{semantic}/{probed or declared or 11}",
            "state": fed_state,
            "aggregate_state": fed.get("aggregate_state"),
        },
        "receipt": {
            "head_sequence": pf_value(receipts.get("head_seq")),
            "head_hash": pf_value(receipts.get("head_hash")),
            "canonical_status": canonical_status,
            "historical_status": historical_status,
            "verify": "PROVEN"
            if verify is True
            else ("NOT_PROVEN" if verify is None else "FAILED"),
            "replay": "PROVEN"
            if replay is True
            else ("NOT_PROVEN" if replay is None else "FAILED"),
            "chain_verified": pf_value(receipts.get("chain_verified")),
            "replay_verified": pf_value(receipts.get("replay_verified")),
            "vault_status": (
                receipts.get("VAULT999")
                or ("HEALTHY" if verify is True else "DEGRADED" if verify is False else "UNKNOWN")
            ),
            "verify_url": "https://arif-fazil.com/999/",
        },
        "findings": {
            "schema_version": PUBLIC_STATE_SCHEMA,
            "open_count": len(open_normalized),
            "by_severity": by_sev_normalized,
            "highest_hold": highest_hold,
            "items": normalized_findings,
            "open": [
                {
                    "id": f.get("id"),
                    "organ_id": f.get("organ_id"),
                    "category": f.get("category"),
                    "severity": f.get("severity"),
                    "description": f.get("description"),
                    "state": f.get("state"),
                    "evidence": f.get("evidence"),
                    "timestamp": f.get("timestamp"),
                    "confidence": f.get("confidence"),
                    "trace": f.get("trace"),
                    "receipt": f.get("receipt"),
                    "evidence_url": f.get("evidence_url"),
                    "status": f.get("status"),
                    "links": f.get("links", {}),
                }
                for f in open_normalized
            ],
        },
        "snapshot": {
            "id": snap_id,
            "observed_at": snap.get("observed_at"),
            "signature_state": (sig.get("state") or "unknown").upper()
            if isinstance(sig.get("state"), str)
            else ("SIGNED" if sig.get("value") else "UNSIGNED"),
            "payload_hash": payload_hash,
            "key_id": sig.get("key_id"),
            "snapshot_url": "https://arifos.arif-fazil.com/.well-known/observatory-snapshot-latest.json",
            "verify_url": f"https://arifos.arif-fazil.com/verify/snapshot/{snap_id}",
        },
        "links": {
            # Cross-cutting surfaces available from public-state.v1
            "graph": "https://arifos.arif-fazil.com/graph",
            "floors": "https://arifos.arif-fazil.com/#sec-governance",
            "authority": "https://arifos.arif-fazil.com/#sec-authority",
            "policy": "https://arifos.arif-fazil.com/policy/",
            "proof": "https://arif-fazil.com/999/",
            # Legacy
            "mcp_gateway": connect_url,
            "observatory": "https://arifos.arif-fazil.com/",
            "verify_release": release_url,
            "verify_receipt": "https://arif-fazil.com/999/",
            "public_state": "https://arifos.arif-fazil.com/api/public-state",
            "public_state_static": "https://arifos.arif-fazil.com/public-state.json",
            "public_state_dev": "http://127.0.0.1:8088/api/public-state",
            "canon": "https://arif-fazil.com/canon/",
            "github": "https://github.com/ariffazil/arifOS",
        },
    }


# ── arifos.public-state.v1 hardening (Prompt: Observatory upgrade) ─────────────
# Goals:
#   1. Stable organ_id values (organs dict keys never drift, ids are versioned).
#   2. Normalized findings items — every entry has a fixed-shape envelope with
#      state / evidence / timestamp / confidence / trace / receipt and explicit
#      links to graph / floors / authority / policy / proof.
#   3. observatory.v1 (the signed snapshot served from
#      /api/observatory/v1/snapshot) remains the downstream schema for
#      evidence-signing; this script is additive. Public-state.v1 never
#      mutates or replaces the signed snapshot contract.

PUBLIC_STATE_SCHEMA = "arifos.public-state.v1"
PUBLIC_STATE_OBSERVATORY_V1_ALIAS = "observatory.v1"  # backward-compat hint
PUBLIC_STATE_EVIDENCE_CLASS = "reported"  # default class; renderer treats lower trust than observatory.v1
ORGAN_ID_ALIASES: dict[str, str] = {
    "arifos_kernel": "arifos",
    "arifos-kernel": "arifos",
    "kernel": "arifos",
    "geox-organ": "geox",
    "wealth-organ": "wealth",
    "well-organ": "well",
    "a-forge": "aforge",
    "a_forge": "aforge",
    "aforge-organ": "aforge",
    "aaa-organ": "aaa",
}


def stable_organ_id(organ_id: Any) -> str:
    """Normalize any caller-supplied organ reference to one of the six canonical ids.

    The set of canonical organ ids is the keys of ORGAN_META — never derived
    from probe / snapshot fields. Returns "unknown" only as a last resort.
    """
    if organ_id is None:
        return "unknown"
    text = str(organ_id).strip().lower()
    if text in ORGAN_META:
        return text
    if text in ORGAN_ID_ALIASES:
        return ORGAN_ID_ALIASES[text]
    # Stable numeric prefix substitutions
    table = str.maketrans({"-": "", "_": "", " ": ""})
    compact = text.translate(table)
    for canonical in ORGAN_META:
        if compact == canonical.translate(table):
            return canonical
    return "unknown"


def _normalize_finding(
    raw: Any,
    index: int,
    organ_id: str = "unknown",
) -> dict[str, Any] | None:
    """Coerce an arbitrary finding item into the public-state.v1 envelope.

    Returns None for items that cannot be salvaged beyond producing a
    SCHEMA_MISMATCH-shaped placeholder. Never raises.
    """
    if not isinstance(raw, dict):
        # Strings, numbers, booleans, lists — capture what we can and mark the
        # mismatch so the renderer knows not to treat this as a real finding.
        synthesized_id = f"finding-{index:04d}"
        return {
            "schema_version": PUBLIC_STATE_SCHEMA,
            "id": synthesized_id,
            "organ_id": organ_id,
            "category": "SCHEMA_MISMATCH",
            "severity": "LOW",
            "status": "OPEN",
            "description": (
                f"upstream finding entry was not an object (got {type(raw).__name__}); "
                "re-classified as SCHEMA_MISMATCH"
            ),
            "evidence_url": None,
            "state": "unknown",
            "evidence": None,
            "timestamp": None,
            "confidence": 0.0,
            "source": "public-state.v1.normalizer",
            "trace": None,
            "receipt": None,
            "links": {
                "graph": f"https://arifos.arif-fazil.com/findings/graph/{synthesized_id}",
                "floors": "https://arifos.arif-fazil.com/#sec-governance",
                "authority": f"https://arifos.arif-fazil.com/findings/authority/{synthesized_id}",
                "policy": f"https://arifos.arif-fazil.com/findings/policy/{synthesized_id}",
                "proof": f"https://arifos.arif-fazil.com/verify/finding/{synthesized_id}",
            },
        }

    # Pull values either from the {value, source, confidence, observed_at} envelope
    # pattern used by observatory_emit.py or from a flat shape used elsewhere.
    pf_value = raw.get("value") if isinstance(raw.get("value"), (str, int, float, bool)) else None
    confidence = raw.get("confidence")
    if confidence is None and isinstance(raw.get("envelope"), dict):
        confidence = raw["envelope"].get("confidence")
    if confidence is None and isinstance(pf_value, dict):
        confidence = pf_value.get("confidence")
    try:
        confidence_float = float(confidence) if confidence is not None else None
    except (TypeError, ValueError):
        confidence_float = None

    timestamp = raw.get("observed_at") or raw.get("timestamp") or raw.get("created_at")
    if timestamp is None and isinstance(raw.get("envelope"), dict):
        timestamp = raw["envelope"].get("observed_at")

    source = raw.get("source")
    if source is None and isinstance(raw.get("envelope"), dict):
        source = raw["envelope"].get("source")
    if source is None and isinstance(pf_value, dict):
        source = pf_value.get("source")

    evidence_block = raw.get("evidence")
    if isinstance(evidence_block, dict):
        evidence_links = {
            key: str(value)
            for key, value in evidence_block.items()
            if isinstance(value, (str, int, float))
        }
    elif isinstance(evidence_block, (str, int, float)):
        evidence_links = {"ref": str(evidence_block)}
    else:
        evidence_links = {}

    trace = raw.get("trace")
    if trace is None and isinstance(raw.get("envelope"), dict):
        trace = raw["envelope"].get("trace")

    receipt = raw.get("receipt") or raw.get("receipt_hash")
    if receipt is None and isinstance(raw.get("envelope"), dict):
        receipt = raw["envelope"].get("receipt")

    severity_value = raw.get("severity") or raw.get("severity_level") or "LOW"
    state_token = raw.get("state") or raw.get("evidence_state") or (
        "observed" if source else "unknown"
    )
    status_token = raw.get("status") or "OPEN"
    category_token = raw.get("category") or raw.get("class") or "GENERAL"
    description_token = (
        raw.get("description")
        or raw.get("summary")
        or raw.get("title")
        or raw.get("message")
        or ""
    )

    finding_id = (
        raw.get("id")
        or raw.get("finding_id")
        or raw.get("uid")
        or raw.get("slug")
        or f"finding-{index:04d}"
    )
    finding_id = str(finding_id)

    upstream_organ = raw.get("organ_id") or raw.get("organ")
    normalized_organ = stable_organ_id(upstream_organ or organ_id)

    raw_evidence_url = raw.get("evidence_url") or raw.get("url") or (
        f"https://arifos.arif-fazil.com/findings/{finding_id}" if finding_id else None
    )

    return {
        "schema_version": PUBLIC_STATE_SCHEMA,
        "id": finding_id,
        "organ_id": normalized_organ,
        "category": str(category_token),
        "severity": str(severity_value),
        "status": str(status_token),
        "description": str(description_token),
        "evidence_url": str(raw_evidence_url) if raw_evidence_url else None,
        "state": str(state_token),
        "evidence": evidence_links or None,
        "timestamp": str(timestamp) if timestamp else None,
        "confidence": (
            confidence_float if confidence_float is not None and 0.0 <= confidence_float <= 1.0
            else None
        ),
        "source": str(source) if source else None,
        "trace": str(trace) if trace else None,
        "receipt": str(receipt) if receipt else None,
        "links": {
            "graph": f"https://arifos.arif-fazil.com/findings/graph/{finding_id}",
            "floors": "https://arifos.arif-fazil.com/#sec-governance",
            "authority": f"https://arifos.arif-fazil.com/findings/authority/{finding_id}",
            "policy": f"https://arifos.arif-fazil.com/findings/policy/{finding_id}",
            "proof": f"https://arifos.arif-fazil.com/verify/finding/{finding_id}",
        },
    }


def normalize_findings(
    raw_findings: Any,
    organ_id: str = "unknown",
) -> list[dict[str, Any]]:
    """Normalize a findings block from any upstream shape.

    Always returns a list (possibly empty). Each entry is the public-state.v1
    envelope. Malformed items become SCHEMA_MISMATCH placeholders instead of
    throwing, so renderers never crash on bad input.
    """
    items: list[Any]
    if isinstance(raw_findings, list):
        items = raw_findings
    elif isinstance(raw_findings, dict):
        if isinstance(raw_findings.get("items"), list):
            items = raw_findings["items"]
        elif isinstance(raw_findings.get("findings"), list):
            items = raw_findings["findings"]
        elif isinstance(raw_findings.get("list"), list):
            items = raw_findings["list"]
        else:
            items = [raw_findings]
    elif raw_findings is None:
        return []
    else:
        # Scalar / unexpected shape — treat as one malformed item so the
        # placeholder flows through.
        return [
            _normalize_finding(
                raw_findings,
                index=0,
                organ_id=organ_id,
            )
        ]  # type: ignore[list-item]

    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        try:
            cleaned = _normalize_finding(item, index=index, organ_id=organ_id)
        except Exception:
            cleaned = None
        if cleaned is not None:
            normalized.append(cleaned)
    return normalized


def normalize_organ_row(row: Any, canonical_id: str | None = None) -> dict[str, Any]:
    """Normalize a single organ row to expose a stable organ_id and the v1 envelope.

    When ``canonical_id`` is supplied, it is trusted as the source of truth
    (the loop iterating the six canonical ids knows the truth). The row's own
    ``id`` / ``organ_id`` / ``organ`` fields are still validated through
    ``stable_organ_id`` for downstream logging but never override the
    canonical key.
    """
    if not isinstance(row, dict):
        row_organ_hint = "unknown"
    else:
        row_organ_hint = stable_organ_id(
            row.get("id") or row.get("organ_id") or row.get("organ") or "unknown"
        )
    if canonical_id:
        organ_id = canonical_id
    elif row_organ_hint != "unknown":
        organ_id = row_organ_hint
    else:
        organ_id = "unknown"
    label = row.get("organ") or row.get("label") or (
        ORGAN_META.get(organ_id, {}).get("label") if organ_id != "unknown" else "UNKNOWN"
    )
    transport = row.get("transport") or row.get("state") or "UNKNOWN"
    confidence = row.get("confidence")
    try:
        confidence_float = float(confidence) if confidence is not None else None
    except (TypeError, ValueError):
        confidence_float = None
    public_tools = row.get("public_tools")
    if not isinstance(public_tools, int):
        public_tools = None
    last_observed = row.get("last_observed") or row.get("observed_at") or now_iso()
    return {
        "schema_version": PUBLIC_STATE_SCHEMA,
        "organ_id": organ_id,
        "label": label,
        "domain": row.get("domain"),
        "transport": transport,
        "state": transport,
        "public_tools": public_tools,
        "release": row.get("release"),
        "identity_state": row.get("identity_state") or transport,
        "last_observed": last_observed,
        "timestamp": last_observed,
        "confidence": (
            confidence_float if confidence_float is not None and 0.0 <= confidence_float <= 1.0
            else None
        ),
        "source": row.get("source") or "127.0.0.1 tcp probe",
        "trace": row.get("probe_reason") or row.get("status_code") or None,
        "receipt": row.get("receipt"),
        "evidence_url": row.get("evidence_url"),
        "website": row.get("website"),
        "mcp": row.get("mcp"),
        "links": {
            "graph": f"https://arifos.arif-fazil.com/organs/{organ_id}",
            "floors": "https://arifos.arif-fazil.com/#sec-governance",
            "authority": row.get("evidence_url")
            or f"https://arifos.arif-fazil.com/organs/{organ_id}#authority",
            "policy": f"https://arifos.arif-fazil.com/organs/{organ_id}#policy",
            "proof": f"https://arifos.arif-fazil.com/verify/organ/{organ_id}",
        },
    }


def write_public_state(state: dict[str, Any]) -> list[Path]:
    encoded = json.dumps(state, indent=2, ensure_ascii=False) + "\n"
    written: list[Path] = []
    for path in (OUT_RUNTIME, OUT_WEBROOT):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(encoded, encoding="utf-8")
            written.append(path)
        except Exception as exc:
            print(f"warn: could not write {path}: {exc}", file=sys.stderr)
    return written


def collect_extras() -> dict[str, Any]:
    """Collect live probes from independent federation organs.

    All probes are best-effort and never raise — failures degrade to None so
    the renderer can render UNKNOWN instead of failing the whole public-state.
    Returns a flat dict keyed by the field names consumed in project_public_state().
    """
    extras: dict[str, Any] = {}
    observed_at = now_iso()

    # ── APEX scalars from AAA (/health): apex_scalars.{G, C_dark, W3, h, QDF}
    aaa = probe_url("http://127.0.0.1:3001/health", timeout=2.0)
    if aaa.get("state") == "PRESENT":
        apex = aaa.get("data", {}).get("apex_scalars") or {}
        extras["apex_G"] = apex.get("G", {}).get("value") if isinstance(apex.get("G"), dict) else apex.get("G")
        extras["apex_C_dark"] = apex.get("C_dark", {}).get("value") if isinstance(apex.get("C_dark"), dict) else apex.get("C_dark")
        extras["apex_W3"] = apex.get("W3", {}).get("value") if isinstance(apex.get("W3"), dict) else apex.get("W3")
        extras["apex_h"] = apex.get("h", {}).get("value") if isinstance(apex.get("h"), dict) else apex.get("h")
        extras["apex_QDF"] = apex.get("QDF", {}).get("value") if isinstance(apex.get("QDF"), dict) else apex.get("QDF")
        extras["apex_source"] = "aaa:3001/health"
        extras["apex_observed_at"] = observed_at

    # ── arifFLOW FQ from /health (Rust daemon :7073)
    flow = probe_url("http://127.0.0.1:7073/health", timeout=2.0)
    if flow.get("state") == "PRESENT":
        fq = flow.get("data", {}).get("fq") or {}
        extras["ariflow_fq_quotient"] = fq.get("quotient")
        extras["ariflow_fq_verdict"] = fq.get("verdict")
        extras["ariflow_execute_count"] = fq.get("execute_count")
        extras["ariflow_verify_count"] = fq.get("verify_count")
        extras["ariflow_receipts"] = flow.get("data", {}).get("receipts")
        extras["ariflow_uptime_ms"] = flow.get("data", {}).get("uptime_ms")
        extras["ariflow_source"] = "ariflow:7073/health"
        extras["ariflow_observed_at"] = observed_at

    # ── Organ identity hashes: arifOS, GEOX, WEALTH, WELL, A-FORGE, AAA, arifFLOW
    organ_health_urls = {
        "arifos": "http://127.0.0.1:8088/health",
        "geox": "http://127.0.0.1:8081/health",
        "wealth": "http://127.0.0.1:18082/health",
        "well": "http://127.0.0.1:18083/health",
        "aforge": "http://127.0.0.1:7071/health",
        "aaa": "http://127.0.0.1:3001/health",
        "ariflow": "http://127.0.0.1:7073/health",
    }
    for organ_id, url in organ_health_urls.items():
        result = probe_url(url, timeout=2.0)
        if result.get("state") == "PRESENT":
            data = result.get("data", {})
            extras[f"identity_{organ_id}"] = (
                data.get("identity_hash") or data.get("identity") or data.get("git_version")
            )
    extras["identity_observed_at"] = observed_at

    # ── Drift log freshness: last entry from /root/.local/share/arifos/vault999/drift_log.jsonl
    drift_log = Path("/root/.local/share/arifos/vault999/drift_log.jsonl")
    if drift_log.exists():
        try:
            # Read last line efficiently (file is large; use reverse byte iterator)
            last_line = None
            with drift_log.open("rb") as f:
                try:
                    f.seek(0, 2)  # end
                    pos = f.tell()
                    buf = b""
                    while pos > 0:
                        pos -= 1
                        f.seek(pos)
                        ch = f.read(1)
                        if ch == b"\n" and buf:
                            break
                        buf = ch + buf
                    last_line = buf.decode("utf-8", errors="replace").strip()
                except Exception:
                    last_line = None
            if last_line:
                try:
                    rec = json.loads(last_line)
                    ts = rec.get("timestamp") or rec.get("checked_at")
                    payload = rec.get("payload") or {}
                    extras["drift_last_check_at"] = ts
                    extras["drift_overall_status"] = payload.get("overall_drift") or rec.get("status")
                    if ts:
                        try:
                            from datetime import datetime, timezone
                            ts_clean = ts.replace("Z", "+00:00") if isinstance(ts, str) else ts
                            dt = datetime.fromisoformat(ts_clean)
                            if dt.tzinfo is None:
                                dt = dt.replace(tzinfo=timezone.utc)
                            extras["drift_age_seconds"] = int((datetime.now(timezone.utc) - dt).total_seconds())
                        except Exception:
                            extras["drift_age_seconds"] = None
                except Exception:
                    pass
        except Exception:
            pass

    # ── Chain integrity: sanitized public card from /api/observatory/v1/seal/verify
    seal = probe_url("http://127.0.0.1:8088/api/observatory/v1/seal/verify", timeout=3.0)
    if seal.get("state") == "PRESENT":
        sd = seal.get("data", {})
        extras["chain_entries"] = sd.get("entries")
        extras["chain_canonical_entries"] = sd.get("canonical_entries")
        extras["chain_historical_entries"] = sd.get("historical_entries")
        extras["chain_corrupt_lines"] = sd.get("corrupt_lines")
        extras["chain_gap_count"] = sd.get("gap_count")
        extras["chain_verified"] = sd.get("verified")
        extras["chain_head_hash"] = sd.get("head_hash")
        extras["chain_head_seq"] = sd.get("head_seq")
        extras["chain_observed_at"] = observed_at

    # ── Kernel canonical verdict: read from arifOS /health state_axes
    arifos = probe_url("http://127.0.0.1:8088/health", timeout=2.0)
    if arifos.get("state") == "PRESENT":
        data = arifos.get("data", {})
        # state_axes carries overall_health, action_judgment, receipt_state
        axes = data.get("state_axes") or {}
        overall = (axes.get("overall_health") or "UNKNOWN").upper()
        # 9-signal plane is exposed via arif_observe, not /health — call it
        obs = probe_url(
            "http://127.0.0.1:8088/mcp",
            timeout=2.0,
        )
        # Actually we can read the nine-signal from the meta of the public-state
        # snapshot (which already has it). Try that first.
        snap = load_snapshot()
        if snap:
            meta = snap.get("meta") or {}
            nine = meta.get("nine_signal") or {}
            overall_block = nine.get("overall") or {}
            extras["kernel_verdict_state"] = overall
            extras["kernel_verdict_native"] = overall_block.get("state", "BELUM_SAH")
            extras["kernel_verdict_native_en"] = overall_block.get("en", "UNAUTHENTICATED")
            extras["kernel_failed_floors"] = meta.get("failed_floors") or []
            extras["kernel_verdict_reason"] = meta.get("reason")
            extras["kernel_next_safe_action"] = meta.get("next_safe_action")
        else:
            extras["kernel_verdict_state"] = overall
            extras["kernel_verdict_native"] = "BELUM_SAH"
            extras["kernel_verdict_native_en"] = "UNAUTHENTICATED"
        extras["kernel_observed_at"] = observed_at
        extras["kernel_source"] = "arifOS:8088/health + snapshot.meta.nine_signal"

    return extras


def main() -> int:
    snap = load_snapshot()
    health = get_health()
    extras = collect_extras()
    if not snap and not health and not extras:
        print("error: no snapshot, no health, no extras", file=sys.stderr)
        return 1
    state = project_public_state(snap, health, extra=extras)
    paths = write_public_state(state)
    print(
        f"public-state {state['schema']} headline={state['headline']!r} "
        f"tools={state['mcp']['public_tools']} "
        f"alignment={state['release']['deployment_alignment']} "
        f"open_findings={state['findings']['open_count']} "
        f"apex_G={state['apex'].get('G')!r} "
        f"ariflow_fq={state['ariflow'].get('fq_verdict')!r} "
        f"kernel_verdict={state['canonical_verdict'].get('native')!r} "
        f"paths={[str(p) for p in paths]}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
