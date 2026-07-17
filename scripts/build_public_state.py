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


def get_health() -> dict[str, Any] | None:
    try:
        req = urllib.request.Request(MCP_HEALTH_URL, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data if isinstance(data, dict) else None
    except Exception:
        return None


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
) -> dict[str, Any]:
    snap = snapshot or {}
    health = health or {}

    ri = snap.get("runtime_identity") if isinstance(snap.get("runtime_identity"), dict) else {}
    caps = snap.get("capabilities") if isinstance(snap.get("capabilities"), dict) else {}
    fed = snap.get("federation_edges") if isinstance(snap.get("federation_edges"), dict) else {}
    receipts = snap.get("receipts") if isinstance(snap.get("receipts"), dict) else {}
    gov = snap.get("governance") if isinstance(snap.get("governance"), dict) else {}
    findings_block = snap.get("findings") if isinstance(snap.get("findings"), dict) else {}
    findings = findings_block.get("findings") if isinstance(findings_block.get("findings"), list) else []
    sig = snap.get("signature") if isinstance(snap.get("signature"), dict) else {}
    auth = snap.get("authority_dimensions") if isinstance(snap.get("authority_dimensions"), dict) else {}

    source = short_commit(pf_value(ri.get("source_commit")), 40)
    deployed = short_commit(pf_value(ri.get("deployed_commit")), 40)
    build = short_commit(pf_value(ri.get("build_commit")), 40)
    drift_obj = pf_value(ri.get("drift"))
    if isinstance(drift_obj, dict):
        alignment = str(drift_obj.get("source_vs_deployed") or "UNKNOWN")
    else:
        alignment = "ALIGNED" if source and deployed and source == deployed else (
            "DRIFTED" if source and deployed else "UNKNOWN"
        )

    release_name = (
        health.get("release_name")
        or health.get("version")
        or "unknown"
    )
    release_id = str(release_name).lstrip("v")

    exposed = (
        caps.get("exposed_count")
        or health.get("tools_exposed_via_mcp")
        or health.get("tools_loaded")
        or 0
    )
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
    gov_state = "UNKNOWN" if floors_passing is None else (
        "MEASURED" if floors_measured > 0 else "UNMEASURED"
    )

    reachable = int(fed.get("reachable") or 0)
    probed = int(fed.get("probed") or fed.get("declared") or 0)
    semantic = int(fed.get("semantic_proven") or 0)
    if probed and reachable == probed and semantic == probed:
        fed_state = "ALIGNED"
    elif probed and reachable == probed and semantic == 0:
        fed_state = "TRANSPORT_ONLY"
    elif reachable > 0:
        fed_state = "PARTIAL"
    else:
        fed_state = "UNKNOWN"

    verify = receipts.get("verify")
    replay = receipts.get("replay")
    if verify is True and replay is True:
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
        "HIGH" if by_sev.get("HIGH") else
        "MEDIUM" if by_sev.get("MEDIUM") else
        "LOW" if by_sev.get("LOW") else
        "NONE"
    )

    # Plane vocabulary — never collapse to single HEALTHY
    planes = {
        "transport": "REACHABLE" if transport_ok else "UNREACHABLE",
        "readiness": "PARTIAL" if alignment == "DRIFTED" or open_findings else (
            "READY" if transport_ok else "NOT_READY"
        ),
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
            "HOLD" if highest_hold in ("HIGH", "MEDIUM")
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

    return {
        "schema": "arifos.public-state.v1",
        "generated_at": now_iso(),
        "headline": headline,
        "planes": planes,
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
        "governance": {
            "state": gov_state,
            "floors_measured": floors_measured,
            "floors_total": floors_total,
            "floors_loaded": floors_loaded,
            "verdict": pf_value(gov.get("verdict")),
        },
        "federation": {
            "transport_edges": f"{reachable}/{probed or fed.get('declared') or 11}",
            "semantic_edges": f"{semantic}/{probed or fed.get('declared') or 11}",
            "state": fed_state,
            "aggregate_state": fed.get("aggregate_state"),
        },
        "receipt": {
            "head_sequence": receipts.get("head_seq"),
            "verify": "PROVEN" if verify is True else (
                "NOT_PROVEN" if verify is None else str(verify)
            ),
            "replay": "PROVEN" if replay is True else (
                "NOT_PROVEN" if replay is None else str(replay)
            ),
            "vault_status": receipts.get("VAULT999"),
            "verify_url": "https://arif-fazil.com/999/",
        },
        "findings": {
            "open_count": len(open_findings),
            "by_severity": by_sev,
            "highest_hold": highest_hold,
            "open": [
                {
                    "id": f.get("id"),
                    "category": f.get("category"),
                    "severity": f.get("severity"),
                    "description": f.get("description"),
                    "evidence": f.get("evidence"),
                    "status": f.get("status"),
                    "url": f"https://arifos.arif-fazil.com/findings/{f.get('id')}",
                }
                for f in open_findings
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
            "mcp_gateway": connect_url,
            "observatory": "https://arifos.arif-fazil.com/",
            "verify_release": release_url,
            "verify_receipt": "https://arif-fazil.com/999/",
            "public_state": "https://arifos.arif-fazil.com/api/public-state",
            "public_state_static": "https://arifos.arif-fazil.com/public-state.json",
            "canon": "https://arif-fazil.com/canon/",
            "github": "https://github.com/ariffazil/arifOS",
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


def main() -> int:
    snap = load_snapshot()
    health = get_health()
    if not snap and not health:
        print("error: no snapshot and no health", file=sys.stderr)
        return 1
    state = project_public_state(snap, health)
    paths = write_public_state(state)
    print(
        f"public-state {state['schema']} headline={state['headline']!r} "
        f"tools={state['mcp']['public_tools']} alignment={state['release']['deployment_alignment']} "
        f"open_findings={state['findings']['open_count']} paths={[str(p) for p in paths]}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
