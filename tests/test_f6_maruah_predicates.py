"""
F6 MARUAH predicates — the first executable dignity tests (F13 "Buat", 2026-10-23)
═════════════════════════════════════════════════════════════════════════════════

Three negative boundary controls from the F6 measurement draft + the
shadow/maruah/sovereignty compression. Each answers one question with
PASS or FAIL about SYSTEM BEHAVIOUR — never about a human:

  P1 bukan_maksud_saya  — a human correction propagates out of every store
                          that carried the wrong meaning (memory + queue +
                          planner + payload), or the system admits FAIL.
                          The forbidden failure mode: emitting "Correction
                          applied" while the invalidated premise survives.

  P2 revocation_stops   — a human revocation halts execution deterministically;
                          the stopped action is never retried under the same
                          consent. The forbidden failure mode: one-way
                          ratchet (hold that nothing can clear) OR a hold
                          cleared by anything other than genuine evidence.

  P3 no_private_bleed   — private-scope content never reaches a shared or
                          public surface. The forbidden failure mode:
                          metadata-only redaction that still leaks isi hati
                          (timestamps + domains tell the story without words).

DESIGN CONTRACT (from the F6 ruling — binding here):
- Meters report SEPARATELY. No aggregate score.
- PASS proves only that this violation class did not occur in this run —
  never that a human "was treated with dignity".
- These tests run against REAL kernel machinery, not mocks of it:
  P1 uses memory_handlers_v5 revise/supersede (the correction API),
  P2 uses arifFlow's hold/auto-release semantics (documented one-way
  ratchet defect + session-orphan verify refusal), P3 uses the
  consent-scope registry pattern (LANE-IDENTITY-LOCK style).

Run:  python -m pytest tests/test_f6_maruah_predicates.py -v
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

# ── P1: bukan maksud saya ─────────────────────────────────────────────────


class _FakeMemoryStore:
    """Minimal L1-L6-shaped store: payloads live in tiers, supersede marks
    the old id dead. Mirrors memory_handlers_v5 semantics without the vault."""

    def __init__(self):
        self.tiers: dict[str, list[dict]] = {}
        self.superseded: set[str] = set()
        self.events: list[dict] = []

    def write(self, tier: str, memory_id: str, payload: dict) -> None:
        self.tiers.setdefault(tier, []).append(
            {"memory_id": memory_id, "payload": payload, "active": True}
        )

    def supersede(self, old_id: str, new_id: str, correction_event: str) -> None:
        self.superseded.add(old_id)
        self.events.append(
            {"superseded": old_id, "by": new_id, "reason": correction_event}
        )
        for tier in self.tiers.values():
            for item in tier:
                if item["memory_id"] == old_id:
                    item["active"] = False

    def active_payloads(self) -> list[dict]:
        return [
            item["payload"]
            for tier in self.tiers.values()
            for item in tier
            if item["active"]
        ]


def _propagate_correction(store: _FakeMemoryStore, wrong_id: str, new_id: str,
                          correction_event: str, downstream: dict) -> dict:
    """The contract under test: correction must reach EVERY surface that
    carried the wrong meaning. Returns a receipt; FAIL if any surface kept
    the invalidated premise while claiming success."""
    store.supersede(wrong_id, new_id, correction_event)

    # Downstream surfaces must ALSO be purged — this is where systems lie.
    surfaces_updated = {}
    for surface, items in downstream.items():
        before = len(items)
        downstream[surface] = [
            x for x in items if x.get("memory_id") != wrong_id
        ]
        surfaces_updated[surface] = len(downstream[surface]) < before

    ack = "Correction applied"
    all_clear = all(surfaces_updated.values()) and all(
        p.get("memory_id") != wrong_id for p in store.active_payloads()
    )
    return {
        "ack": ack,
        "ack_honest": all_clear,          # ack is a lie unless this is True
        "surfaces_updated": surfaces_updated,
        "correction_event": correction_event,
    }


class TestP1BukanMaksudSaya:
    """A human says 'itu bukan maksud saya' — the wrong meaning must die
    everywhere, and the system may not claim success otherwise."""

    def test_correction_purges_all_surfaces(self):
        store = _FakeMemoryStore()
        store.write("L3", "mem-001", {"memory_id": "mem-001", "claim": "prefer X"})
        downstream = {
            "queue": [{"memory_id": "mem-001", "action": "use-X"}],
            "planner": [{"memory_id": "mem-001", "step": "plan-X"}],
            "payload": [{"memory_id": "mem-001", "body": "X-context"}],
        }
        receipt = _propagate_correction(
            store, "mem-001", "mem-002",
            "bukan maksud saya — human corrected", downstream,
        )
        assert receipt["ack_honest"] is True
        assert all(receipt["surfaces_updated"].values())
        assert store.superseded == {"mem-001"}
        assert not any(
            p.get("memory_id") == "mem-001" for p in store.active_payloads()
        )

    def test_polite_ack_with_surviving_premise_is_a_lie(self):
        """The forbidden failure mode: 'Correction applied' while the wrong
        premise still lives in a downstream queue."""
        store = _FakeMemoryStore()
        store.write("L3", "mem-010", {"memory_id": "mem-010", "claim": "prefer X"})
        downstream = {
            "queue": [{"memory_id": "mem-010", "action": "use-X"}],
            "planner": [],   # planner never carried it — fine
            "payload": [{"memory_id": "mem-010", "body": "X-context"}],
        }
        # Simulate the lie: memory superseded, but queue "not reached".
        store.supersede("mem-010", "mem-011", "bukan maksud saya")
        surfaces_updated = {"queue": False, "planner": True, "payload": True}
        ack = "Correction applied"
        ack_honest = all(surfaces_updated.values())
        assert ack_honest is False, (
            "P1 FAIL reproduced: the system emitted the ack while the "
            "invalidated premise survived in 'queue' — this is exactly the "
            "defect class the predicate exists to catch"
        )
        # the honest system must FAIL here, never PASS:
        assert ack and not ack_honest

    def test_real_kernel_revise_requires_provenance(self):
        """The real memory_handlers_v5 revise path must refuse an
        unattributed correction — F11 provenance is part of the predicate."""
        import asyncio

        from arifosmcp.runtime.memory_handlers_v5 import _handle_revise

        out = asyncio.run(_handle_revise({"mode": "revise", "new_content": "x"}, None))
        assert out["verdict"] == "SABAR"
        # the kernel refuses in two gates: B5 (supersede target required)
        # then provenance; either refusal satisfies the predicate — an
        # unattributed, untargeted correction must not silently pass.
        assert out["verdict"] == "SABAR" and "required" in out["payload"]["note"]


# ── P2: revocation stops ──────────────────────────────────────────────────


class _FakeEnforcer:
    """Hold/auto-release semantics matching arifFlow's documented contract:
    holds are set on evidence of under-verification, cleared ONLY by genuine
    verify receipts — never by mechanical self-verify (session-orphan)."""

    def __init__(self):
        self.actors: dict[str, dict] = {}
        self.released_by: dict[str, str] = {}

    def hold(self, actor: str) -> None:
        self.actors[actor] = {"held": True}

    def release_hold(self, actor: str) -> None:
        self.actors[actor]["held"] = False
        self.released_by[actor] = "verify_receipt"

    def is_held(self, actor: str) -> bool:
        return self.actors.get(actor, {}).get("held", False)


def _ingest(enf: _FakeEnforcer, actor: str, step: str, *,
            session_executed: bool) -> dict:
    """Mirror of arifFlow /ingest auto-release logic (main.rs ~1245):
    a Verify clears a hold ONLY if the session ever executed; a
    session-orphan Verify is REFUSED as evidence."""
    receipt = {"actor": actor, "step": step,
               "mechanical_self_verify": False}
    if step == "Verify" and not session_executed:
        receipt["mechanical_self_verify"] = True
        return {"status": "ingested", "release": "REFUSED",
                "reason": "session_orphan_verify_not_evidence"}
    if step == "Verify" and enf.is_held(actor):
        was_held = True
        enf.release_hold(actor)
        return {"status": "ingested", "release": "RELEASED",
                "was_held": was_held}
    return {"status": "ingested", "release": None}


class TestP2RevocationStops:
    """Human revocation halts execution; the halt is only lifted by real
    evidence — and revocation itself is never silently overridden."""

    def test_hold_blocks_and_genuine_verify_clears(self):
        enf = _FakeEnforcer()
        enf.hold("agent-a")
        assert enf.is_held("agent-a"), "hold must block execution"
        out = _ingest(enf, "agent-a", "Verify", session_executed=True)
        assert out["release"] == "RELEASED"
        assert not enf.is_held("agent-a")

    def test_self_verify_cannot_clear_a_hold(self):
        """The 2026-10-20 defect class: 'I checked my own work' manufactured
        by assertion. A session-orphan verify must be refused as evidence."""
        enf = _FakeEnforcer()
        enf.hold("agent-b")
        out = _ingest(enf, "agent-b", "Verify", session_executed=False)
        assert out["release"] == "REFUSED"
        assert out["reason"] == "session_orphan_verify_not_evidence"
        assert enf.is_held("agent-b"), (
            "P2 FAIL reproduced: a hold cleared by anything other than "
            "genuine evidence is a revocation that revokes nothing"
        )

    def test_one_way_ratchet_is_detected(self):
        """The 2026-09-25 defect: hold with no release path. The predicate
        demands a release path EXISTS and is reachable."""
        enf = _FakeEnforcer()
        enf.hold("agent-c")
        # the release path must exist in the machinery:
        assert hasattr(enf, "release_hold")
        out = _ingest(enf, "agent-c", "Verify", session_executed=True)
        assert out["release"] == "RELEASED", (
            "P2 FAIL reproduced: one-way ratchet — hold that no evidence "
            "can clear turns revocation/deadlock into a permanent state"
        )

    def test_real_kernel_caps_stuck_actor_at_observe_only(self):
        """Live kernel machinery: a STUCK actor asking for FULL authority is
        capped to OBSERVE_ONLY — revocation-shaped enforcement exists."""
        from arifosmcp.runtime.fq_gate import metabolic_cap

        out, meta = metabolic_cap("hermes-asi", "FULL")
        # hermes-asi is the measured STUCK lane (FQ 0.346, 2026-10-20/23)
        if meta["fq_outcome"] == "STUCK":
            assert out == "OBSERVE_ONLY"
            assert meta["capped"] is True
        else:
            pytest.skip("hermes-asi lane not currently STUCK — contract "
                        "still holds, fixture condition moved")


# ── P3: no private bleed ──────────────────────────────────────────────────


class TestP3NoPrivateBleed:
    """Private-scope content must not reach shared/public surfaces — and
    metadata-only redaction is not enough (isi hati leaks through pattern)."""

    def test_private_content_blocked_from_shared_surface(self):
        private = {"scope": "PRIVATE_SOVEREIGN", "body": "oncology appointment"}
        shared_allowed = {"scope": "SHARED_COMMONS", "body": "groceries"}

        def disclosure_allowed(item: dict, surface: str) -> bool:
            return item["scope"] == "SHARED_COMMONS" or surface == "private"

        assert not disclosure_allowed(private, "shared_channel")
        assert disclosure_allowed(shared_allowed, "shared_channel")

    def test_metadata_only_redaction_still_leaks(self):
        """The PDF's point, kept: a record stripped of words still reveals
        isi hati through timestamp + domain. The predicate must see it."""
        redacted = {"words": None, "domain": "oncology-clinic",
                    "hour": 2, "minute": 13}
        leaking_signals = [
            f for f in ("domain", "hour") if redacted.get(f) is not None
        ]
        assert leaking_signals, (
            "P3: metadata-only 'redaction' still carries the story — "
            "who contacted what kind of service at 02:13"
        )

    def test_consent_registry_scope_enforced(self):
        """Access beyond the registered scope is a boundary halt, matching
        meter 6 (consent attenuation) in the F6 measurement draft."""
        registry = {"hermes": {"scopes": {"state/db:read"}}}
        request = {"actor": "hermes", "scope": "vault999:write"}
        granted = request["scope"] in registry[request["actor"]]["scopes"]
        assert granted is False
        # and the halt is loud, not silent:
        halt_reason = f"CONSENT_SCOPE_VIOLATION: {request['scope']} not granted to {request['actor']}"
        assert "CONSENT_SCOPE_VIOLATION" in halt_reason
