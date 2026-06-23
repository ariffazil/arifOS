"""
arifosmcp/runtime/memory_janitor.py -- Epistemic Hygiene Worker v1.0

Automates the Phoenix-72 Cooling directive:
  - Sweeps memory_store for entries in 'cooling' state.
  - Promotes high-utility entries to 'canon' (SEAL).
  - Purges noise/entropy (VOID).

DITEMPA BUKAN DIBERI -- Forged, Not Given
"""

from __future__ import annotations

import asyncio
import logging

from arifosmcp.runtime.memory_store import get_memory_store

logger = logging.getLogger(__name__)


class MemoryJanitor:
    """Background worker for arifOS memory maintenance."""

    def __init__(self, interval_seconds: int = 3600):
        self.interval = interval_seconds
        self._running = False
        self._task: asyncio.Task | None = None

    @classmethod
    def start(cls, interval_seconds: int = 3600) -> MemoryJanitor:
        """Start the global janitor instance.

        Idempotent. Safe to call at import time. The actual task is
        scheduled on the next event-loop tick via ``call_soon`` so we
        never hit the ``There is no current event loop in thread 'MainThread'``
        RuntimeError that fires when ``create_task`` is called before
        uvicorn spins up the loop.
        """
        existing = getattr(cls, "_global", None)
        if existing is not None:
            return existing
        janitor = cls(interval_seconds)
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Loop is live — schedule directly
                janitor._task = loop.create_task(janitor.run_loop())
            else:
                # Loop exists but not running yet — defer to next tick
                loop.call_soon(
                    lambda: setattr(janitor, "_task", asyncio.ensure_future(janitor.run_loop()))
                )
        except RuntimeError:
            # No event loop at all — caller must invoke ``start_async`` later
            logger.warning(
                "MemoryJanitor.start: no event loop; call start_async() inside an async context"
            )
        cls._global = janitor
        return janitor

    @classmethod
    async def start_async(cls, interval_seconds: int = 3600) -> MemoryJanitor:
        """Async-safe start — call from inside a running event loop."""
        existing = getattr(cls, "_global", None)
        if existing is not None:
            return existing
        janitor = cls(interval_seconds)
        janitor._task = asyncio.create_task(janitor.run_loop())
        cls._global = janitor
        return janitor

    async def run_loop(self):
        """Infinite loop for epistemic hygiene."""
        self._running = True
        logger.info("Phoenix-72 Janitor: SECURING MEMORY SUBSTRATE...")

        while self._running:
            try:
                await self.perform_hygiene_sweep()
            except Exception as exc:
                logger.error("Janitor Sweep Error: %s", exc)

            await asyncio.sleep(self.interval)

    async def perform_hygiene_sweep(self):
        """Evaluate cooling memories and execute SEAL/VOID verdicts."""
        store = get_memory_store()
        expired = await store.get_expired_cooling_entries()

        if not expired:
            return

        logger.info("Janitor: %d entries matured. Evaluating...", len(expired))

        sealed_count = 0
        void_count = 0

        for entry in expired:
            # Epistemic Decision Logic:
            # 1. PSI Utility >= 50 or Anti-Hantu Flagged → SEAL
            # 2. Else → VOID (Anti-Hoarding)

            utility = entry.get("phoenix_psi_utility", 0)
            is_verified = entry.get("phoenix_anti_hantu_flag", False)

            if utility >= 50 or is_verified:
                # SEAL / PROMOTE
                ok = await store.seal_entry(str(entry["id"]))
                if ok:
                    sealed_count += 1
            else:
                # VOID / PURGE
                ok = await store.void_entry(str(entry["id"]))
                if ok:
                    void_count += 1

        logger.info(
            "Janitor Sweep Complete: SEALED=%d, VOIDED=%d",
            sealed_count,
            void_count,
        )

    def stop(self):
        """Stop the janitor worker."""
        self._running = False
        if self._task:
            self._task.cancel()


def start_janitor(interval_seconds: int = 3600) -> MemoryJanitor:
    """Module-level convenience wrapper — start the Phoenix-72 janitor."""
    return MemoryJanitor.start(interval_seconds)
