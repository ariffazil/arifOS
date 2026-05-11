from __future__ import annotations

import hashlib
import json
import time
from arifos.core.governance import (
    ThermodynamicMetrics,
    governed_return,
    append_vault999_event,
    Verdict,
)
from arifos.tools._tool_support import (
    invariant_fields,
    probe_tcp_endpoint,
    resolve_tcp_endpoint,
)


async def execute(
    action: str = "query",
    query: str | None = None,
    operator_id: str | None = None,
    session_id: str | None = None,
) -> dict:
    # ─── Phase 1: Pre-flight readiness probe (postgres + redis) ─────────────────
    readiness_probe = "PASS"
    readiness_detail_parts = []

    pg_probe = probe_tcp_endpoint(
        resolve_tcp_endpoint(
            host_env="ARIFOS_PG_HOST",
            port_env="ARIFOS_PG_PORT",
            url_envs=("DATABASE_URL",),
            default_port=5432,
        )
    )
    readiness_detail_parts.append(f"postgres:{pg_probe['detail']}")
    if pg_probe["configured"] and pg_probe["reachable"] is False:
        readiness_probe = "FAIL"

    redis_probe = probe_tcp_endpoint(
        resolve_tcp_endpoint(
            host_env="ARIFOS_REDIS_HOST",
            port_env="ARIFOS_REDIS_PORT",
            url_envs=("REDIS_URL",),
            default_port=6379,
        )
    )
    readiness_detail_parts.append(f"redis:{redis_probe['detail']}")
    if redis_probe["configured"] and redis_probe["reachable"] is False:
        readiness_probe = "FAIL"

    readiness_detail = (
        ", ".join(readiness_detail_parts) if readiness_detail_parts else "no_checks"
    )

    # ─── Main logic ───────────────────────────────────────────────────────────
    report = {
        "action": action,
        "query": query,
        "memory_status": "GOVERNED_RECALL",
        "temporal_coherence": None,
    }
    report.update(
        invariant_fields(
            tool_name="arifos_555_memory",
            input_payload={
                "action": action,
                "query": query,
                "operator_id": operator_id,
                "session_id": session_id,
            },
            assumptions=[
                "Memory stage runs in bounded recall mode unless a concrete backend is explicitly configured.",
                "Backend probes are advisory when runtime endpoints are absent, not proof of memory corruption.",
                "This stage reports governed recall posture rather than full semantic retrieval guarantees.",
            ],
            floors_evaluated=["F11"],
            confidence=0.72 if readiness_probe == "PASS" else 0.58,
            extra_meta={"backend_probe": {"postgres": pg_probe, "redis": redis_probe}},
        )
    )

    # Removed hardcoded metric assertions — set to NULL/UNKNOWN
    metrics = ThermodynamicMetrics(
        truth_score=None,
        delta_s=None,
        omega_0=None,
        peace_squared=None,
        amanah_lock=None,
        tri_witness_score=None,
        stakeholder_safety=None,
    )

    result = governed_return(
        "arifos_555_memory", report, metrics, operator_id, session_id
    )

    # ─── Phase 1: Append metabolic_metadata ───────────────────────────────────
    output_str = json.dumps(report, sort_keys=True, ensure_ascii=False)
    source_integrity = hashlib.sha256(output_str.encode("utf-8")).hexdigest()

    result["metabolic_metadata"] = {
        "source_integrity": source_integrity,
        "confidence_score": None,
        "floor_alignment": ["F2", "F4", "F7"],
        "readiness_probe": readiness_probe,
        "readiness_detail": readiness_detail,
        "verdict": result.get("verdict", Verdict.CLAIM_ONLY),
        "vault_receipt": None,
        "delta_s": None,
        "peace_squared": None,
        "omega_0": None,
        "timestamp_epoch": time.time(),
    }

    # ─── Phase 1: Vault-999 event ─────────────────────────────────────────────
    try:
        vault_receipt = append_vault999_event(
            event_type="arifos_555_memory",
            payload={
                "report": report,
                "metabolic_metadata": result["metabolic_metadata"],
            },
            operator_id=operator_id,
            session_id=session_id,
        )
        result["metabolic_metadata"]["vault_receipt"] = vault_receipt
    except Exception as e:
        result["metabolic_metadata"]["vault_receipt"] = f"FAIL({e})"

    return result
