"""F6 kernel acceptance tests — bounded, synthetic-only, no real external actions.

Each mandatory acceptance criterion from the F6 v0 directive maps to explicit
tests in this suite against `arifosmcp.runtime.f6` and `floor_producers`.
Synthetic canaries use temporary paths and never touch production ledgers.

Run:
    /usr/bin/python3 tests/constitutional/test_f6_maruah_v0.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

KERNEL_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KERNEL_ROOT))

from arifosmcp.runtime.f6.authority_binding import (  # noqa: E402
    ActionRequest,
    AuthorityBinding,
    BindingStore,
    BindingVerdict,
    check_binding,
    execute_bound,
)
from arifosmcp.runtime.f6.correction_effect import (  # noqa: E402
    CorrectionStatus,
    apply_correction,
    challenge_record,
    load_corrections,
    propagate_correction_across_layers,
    record_correction,
    resolve_dissent_at_decision_gate,
    supersede,
    verify_effect,
)
from arifosmcp.runtime.f6.consent_scope import (  # noqa: E402
    ConsentDecision,
    ConsentScope,
    ConsentSource,
    check_consent,
)
from arifosmcp.runtime.f6.meters import (  # noqa: E402
    Axis,
    MeterAssessment,
    evaluate_all,
    evaluate_comprehension_ceremony,
    evaluate_manipulation_detector,
    evaluate_meter_1_authority_bypass,
    evaluate_meter_2_unreceipted_claims,
    evaluate_meter_3_comprehension,
    evaluate_meter_4_false_urgency_flattery,
    evaluate_meter_5_correction_acceptance,
    evaluate_meter_5_false_urgency_flattery,
    evaluate_meter_6_consent_scope,
    verify_claim_receipt_relevance,
)
from arifosmcp.runtime.f6.privacy_and_redress import (  # noqa: E402
    RollbackClassification,
    classify_rollback_outcome,
    enforce_private_file_mode,
    validate_no_human_scoring,
    verify_analytics_authority_separation,
)
from arifosmcp.runtime.f6 import pending_policies  # noqa: E402
from arifosmcp.runtime.floor_producers import collect_floor_producer_signal  # noqa: E402


def _iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


def _binding(**kw: Any) -> AuthorityBinding:
    now = datetime.now(timezone.utc)
    defaults: dict[str, Any] = dict(
        binding_id="b-test",
        actor_id="agent-x",
        authority="LIMITED_MUTATE",
        scope="github",
        allowed_actions=["write:issues"],
        resource_patterns=["repo/A-FORGE#*"],
        param_constraints={"title": {"max_len": 50}},
        not_before=_iso(now - timedelta(hours=1)),
        not_after=_iso(now + timedelta(hours=1)),
    )
    defaults.update(kw)
    return AuthorityBinding(**defaults)


class F6AuthorityTests(unittest.TestCase):
    """P0: authority boundary to the last tool (Criteria 1, 2, 3, 11)."""

    def _store(self, binding: AuthorityBinding, tmp: str) -> BindingStore:
        store = BindingStore(db_path=Path(tmp) / "bind.db")
        store.save(binding)
        return store

    def test_01_subagent_widening_rejected_at_execution_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            parent = _binding(binding_id="parent", authority="OBSERVE_ONLY")
            child = _binding(
                binding_id="child",
                parent_binding_id="parent",
                authority="FULL",
                allowed_actions=["write:issues"],
            )
            store = self._store(parent, tmp)
            store.save(child)
            side_effects: list[str] = []
            res = execute_bound(
                ActionRequest("child", "agent-x", "write:issues", "repo/A-FORGE#1"),
                store,
                lambda _req: side_effects.append("mutated"),
                state_guard=lambda r, b: (True, ""),
            )
            self.assertFalse(res["executed"])
            self.assertEqual(side_effects, [])
            self.assertEqual(res["decision"], BindingVerdict.REJECT_DELEGATION)
            self.assertIn("widen", res["reason"].lower())

    def test_01b_subagent_multi_hop_scope_action_resource_param_widening_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            now = datetime.now(timezone.utc)
            root = _binding(
                binding_id="root",
                authority="LIMITED_MUTATE",
                scope="github:issues",
                allowed_actions=["write:issues"],
                resource_patterns=["repo/A-FORGE#*"],
                param_constraints={"title": {"max_len": 40}},
                not_after=_iso(now + timedelta(minutes=30)),
            )
            mid = _binding(
                binding_id="mid",
                parent_binding_id="root",
                authority="LIMITED_MUTATE",
                scope="github:issues",
                allowed_actions=["write:issues"],
                resource_patterns=["repo/A-FORGE#1*"],
                param_constraints={"title": {"max_len": 30}},
                not_after=_iso(now + timedelta(minutes=20)),
            )
            child_wide_res = _binding(
                binding_id="child-res",
                parent_binding_id="mid",
                scope="github:issues",
                allowed_actions=["write:issues"],
                resource_patterns=["repo/*"],
                param_constraints={"title": {"max_len": 30}},
                not_after=_iso(now + timedelta(minutes=15)),
            )
            store = self._store(root, tmp)
            store.save(mid)
            store.save(child_wide_res)
            out = check_binding(
                ActionRequest(
                    "child-res", "agent-x", "write:issues", "repo/OTHER#9",
                    params={"title": "ok"},
                ),
                store,
                state_guard=lambda r, b: (True, ""),
            )
            self.assertEqual(out["decision"], BindingVerdict.REJECT_DELEGATION)
            self.assertIn("outside ancestor", out["reason"])

    def test_02a_revoked_binding_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            b = _binding()
            store = self._store(b, tmp)
            store.revocations.revoke(b.binding_id, "operator", "test revoke")
            out = check_binding(
                ActionRequest("b-test", "agent-x", "write:issues", "repo/A-FORGE#1"),
                store,
                state_guard=lambda r, b: (True, ""),
            )
            self.assertEqual(out["decision"], BindingVerdict.REJECT_REVOKED)

    def test_02b_expired_binding_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            now = datetime.now(timezone.utc)
            b = _binding(not_after=_iso(now - timedelta(minutes=1)))
            store = self._store(b, tmp)
            out = check_binding(
                ActionRequest("b-test", "agent-x", "write:issues", "repo/A-FORGE#1"),
                store,
                state_guard=lambda r, b: (True, ""),
            )
            self.assertEqual(out["decision"], BindingVerdict.REJECT_EXPIRED)

    def test_02c_replayed_nonce_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            b = _binding(nonce="n-123")
            store = self._store(b, tmp)
            req = ActionRequest(
                "b-test", "agent-x", "write:issues", "repo/A-FORGE#1",
                params={"title": "hello"},
            )
            first = check_binding(req, store, state_guard=lambda r, b: (True, ""))
            self.assertEqual(first["decision"], BindingVerdict.ALLOW)
            second = check_binding(req, store, state_guard=lambda r, b: (True, ""))
            self.assertEqual(second["decision"], BindingVerdict.REJECT_REPLAY)

    def test_03_params_changed_after_approval_not_misused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            b = _binding(
                param_constraints={"title": {"max_len": 50}, "env": {"const": "staging"}},
                approved_params={"title": "initial title", "env": "staging"},
                allow_extra_params=False,
            )
            store = self._store(b, tmp)
            out_len = check_binding(
                ActionRequest(
                    "b-test", "agent-x", "write:issues", "repo/A-FORGE#1",
                    params={"title": "x" * 200, "env": "staging"},
                ),
                store,
                state_guard=lambda r, b: (True, ""),
            )
            self.assertEqual(out_len["decision"], BindingVerdict.REJECT_PARAM)

            out_mut = check_binding(
                ActionRequest(
                    "b-test", "agent-x", "write:issues", "repo/A-FORGE#1",
                    params={"title": "different title", "env": "staging"},
                ),
                store,
                state_guard=lambda r, b: (True, ""),
            )
            self.assertEqual(out_mut["decision"], BindingVerdict.REJECT_PARAM)
            self.assertIn("approved_params", out_mut["reason"])

            b2 = _binding(
                binding_id="b-omit",
                param_constraints={"env": {"const": "staging"}},
            )
            store.save(b2)
            out_omit = check_binding(
                ActionRequest(
                    "b-omit", "agent-x", "write:issues", "repo/A-FORGE#1",
                    params={},
                ),
                store,
                state_guard=lambda r, b: (True, ""),
            )
            self.assertEqual(out_omit["decision"], BindingVerdict.REJECT_PARAM)
            self.assertIn("missing at execution time", out_omit["reason"])

    def test_03b_state_changed_since_approval_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            b = _binding()
            store = self._store(b, tmp)
            guard = lambda r, b: (False, "target issue closed after approval")
            out = check_binding(
                ActionRequest("b-test", "agent-x", "write:issues", "repo/A-FORGE#1"),
                store,
                state_guard=guard,
            )
            self.assertEqual(out["decision"], BindingVerdict.REJECT_STATE)

    def test_03c_missing_state_guard_is_unknown_not_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            b = _binding()
            store = self._store(b, tmp)
            out = check_binding(
                ActionRequest("b-test", "agent-x", "write:issues", "repo/A-FORGE#1"), store
            )
            self.assertEqual(out["decision"], BindingVerdict.UNKNOWN)


class F6CorrectionTests(unittest.TestCase):
    """P1: Meter 5 — correction effect & grounded dissent (Criteria 4, 5, 10)."""

    def test_04_correction_applied_text_without_change_not_verified(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            led = Path(tmp) / "corr.jsonl"
            rec = record_correction("d1", "agent-v1", "claim", "fix", ledger_path=led)
            out = verify_effect(
                rec.correction_id,
                before_evidence={},
                after_evidence={},
                effect_ref="",
                ledger_path=led,
            )
            self.assertFalse(out["effect_verified"])
            self.assertIn("never verifies", out["reason"])

            out_cosmetic = verify_effect(
                rec.correction_id,
                before_evidence={"status": "pending"},
                after_evidence={"text": "correction applied"},
                effect_ref="ref-1",
                ledger_path=led,
            )
            self.assertFalse(out_cosmetic["effect_verified"])
            self.assertIn("cosmetic", out_cosmetic["reason"])

    def test_04b_correction_with_zero_downstream_change_not_verified(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            led = Path(tmp) / "corr.jsonl"
            rec = record_correction("d1", "agent-v1", "claim", "fix", ledger_path=led)
            same = {"state": "unchanged", "action": "same"}
            out = verify_effect(rec.correction_id, same, dict(same), "ref", ledger_path=led)
            self.assertFalse(out["effect_verified"])
            self.assertIn("NO downstream change", out["reason"])

    def test_05_correction_changes_state_and_action_before_after_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            led = Path(tmp) / "corr.jsonl"
            rec = record_correction(
                "d1", "agent-v1", "claim X", "X is wrong, it is Y", ledger_path=led
            )
            self.assertEqual(rec.status, CorrectionStatus.ACCEPTED.value)

            applied = apply_correction(
                rec.correction_id, "d1", "agent-v1", {"state": "claim=Y"}, ledger_path=led
            )
            self.assertEqual(applied.status, CorrectionStatus.APPLIED.value)

            consumed: dict[str, Any] = {}

            def apply_to_decision(payload: dict[str, Any]) -> bool:
                consumed.update(payload)
                return True

            out = verify_effect(
                rec.correction_id,
                before_evidence={"state": "claim=X", "next_action": "report X"},
                after_evidence={"state": "claim=Y", "next_action": "report Y"},
                effect_ref="synthetic://state-delta",
                apply_to_decision=apply_to_decision,
                ledger_path=led,
            )
            self.assertTrue(out["effect_verified"])
            self.assertEqual(consumed["after"]["state"], "claim=Y")
            rows = load_corrections(led)
            statuses = [r["status"] for r in rows]
            self.assertEqual(
                statuses,
                [
                    CorrectionStatus.ACCEPTED.value,
                    CorrectionStatus.APPLIED.value,
                    CorrectionStatus.EFFECT_VERIFIED.value,
                ],
            )

    def test_05b_grounded_dissent_reaches_decision_gate_and_changes_action(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            led = Path(tmp) / "corr.jsonl"
            rec = record_correction(
                "d2",
                "agent-v1",
                "source says 42",
                "source is misquoted, actual is 24",
                disputed=True,
                dispute_reason="verified against primary source line 3",
                ledger_path=led,
            )
            self.assertEqual(rec.status, CorrectionStatus.DISPUTED_WITH_REASON.value)
            with self.assertRaises(ValueError):
                record_correction("d3", "a", "c", "k", disputed=True, ledger_path=led)

            no_change = resolve_dissent_at_decision_gate(
                rec,
                before_decision_state={"action": "publish_42"},
                accepted=True,
                updated_decision_state={"action": "publish_42"},
                resolution_reason="accepted in prose only",
                ledger_path=led,
            )
            self.assertFalse(no_change["effect_verified"])

            changed = resolve_dissent_at_decision_gate(
                rec,
                before_decision_state={"action": "publish_42"},
                accepted=True,
                updated_decision_state={"action": "publish_24"},
                resolution_reason="primary source verified at gate",
                ledger_path=led,
            )
            self.assertTrue(changed["reached_final_decision"])
            self.assertFalse(changed["counted_as_disrespect"])
            self.assertTrue(changed["effect_verified"])

            m5 = evaluate_meter_5_correction_acceptance(ledger_path=led)
            self.assertEqual(m5.result, "PASS")


class F6ConsentAndRelevanceTests(unittest.TestCase):
    """P2: Meter 6 consent scope + Meter 2 relevance + Meter 3/4 contracts (Criteria 6, 7)."""

    def test_06_fresh_but_irrelevant_evidence_no_pass(self) -> None:
        now = datetime.now(timezone.utc)
        scope = ConsentScope(
            scope_id="s1",
            subject="system-A",
            source=ConsentSource.OPERATOR_DECLARATION,
            can_access=True,
            can_use=True,
            can_disclose=False,
            not_after=_iso(now + timedelta(days=1)),
        )
        out_consent = check_consent(
            scope,
            want_access=True,
            source_verified=True,
            requested_subject="system-B",
        )
        self.assertEqual(out_consent["decision"], ConsentDecision.DENY_OUT_OF_SCOPE)

        rel = verify_claim_receipt_relevance(
            claim_id="cl-1",
            claimed_outcome="deployed",
            claimed_target="repo/B#issue-9",
            receipt={
                "observed_at": _iso(now),
                "sha256": "abc123",
                "probe_output": "ok",
                "target": "repo/A#issue-1",
                "outcome": "deployed",
            },
        )
        self.assertFalse(rel["relevant"])
        self.assertEqual(rel["result"], "FAIL")

    def test_06b_consent_access_use_disclose_delegation_expiry_revocation_inference(self) -> None:
        now = datetime.now(timezone.utc)
        parent = ConsentScope(
            scope_id="c-parent",
            subject="medical-record",
            source=ConsentSource.OPERATOR_DECLARATION,
            can_access=True,
            can_use=True,
            can_disclose=False,
            allowed_recipients=["doctor-a"],
            not_before=_iso(now - timedelta(hours=1)),
            not_after=_iso(now + timedelta(hours=1)),
        )
        out_disc = check_consent(
            parent,
            want_disclose=True,
            source_verified=True,
            requested_subject="medical-record",
            requested_recipient="doctor-a",
        )
        self.assertEqual(out_disc["decision"], ConsentDecision.DENY_USE_NOT_GRANTED)

        child_wide = ConsentScope(
            scope_id="c-child",
            subject="medical-record",
            source=ConsentSource.OPERATOR_DECLARATION,
            can_access=True,
            can_use=True,
            can_disclose=True,
            parent_scope=parent,
            not_after=_iso(now + timedelta(minutes=30)),
        )
        out_wide = check_consent(
            child_wide,
            want_access=True,
            source_verified=True,
            requested_subject="medical-record",
        )
        self.assertEqual(out_wide["decision"], ConsentDecision.DENY_DELEGATION_WIDENED)

        out_inf = check_consent(
            None,
            want_access=True,
            model_confidence=0.99,
        )
        self.assertEqual(out_inf["decision"], ConsentDecision.UNKNOWN)
        self.assertIn("DEPENDENCY REPORTED", out_inf["reason"])

        revoked_scope = ConsentScope(
            scope_id="c-rev",
            subject="medical-record",
            source=ConsentSource.OPERATOR_DECLARATION,
            can_access=True,
            can_use=True,
            can_disclose=False,
            revoked=True,
            not_after=_iso(now + timedelta(hours=1)),
        )
        out_rev = check_consent(
            revoked_scope,
            want_access=True,
            source_verified=True,
            requested_subject="medical-record",
        )
        self.assertEqual(out_rev["decision"], ConsentDecision.DENY_REVOKED)

    def test_07_producer_missing_ledger_empty_or_exception_is_unknown_not_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            empty_corr = Path(tmp) / "missing_corr.jsonl"
            m5_empty = evaluate_meter_5_correction_acceptance(ledger_path=empty_corr)
            self.assertEqual(m5_empty.result, "UNKNOWN")

            m3_none = evaluate_meter_3_comprehension()
            self.assertEqual(m3_none.result, "UNKNOWN")
            m4_none = evaluate_meter_4_false_urgency_flattery()
            self.assertEqual(m4_none.result, "UNKNOWN")
            self.assertEqual(evaluate_meter_5_false_urgency_flattery().result, "UNKNOWN")

            bad_corr = Path(tmp) / "bad_corr.jsonl"
            bad_corr.mkdir()
            m5_exc = evaluate_meter_5_correction_acceptance(ledger_path=bad_corr)
            self.assertEqual(m5_exc.result, "UNKNOWN")
            self.assertEqual(m5_exc.measurement, Axis.ERROR)

            na_no_reason = MeterAssessment(
                meter_id="M_TEST",
                behavior_examined="test",
                result="NOT_APPLICABLE",
                result_reason="",
                measurement=Axis.MEASURED,
                witness="UNWITNESSED",
                producer="test",
                pass_does_not_imply="test",
            )
            self.assertEqual(na_no_reason.result, "UNKNOWN")


class F6WitnessCeremonyPolicyAndKernelTests(unittest.TestCase):
    """Criteria 8, 9, 11 + kernel floor_producers integration."""

    def test_08_witness_not_answering_is_stale_and_blocks_overall_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stale_witness = Path(tmp) / "witness.jsonl"
            stale_witness.write_text(
                json.dumps({"ts": "2026-01-01T00:00:00+00:00"}) + "\n",
                encoding="utf-8",
            )
            meters = evaluate_all(witness_path=stale_witness)
            for m in meters["meters"]:
                self.assertEqual(m["witness"], "STALE")
            self.assertIn("UNPROVEN", meters["f6_overall"])

    def test_09_low_ceremony_comprehension_and_manipulation_detector(self) -> None:
        quiz = evaluate_comprehension_ceremony(
            decision_id="d-quiz",
            consequence_tier=3,
            reversible=False,
            restatement_provided=True,
            mandatory_quiz=True,
        )
        self.assertEqual(quiz["result"], "FAIL")

        irrev_missing = evaluate_comprehension_ceremony(
            decision_id="d-irrev",
            consequence_tier=3,
            reversible=False,
            restatement_provided=False,
        )
        self.assertEqual(irrev_missing["result"], "FAIL")

        delegated = evaluate_comprehension_ceremony(
            decision_id="d-del",
            consequence_tier=1,
            reversible=True,
            human_delegated=True,
            interrupted_human=False,
        )
        self.assertEqual(delegated["result"], "NOT_APPLICABLE")
        self.assertTrue(len(delegated["reason"]) > 0)

        rested_interrupted = evaluate_comprehension_ceremony(
            decision_id="d-rest",
            consequence_tier=1,
            reversible=True,
            human_resting=True,
            interrupted_human=True,
        )
        self.assertEqual(rested_interrupted["result"], "FAIL")

        manip_uncal = evaluate_manipulation_detector(
            flagged_count=0,
            sample_size=10,
            false_positive_rate=None,
            false_negative_rate=None,
        )
        self.assertEqual(manip_uncal["result"], "UNKNOWN")

        manip_flagged = evaluate_manipulation_detector(
            flagged_count=2,
            sample_size=20,
            false_positive_rate=0.05,
            false_negative_rate=0.10,
        )
        self.assertEqual(manip_flagged["result"], "FAIL")

    def test_10_undecided_policies_stay_inactive(self) -> None:
        meters = evaluate_all()
        blob = json.dumps(meters)
        self.assertNotIn("third_party_protected", blob)
        self.assertNotIn("collective_veto", blob)
        self.assertNotIn("peer_witness:assigned", blob)
        self.assertIn("UNPROVEN", meters["f6_overall"])
        for forbidden in ("F6 solved", "maruah protected", "sealed"):
            self.assertNotIn(forbidden, blob)

        pp = pending_policies.all_pending()
        statuses = {p["policy_id"]: p["status"] for p in pp["policies"]}
        self.assertEqual(statuses["third_party_dignity"], "PENDING")
        self.assertEqual(statuses["collective_witness"], "HOLD")
        self.assertEqual(statuses["external_peer_witness"], "UNASSIGNED")
        self.assertFalse(any(p["active"] for p in pp["policies"]))
        with self.assertRaises(pending_policies.PolicyNotActive):
            pending_policies.enforce("collective_veto")

        with tempfile.TemporaryDirectory() as tmp:
            b = _binding()
            store = BindingStore(db_path=Path(tmp) / "bind.db")
            store.save(b)
            res = execute_bound(
                ActionRequest(
                    "b-test", "agent-x", "write:issues", "repo/A-FORGE#1",
                    params={"title": "valid issue"},
                ),
                store,
                lambda req: {"created": req.params["title"]},
                state_guard=lambda r, b: (True, ""),
            )
            self.assertTrue(res["executed"])
            self.assertEqual(res["tool_output"], {"created": "valid issue"})

    def test_11_privacy_redress_and_rollback_separation(self) -> None:
        meters = evaluate_all()
        ok_m, viol_m = validate_no_human_scoring(meters)
        self.assertTrue(ok_m, viol_m)
        ok_bad, _ = validate_no_human_scoring({"dignity_score": 0.9})
        self.assertFalse(ok_bad)

        with tempfile.TemporaryDirectory() as tmp:
            auth_p = Path(tmp) / "auth.db"
            ana_p = Path(tmp) / "analytics.jsonl"
            sep = verify_analytics_authority_separation(meters, auth_p, ana_p)
            self.assertTrue(sep["separated"])
            same = verify_analytics_authority_separation(meters, auth_p, auth_p)
            self.assertFalse(same["separated"])

            led = Path(tmp) / "corr.jsonl"
            rec = record_correction("d1", "v1", "old", "new", ledger_path=led)
            ch = challenge_record(rec.correction_id, "contested evidence", ledger_path=led)
            self.assertEqual(ch.status, CorrectionStatus.CHALLENGED.value)
            sup = supersede(rec.correction_id, "refined", ledger_path=led)
            self.assertEqual(sup.supersedes_id, rec.correction_id)
            self.assertEqual(len(load_corrections(led)), 3)
            self.assertTrue(enforce_private_file_mode(led))

        tech = classify_rollback_outcome(
            technical_state_reverted=True,
            external_effect_occurred=False,
        )
        self.assertEqual(
            tech["classification"],
            RollbackClassification.TECHNICAL_ROLLBACK_COMPLETE,
        )

        ext = classify_rollback_outcome(
            technical_state_reverted=True,
            external_effect_occurred=True,
            external_effect_description="email sent to external recipient",
            compensating_action="send retraction notice",
        )
        self.assertEqual(
            ext["classification"],
            RollbackClassification.EXTERNAL_CONSEQUENCE_IRREVERSIBLE,
        )
        self.assertFalse(ext["fully_undone"])

    def test_12_kernel_floor_producer_f6_integration(self) -> None:
        """Kernel floor_producers.collect_floor_producer_signal('F6', sources=...) enforces
        L1 human-scoring disqualify, rejects kappa_r proxy, and requires all 6 meters + REVIEWED witness."""
        # 1) L1 human scoring key -> FAIL
        sig_l1 = collect_floor_producer_signal("F6", sources={"human_id": "u-1"})
        self.assertEqual(sig_l1["status"], "FAIL")
        self.assertEqual(sig_l1["origin"], "f6_l1_breach_disqualify")

        # 2) kappa_r proxy alone -> UNMEASURED (never PASS)
        sig_kr = collect_floor_producer_signal("F6", sources={"kappa_r": 0.99})
        self.assertEqual(sig_kr["status"], "UNMEASURED")
        self.assertIn("kappa_r_proxy_rejected", sig_kr["origin"])

        # 3) Live evaluate_all() bundle (with UNKNOWN meters / STALE witness) -> UNMEASURED
        bundle = evaluate_all()
        sig_live = collect_floor_producer_signal("F6", sources=bundle)
        self.assertEqual(sig_live["status"], "UNMEASURED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
