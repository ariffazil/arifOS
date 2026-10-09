"""
memory_reconciler.py — Autonomous Background Reality-Veto Reconciliation Engine.

DITEMPA BUKAN DIBERI — Forged, not given.
Prime Directive:
    Reality(t+1) has veto power over Memory(t).
    A stored representation never outranks fresh, authenticated reality.

Canonical owner for:
    - P1-MEM-001: Background reality-veto periodic reconciliation
    - P1-MEM-002: Semantic vector layer (Qdrant) supersession synchronization
    - P1-MEM-003: Temporal graph edge retirement (respecting retired_888 status)

Architecture:
    PostgreSQL = canonical corrigible epistemic record
    Qdrant     = semantic retrieval index
    Graph      = temporal relationship projection (currently retired_888)
    VAULT999   = immutable witness
"""

import argparse
import asyncio
import hashlib
import json
import logging
import subprocess
import time
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from arifosmcp.runtime.memory_store import (
    _PG_URL,
    execute_reality_veto,
    reality_veto_check,
)

logger = logging.getLogger("arifOS.memory_reconciler")
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")


# ── Built-in Re-Observable Reality Probes ────────────────────────────────────


def probe_git_head(repo_path: str = "/root/arifOS") -> dict[str, Any]:
    """Probe current git HEAD commit SHA."""
    try:
        head = subprocess.check_output(
            ["git", "-C", repo_path, "rev-parse", "HEAD"],
            text=True,
            timeout=5,
        ).strip()
        return {"git_head": head, "repo": repo_path, "observed_at": datetime.now(UTC).isoformat()}
    except Exception as exc:
        return {"error": str(exc), "repo": repo_path}


def probe_service_health(url: str = "http://127.0.0.1:8088/health") -> dict[str, Any]:
    """Probe live HTTP health endpoint."""
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
        return {
            "service_health": data.get("service_health", "unknown"),
            "live_commit": data.get("live_commit", "unknown"),
            "runtime_drift": data.get("runtime_drift", None),
            "observed_at": datetime.now(UTC).isoformat(),
        }
    except Exception as exc:
        return {"error": str(exc), "url": url}


def probe_file_hash(file_path: str) -> dict[str, Any]:
    """Compute SHA256 of a local file."""
    try:
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return {
            "file_path": file_path,
            "sha256": h.hexdigest(),
            "observed_at": datetime.now(UTC).isoformat(),
        }
    except Exception as exc:
        return {"error": str(exc), "file_path": file_path}


def probe_systemd_status(service_name: str) -> dict[str, Any]:
    """Probe systemd service active status."""
    try:
        res = subprocess.check_output(
            ["systemctl", "is-active", service_name],
            text=True,
            timeout=5,
        ).strip()
        return {
            "service": service_name,
            "status": res,
            "observed_at": datetime.now(UTC).isoformat(),
        }
    except subprocess.CalledProcessError as e:
        return {
            "service": service_name,
            "status": e.output.strip(),
            "observed_at": datetime.now(UTC).isoformat(),
        }
    except Exception as exc:
        return {"error": str(exc), "service": service_name}


PROBE_REGISTRY: dict[str, Callable[..., dict[str, Any]]] = {
    "git_head": probe_git_head,
    "service_health": probe_service_health,
    "file_hash": probe_file_hash,
    "systemd_status": probe_systemd_status,
}


# ── Canonical Memory Reconciler ──────────────────────────────────────────────


