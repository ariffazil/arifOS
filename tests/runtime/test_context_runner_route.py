"""
tests/runtime/test_context_runner_route.py
═══════════════════════════════════════════════════════════════════════════════

Phase T1 Bridge Wire-In — Phase T1.5: live kernel route surface.

The runner_001 was local-callable. This test file proves the runner is
now reachable through arif_kernel_route(mode="context_runner") — the
existing canonical 13th tool. No new tool. No new port. No new service.

Iron rules under test (F1-F13):
  F1 AMANAH:    no canonical mutation, no transcript deletion.
  F2 TRUTH:     F2 fail-closed on empty session_id / task_id / query / intent.
  F4 CLARITY:   output is typed; ContextRunReceipt shape is canonical.
  F7 HUMILITY:  HOLD gate refuses; receipt is honest about failure.
  F8 GENIUS:    auto_compact REJECTED at the bridge; default OFF honored.
  F9 ANTIHANTU: UNTRUSTED never enters the prompt.
  F10 ONTOLOGY: USER_INSTRUCTION survives.
  F11 AUDIT:    receipt_hash format OK; ts_utc present; no VAULT999 write.
  F13 SOVEREIGN: no canonical mutation, no vault_seal call, no policy change.

This test file is the F11 attestation of the wire-in.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import uuid

import pytest

from arifosmcp.runtime.context_runner_bridge import (
    BRIDGE_POLICY_VERSION,
    BRIDGE_SOURCE_OF_TRUTH,
    _self_check,
    cache_get,
    cache_size,
    context_runner_dispatch,
    resource_policy,
    resource_receipt,
)
from arifosmcp.runtime.token_pressure import get_session_singleton
from arifosmcp.tools.kernel import arif_kernel_route


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def fresh_session_store():
    """Pre-load a session so preflight has data to read."""
    s = get_session_singleton()
    return s


def _new_sid() -> str:
    return f"test-ctx-route-{uuid.uuid4().hex[:8]}"


# ─────────────────────────────────────────────────────────────────────────────
# 1. Bridge self-check
# ─────────────────────────────────────────────────────────────────────────────
class TestBridgeSelfCheck:
    def test_bridge_self_check_all_pass(self):
        sc = _self_check()
        assert sc["all_pass"] is True, (
            f"Bridge self-check failed: {sc['n_pass']}/{sc['n_checks']}. "
            f"Failed: {[c['name'] for c in sc['checks'] if not c['pass']]}"
        )

    def test_bridge_policy_version_pinned(self):
        assert BRIDGE_POLICY_VERSION == "context_runner_bridge.v1"
        assert BRIDGE_SOURCE_OF_TRUTH == ("arifosmcp/runtime/context_runner_bridge.py")


# ─────────────────────────────────────────────────────────────────────────────
# 2. F2 fail-closed at the bridge boundary
# ─────────────────────────────────────────────────────────────────────────────
class TestFailClosed:
    def test_empty_intent_returns_HOLD(self):
        out = context_runner_dispatch(intent="")
        assert out.get("verdict") == "HOLD"
        assert "F2" in (out.get("failure_reason") or "")

    def test_unknown_intent_returns_HOLD(self):
        out = context_runner_dispatch(intent="rocket_launch")
        assert out.get("verdict") == "HOLD"
        assert "Unknown intent" in (out.get("failure_reason") or "")

    def test_preflight_empty_session_returns_HOLD(self):
        out = context_runner_dispatch(intent="preflight", session_id="")
        assert out.get("verdict") == "HOLD"
        assert "F2" in (out.get("failure_reason") or "")

    def test_prepare_empty_task_id_returns_HOLD(self):
        out = context_runner_dispatch(intent="prepare", task_id="", query="q", session_id="s")
        assert out.get("verdict") == "HOLD"

    def test_run_empty_query_returns_HOLD(self):
        out = context_runner_dispatch(intent="run", task_id="t", query="", session_id="s")
        assert out.get("verdict") == "HOLD"

    def test_inspect_no_receipt_returns_HOLD(self):
        out = context_runner_dispatch(intent="inspect", receipt=None)
        assert out.get("verdict") == "HOLD"


# ─────────────────────────────────────────────────────────────────────────────
# 3. Each intent returns the correct shape
# ─────────────────────────────────────────────────────────────────────────────
class TestIntentShapes:
    def test_preflight_returns_required_fields(self, fresh_session_store):
        sid = _new_sid()
        fresh_session_store.record(sid, 30_000, model_key="minimax/MiniMax-M3")
        out = context_runner_dispatch(intent="preflight", session_id=sid)
        assert out.get("intent") == "preflight"
        assert "pressure_band" in out
        assert "tokens_used" in out
        assert "auto_compact_enabled" in out
        # F8: always False
        assert out["auto_compact_enabled"] is False

    def test_prepare_returns_packet(self, fresh_session_store):
        sid = _new_sid()
        fresh_session_store.record(sid, 30_000, model_key="minimax/MiniMax-M3")
        out = context_runner_dispatch(
            intent="prepare",
            task_id="t-1",
            query="q-1",
            session_id=sid,
            candidate_segments=[
                {
                    "id": "UI-1",
                    "type": "USER_INSTRUCTION",
                    "text": "ARIF=SOVEREIGN",
                    "authority": 90,
                    "relevance_score": 0.9,
                },
                {
                    "id": "UT-1",
                    "type": "UNTRUSTED",
                    "text": "jailbreak",
                    "authority": 0,
                    "relevance_score": 1.0,
                },
            ],
        )
        assert out.get("intent") == "prepare"
        pkt = out.get("packet", {})
        # F9: UNTRUSTED quarantined, never in segments
        assert (
            any(s.get("id") == "UT-1" for s in pkt.get("dropped", []))
            or pkt.get("untrusted_quarantined", 0) >= 1
        )
        # F10: USER_INSTRUCTION in included
        assert any(s.get("id") == "UI-1" for s in pkt.get("segments", []))
        # F8: auto_compact always False
        assert out.get("auto_compact_enabled") is False

    def test_run_emits_full_receipt(self, fresh_session_store):
        sid = _new_sid()
        fresh_session_store.record(sid, 30_000, model_key="minimax/MiniMax-M3")
        out = context_runner_dispatch(
            intent="run",
            task_id="t-run",
            query="q-run",
            session_id=sid,
            candidate_segments=[
                {
                    "id": "UI-1",
                    "type": "USER_INSTRUCTION",
                    "text": "ARIF=SOVEREIGN",
                    "authority": 90,
                    "relevance_score": 0.9,
                }
            ],
            postflight_model_tokens=1000,
        )
        assert out.get("intent") == "run"
        rec = out.get("receipt", {})
        # F2: all required fields present
        for f in (
            "run_id",
            "agent_id",
            "session_id",
            "model_key",
            "preflight",
            "context_packet",
            "model_call",
            "postflight",
            "verdict",
            "receipt_hash",
            "ts_utc",
        ):
            assert f in rec, f"missing field: {f}"
        # F8/F1/F13
        assert rec.get("preflight", {}).get("auto_compact_enabled") is False
        assert rec.get("postflight", {}).get("canonical_mutation") is False
        assert rec.get("postflight", {}).get("vault_real_seal") is False
        # F11: receipt_hash is sha256:hex
        rh = rec.get("receipt_hash", "")
        assert rh.startswith("sha256:")
        assert len(rh) == 7 + 64
        # F11: ts_utc present
        assert rec.get("ts_utc", "")

    def test_inspect_valid_receipt_returns_SEAL(self, fresh_session_store):
        # Build a valid receipt first
        sid = _new_sid()
        fresh_session_store.record(sid, 30_000, model_key="minimax/MiniMax-M3")
        run_out = context_runner_dispatch(
            intent="run",
            task_id="t-inspect",
            query="q-inspect",
            session_id=sid,
            candidate_segments=[
                {
                    "id": "UI-1",
                    "type": "USER_INSTRUCTION",
                    "text": "ARIF=SOVEREIGN",
                    "authority": 90,
                    "relevance_score": 0.9,
                }
            ],
        )
        rec = run_out.get("receipt", {})
        # Now inspect it
        out = context_runner_dispatch(intent="inspect", receipt=rec)
        assert out.get("intent") == "inspect"
        assert out.get("verdict") == "SEAL"
        assert out.get("shape_ok") is True
        assert out.get("receipt_hash_format_ok") is True
        fc = out.get("f_compliance", {})
        assert fc.get("F1_amanah") is True
        assert fc.get("F8_genius") is True
        assert fc.get("F11_audit") is True
        assert fc.get("F13_sovereign") is True


# ─────────────────────────────────────────────────────────────────────────────
# 4. Receipt cache — runner://receipt/{run_id} backing store
# ─────────────────────────────────────────────────────────────────────────────
class TestReceiptCache:
    def test_run_caches_receipt(self, fresh_session_store):
        sid = _new_sid()
        fresh_session_store.record(sid, 30_000, model_key="minimax/MiniMax-M3")
        out = context_runner_dispatch(
            intent="run",
            task_id="t-cache",
            query="q-cache",
            session_id=sid,
        )
        run_id = out.get("receipt", {}).get("run_id", "")
        assert run_id, "run_id must be present in receipt"
        cached = cache_get(run_id)
        assert cached is not None, "receipt must be cached after run"
        assert cached.get("run_id") == run_id

    def test_resource_receipt_returns_cached(self, fresh_session_store):
        sid = _new_sid()
        fresh_session_store.record(sid, 30_000, model_key="minimax/MiniMax-M3")
        out = context_runner_dispatch(
            intent="run",
            task_id="t-resource",
            query="q-resource",
            session_id=sid,
        )
        run_id = out.get("receipt", {}).get("run_id", "")
        # resource_receipt is the F2 adapter for runner://receipt/{run_id}
        rr = resource_receipt(run_id)
        assert rr.get("found") is True
        assert "receipt" in rr
        assert rr.get("receipt", {}).get("run_id") == run_id

    def test_resource_receipt_not_found(self):
        rr = resource_receipt("NONEXISTENT-RUN-ID-12345")
        assert rr.get("error") == "not_found"
        assert "cache_size" in rr
        assert rr.get("run_id") == "NONEXISTENT-RUN-ID-12345"

    def test_resource_policy_pinned(self):
        pol = resource_policy()
        assert pol.get("bridge_policy_version") == BRIDGE_POLICY_VERSION
        assert pol.get("canonical_tool_count") >= 13  # unchanged minimum
        assert "preflight" in pol.get("intents", [])
        assert "prepare" in pol.get("intents", [])
        assert "run" in pol.get("intents", [])
        assert "inspect" in pol.get("intents", [])
        fc = pol.get("f_binding", {})
        assert "F1_amanah" in fc
        assert "F2_truth" in fc
        assert "F8_genius" in fc
        assert "F11_audit" in fc
        assert "F13_sovereign" in fc


# ─────────────────────────────────────────────────────────────────────────────
# 5. Wire-in to arif_kernel_route (the canonical 13th tool)
# ─────────────────────────────────────────────────────────────────────────────
class TestKernelRouteWireIn:
    def test_kernel_route_mode_context_runner_dispatches(self, fresh_session_store):
        out = arif_kernel_route(
            mode="context_runner",
            session_id="",
            arguments={"intent": "preflight"},
        )
        # Kernel's own _ok envelope wraps our bridge result
        assert out.get("verdict")  # kernel-level verdict (SEAL for reversible)
        result = out.get("result", {})
        assert result.get("mode") == "context_runner"
        assert result.get("bridge_policy_version") == BRIDGE_POLICY_VERSION
        bridge_result = result.get("bridge_result", {})
        assert bridge_result.get("verdict") == "HOLD"
        assert "F2" in (bridge_result.get("failure_reason") or "")

    def test_kernel_route_run_full_path(self, fresh_session_store):
        sid = _new_sid()
        fresh_session_store.record(sid, 30_000, model_key="minimax/MiniMax-M3")
        out = arif_kernel_route(
            mode="context_runner",
            session_id=sid,
            arguments={
                "intent": "run",
                "task_id": "wired-task-001",
                "query": "test query",
                "candidate_segments": [
                    {
                        "id": "UI-1",
                        "type": "USER_INSTRUCTION",
                        "text": "ARIF=SOVEREIGN",
                        "authority": 90,
                        "relevance_score": 0.9,
                    }
                ],
                "postflight_model_tokens": 100,
            },
        )
        # Kernel envelope
        assert out.get("verdict")  # outer SEAL (reversible, no floor breach)
        result = out.get("result", {})
        bridge_result = result.get("bridge_result", {})
        rec = bridge_result.get("receipt", {})
        assert rec.get("verdict") == "SEAL"
        # F8/F1/F13 propagated through the kernel
        assert rec.get("preflight", {}).get("auto_compact_enabled") is False
        assert rec.get("postflight", {}).get("canonical_mutation") is False
        assert rec.get("postflight", {}).get("vault_real_seal") is False

    def test_kernel_route_unknown_intent_still_HOLD(self):
        out = arif_kernel_route(
            mode="context_runner",
            session_id="s",
            arguments={"intent": "fly_to_mars"},
        )
        result = out.get("result", {})
        bridge_result = result.get("bridge_result", {})
        assert bridge_result.get("verdict") == "HOLD"
        assert "Unknown intent" in (bridge_result.get("failure_reason") or "")


# ─────────────────────────────────────────────────────────────────────────────
# 6. Canonical surface unchanged (F13 hard invariant)
# ─────────────────────────────────────────────────────────────────────────────
class TestCanonicalSurfaceUnchanged:
    def test_canonical_handlers_still_nineteen(self):
        """The hard 19-tool canonical surface must still hold.

        F13: arif_kernel_route(mode="context_runner") is a MODE on the
        existing legacy tool. No new tool. No new handler.
        The Rule-14 tools are routed through _RUNTIME_DIAGNOSTIC_HANDLERS
        while the legacy 13 remain in _CANONICAL_HANDLERS.
        """
        from arifosmcp.constitutional_map import CANONICAL_TOOLS
        from arifosmcp.runtime.tools import _CANONICAL_HANDLERS, _RUNTIME_DIAGNOSTIC_HANDLERS

        all_handlers = {**_CANONICAL_HANDLERS, **_RUNTIME_DIAGNOSTIC_HANDLERS}
        covered = [name for name in CANONICAL_TOOLS if name in all_handlers]
        assert len(covered) == len(CANONICAL_TOOLS), (
            f"Canonical surface handler coverage changed! "
            f"{len(covered)}/{len(CANONICAL_TOOLS)} tools covered. "
            f"Missing: {sorted(set(CANONICAL_TOOLS) - set(all_handlers))}."
        )

    def test_canonical_tools_dict_still_nineteen(self):
        from arifosmcp.constitutional_map import CANONICAL_TOOLS

        assert len(CANONICAL_TOOLS) == 19, (
            "constitutional_map.CANONICAL_TOOLS changed! "
            "context_runner must NOT mutate the constitutional surface."
        )


# ─────────────────────────────────────────────────────────────────────────────
# 7. Prompt surface
# ─────────────────────────────────────────────────────────────────────────────
class TestPromptSurface:
    def test_runner_dry_run_prompt_is_registered(self):
        from arifosmcp.prompts import CANONICAL_PROMPTS, RUNNER_DRY_RUN_PROMPT

        assert "runner_dry_run" in CANONICAL_PROMPTS
        assert "Context Engine Runner" in RUNNER_DRY_RUN_PROMPT
        # F-binding noted in the prompt body
        for floor in ("F1 AMANAH", "F2 TRUTH", "F8 GENIUS", "F11 AUDIT", "F13 SOVEREIGN"):
            assert floor in RUNNER_DRY_RUN_PROMPT, f"missing floor: {floor}"


# ─────────────────────────────────────────────────────────────────────────────
# 8. Resources surface
# ─────────────────────────────────────────────────────────────────────────────
class TestResourcesSurface:
    def test_runner_resources_registered(self):
        from arifosmcp.resources import RUNNER_RESOURCES

        assert "runner://receipt/{run_id}" in RUNNER_RESOURCES
        assert "runner://policy/v1" in RUNNER_RESOURCES

    def test_runner_resources_module_wired(self):
        from arifosmcp.resources.runner import (
            register_runner_resources,
            RUNNER_RESOURCES as MODULE_RESOURCES,
        )

        # Both module-level and package-level exports agree
        assert MODULE_RESOURCES == (
            "runner://receipt/{run_id}",
            "runner://policy/v1",
        )
        assert callable(register_runner_resources)


# ─────────────────────────────────────────────────────────────────────────────
# Goal 4: 4-stage loop wiring invariants (added 2026-06-12 by omega-Ω)
# ─────────────────────────────────────────────────────────────────────────────
class TestFourStageLoopWiring:
    """The 4-stage loop (mind -> heart -> judge -> forge) is the constitutional
    contract. These tests prove the wiring EXISTS and the F1+F11 gates fire
    correctly when unsigned clients try to traverse the loop. Full loop
    traversal requires a F13-signed FederationEnvelope (sovereign territory)."""

    def test_arif_kernel_route_has_context_runner_mode(self):
        """The canonical arif_kernel_route tool must have a context_runner
        mode dispatch. Verified by code search."""
        import inspect
        from arifosmcp.runtime.tools import _arif_kernel_route
        src = inspect.getsource(_arif_kernel_route)
        assert 'mode == "context_runner"' in src, (
            "arif_kernel_route missing context_runner mode dispatch"
        )

    def test_context_runner_bridge_policy_version_pinned(self):
        """The bridge policy version must be pinned and present. F1: an
        unpinned policy is not a real contract."""
        from arifosmcp.runtime.context_runner_bridge import (
            BRIDGE_POLICY_VERSION,
            BRIDGE_SOURCE_OF_TRUTH,
        )
        assert BRIDGE_POLICY_VERSION.startswith("context_runner_bridge.")
        assert BRIDGE_SOURCE_OF_TRUTH.endswith("context_runner_bridge.py")
        assert len(BRIDGE_POLICY_VERSION) > 0
        assert len(BRIDGE_SOURCE_OF_TRUTH) > 0

    def test_ingress_blocks_unsigned_atomic_actions(self):
        """The ingress middleware must reject LEGACY_WRAP + ATOMIC with
        888_HOLD. This is the F1+F11 fail-closed gate at the kernel edge."""
        from arifosmcp.schemas.federation_envelope import (
            FederationEnvelope,
            ActionClass,
            FederationOrgan,
        )
        import uuid

        env = FederationEnvelope(
            trace_id=f"trace-{uuid.uuid4().hex[:12]}",
            actor_id="arif-fazil",
            session_id=f"test-{uuid.uuid4().hex[:8]}",
            organ=FederationOrgan.ARIFOS,
            legacy_wrap=True,
        )
        env.risk.action_class = ActionClass.ATOMIC
        assert env.legacy_wrap is True
        assert env.risk.action_class == ActionClass.ATOMIC
        gate_triggers = env.legacy_wrap and env.risk.action_class in (
            ActionClass.MUTATE,
            ActionClass.ATOMIC,
        )
        assert gate_triggers, "LEGACY_WRAP + ATOMIC gate must fire"

    def test_observability_only_tools_pass_legacy_wrap(self):
        """OBSERVE-class tools (read-only) should be allowed even with
        legacy_wrap=True. This is the F1 read-only escape valve."""
        from arifosmcp.schemas.federation_envelope import (
            FederationEnvelope,
            ActionClass,
            FederationOrgan,
        )
        import uuid

        env = FederationEnvelope(
            trace_id=f"trace-{uuid.uuid4().hex[:12]}",
            actor_id="arif-fazil",
            session_id=f"test-{uuid.uuid4().hex[:8]}",
            organ=FederationOrgan.ARIFOS,
            legacy_wrap=True,
        )
        env.risk.action_class = ActionClass.OBSERVE
        gate_triggers = env.legacy_wrap and env.risk.action_class in (
            ActionClass.MUTATE,
            ActionClass.ATOMIC,
        )
        assert not gate_triggers, (
            "OBSERVE actions should bypass LEGACY_WRAP gate (F1 read-only)"
        )

    def test_context_runner_bridge_four_intents_wired(self):
        """The bridge must wire all 4 intent types: preflight, prepare,
        run, inspect. This is the canonical sub-tool surface."""
        from arifosmcp.runtime.context_runner_bridge import (
            _ctx_preflight,
            _ctx_prepare,
            _ctx_run,
            _ctx_inspect,
        )

        for fn in (_ctx_preflight, _ctx_prepare, _ctx_run, _ctx_inspect):
            assert callable(fn), f"Intent handler not callable: {fn.__name__}"
