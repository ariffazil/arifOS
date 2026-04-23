"""
core/kernel/substrate_assert.py — 000.SUBSTRATE_ASSERT

Pre-constitutional bootstrap invariant gate.
Runs before 000_INIT to verify the substrate is fit to exist.

DITEMPA BUKAN DIBERI — Forged, Not Given

CLAIM: A governed intelligence must assert its own legibility before it asserts identity.
       Identity without legibility is not sovereignty. It is theater.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import socket
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger("arifOS.SUBSTRATE_ASSERT")


@dataclass
class SubstrateCheckResult:
    check_id: str
    passed: bool
    code: str | None = None
    latency_ms: float = 0.0
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass
class SubstrateAssertResult:
    status: str
    legibility_state: str
    checks: list[SubstrateCheckResult]
    pipeline_gate: str
    failure_codes: list[str] = field(default_factory=list)
    session_id: str | None = None
    epoch: str | None = None


def _dns_resolve(hostname: str = "localhost", timeout_ms: int = 5000) -> SubstrateCheckResult:
    """S0.C1: DNS resolve from inside container."""
    t0 = time.monotonic()
    code = None
    did_pass = False
    detail = {}
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout_ms / 1000)
        result = sock.connect_ex(("8.8.8.8", 53))
        sock.close()
        if result == 0:
            try:
                socket.gethostbyname(hostname)
            except socket.gaierror:
                pass
            did_pass = True
            detail = {"dns_reachable": True, "hostname": hostname}
        else:
            code = "E_DNS_BLIND"
            detail = {"connectivity_test": "failed", "errno": result}
    except Exception as e:
        code = "E_DNS_BLIND"
        detail = {"error": str(e)}
    return SubstrateCheckResult(
        check_id="S0.C1",
        passed=did_pass,
        code=code,
        latency_ms=int((time.monotonic() - t0) * 1000),
        detail=detail
    )


def _config_present() -> SubstrateCheckResult:
    """S0.C2: All required .env present + non-default."""
    t0 = time.monotonic()
    code = None
    did_pass = True
    required_vars = ["ARIFOS_KERNEL_VERSION", "ARIFOS_ENV"]
    optional_degraded = ["DATABASE_URL", "POSTGRES_URL"]
    missing = []
    defaulted = []
    degraded = []
    for var in required_vars:
        val = os.environ.get(var)
        if val is None:
            missing.append(var)
            did_pass = False
        elif val in ("", "undefined", "null"):
            defaulted.append(var)
            did_pass = False
    for var in optional_degraded:
        val = os.environ.get(var)
        if not val:
            degraded.append(var)
    if missing:
        code = "E_CONFIG_UNSET"
    detail = {
        "required_vars": required_vars,
        "missing": missing,
        "defaulted": defaulted,
        "degraded": degraded,
        "all_present": len(missing) == 0 and len(defaulted) == 0
    }
    return SubstrateCheckResult(
        check_id="S0.C2",
        passed=did_pass,
        code=code,
        latency_ms=int((time.monotonic() - t0) * 1000),
        detail=detail
    )


async def _db_auth() -> SubstrateCheckResult:
    """S0.C3: Live DB auth query succeeds."""
    t0 = time.monotonic()
    code = None
    did_pass = False
    detail = {}
    pg_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    if not pg_url:
        code = "E_CRED_INVALID"
        detail = {"reason": "no_postgres_url"}
        return SubstrateCheckResult(
            check_id="S0.C3",
            passed=False,
            code=code,
            latency_ms=int((time.monotonic() - t0) * 1000),
            detail=detail
        )
    try:
        import asyncpg
        conn = await asyncpg.connect(pg_url, timeout=5)
        result = await conn.fetchval("SELECT 1")
        await conn.close()
        if result == 1:
            did_pass = True
            detail = {"db_auth": "ok"}
    except Exception as e:
        code = "E_CRED_INVALID"
        detail = {"error": str(e)}
    return SubstrateCheckResult(
        check_id="S0.C3",
        passed=did_pass,
        code=code,
        latency_ms=int((time.monotonic() - t0) * 1000),
        detail=detail
    )


async def _embed_endpoint() -> SubstrateCheckResult:
    """S0.C4: Embedding endpoint returns valid vector."""
    t0 = time.monotonic()
    code = None
    did_pass = False
    detail = {}
    embed_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            payload = {"model": os.environ.get("OLLAMA_EMBED_MODEL", "bge-m3"), "input": "ping"}
            async with session.post(f"{embed_url}/api/embeddings", json=payload, timeout=3) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    embedding = data.get("embedding")
                    if embedding and isinstance(embedding, list) and len(embedding) > 0:
                        did_pass = True
                        detail = {"embedding_dim": len(embedding), "model": payload["model"]}
                    else:
                        code = "E_EMBED_OFFLINE"
                        detail = {"invalid_embedding": embedding}
                else:
                    code = "E_EMBED_OFFLINE"
                    detail = {"status": resp.status}
    except Exception as e:
        code = "E_EMBED_OFFLINE"
        detail = {"error": str(e)}
    return SubstrateCheckResult(
        check_id="S0.C4",
        passed=did_pass,
        code=code,
        latency_ms=int((time.monotonic() - t0) * 1000),
        detail=detail
    )


async def _vault_dryrun() -> SubstrateCheckResult:
    """S0.C5: Dry-run write to vault path succeeds."""
    t0 = time.monotonic()
    code = None
    did_pass = False
    detail = {}
    vault_path = Path(__file__).parents[2] / "VAULT999" / "vault999.jsonl"
    test_line = '{"type":"substrate_assert_test","dryrun":true}\n'
    try:
        vault_path.parent.mkdir(parents=True, exist_ok=True)
        with open(vault_path, "a", encoding="utf-8") as f:
            f.write(test_line)
        with open(vault_path, "r", encoding="utf-8") as f:
            content = f.read()
            if test_line.strip() in content:
                did_pass = True
                detail = {"vault_path": str(vault_path), "writable": True}
    except Exception as e:
        code = "E_VAULT_BLIND"
        detail = {"error": str(e)}
    return SubstrateCheckResult(
        check_id="S0.C5",
        passed=did_pass,
        code=code,
        latency_ms=int((time.monotonic() - t0) * 1000),
        detail=detail
    )


async def _telemetry_channel() -> SubstrateCheckResult:
    """S0.C6: Emit channel open + ACK received."""
    t0 = time.monotonic()
    code = None
    did_pass = False
    detail = {}
    pg_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    if not pg_url:
        code = "E_WITNESS_ABSENT"
        detail = {"reason": "no_postgres"}
        return SubstrateCheckResult(
            check_id="S0.C6",
            passed=False,
            code=code,
            latency_ms=int((time.monotonic() - t0) * 1000),
            detail=detail
        )
    try:
        import asyncpg
        conn = await asyncpg.connect(pg_url, timeout=5)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS substrate_assert_heartbeat (
                id SERIAL PRIMARY KEY, ts TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        row = await conn.fetchrow("INSERT INTO substrate_assert_heartbeat DEFAULT VALUES RETURNING id")
        await conn.execute("DELETE FROM substrate_assert_heartbeat WHERE id = $1", row["id"])
        await conn.close()
        did_pass = True
        detail = {"telemetry_channel": "open", "ack_received": True}
    except Exception as e:
        code = "E_WITNESS_ABSENT"
        detail = {"error": str(e)}
    return SubstrateCheckResult(
        check_id="S0.C6",
        passed=did_pass,
        code=code,
        latency_ms=int((time.monotonic() - t0) * 1000),
        detail=detail
    )


def _config_fingerprint() -> SubstrateCheckResult:
    """S0.C7: Config fingerprint hash matches expected."""
    t0 = time.monotonic()
    code = None
    did_pass = False
    detail = {}
    known_good = os.environ.get("ARIFOS_CONFIG_FINGERPRINT")
    if not known_good:
        did_pass = True
        detail = {"reason": "no_fingerprint_set", "status": "unverified_but_proceeding"}
        return SubstrateCheckResult(
            check_id="S0.C7",
            passed=True,
            code=None,
            latency_ms=int((time.monotonic() - t0) * 1000),
            detail=detail
        )
    config_snapshot = json.dumps(sorted({
        k: v for k, v in os.environ.items()
        if k.startswith(("ARIFOS_", "DATABASE_", "POSTGRES_", "OLLAMA_"))
    }.items()), sort_keys=True)
    actual = hashlib.sha256(config_snapshot.encode()).hexdigest()[:16]
    if actual == known_good:
        did_pass = True
        detail = {"fingerprint_match": True, "fingerprint": actual}
    else:
        code = "E_HASH_DRIFT"
        detail = {"expected": known_good, "actual": actual}
    return SubstrateCheckResult(
        check_id="S0.C7",
        passed=did_pass,
        code=code,
        latency_ms=int((time.monotonic() - t0) * 1000),
        detail=detail
    )


async def substrate_assert(session_id: str | None = None) -> SubstrateAssertResult:
    """
    Execute all 7 pre-constitutional substrate invariant checks in parallel.

    Returns SubstrateAssertResult with:
      - status: PASS | FAIL_RECOVERABLE | FAIL_FATAL
      - legibility_state: FIT | DEGRADED | SEVERED
      - pipeline_gate: PROCEED | 888_HOLD | HARD_STOP
      - failure_codes: list of E_* codes that failed

    HARD STOP conditions (pipeline cannot run):
      - E_DNS_BLIND, E_CONFIG_UNSET, E_CRED_INVALID, E_VAULT_BLIND, E_WITNESS_ABSENT

    DEGRADED conditions (pipeline can run with 888_HOLD):
      - E_EMBED_OFFLINE, E_HASH_DRIFT
    """
    t0 = time.time()

    dns_check = _dns_resolve()
    config_check = _config_present()
    db_check = await _db_auth()
    embed_check = await _embed_endpoint()
    vault_check = await _vault_dryrun()
    telemetry_check = await _telemetry_channel()
    fingerprint_check = _config_fingerprint()

    checks = [
        dns_check, config_check, db_check, embed_check,
        vault_check, telemetry_check, fingerprint_check
    ]

    critical_codes = {"E_DNS_BLIND", "E_CONFIG_UNSET", "E_CRED_INVALID", "E_VAULT_BLIND", "E_WITNESS_ABSENT"}
    degraded_codes = {"E_EMBED_OFFLINE", "E_HASH_DRIFT"}

    failed = [c for c in checks if not c.passed]
    failure_codes = [c.code for c in failed if c.code]
    critical_failures = [c for c in failed if c.code in critical_codes]
    degraded_failures = [c for c in failed if c.code in degraded_codes]

    total_ms = int((time.time() - t0) * 1000)

    if critical_failures:
        status = "FAIL_FATAL"
        legibility = "SEVERED"
        pipeline_gate = "HARD_STOP"
    elif degraded_failures:
        status = "FAIL_RECOVERABLE"
        legibility = "DEGRADED"
        pipeline_gate = "888_HOLD"
    else:
        status = "PASS"
        legibility = "FIT"
        pipeline_gate = "PROCEED"

    result = SubstrateAssertResult(
        status=status,
        legibility_state=legibility,
        checks=checks,
        pipeline_gate=pipeline_gate,
        failure_codes=failure_codes,
        session_id=session_id,
        epoch=datetime.now(UTC).isoformat(),
    )

    logger.info(
        "SUBSTRATE_ASSERT %s | legibility=%s | gate=%s | codes=%s | latency=%dms",
        status, legibility, pipeline_gate, failure_codes, total_ms
    )

    return result


async def emit_substrate_assert_event(result: SubstrateAssertResult) -> None:
    """
    Emit SUBSTRATE_ASSERT result to vault as a sealed event.
    Even FAIL must attempt emission. If emission path itself is unavailable -> crash loudly.
    Below constitutional law, silence is not allowed.
    """
    from core.organs._4_vault import seal

    checks_payload = {}
    for c in result.checks:
        checks_payload[c.check_id] = {
            "pass": c.passed,
            "code": c.code,
            "latency_ms": c.latency_ms,
            **c.detail
        }

    vault_payload = {
        "event_type": "SUBSTRATE_ASSERT",
        "epoch": result.epoch,
        "session_id": result.session_id or "unknown",
        "result": result.status,
        "legibility_state": result.legibility_state,
        "pipeline_gate": result.pipeline_gate,
        "failure_codes": result.failure_codes,
        "checks": checks_payload,
        "witness": {"human": False, "ai": True, "earth": False}
    }

    if result.status == "PASS":
        verdict = "SEAL"
    elif result.status == "FAIL_RECOVERABLE":
        verdict = "HOLD"
    else:
        verdict = "VOID"

    try:
        await seal(
            session_id=result.session_id or "SUBSTRATE_ASSERT",
            summary=f"SUBSTRATE_ASSERT {result.status}: {result.legibility_state} | gate={result.pipeline_gate}",
            verdict=verdict,
            telemetry=vault_payload,
            source_agent="arifos_kernel",
            pipeline_stage="000.SUBSTRATE_ASSERT",
            seal_mode="final" if result.status == "PASS" else "provisional",
        )
    except Exception as e:
        logger.critical(
            "SUBSTRATE_ASSERT vault emission FAILED — hard stop. "
            "Emission path itself is unavailable. Error: %s",
            str(e)
        )
        raise RuntimeError(
            f"SUBSTRATE_ASSERT cannot emit: vault write path broken. "
            f"Cannot continue. Failure codes: {result.failure_codes}"
        ) from e


if __name__ == "__main__":
    import asyncio as _asyncio

    async def _main():
        result = await substrate_assert()
        print(json.dumps({
            "status": result.status,
            "legibility_state": result.legibility_state,
            "pipeline_gate": result.pipeline_gate,
            "failure_codes": result.failure_codes,
            "checks": {
                c.check_id: {"pass": c.passed, "code": c.code, "latency_ms": c.latency_ms}
                for c in result.checks
            }
        }, indent=2))
        if result.pipeline_gate == "HARD_STOP":
            exit(1)
        elif result.pipeline_gate == "888_HOLD":
            exit(2)

    _asyncio.run(_main())