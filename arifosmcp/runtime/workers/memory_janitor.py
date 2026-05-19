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
        """Start the global janitor instance."""
        janitor = cls(interval_seconds)
        # Use get_event_loop().create_task() instead of asyncio.create_task()
        # so the janitor can be instantiated at import time before uvicorn
        # has started the event loop. The task is scheduled and will begin
        # executing once the loop starts.
        loop = asyncio.get_event_loop()
        janitor._task = loop.create_task(janitor.run_loop())
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
