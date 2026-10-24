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
OUT_WEBROOT_WELLKNOWN = Path(
    "/var/www/html/arifos/.well-known/public-state.json"
)  # FIX-1 mirror 2026-08-14: observatory.js fallback surface
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


def _first_health_field(
    health_data: dict[str, Any] | None, keys: tuple[str, ...]
) -> dict[str, Any] | None:
    """First-present raw /health field with the key it came from. None if absent.

    P1 (2026-10-20): evidence passthrough for governance / receipt / contract
    signals — raw values only, source names the actual key, no inference.
    """
    if not isinstance(health_data, dict):
        return None
    for k in keys:
        v = health_data.get(k)
        if v is not None:
            return {"value": v, "key": k}
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
        # Evidence passthrough (P1, additive) for governance/receipt/contract
        # signals — raw /health fields, source names the key, never inferred.
        "governance_evidence": _first_health_field(
            health_data, ("kernel_verdict", "governance", "verdict")
        ),
        "receipt_evidence": _first_health_field(
            health_data, ("runtime_seal_state", "vault999_health", "seal_state")
        ),
        "contract_evidence": _first_health_field(
            health_data, ("federation_schema_version", "contract_status")
        ),
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


def _override_floors_with_canonical(
    floors: dict[str, Any], extras: dict[str, Any]
) -> dict[str, Any]:
    """T1.4 — flip floor status to FAIL for any floor in kernel canonical_verdict.failed_floors.

    The snapshot's `_floor_passes` returns True for F4/F9/F12 because of strict-< comparator
    bands (ΔS ≤ 0, C_dark < 0.30, Risk < 0.85). But the kernel's 9-signal plane can
    independently mark these floors as failed when sub-signal floors dominate the
    aggregate (verdict_monotonicity: pending → SYUBHAH). We never override the score
    — only the status — so the underlying measurement stays visible.
    """
    failed = list(extras.get("kernel_failed_floors") or [])
    if not failed:
        return floors
    out: dict[str, Any] = {}
    for fid, fdata in floors.items():
        if fid in failed and isinstance(fdata, dict):
            fdata = dict(fdata)
            status = fdata.get("status")
            if isinstance(status, dict):
                fdata["status"] = {
                    **status,
                    "value": "fail",
                    "source": "kernel canonical_verdict (overrides _floor_passes band)",
                }
            else:
                fdata["status"] = {
                    "value": "fail",
                    "source": "kernel canonical_verdict (overrides _floor_passes band)",
                    "state": "derived",
                    "confidence": 0.95,
                    "observation_method": "kernel_override",
                    "observed_at": extras.get("kernel_observed_at"),
                }
        out[fid] = fdata
    return out


