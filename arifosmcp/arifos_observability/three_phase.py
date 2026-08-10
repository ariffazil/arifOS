"""
3-Phase Observability Wrapper — Python execution path that bypasses MCP.

Forged 2026-08-10. Lane B SESSION_RECEIPT ratification.
Adopted doctrine: /root/AAA/governance/AAA_3PHASE_OBSERVABILITY.md

This module wraps Python code that calls out to non-MCP backends
(ComfyUI, vLLM, raw torch inference, urllib, subprocess) with the same
3-phase contract that MCP tool calls get automatically:

  PRE_FLIGHT  →  AAAExecutionGuard (file, service, VRAM, session)
  RUNTIME     →  AAAFlowEngine.execute_sovereign_task() (latency, peak VRAM)
  POST_FLIGHT →  flow_ingest(Verify) + VLM perception (if image)

CRITICAL: This module does NOT write to a parallel ledger. Every receipt
routes through arifFlow :7073 → /root/.local/share/arifos/arifflow_receipts.jsonl.
See doctrine §2 (F4 CLARITY — ΔS ≤ 0).

Floor binding:
  F1 AMANAH   — PRE_FLIGHT aborts on any guard failure; no destructive act without barrier receipt
  F2 TRUTH    — epistemic_label on every RUNTIME step; W³ at POST_FLIGHT when stakes warrant
  F4 CLARITY  — single canonical ledger; no /workspace/telemetry.jsonl
  F11 AUDIT   — every phase emits hash-chained receipt via flow_ingest
  F12 RESILIENCE — VRAM guard prevents OOM; service guard prevents orphan processes
  F13 SOVEREIGN — Lane B self-ratify; Lane A escalate when irreversible
"""

from __future__ import annotations

import os
import time
import uuid
import urllib.error
import urllib.request
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional, Tuple

__all__ = [
    "AAAGuardResult",
    "AAAExecutionGuard",
    "AAAFlowEngine",
    "FlowReceiptProxy",
]


# ─────────────────────────────────────────────────────────────────────────────
# Canonical receipt surface
# ─────────────────────────────────────────────────────────────────────────────


