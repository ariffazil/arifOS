"""
arifOS RSI — SEAL → INIT → Scaffold → Diff event bus.

Forged 2026-07-04 (YELLOW) by Hermes/MiniMax-M3.
Revised 2026-07-04 (YELLOW) under sovereign 999_HOLD correction:
    "SEAL → INIT → Scaffold is not the mutation path. It is the regeneration
     review path. The missing stage is Diff."

Doctrine (from arif-fazil.com/essays/ + AGENTS.md):
    SEAL is irreversible. It locks the receipt and triggers RSI_REVIEW.
    RSI_REVIEW may emit a SkillDelta (proposal). It must never autonomously
    mutate the system. Judge owns semantic change. A-FORGE applies patches
    only after Judge + cooling.

This is the irreducible trigger. It does not run the 9 stages itself — that
work is fanned out as registered hooks. Each stage lives in its own file
under `arifosmcp/rsi/stages/` and is registered here by name. Wiring is
intentionally explicit: any agent can read this file and know exactly what
fires on every SEAL — and which stages are review-only vs. proposal-only.

Bound to the trim 2026-07-04 — kernel now exposes `arif_judge` (which can
return SEAL_CANDIDATE) and `arif_forge` (gated execution). VAULT999 owns the
actual receipt. This bus only fires AFTER VAULT999 has anchored the seal.

Hard rules (F13 SOVEREIGN, 2026-07-04):
  - The bus cannot apply patches.
  - The bus cannot change the tool surface.
  - The bus cannot change A-FORGE execution policy.
  - The bus cannot mark a SEAL.
  - The bus cannot bypass cooling.
  - The bus cannot remove human-ack for irreversible actions.

F13 SOVEREIGN: enabling the bus in production is HIGH-IMPACT. The bus is
no-op by default. Opt-in via ARIFOS_RSI_AUTOREBUILD=1 or explicit call to
`enable_post_seal_rebuild()`. F13 ratification gates the production flip.

YELLOW band: design-layer ship; not exercised by live SEAL events yet.
"""

from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable
from uuid import uuid4

logger = logging.getLogger("arifOS.rsi.event_bus")


# ── The 9 stages of the bounded RSI review loop (frozen 2026-07-04) ─────────
# Order is physics, not preference. Do not reorder.
# Inserted `skill_diff` between `skill_rebuild` and `organ_rebind` — under
# sovereign 999_HOLD: "the missing stage is Diff. Without Diff, the system
# cannot know whether it regenerated or mutated."
RSI_STAGES: tuple[str, ...] = (
    "seal",                # physics: irreversibility lock (review-only)
    "init_regeneration",   # biology: stem-cell reset (loads invariants; no mutation)
    "scaffold_rebuild",    # chemistry: reaction pathway rebuild (PROPOSES delta only)
    "skill_rebuild",       # RSI core: 12 skills re-derive contracts (PROPOSES only)
    "skill_diff",          # diff: compare old vs proposed; classify risk; emit GateDecision
    "organ_rebind",        # AAA + 6 organs rebind (routing-only; gated by GateDecision)
    "receipt_replay",      # restore scars, lineage, cooling ledger (read-only)
    "cooling",             # entropy sink (rate-limits mutation attempts)
    "resume_execution",    # A-FORGE gated resumption (blocked unless resume_allowed=True)
)


# ── Public trigger contract ─────────────────────────────────────────────────


@dataclass(frozen=True)
class SealEvent:
    """A single SEAL event payload, fanned out to every registered hook.

    seal_id       — VAULT999-anchored receipt id (must already exist when this fires).
    verdict_id    — the prior arif_judge SEAL_CANDIDATE verdict.
    actor         — identity binding from arif_init.
    session       — session_ref (the lifecycle we are regenerating).
    uncertainty   — Ω₀ band from the verdict (must be 0.03–0.05 per L07).
    scars         — non-empty list of unresolved scars if any (F9 carries these forward).
    floors_active — list of L-floors that fired.
    payload       — the original judgment payload (read-only).
    """

    seal_id: str
    verdict_id: str
    actor: str
    session: str
    uncertainty: tuple[float, float]
    scars: tuple[str, ...] = field(default_factory=tuple)
    floors_active: tuple[str, ...] = field(default_factory=tuple)
    payload: dict[str, Any] = field(default_factory=dict)