def _override_verdict_with_canonical(gov: dict[str, Any], extras: dict[str, Any]) -> dict[str, Any]:
    """T1.4 — replace the snapshot's parser verdict (UNKNOWN) with the kernel
    canonical_verdict (e.g. SYUBHAH, SABAR, SEAL, HOLD) so the renderer
    displays the truth instead of "HOLD (raw UNKNOWN)".
    """
    canonical = extras.get("kernel_canonical_verdict")
    if not canonical:
        return gov
    out = dict(gov)
    verdict = out.get("verdict")
    if isinstance(verdict, dict):
        verdict = dict(verdict)
        verdict["value"] = canonical
        verdict["source"] = "kernel canonical_verdict (overrides parser UNKNOWN)"
        out["verdict"] = verdict
    else:
        out["verdict"] = {
            "value": canonical,
            "source": "kernel canonical_verdict (overrides parser UNKNOWN)",
            "state": "observed",
            "confidence": 0.95,
            "observation_method": "kernel_override",
            "observed_at": extras.get("kernel_observed_at"),
        }
    return out


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

    # T1.4: override verdict + failed floors with kernel canonical_verdict.
    if extra:
        canon_failed = list(extra.get("kernel_failed_floors") or [])
        canon_verdict = extra.get("kernel_canonical_verdict")
        if canon_failed or canon_verdict:
            raw_floors = gov.get("floors") if isinstance(gov.get("floors"), dict) else {}
            gov = dict(gov)
            gov["floors"] = _override_floors_with_canonical(raw_floors, extra)
            gov = _override_verdict_with_canonical(gov, extra)

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
        f
        for f in normalized_findings
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
        # ── Class B (2026-10-20): carry the snapshot's metabolism stages
        # (000_INIT…, per-field envelopes with origin + confidence) so the
        # observatory renderMetabolism panel reads measured data instead of
        # "unavailable". Projection-carry only — no new telemetry.
        "metabolism": snap.get("metabolism") if isinstance(snap.get("metabolism"), list) else [],
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
        # ── Observatory wiring (class A, 2026-10-20, additive) ──────────────
        # observatory.js renderIdentity() reads data.runtime_identity.* — the
        # snapshot already carries this (ri); carry it through merged with the
        # release commits so the F2 panel shows real data, not "source: missing".
        "runtime_identity": {
            "source_commit": pf_value(ri.get("workspace_source_commit"))
            or pf_value(ri.get("source_commit"))
            or short_commit(source, 7),
            "source_commit_full": source,
            "deployed_commit": pf_value(ri.get("deployed_commit")) or short_commit(deployed, 7),
            "build_commit": pf_value(ri.get("build_commit")) or short_commit(build, 7),
            "drift": drift_obj if drift_obj is not None else alignment,
            # 2026-10-24 333-AGI — "capability: DRIFTED" is an enum with no units, so
            # the page could not say WHAT drifted. It is a coverage statement, not a
            # mismatch: the matrix marks a public verb degraded whenever truth is not
            # PASS/PROVEN, and a verb whose happy path never refreshes the test cache
            # can never leave that state. Publish the counts beside the word.
            "drift_counts": {
                "tested_fresh": tested,
                "proven_live": proven,
                "untested": caps.get("untested_count"),
                "public_tools": public_tools,
                "read_as": "DRIFTED here means NOT-PROVEN, not declared!=actual",
            },
            "deployment_mode": pf_value(ri.get("deployment_mode")) or health.get("deployment_mode"),
            "process_started_at": pf_value(ri.get("process_started_at")),
            "platform": pf_value(ri.get("platform")),
            "kernel_epoch": pf_value(ri.get("kernel_epoch")),
            "confidence": ri.get("confidence"),
            "source": "snapshot.runtime_identity+release",
            "observed_at": snap.get("observed_at"),
        },
        # ── Footer signature (P1, additive): observatory.js footer reads
        # data.signature.{algorithm,key_id,payload_hash,signed_at} and derives
        # trust display from signature.algorithm. The snapshot already carries
        # a full ed25519 signature record — carry it through so the footer
        # reports the real signature instead of the 'unsigned' fallback.
        "signature": {
            "algorithm": (snap.get("signature") or {}).get("algorithm"),
            "key_id": (snap.get("signature") or {}).get("key_id"),
            "payload_hash": (snap.get("signature") or {}).get("payload_hash"),
            "signed_at": (snap.get("signature") or {}).get("signed_at"),
            "state": (snap.get("signature") or {}).get("state"),
            "verification_url": (snap.get("signature") or {}).get("verification_url"),
            "source": "snapshot.signature",
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
        # Three stable fleet facts replace the deprecated FQ scalar on the face
        # of the page (F13 directive 2026-10-24: "jangan sentuh FQ, buang dari
        # muka depan — tunjuk berapa aktif, berapa tertahan, dan kenapa").
        "fleet": {
            "actors_tracked": extra.get("fleet_actors_tracked"),
            "held": extra.get("fleet_held"),
            "held_actors": extra.get("fleet_held_actors") or [],
            "reason": extra.get("fleet_held_reason"),
            "source": "ariflow:7073/health :: fq.per_actor",
            "observed_at": extra.get("ariflow_observed_at"),
        },
        "ariflow": {
            "fq_quotient": extra.get("ariflow_fq_quotient"),
            "fq_verdict": extra.get("ariflow_fq_verdict"),
            "execute_count": extra.get("ariflow_execute_count"),
            "verify_count": extra.get("ariflow_verify_count"),
            "receipts": extra.get("ariflow_receipts"),
            "uptime_ms": extra.get("ariflow_uptime_ms"),
            "status": extra.get("ariflow_status"),  # P0-A
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
            "source": extra.get(
                "drift_source", "/root/.local/share/arifos/vault999/drift_log.jsonl"
            ),
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
            # 2026-10-24 333-AGI — scope-explicit so a historical-era blend cannot
            # be read as a broken forward chain. `verified`/`gap_count` stay as the
            # full-file census (back-compat); `*_canonical` is the governed scope.
            "scope": extra.get("chain_scope", "full"),
            "verified_canonical": extra.get("chain_canonical_verified"),
            "gap_count_canonical": extra.get("chain_canonical_gap_count"),
            "gap_count_historical": extra.get("chain_historical_gap_count"),
            "head_seq_canonical": extra.get("chain_canonical_head_seq"),
            "head_count_seq_canonical": extra.get("chain_canonical_head_count_seq"),
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
            # 2026-10-24 333-AGI — two quantities shared one name. `head_seq` from
            # the vault head is the COUNT of canonical-envelope entries (73);
            # the chain's own sequence is 56. Publishing the count as
            # "head_sequence" is what made head/tail look 17 entries apart.
            # Prefer the measured chain sequence; keep the count by its own name.
            "head_sequence": (
                extra.get("chain_canonical_head_seq")
                if extra.get("chain_canonical_head_seq") is not None
                else pf_value(receipts.get("head_seq"))
            ),
            "head_sequence_basis": (
                "chain_sequence"
                if extra.get("chain_canonical_head_seq") is not None
                else "vault_head_count_unverified"
            ),
            "canonical_entry_count": (
                extra.get("chain_canonical_head_count_seq")
                if extra.get("chain_canonical_head_count_seq") is not None
                else (
                    extra.get("chain_canonical_entries")
                    if extra.get("chain_canonical_entries") is not None
                    else pf_value(receipts.get("head_seq"))
                )
            ),
            "head_hash": pf_value(receipts.get("head_hash")),
            # 2026-10-24 333-AGI — canonical_status arrived as None upstream, so the
            # page rendered "canonical UNKNOWN" for a chain we can and did measure.
            # Derive it from the canonical-scope census by name. Never green when a
            # gap exists: a non-zero count publishes as CLASSIFIED_GAPS:n.
            "canonical_status": (
                canonical_status
                if canonical_status is not None
                else (
                    "VERIFIED"
                    if extra.get("chain_canonical_gap_count") == 0
                    else (
                        f"CLASSIFIED_GAPS:{extra.get('chain_canonical_gap_count')}"
                        if extra.get("chain_canonical_gap_count") is not None
                        else None
                    )
                )
            ),
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
PUBLIC_STATE_EVIDENCE_CLASS = (
    "reported"  # default class; renderer treats lower trust than observatory.v1
)
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
    state_token = (
        raw.get("state") or raw.get("evidence_state") or ("observed" if source else "unknown")
    )
    status_token = raw.get("status") or "OPEN"
    category_token = raw.get("category") or raw.get("class") or "GENERAL"
    description_token = (
        raw.get("description") or raw.get("summary") or raw.get("title") or raw.get("message") or ""
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

    raw_evidence_url = (
        raw.get("evidence_url")
        or raw.get("url")
        or (f"https://arifos.arif-fazil.com/findings/{finding_id}" if finding_id else None)
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
            confidence_float
            if confidence_float is not None and 0.0 <= confidence_float <= 1.0
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
    label = (
        row.get("organ")
        or row.get("label")
        or (ORGAN_META.get(organ_id, {}).get("label") if organ_id != "unknown" else "UNKNOWN")
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
            confidence_float
            if confidence_float is not None and 0.0 <= confidence_float <= 1.0
            else None
        ),
        "source": row.get("source") or "127.0.0.1 tcp probe",
        "trace": row.get("probe_reason") or row.get("status_code") or None,
        "receipt": row.get("receipt"),
        # P1 passthrough (2026-10-20): raw probe evidence for readiness /
        # governance / receipt / contract signals — whitelisted through so the
        # contract wire can emit sourced records instead of honest-null.
        "probe_status_code": row.get("probe_status_code"),
        "governance_evidence": row.get("governance_evidence"),
        "receipt_evidence": row.get("receipt_evidence"),
        "contract_evidence": row.get("contract_evidence"),
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
    for path in (OUT_RUNTIME, OUT_WEBROOT, OUT_WEBROOT_WELLKNOWN):
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
        extras["apex_G"] = (
            apex.get("G", {}).get("value") if isinstance(apex.get("G"), dict) else apex.get("G")
        )
        extras["apex_C_dark"] = (
            apex.get("C_dark", {}).get("value")
            if isinstance(apex.get("C_dark"), dict)
            else apex.get("C_dark")
        )
        extras["apex_W3"] = (
            apex.get("W3", {}).get("value") if isinstance(apex.get("W3"), dict) else apex.get("W3")
        )
        extras["apex_h"] = (
            apex.get("h", {}).get("value") if isinstance(apex.get("h"), dict) else apex.get("h")
        )
        extras["apex_QDF"] = (
            apex.get("QDF", {}).get("value")
            if isinstance(apex.get("QDF"), dict)
            else apex.get("QDF")
        )
        extras["apex_source"] = "aaa:3001/health"
        extras["apex_observed_at"] = observed_at

    # ── arifFLOW FQ from /health (Rust daemon :7073)
    flow = probe_url("http://127.0.0.1:7073/health", timeout=2.0)
    if flow.get("state") == "PRESENT":
        fq = flow.get("data", {}).get("fq") or {}
        # Daemon emits legacy_verdict/legacy_diagnosis (qg.v0.3.1-vector);
        # bare verdict/quotient keys never existed — schema drift found
        # 2026-09-28 (ariflow_fq rendered None despite a live daemon).
        extras["ariflow_fq_quotient"] = fq.get("quotient")
        extras["ariflow_fq_verdict"] = fq.get("verdict") or fq.get("legacy_verdict")
        extras["ariflow_fq_diagnosis"] = fq.get("diagnosis") or fq.get("legacy_diagnosis")
        extras["ariflow_execute_count"] = fq.get("execute_count")
        extras["ariflow_verify_count"] = fq.get("verify_count")
        extras["ariflow_receipts"] = flow.get("data", {}).get("receipts")
        extras["ariflow_uptime_ms"] = flow.get("data", {}).get("uptime_ms")
        extras["ariflow_status"] = flow.get("data", {}).get(
            "status"
        )  # P0-A: flow health badge (single-f — MUST match emitter key extra.get("arifflow_status"→"ariflow_status") at project_public_state; 2026-10-20 one-char fix)
        extras["ariflow_source"] = "ariflow:7073/health"
        extras["ariflow_observed_at"] = observed_at
        # 2026-10-24 333-AGI — FQ is deprecated by its own producer as a health
        # indicator and moves every cycle; four readings appeared in forty
        # minutes across three surfaces. Front pages therefore stop publishing
        # the scalar and publish three STABLE facts instead: actors tracked,
        # actors held, and why. Nothing here fixes or replaces FQ.
        _pa = fq.get("per_actor") or {}
        _held = sorted(a for a, v in _pa.items() if isinstance(v, dict) and v.get("held"))
        extras["fleet_actors_tracked"] = len(_pa)
        extras["fleet_held"] = len(_held)
        extras["fleet_held_actors"] = _held
        _why = []
        for _a in _held:
            _v = _pa.get(_a) or {}
            _q = _v.get("quotient")
            if _q is None:
                _why.append(f"{_a}: tiada kaunter semasa")
            else:
                _why.append(f"{_a}: FQ {float(_q):.2f} vs paras {_v.get('fq_required')}")
        extras["fleet_held_reason"] = "; ".join(_why) if _why else None

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
                    extras["drift_overall_status"] = payload.get("overall_drift") or rec.get(
                        "status"
                    )
                    if ts:
                        try:
                            from datetime import datetime, timezone

                            ts_clean = ts.replace("Z", "+00:00") if isinstance(ts, str) else ts
                            dt = datetime.fromisoformat(ts_clean)
                            if dt.tzinfo is None:
                                dt = dt.replace(tzinfo=timezone.utc)
                            extras["drift_age_seconds"] = int(
                                (datetime.now(timezone.utc) - dt).total_seconds()
                            )
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
        # 2026-10-24 333-AGI — scope split. The route defaults to scope=full, so the
        # top-level gap_count blends ~39 HISTORICAL-era gaps (missing fields, epoch
        # resets) with the 1 canonical gap, and published as verified:false →
        # "vault DEGRADED / canonical UNKNOWN / head_seq 73". Measured on the same
        # chain: canonical scope = 56 contiguous entries, 55/56 hash-verifiable,
        # 1 classified OUT_OF_BAND_APPEND. Publish both populations by name so the
        # forward (governed) chain is not read through a historical-era blend.
        _sc = sd.get("scope_canonical")
        if isinstance(_sc, dict) and not _sc.get("error"):
            extras["chain_scope"] = "canonical + historical"
            extras["chain_canonical_verified"] = _sc.get("verified")
            extras["chain_canonical_gap_count"] = _sc.get("gap_count")
            extras["chain_canonical_head_seq"] = _sc.get("head_seq")
            extras["chain_canonical_head_count_seq"] = _sc.get("head_count_seq")
            try:
                extras["chain_historical_gap_count"] = int(sd.get("gap_count") or 0) - int(
                    _sc.get("gap_count") or 0
                )
            except (TypeError, ValueError):
                extras["chain_historical_gap_count"] = None
        extras["chain_observed_at"] = observed_at

    # ── Kernel canonical verdict: read from arifOS /health state_axes
    arifos = probe_url("http://127.0.0.1:8088/health", timeout=2.0)
    if arifos.get("state") == "PRESENT":
        data = arifos.get("data", {})
        # state_axes carries overall_health, action_judgment, receipt_state
        axes = data.get("state_axes") or {}
        overall = (axes.get("overall_health") or "UNKNOWN").upper()
        # 9-signal + canonical_verdict live inside arif_observe (MCP JSON-RPC).
        # Call it directly so the public-state carries the kernel's real verdict.
        try:
            payload = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {"name": "arif_observe", "arguments": {"mode": "identity"}},
                }
            ).encode("utf-8")
            req = urllib.request.Request(
                "http://127.0.0.1:8088/mcp",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                },
            )
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
            # SSE / JSON response — extract the JSON line
            text_blob = ""
            for line in raw.split("\n"):
                if line.startswith("data:"):
                    text_blob = line[5:].strip()
                    break
                if line.startswith("{") and '"jsonrpc"' in line:
                    text_blob = line.strip()
                    break
            if text_blob:
                rpc = json.loads(text_blob)
                content = (rpc.get("result") or {}).get("content") or []
                if content:
                    inner = json.loads(content[0].get("text", "{}"))
                    meta = inner.get("meta") or {}
                    nine = meta.get("nine_signal") or {}
                    overall_block = nine.get("overall") or {}
                    failed = meta.get("failed_floors") or []
                    # Legacy L01–L13 aliases are accepted; normalise to F01–F13.
                    extras["kernel_failed_floors"] = [
                        f"F{n}" if f.upper().startswith("L") and f[1:].isdigit() else f
                        for f in failed
                    ]
                    extras["kernel_verdict_state"] = overall
                    extras["kernel_verdict_native"] = overall_block.get("state", "BELUM_SAH")
                    extras["kernel_verdict_native_en"] = overall_block.get("en", "UNAUTHENTICATED")
                    extras["kernel_verdict_reason"] = meta.get("reason")
                    extras["kernel_next_safe_action"] = meta.get("next_safe_action")
                    # The witness reason is also surfaced in evidence_reference of action
                    action = (inner.get("verdicts") or {}).get("action") or {}
                    extras["kernel_canonical_verdict"] = action.get(
                        "evidence_reference", ""
                    ).replace("canonical_verdict=", "")
                    extras["kernel_source"] = "arifOS:8088/mcp tools/call arif_observe"
        except Exception as exc:
            extras["kernel_error"] = f"{type(exc).__name__}:{str(exc)[:80]}"
            extras["kernel_verdict_state"] = overall
            extras["kernel_verdict_native"] = "BELUM_SAH"
            extras["kernel_verdict_native_en"] = "UNAUTHENTICATED"
            extras["kernel_source"] = "arifOS:8088/health (fallback)"
        extras["kernel_observed_at"] = observed_at

    return extras


def wire_observatory_contract(state: dict[str, Any]) -> dict[str, Any]:
    """Class A projection wiring (2026-10-20, additive).

    observatory.js flowSnapshot() candidates are arifFLOW / arifFlow /
    arifflow / arif_flow / flow_plane — the canonical key ``ariflow``
    (single f) matches NONE of them, so the FLOW panel read nothing.
    Emit alias keys alongside the canonical block. Also derive per-organ
    signal records (liveness/readiness/capability/authorization) from
    data the probe ALREADY collected — no new telemetry. Signals without
    a producer stay absent so the page renders honest 'unknown', never
    green.
    """
    flow = state.get("ariflow")
    if isinstance(flow, dict):
        state["arifflow"] = flow
        state["arifFlow"] = flow
        _p0a_wire_census(state, flow)
    organs = state.get("organs")
    if isinstance(organs, dict):
        for organ_id, row in organs.items():
            if not isinstance(row, dict):
                continue
            transport = str(row.get("transport") or "")
            row["liveness"] = {
                "value": "live" if transport == "PRESENT" else (transport or None),
                "state": "healthy" if transport == "PRESENT" else "unknown",
                "source": "live /health probe",
                "confidence": row.get("confidence"),
            }
            status_code = row.get("probe_status_code")
            if status_code is not None:
                row["readiness"] = {
                    "value": f"http {status_code}",
                    "state": "healthy" if status_code == 200 else "degraded",
                    "source": "live /health probe",
                    "confidence": row.get("confidence"),
                }
            tools = row.get("public_tools")
            if isinstance(tools, int):
                row["capability"] = {
                    "value": f"{tools} public tools",
                    "state": "healthy" if tools > 0 else "unknown",
                    "source": "mcp tools/list probe",
                    "confidence": row.get("confidence"),
                }
            identity_state = str(row.get("identity_state") or "")
            row["authorization"] = {
                "value": identity_state or None,
                "state": "healthy"
                if identity_state == "VERIFIED"
                else ("degraded" if identity_state == "PRESENT" else "unknown"),
                "source": "identity probe",
                "confidence": row.get("confidence"),
            }
            identity_state = str(row.get("identity_state") or "")
            row["identity"] = {
                "value": identity_state or None,
                "state": row["authorization"]["state"],
                "source": "identity probe",
                "confidence": row.get("confidence"),
            }
            if "readiness" in row:
                row["dependency"] = row["readiness"]  # pulse-grid + vocab alias
            # P1 (2026-10-20): governance / receipt / contract now wire from the
            # raw /health evidence probe_organ passes through. Absent evidence →
            # key stays absent → the page renders honest 'unknown', never green.
            ge = row.get("governance_evidence")
            if ge:
                row["governance"] = {
                    "value": ge["value"],
                    "state": "reported",
                    "source": f"live /health→{ge['key']}",
                    "confidence": row.get("confidence"),
                }
            rev = row.get("receipt_evidence")
            if rev:
                row["last_receipt"] = {
                    "value": rev["value"],
                    "state": "reported",
                    "source": f"live /health→{rev['key']}",
                    "confidence": row.get("confidence"),
                }
            ce = row.get("contract_evidence")
            if ce:
                row["contract"] = {
                    "value": ce["value"],
                    "state": "observed",
                    "source": f"live /health→{ce['key']}",
                    "confidence": row.get("confidence"),
                }
    _p0a_wire_organs(
        state
    )  # P0-A: pulse-grid aliases (after organ loop populated liveness/authorization)
    return state


def main() -> int:
    snap = load_snapshot()
    health = get_health()
    extras = collect_extras()
    if not snap and not health and not extras:
        print("error: no snapshot, no health, no extras", file=sys.stderr)
        return 1
    state = project_public_state(snap, health, extra=extras)
    state = wire_observatory_contract(state)
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


def _p0a_wire_census(state: dict[str, Any], flow: dict[str, Any]) -> None:
    """P0-A (2026-10-20): project vault receipt census into observatory.js keys.

    renderFlowPlane chain read = flowField(record,'chain','chain_status',...)
    and the VAULT999 line = firstPresent(governance.vault999, substrate.vault999,
    receipts.chain_status). The census data already exists in the receipt block —
    re-key it additively. No new telemetry.
    """
    rb = state.get("receipt") if isinstance(state.get("receipt"), dict) else {}
    if not rb:
        return
    chain_ok = bool(rb.get("chain_verified"))
    # 2026-10-24 333-AGI: the chip previously read "canonical UNKNOWN · head_seq 73"
    # — a status that was never measured plus a COUNT wearing a sequence label.
    # Publish the measured sequence, the entry count under its own name, and the
    # canonical-scope verdict (CLASSIFIED_GAPS:n when a gap exists).
    _seq = rb.get("head_sequence")
    _cnt = rb.get("canonical_entry_count")
    _entries = f" · entries {_cnt}" if _cnt is not None else ""
    flow["chain_status"] = {
        "value": (
            f"canonical {rb.get('canonical_status') or 'UNKNOWN'}"
            f" · head_seq {_seq}"
            f"{_entries}"
            f" · replay {'verified' if rb.get('replay_verified') else 'unverified'}"
        ),
        "state": "healthy" if chain_ok else "unknown",
        "source": "vault receipt census",
        "confidence": None,
    }
    gov = state.get("governance")
    if isinstance(gov, dict):
        gov["vault999"] = {
            "value": (
                f"vault {rb.get('vault_status') or 'UNKNOWN'}"
                f" · canonical {rb.get('canonical_status') or 'UNKNOWN'}"
                f" · head_seq {_seq}"
                f"{_entries}"
                f" · replay {'verified' if rb.get('replay_verified') else 'unverified'}"
            ),
            "state": "healthy" if chain_ok else "unknown",
            "source": "vault receipt census (build_public_state receipt block)",
            "confidence": None,
        }


def _p0a_wire_organs(state: dict[str, Any]) -> None:
    """P0-A (2026-10-20): alias per-organ records to pulse-grid signal keys.

    renderOrgans reads ['transport','dependency','capability','governance',
    'identity','last_receipt','contract'] — alias liveness→transport and
    authorization→identity. Keys without a producer stay absent → honest
    'unknown', never green-washed.
    """
    organs = state.get("organs")
    if not isinstance(organs, dict):
        return
    for row in organs.values():
        if not isinstance(row, dict):
            continue
        if isinstance(row.get("liveness"), dict):
            row["transport"] = row["liveness"]
        if isinstance(row.get("authorization"), dict):
            row["identity"] = row["authorization"]


if __name__ == "__main__":
    raise SystemExit(main())