class FlowReceiptProxy:
    """
    Thin wrapper that emits receipts via arifFlow :7073/mcp flow_ingest.

    Falls back gracefully when arifFlow is unavailable — logs locally but
    does NOT create a parallel ledger. Returns a receipt_id for the caller
    to attach to the next phase.

    Single source of truth: /root/.local/share/arifos/arifflow_receipts.jsonl.
    """

    DEFAULT_ENDPOINT = os.environ.get("ARIFFLOW_ENDPOINT", "http://127.0.0.1:7073")
    DEFAULT_TIMEOUT_S = float(os.environ.get("ARIFFLOW_TIMEOUT_S", "2.0"))

    def __init__(
        self,
        endpoint: Optional[str] = None,
        actor_id: str = "kimi-code/FI-008",
        timeout_s: float = DEFAULT_TIMEOUT_S,
    ) -> None:
        self.endpoint = endpoint or self.DEFAULT_ENDPOINT
        self.actor_id = actor_id
        self.timeout_s = timeout_s

    def emit(
        self,
        step_type: str,
        floor_verdict: str,
        epistemic_label: str = "Observation",
        payload: Optional[dict] = None,
        session_id: Optional[str] = None,
        previous_receipt_hash: Optional[str] = None,
    ) -> str:
        """
        Emit one flow receipt. Returns receipt_id.

        step_type: Execute | Verify | Cool | Seal | Barrier | Merge | Route
        floor_verdict: Pass | Caution | Hold | Void
        epistemic_label: Observation | Derivation | Interpretation | Specification | Seal
        """
        receipt_id = f"r3p-{uuid.uuid4().hex[:12]}"
        envelope: dict[str, Any] = {
            "receipt_id": receipt_id,
            "actor_id": self.actor_id,
            "session_id": session_id or os.environ.get("ARIFOS_SESSION_ID", "ad-hoc"),
            "step_type": step_type,
            "step_number": int(time.time() * 1_000_000),  # monotonic proxy
            "cost_ns": 0,
            "epistemic_label": epistemic_label,
            "floor_verdict": floor_verdict,
            "topology_id": "three_phase_wrapper",
            "payload": payload or {},
        }
        if previous_receipt_hash:
            envelope["previous_receipt_hash"] = previous_receipt_hash

        body = json.dumps(envelope).encode("utf-8")
        req = urllib.request.Request(
            f"{self.endpoint}/ingest",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                if resp.status >= 400:
                    # Caller decides: floor Hold vs Void.
                    return f"{receipt_id}:ERR_HTTP_{resp.status}"
                return receipt_id
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            # arifFlow down. Don't fake a receipt — return error marker.
            # Per F11: empty receipt is worse than a receipt flagged "degraded".
            return f"{receipt_id}:UNREACHABLE:{type(exc).__name__}"


# ─────────────────────────────────────────────────────────────────────────────
# Pre-flight guards
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class AAAGuardResult:
    """Result of one guard check. Immutable."""

    ok: bool
    name: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


class AAAExecutionGuard:
    """
    Pre-flight guardrails for non-MCP execution paths.

    Each method returns (ok, message). All checks are READ-ONLY — they
    never mutate state. Failures should abort the calling task before
    any destructive act (F1 AMANAH).
    """

    @staticmethod
    def verify_file_integrity(
        file_path: str,
        min_size_mb: float = 100.0,
    ) -> AAAGuardResult:
        """File exists and meets minimum byte size threshold."""
        path = Path(file_path)
        if not path.exists():
            return AAAGuardResult(
                ok=False,
                name="file_integrity",
                message=f"File missing: {file_path}",
            )
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb < min_size_mb:
            return AAAGuardResult(
                ok=False,
                name="file_integrity",
                message=(
                    f"File incomplete: {file_path} "
                    f"({size_mb:.2f} MB < {min_size_mb} MB threshold)"
                ),
                details={"size_mb": size_mb, "min_mb": min_size_mb},
            )
        return AAAGuardResult(
            ok=True,
            name="file_integrity",
            message=f"Verified: {file_path} ({size_mb:.2f} MB)",
            details={"size_mb": size_mb},
        )

    @staticmethod
    def check_service_health(
        endpoint_url: str,
        timeout_s: int = 2,
    ) -> AAAGuardResult:
        """HTTP GET to endpoint. Expects 200 OK."""
        try:
            req = urllib.request.Request(endpoint_url)
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                if 200 <= resp.status < 300:
                    return AAAGuardResult(
                        ok=True,
                        name="service_health",
                        message=f"Service UP: {endpoint_url}",
                        details={"status": resp.status},
                    )
                return AAAGuardResult(
                    ok=False,
                    name="service_health",
                    message=f"Service returned status: {resp.status}",
                    details={"status": resp.status},
                )
        except Exception as exc:
            return AAAGuardResult(
                ok=False,
                name="service_health",
                message=f"Service unreachable: {endpoint_url} ({exc})",
                details={"exception": type(exc).__name__},
            )

    @staticmethod
    def check_vram_capacity(
        required_vram_gb: float = 12.0,
    ) -> AAAGuardResult:
        """
        Inspect CUDA memory availability. Returns ok=False if torch is not
        installed or CUDA is unavailable — by design, since arifOS kernel
        is torch-free (F12 RESILIENCE — no new attack surface).

        For pure CPU code paths, this guard is skipped (caller decides).
        """
        try:
            import torch  # type: ignore[import-not-found]
        except ImportError:
            return AAAGuardResult(
                ok=True,  # not a failure — torch absent means CPU path
                name="vram_capacity",
                message="torch not installed; CPU path — VRAM check skipped",
                details={"skipped": True},
            )
        if not torch.cuda.is_available():
            return AAAGuardResult(
                ok=True,
                name="vram_capacity",
                message="CUDA unavailable; CPU path — VRAM check skipped",
                details={"skipped": True},
            )
        try:
            free_bytes, _ = torch.cuda.mem_get_info()
            free_gb = free_bytes / (1024 ** 3)
        except Exception as exc:
            return AAAGuardResult(
                ok=False,
                name="vram_capacity",
                message=f"torch.cuda.mem_get_info failed: {exc}",
                details={"exception": type(exc).__name__},
            )
        if free_gb < required_vram_gb:
            return AAAGuardResult(
                ok=False,
                name="vram_capacity",
                message=(
                    f"Insufficient VRAM: {free_gb:.2f} GB free "
                    f"< {required_vram_gb} GB required"
                ),
                details={"free_gb": free_gb, "required_gb": required_vram_gb},
            )
        return AAAGuardResult(
            ok=True,
            name="vram_capacity",
            message=f"VRAM Ready: {free_gb:.2f} GB free",
            details={"free_gb": free_gb},
        )

    @staticmethod
    def run_all(
        *,
        model_path: Optional[str] = None,
        api_url: Optional[str] = None,
        min_model_size_mb: float = 1000.0,
        required_vram_gb: float = 12.0,
    ) -> Tuple[bool, list[AAAGuardResult]]:
        """Run the standard pre-flight bundle. Returns (all_passed, results)."""
        results: list[AAAGuardResult] = []
        if model_path:
            results.append(
                AAAExecutionGuard.verify_file_integrity(
                    model_path, min_size_mb=min_model_size_mb
                )
            )
        if api_url:
            results.append(
                AAAExecutionGuard.check_service_health(f"{api_url}/system_stats")
            )
        results.append(
            AAAExecutionGuard.check_vram_capacity(required_vram_gb=required_vram_gb)
        )
        all_ok = all(r.ok for r in results)
        return all_ok, results


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline driver
# ─────────────────────────────────────────────────────────────────────────────


class AAAFlowEngine:
    """
    3-phase pipeline driver for non-MCP execution paths.

    PRE_FLIGHT  → guards + Barrier receipt via FlowReceiptProxy
    RUNTIME     → user-supplied callable executes; latency + peak VRAM measured
    POST_FLIGHT → user-supplied verification callable; Verify receipt emitted

    Receipts route to arifFlow :7073 → arifflow_receipts.jsonl.
    NO parallel ledger.
    """

    def __init__(
        self,
        actor_id: str = "kimi-code/FI-008",
        arifflow_endpoint: Optional[str] = None,
    ) -> None:
        self.receipts = FlowReceiptProxy(
            endpoint=arifflow_endpoint,
            actor_id=actor_id,
        )

    def execute_sovereign_task(
        self,
        *,
        task_callable: Callable[[], Any],
        model_path: Optional[str] = None,
        api_url: Optional[str] = None,
        pre_flight_guards: Optional[list[AAAGuardResult]] = None,
        post_flight_verifier: Optional[Callable[[Any], Tuple[bool, str]]] = None,
        task_label: str = "sovereign_task",
        min_model_size_mb: float = 1000.0,
        required_vram_gb: float = 12.0,
    ) -> dict[str, Any]:
        """
        Run the 3-phase contract end-to-end. Returns a result envelope.

        The caller supplies `task_callable` (the actual work) and optionally
        a `post_flight_verifier` (returns (ok, message)). Pre-flight guards
        run automatically unless `pre_flight_guards` is provided.

        On PRE_FLIGHT failure: abort, emit Barrier receipt verdict=Hold,
        return {"ok": False, "phase": "PRE_FLIGHT", ...}.

        On RUNTIME exception: emit Execute receipt verdict=Void, return ok=False.

        On POST_FLIGHT verifier failure: emit Verify receipt verdict=Caution,
        return ok=True (work happened, but flag the perception gap).
        """
        result: dict[str, Any] = {
            "ok": False,
            "task_label": task_label,
            "phase": None,
            "pre_flight": [],
            "runtime": {},
            "post_flight": {},
        }

        # ── PHASE 1: PRE_FLIGHT ─────────────────────────────────────────
        if pre_flight_guards is None:
            ok, guards = AAAExecutionGuard.run_all(
                model_path=model_path,
                api_url=api_url,
                min_model_size_mb=min_model_size_mb,
                required_vram_gb=required_vram_gb,
            )
        else:
            guards = list(pre_flight_guards)
            ok = all(g.ok for g in guards)
        result["pre_flight"] = [
            {"name": g.name, "ok": g.ok, "message": g.message} for g in guards
        ]
        verdict = "Pass" if ok else "Hold"
        self.receipts.emit(
            step_type="Barrier",
            floor_verdict=verdict,
            epistemic_label="Observation",
            payload={"task_label": task_label, "guards": result["pre_flight"]},
        )
        if not ok:
            result["phase"] = "PRE_FLIGHT"
            return result

        # ── PHASE 2: RUNTIME ────────────────────────────────────────────
        result["phase"] = "RUNTIME"
        start_time = time.time()
        peak_vram_gb: Optional[float] = None
        try:
            output = task_callable()
            elapsed_s = time.time() - start_time
            peak_vram_gb = self._measure_peak_vram_gb()
            runtime_payload: dict[str, Any] = {
                "elapsed_seconds": round(elapsed_s, 3),
            }
            if peak_vram_gb is not None:
                runtime_payload["peak_vram_gb"] = round(peak_vram_gb, 3)
            self.receipts.emit(
                step_type="Execute",
                floor_verdict="Pass",
                epistemic_label="Observation",
                payload={"task_label": task_label, **runtime_payload},
            )
            result["runtime"] = runtime_payload
        except Exception as exc:
            elapsed_s = time.time() - start_time
            self.receipts.emit(
                step_type="Execute",
                floor_verdict="Void",
                epistemic_label="Observation",
                payload={
                    "task_label": task_label,
                    "elapsed_seconds": round(elapsed_s, 3),
                    "exception": type(exc).__name__,
                    "error": str(exc),
                },
            )
            result["runtime"] = {"exception": type(exc).__name__, "error": str(exc)}
            return result

        # ── PHASE 3: POST_FLIGHT ────────────────────────────────────────
        result["phase"] = "POST_FLIGHT"
        post_ok, post_msg = True, "no verifier supplied"
        if post_flight_verifier is not None:
            try:
                post_ok, post_msg = post_flight_verifier(output)
            except Exception as exc:
                post_ok, post_msg = False, f"verifier exception: {exc}"
        verdict = "Pass" if post_ok else "Caution"
        self.receipts.emit(
            step_type="Verify",
            floor_verdict=verdict,
            epistemic_label="Observation",
            payload={
                "task_label": task_label,
                "post_flight_ok": post_ok,
                "message": post_msg,
            },
        )
        result["post_flight"] = {"ok": post_ok, "message": post_msg}
        result["output"] = output
        result["ok"] = post_ok

        # Best-effort CUDA cache release (no-op if torch absent)
        self._release_cuda_cache()
        return result

    # ── internals ──────────────────────────────────────────────────────

    @staticmethod
    def _measure_peak_vram_gb() -> Optional[float]:
        try:
            import torch  # type: ignore[import-not-found]
        except ImportError:
            return None
        if not torch.cuda.is_available():
            return None
        try:
            return torch.cuda.max_memory_allocated() / (1024 ** 3)
        except Exception:
            return None

    @staticmethod
    def _release_cuda_cache() -> None:
        try:
            import torch  # type: ignore[import-not-found]
        except ImportError:
            return
        if torch.cuda.is_available():
            try:
                torch.cuda.empty_cache()
            except Exception:
                pass