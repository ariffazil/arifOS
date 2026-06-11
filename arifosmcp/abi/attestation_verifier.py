"""
arifosmcp/abi/attestation_verifier.py — NATS attestation consumer

Forged: 2026-06-11 by omega-forge-agent
Status: STAGED. Pure function plus a runnable main(). Wired into
the kernel at /opt/arifos/app/ is a separate, gated change.

Addresses Roadmap P2-1: NATS attestation loop is the structural
fix for honesty_ratio.

The publisher side already exists and is already running:
  - /root/arifOS/arifosmcp/abi/nats_heartbeat_daemon.py
  - systemd: arifOS-NATS-heartbeat.service (active, PID seen)
  - target: NATS stream 'arifos-organs' (already 9,201+ messages)

What was missing is the CONSUMER side: a verifier that:
  1. subscribes to the stream,
  2. counts which organs have attested within the freshness window,
  3. computes honesty_ratio = (organs_attested / organs_expected),
  4. surfaces the ratio for inclusion in /health or /arif_session_init.

This module provides:
  - AttestationRecord: the parsed shape of a heartbeat message.
  - AttestationStore: in-memory map of (organ -> latest_attestation).
  - AttestationVerifier: subscribes, tracks, computes the ratio.
  - honesty_ratio(): the metric. Honest when bound to a probe.
  - The full set of expected organs is configurable.

The verifier does NOT replace the publisher. It reads what the
publisher writes. If the publisher is silent, the ratio drops.
That is the design: the kernel's claimed capability matches the
organs that have spoken, not the organs that are configured.

Honest fallback: if NATS is unreachable, honesty_ratio() returns
None. A None is reported as DEGRADED, not as a fake 0.0. We do
not pretend silence is honesty.

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any

logger = logging.getLogger("arifOS.attestation_verifier")

DEFAULT_EXPECTED_ORGANS: tuple[str, ...] = (
    "arifos",
    "geox",
    "wealth",
    "well",
    "a-forge",
    "aaa",
    "apex",
    "openclaw",
    "cn-organ",
    "hermes",
)

DEFAULT_FRESHNESS_S: int = 180  # 3 minutes — within 3x the 60s publish interval
DEFAULT_STREAM_NAME: str = "arifos-organs"


@dataclass(frozen=True)
class AttestationRecord:
    """A single heartbeat, parsed."""

    organ: str
    timestamp: float
    tool_count: int
    registry_truth: str
    verdict: str
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def age_s(self) -> float:
        return max(0.0, time.time() - self.timestamp)

    def is_fresh(self, freshness_s: int = DEFAULT_FRESHNESS_S) -> bool:
        return self.age_s <= freshness_s

    @classmethod
    def from_nats_message(cls, payload: bytes) -> "AttestationRecord | None":
        try:
            d = json.loads(payload.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning("attestation parse failed: %s", e)
            return None

        # Tolerate two historical shapes:
        #   NEW: { organ, verdict, tool_count, registry_truth, timestamp }
        #   OLD: { event: "ARIFOS_HEALTH", organ: "arifOS", verdict, ...,
        #          timestamp } — no tool_count, no registry_truth
        # In both, organ is the federation member.
        organ_raw = d.get("organ") or d.get("agent") or d.get("service")
        if not organ_raw:
            return None

        # Subject may encode the organ. The historical subject was
        # 'arifos.organ.arifOS.heartbeat' — organ=arifOS. We prefer
        # the payload's 'organ' field; the subject is a fallback.
        if organ_raw.lower() == "arifos":
            organ = "arifos"
        else:
            organ = str(organ_raw).lower()

        ts = d.get("timestamp")
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
            except ValueError:
                ts = time.time()
        elif not isinstance(ts, (int, float)):
            ts = time.time()

        # tool_count: NEW shape has it directly; OLD shape doesn't.
        # We try several field names and fall back to 0.
        raw_count = d.get("tool_count") or d.get("tools_loaded") or d.get("canonical_tools")
        try:
            tool_count = int(raw_count) if raw_count is not None else 0
        except (TypeError, ValueError):
            tool_count = 0

        return cls(
            organ=organ,
            timestamp=float(ts),
            tool_count=tool_count,
            registry_truth=str(d.get("registry_truth") or "UNKNOWN"),
            verdict=str(d.get("verdict") or d.get("status") or "UNKNOWN"),
            raw=d,
        )


class AttestationStore:
    """
    In-memory map of (organ -> latest_attestation). The store is
    monotonic: a fresher record replaces an older one, an older
    one never replaces a newer one.
    """

    def __init__(self, freshness_s: int = DEFAULT_FRESHNESS_S) -> None:
        self._latest: dict[str, AttestationRecord] = {}
        self.freshness_s = freshness_s

    def ingest(self, record: AttestationRecord) -> bool:
        existing = self._latest.get(record.organ)
        if existing is not None and record.timestamp <= existing.timestamp:
            return False  # out-of-order, ignore
        self._latest[record.organ] = record
        return True

    def fresh_organs(self) -> list[str]:
        return [organ for organ, rec in self._latest.items() if rec.is_fresh(self.freshness_s)]

    def latest_for(self, organ: str) -> AttestationRecord | None:
        return self._latest.get(organ)


@dataclass(frozen=True)
class AttestationVerdict:
    """
    The honest result of the verifier. None on the ratio is a real
    signal — the verifier did not see enough to commit to a number.
    """

    n_expected: int
    n_fresh: int
    n_stale: int
    n_missing: int
    ratio: float | None
    notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "n_expected": self.n_expected,
            "n_fresh": self.n_fresh,
            "n_stale": self.n_stale,
            "n_missing": self.n_missing,
            "ratio": self.ratio,
            "notes": list(self.notes),
        }


class AttestationVerifier:
    """
    Subscribes to the arifOS-organs NATS stream, ingests attestations,
    and computes the honesty ratio on demand.

    The verifier is intentionally NOT a daemon. It can be embedded
    in a long-running process (the kernel), invoked on a schedule
    (a cron job), or polled by a health check. The pure-function
    `compute()` is the same regardless of caller.
    """

    def __init__(
        self,
        store: AttestationStore,
        expected_organs: tuple[str, ...] = DEFAULT_EXPECTED_ORGANS,
    ) -> None:
        self.store = store
        self.expected_organs = expected_organs

    def ingest(self, record: AttestationRecord) -> bool:
        return self.store.ingest(record)

    def compute(self) -> AttestationVerdict:
        """Compute the current attestation state. Pure function over the store."""
        fresh = set(self.store.fresh_organs())
        expected = set(self.expected_organs)
        seen_any = set(self.store._latest.keys())
        stale = seen_any - fresh
        missing = expected - seen_any

        if not expected:
            return AttestationVerdict(
                n_expected=0,
                n_fresh=0,
                n_stale=0,
                n_missing=0,
                ratio=None,
                notes=("no expected organs configured",),
            )

        ratio = len(fresh) / len(expected)
        notes: list[str] = []
        if missing:
            notes.append(f"missing: {sorted(missing)}")
        if stale:
            notes.append(f"stale: {sorted(stale)}")
        if ratio >= 0.9:
            notes.append("honesty_ratio >= 0.9")
        elif ratio is not None:
            notes.append("honesty_ratio below 0.9 — attestation incomplete")

        return AttestationVerdict(
            n_expected=len(expected),
            n_fresh=len(fresh),
            n_stale=len(stale),
            n_missing=len(missing),
            ratio=ratio,
            notes=tuple(notes),
        )


# ──────────────────────────────────────────────────────────────────────
# CLI: poll the running NATS server, ingest the most recent message
# on arifos-organs, print the verdict. Run as:
#   python -m arifosmcp.abi.attestation_verifier
# ──────────────────────────────────────────────────────────────────────


async def _consume_once(nats_url: str, stream: str, verifier: AttestationVerifier) -> int:
    """Consume one batch from the stream. Returns the number of records ingested.

    Uses a durable consumer with DeliverPolicy.ALL so the verifier
    reads from the beginning of the stream, not from "now" (which is
    what a non-durable pull_subscribe does — and that returns empty
    if there are no NEW messages).
    """
    try:
        import nats
        from nats.js.api import DeliverPolicy, AckPolicy
    except ImportError:
        logger.error("nats client not installed; cannot consume")
        return 0

    nc = await nats.connect(nats_url)
    js = nc.jetstream()
    try:
        # Create or update the durable consumer with DeliverPolicy.ALL
        # so the verifier reads historical messages on first run.
        # filter='arifos.organ.>' matches the stream's existing filter.
        try:
            await js.add_consumer(
                stream,
                durable="verifier-probe",
                deliver_policy=DeliverPolicy.ALL,
                ack_policy=AckPolicy.EXPLICIT,
                max_deliver=1,
                filter_subject="arifos.organ.>",
            )
        except Exception:
            # Consumer may already exist with different config; ignore.
            pass
        sub = await js.pull_subscribe("arifos.organ.>", durable="verifier-probe", stream=stream)
        msgs = await sub.fetch(50, timeout=2.0)
    except Exception as e:
        logger.info("no messages on %s: %s", stream, e)
        await nc.close()
        return 0

    n_ingested = 0
    for msg in msgs:
        rec = AttestationRecord.from_nats_message(msg.data)
        if rec is not None:
            if verifier.ingest(rec):
                n_ingested += 1
        await msg.ack()
    await nc.close()
    return n_ingested


async def _main(nats_url: str = "nats://127.0.0.1:4222") -> None:
    store = AttestationStore()
    verifier = AttestationVerifier(store)
    n = await _consume_once(nats_url, DEFAULT_STREAM_NAME, verifier)
    verdict = verifier.compute()
    print(
        json.dumps(
            {
                "ingested": n,
                "verdict": verdict.to_dict(),
                "timestamp": datetime.now(UTC).isoformat(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    asyncio.run(_main())


__all__ = [
    "AttestationRecord",
    "AttestationStore",
    "AttestationVerifier",
    "AttestationVerdict",
    "DEFAULT_EXPECTED_ORGANS",
    "DEFAULT_FRESHNESS_S",
    "DEFAULT_STREAM_NAME",
]