class MemoryReconciler:
    """Continuously reconciles active stored memories against physical reality."""

    def __init__(
        self,
        pg_url: str | None = None,
        dry_run: bool = False,
    ):
        self.pg_url = pg_url or _PG_URL
        self.dry_run = dry_run

    async def fetch_active_claims(self, limit: int = 100) -> list[dict[str, Any]]:
        """Fetch active, un-superseded memory claims from PostgreSQL."""
        import asyncpg  # noqa: PLC0415

        conn = await asyncpg.connect(self.pg_url, timeout=5, statement_cache_size=0)
        try:
            rows = await conn.fetch(
                """
                SELECT id, tier, text, metadata, qdrant_id, session_id, created_at
                FROM memory_store
                WHERE deleted_at IS NULL
                  AND (metadata->>'status' IS NULL
                       OR metadata->>'status' NOT IN ('superseded', 'revoked'))
                ORDER BY created_at DESC
                LIMIT $1
                """,
                limit,
            )
            claims = []
            for r in rows:
                meta = (
                    json.loads(r["metadata"])
                    if isinstance(r["metadata"], str)
                    else (r["metadata"] or {})
                )
                claims.append(
                    {
                        "id": str(r["id"]),
                        "tier": r["tier"],
                        "text": r["text"],
                        "metadata": meta,
                        "qdrant_id": str(r["qdrant_id"]) if r["qdrant_id"] else None,
                        "session_id": r["session_id"],
                        "created_at": r["created_at"].isoformat() if r["created_at"] else None,
                    }
                )
            return claims
        finally:
            await conn.close()

    def evaluate_claim(self, claim: dict[str, Any]) -> dict[str, Any]:
        """Evaluate an individual claim against its probe contract."""
        meta = claim.get("metadata", {})
        contract = meta.get("probe_contract") or meta.get("probe")
        if not contract or not isinstance(contract, dict):
            # No re-observable contract registered
            return {"reconcilable": False, "reason": "no_probe_contract"}

        probe_type = contract.get("type")
        probe_fn = PROBE_REGISTRY.get(probe_type)
        if not probe_fn:
            return {"reconcilable": False, "reason": f"unknown_probe_type:{probe_type}"}

        probe_args = contract.get("args", {})
        fresh_obs = probe_fn(**probe_args)
        if "error" in fresh_obs:
            return {"reconcilable": False, "reason": f"probe_error:{fresh_obs['error']}"}

        # Stored expected value
        stored_values = (
            meta.get("expected_values") or meta.get("observed_reality") or meta.get("claim")
        )
        if not stored_values or not isinstance(stored_values, dict):
            stored_values = contract.get("expected", {})

        key_fields = contract.get("key_fields") or list(
            set(stored_values.keys()) & set(fresh_obs.keys())
        )
        veto_res = reality_veto_check(stored_values, fresh_obs, key_fields=key_fields)

        return {
            "reconcilable": True,
            "probe_type": probe_type,
            "stored_values": stored_values,
            "fresh_observation": fresh_obs,
            "veto_result": veto_res,
        }

    async def reconcile_single_claim(
        self,
        claim: dict[str, Any],
        eval_result: dict[str, Any],
        *,
        trace_id: str,
        objective_id: str,
    ) -> dict[str, Any]:
        """Apply reality veto if contradiction detected."""
        veto_res = eval_result.get("veto_result", {})
        if not veto_res.get("veto"):
            return {"status": "consistent", "claim_id": claim["id"]}

        reason = veto_res.get("reason", "reality_veto")
        if self.dry_run:
            logger.info("[DRY-RUN] Reality veto detected on claim %s: %s", claim["id"], reason)
            return {
                "status": "veto_detected_dry_run",
                "claim_id": claim["id"],
                "reason": reason,
                "fresh_observation": eval_result.get("fresh_observation"),
            }

        logger.info("Executing reality veto on claim %s: %s", claim["id"], reason)
        exec_res = await execute_reality_veto(
            stored_memory_id=claim["id"],
            stored_claim=eval_result.get("stored_values", {}),
            fresh_observation=eval_result.get("fresh_observation", {}),
            actor_id="memory_reconciler",
            session_id="session-reconcile-daemon",
            trace_id=trace_id,
            objective_id=objective_id,
            reason=reason,
        )

        return {
            "status": "veto_executed",
            "claim_id": claim["id"],
            "reason": reason,
            "execution": exec_res,
        }

    async def run(
        self,
        *,
        limit: int = 100,
        trace_id: str | None = None,
        objective_id: str = "obj-memory-homeostasis",
    ) -> dict[str, Any]:
        """Run full reconciliation pass across stored memory claims."""
        start_t = time.time()
        tid = trace_id or f"trc-reconcile-{int(time.time())}"

        claims = await self.fetch_active_claims(limit=limit)
        scanned = len(claims)
        evaluated = 0
        consistent = 0
        vetoes = 0
        details = []

        for claim in claims:
            res = self.evaluate_claim(claim)
            if not res.get("reconcilable"):
                continue

            evaluated += 1
            action_res = await self.reconcile_single_claim(
                claim,
                res,
                trace_id=tid,
                objective_id=objective_id,
            )

            if action_res.get("status") == "consistent":
                consistent += 1
            elif "veto" in action_res.get("status", ""):
                vetoes += 1
                details.append(action_res)

        elapsed = round(time.time() - start_t, 3)
        summary = {
            "status": "completed",
            "dry_run": self.dry_run,
            "scanned_claims": scanned,
            "evaluated_claims": evaluated,
            "consistent_claims": consistent,
            "vetoes_triggered": vetoes,
            "trace_id": tid,
            "objective_id": objective_id,
            "duration_seconds": elapsed,
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "details": details,
        }
        logger.info(
            "Reconciliation pass complete: scanned=%d evaluated=%d consistent=%d vetoes=%d (%ss)",
            scanned,
            evaluated,
            consistent,
            vetoes,
            elapsed,
        )
        return summary


# ── CLI ──────────────────────────────────────────────────────────────────────


async def _main():
    parser = argparse.ArgumentParser(description="arifOS Memory Reconciler")
    parser.add_argument(
        "--dry-run", action="store_true", help="Detect contradictions without superseding"
    )
    parser.add_argument(
        "--apply", action="store_true", help="Execute reality veto on contradictions"
    )
    parser.add_argument("--limit", type=int, default=100, help="Max claims to scan")
    parser.add_argument("--trace-id", type=str, default=None, help="Custom trace ID")
    args = parser.parse_args()

    dry_run = not args.apply
    reconciler = MemoryReconciler(dry_run=dry_run)
    report = await reconciler.run(limit=args.limit, trace_id=args.trace_id)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    asyncio.run(_main())