# Hook signature: takes a SealEvent, returns a StageResult. Hooks MUST be
# idempotent — the bus may retry on transient failure. Hooks MUST NOT raise.
PostSealHook = Callable[[SealEvent], "StageResult"]


@dataclass(frozen=True)
class StageResult:
    """Return value of a single hook. Failures are reported but never raised.

    `gate_decision` (optional) is the SkillDelta GateDecision when this hook
    was a diff stage. The bus uses this to gate downstream stages — the
    `resume_execution` stage refuses to fire if no APPROVE_C0_C3 with
    resume_allowed=True is in the receipt.
    """

    ok: bool
    stage: str
    hook_name: str
    elapsed_ms: float
    detail: str = ""
    scar: str | None = None  # if a failure is non-fatal, capture as scar
    gate_decision: Any = None  # Optional[GateDecision] — typed as Any to avoid runtime import cycle


# ── The registry ────────────────────────────────────────────────────────────


class SealEventBus:
    """Single-instance fan-out of SealEvent to ordered PostSealHook chains.

    Thread-safe. Hooks per stage run in registration order. Failures in one
    hook DO NOT block downstream hooks — they are captured as scars on the
    aggregated RSIReceipt.

    Default state: no-op. Call `enable_post_seal_rebuild()` or set
    ARIFOS_RSI_AUTOREBUILD=1 to opt in.
    """

    def __init__(self) -> None:
        self._enabled: bool = False
        self._lock = threading.RLock()
        self._chains: dict[str, list[tuple[str, PostSealHook]]] = {
            stage: [] for stage in RSI_STAGES
        }
        self._history_max = 64
        self._history: list["RSIReceipt"] = []

    # ── registration ────────────────────────────────────────────────────

    def register(self, stage: str, name: str, hook: PostSealHook) -> None:
        """Register a hook under a stage. Raises if stage is unknown.

        `name` is the human label for the hook (used in receipts).
        `hook` is a callable: SealEvent → StageResult.
        """
        if stage not in RSI_STAGES:
            raise ValueError(
                f"unknown stage {stage!r}; must be one of {RSI_STAGES}"
            )
        if not callable(hook):
            raise TypeError(f"hook for {stage}/{name} must be callable")
        with self._lock:
            self._chains[stage].append((name, hook))

    def chain(self, stage: str) -> list[tuple[str, PostSealHook]]:
        with self._lock:
            return list(self._chains[stage])

    # ── enable / disable ────────────────────────────────────────────────

    def enable_post_seal_rebuild(self) -> None:
        """Opt the bus in. Idempotent.

        F13 SOVEREIGN: flipping this in production is HIGH-IMPACT. The bus is
        no-op by default so a misconfigured install cannot accidentally rebuild
        skills on every seal cycle. Use this together with F13 ratification.
        """
        with self._lock:
            self._enabled = True
            logger.info(
                "RSI bus ENABLED — every SEAL event will trigger the "
                "8-stage regeneration chain"
            )

    def disable_post_seal_rebuild(self) -> None:
        with self._lock:
            self._enabled = False
            logger.warning("RSI bus DISABLED — SEAL events will no-op")

    @property
    def enabled(self) -> bool:
        return self._enabled

    # ── the trigger ─────────────────────────────────────────────────────

    def fire(self, event: SealEvent) -> "RSIReceipt":
        """Fan a SealEvent out through the 8-stage chain.

        Returns an RSIReceipt capturing per-stage results. Never raises — every
        exception is captured as a scar on the receipt.
        """
        with self._lock:
            if not self._enabled:
                logger.debug(
                    "RSI bus disabled — SEAL %s no-ops to receipt",
                    event.seal_id,
                )
                receipt = RSIReceipt(
                    seal_id=event.seal_id,
                    verdict_id=event.verdict_id,
                    session=event.session,
                    fired_at=0.0,
                    stage_results=(),
                    scars=(),
                    verdict="NOOP",
                )
                return receipt
            return self._fire_locked(event)

    def _fire_locked(self, event: SealEvent) -> "RSIReceipt":
        import time as _t
        results: list[StageResult] = []
        scars: list[str] = []
        t0 = _t.monotonic()
        # Gate state — populated as `skill_diff` hooks run.
        # `resume_execution` will be skipped unless at least one diff passed
        # with APPROVE_C0_C3 + resume_allowed=True. This is the engineered
        # protection against autonomous self-modifying loops.
        gate_open: bool = False
        for stage in RSI_STAGES:
            if stage == "resume_execution" and not gate_open:
                # Engine gate: do not fire resume hooks unless a diff passed.
                logger.warning(
                    "RSI bus: resume_execution stage SKIPPED — no diff opened "
                    "the gate (skill_diff chain did not emit an APPROVE_C0_C3 "
                    "with resume_allowed=True). seal=%s",
                    event.seal_id,
                )
                scars.append("resume_blocked_by_gate")
                continue
            hooks = self._chains[stage]
            if not hooks:
                # log only the first time per session
                logger.debug("stage %s: no hooks registered", stage)
                continue
            for name, hook in hooks:
                ts = _t.monotonic()
                try:
                    r = hook(event)
                    # ensure caller returned a StageResult we expect
                    if not isinstance(r, StageResult):
                        detail_msg = (
                            f"hook returned {type(r).__name__}, "
                            f"expected StageResult"
                        )
                        r = StageResult(
                            ok=False,
                            stage=stage,
                            hook_name=name,
                            elapsed_ms=(_t.monotonic() - ts) * 1000,
                            detail=detail_msg,
                            scar=(
                                f"{stage}/{name} returned "
                                f"{type(r).__name__}; expected StageResult"
                            ),
                        )
                except Exception as e:  # never raise from a hook
                    r = StageResult(
                        ok=False,
                        stage=stage,
                        hook_name=name,
                        elapsed_ms=(_t.monotonic() - ts) * 1000,
                        detail=f"exception: {type(e).__name__}: {e}",
                        scar=f"{stage}/{name} crashed: {e}",
                    )
                results.append(r)
                if not r.ok and r.scar:
                    scars.append(r.scar)
                # Promote gate if a diff hook approves.
                if stage == "skill_diff" and r.ok and r.gate_decision is not None:
                    gd = r.gate_decision
                    verdict = getattr(gd, "verdict", "")
                    resume_allowed = getattr(gd, "resume_allowed", False)
                    if verdict == "APPROVE_C0_C3" and resume_allowed:
                        gate_open = True
        elapsed_ms = (_t.monotonic() - t0) * 1000
        # Verdict policy (most severe wins):
        #   1. resume_blocked_by_gate present → SEAL_HOLD_GATE_NOT_OPENED.
        #      This is the engineered protection: no diff opened the gate.
        #   2. skill_diff fired but did NOT open gate → SEAL_HOLD_GATE_NOT_OPENED.
        #   3. all hooks ok → SEAL_REBUILT.
        #   4. some hooks ok → SEAL_PARTIAL.
        #   5. no hooks → NOOP.
        all_ok = all(r.ok for r in results) if results else True
        gate_blocked_scar = any(s == "resume_blocked_by_gate" for s in scars)
        diff_fired_not_opened = (
            any(r.stage == "skill_diff" for r in results)
            and not gate_open
        )
        if gate_blocked_scar or diff_fired_not_opened:
            verdict = "SEAL_HOLD_GATE_NOT_OPENED"
        elif all_ok and results:
            verdict = "SEAL_REBUILT"
        elif results:
            verdict = "SEAL_PARTIAL"
        else:
            verdict = "NOOP"
        receipt = RSIReceipt(
            seal_id=event.seal_id,
            verdict_id=event.verdict_id,
            session=event.session,
            fired_at=elapsed_ms,
            stage_results=tuple(results),
            scars=tuple(scars),
            verdict=verdict,
        )
        with self._lock:
            self._history.append(receipt)
            while len(self._history) > self._history_max:
                self._history.pop(0)
        if verdict == "SEAL_REBUILT":
            logger.info(
                "RSI cycle for seal=%s OK in %.1fms across %d hooks",
                event.seal_id, elapsed_ms, len(results),
            )
        else:
            logger.warning(
                "RSI cycle for seal=%s verdict=%s scars=%d elapsed=%.1fms",
                event.seal_id, verdict, len(scars), elapsed_ms,
            )
        return receipt

    # ── introspection ───────────────────────────────────────────────────

    def recent_receipts(self, limit: int = 8) -> list["RSIReceipt"]:
        with self._lock:
            return list(self._history[-limit:])


@dataclass(frozen=True)
class RSIReceipt:
    """Outcome of one SEAL-driven regeneration cycle."""

    seal_id: str
    verdict_id: str
    session: str
    fired_at: float  # ms
    stage_results: tuple[StageResult, ...]
    scars: tuple[str, ...]
    verdict: str  # "SEAL_REBUILT" | "SEAL_PARTIAL" | "NOOP"

    def stages_fired(self) -> list[str]:
        return sorted({r.stage for r in self.stage_results})

    def hook_count(self) -> int:
        return len(self.stage_results)


# ── Module singleton ────────────────────────────────────────────────────────


_BUS: SealEventBus | None = None


def get_bus() -> SealEventBus:
    """Return the single shared SealEventBus.

    Idempotent: same instance across imports. The bus is NO-OP until
    `enable_post_seal_rebuild()` is called or ARIFOS_RSI_AUTOREBUILD=1
    is set in the environment.
    """
    global _BUS
    if _BUS is None:
        with threading.Lock():
            if _BUS is None:
                _BUS = SealEventBus()
                if os.getenv("ARIFOS_RSI_AUTOREBUILD", "").lower() in (
                    "1", "true", "yes", "on"
                ):
                    _BUS.enable_post_seal_rebuild()
                    logger.info(
                        "RSI bus auto-enabled from ARIFOS_RSI_AUTOREBUILD=1"
                    )
    return _BUS


# ── Public facade ──────────────────────────────────────────────────────────


def register_post_seal_hook(stage: str, name: str, hook: PostSealHook) -> None:
    """Public facade — register a hook on the bus.

    Convenience wrapper around `SealEventBus.register` for callers that do not
    need to hold a bus reference. See the module docstring for stage names.
    """
    get_bus().register(stage, name, hook)


def fire_post_seal(event: SealEvent) -> RSIReceipt:
    """Public facade — fire a SealEvent through the bus."""
    return get_bus().fire(event)


def enable_post_seal_rebuild() -> None:
    """Public facade — enable the bus (F13-gated in production)."""
    get_bus().enable_post_seal_rebuild()


def disable_post_seal_rebuild() -> None:
    """Public facade — disable the bus."""
    get_bus().disable_post_seal_rebuild()


__all__ = [
    "RSI_STAGES",
    "RSIReceipt",
    "SealEvent",
    "SealEventBus",
    "StageResult",
    "disable_post_seal_rebuild",
    "enable_post_seal_rebuild",
    "fire_post_seal",
    "get_bus",
    "register_post_seal_hook",
]
