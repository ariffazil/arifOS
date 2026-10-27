"""tests/test_kx010_measurement_contract.py — KX-010 closed-set contract tests.

VD-888-KX010-APEX-MEASUREMENT-CONTRACT-2026-10-27 (SEAL_WITH_SCOPE). P5 as
amended. The allowlist and the out-of-scope roster live here as DATA (mission
rule 1: no new registry file).

What this pins:
  P5(a) CLOSED SET — every contracted wire path carries the five-field
        contract + provenance + decision_eligibility, and every numeric leaf
        in the thermodynamic / governance / apex_scalars / eureka_margin /
        measurement_basis blocks of the live /health payload is EITHER in the
        allowlist (contracted) OR in the named out-of-scope roster. An
        unclassified leaf FAILS — a new numeric producer cannot ship naked.
  P5(b) synthetic uncontracted scalar resolves decision_eligibility=NONE
        (fail closed — never zero, never pass).
  P5(c) historical receipt JSON is untouched by the patch's read/build paths.
  P5(d) the A-FORGE passthrough contract (fixture replication; the real TS
        passthrough + guards are additionally exercised on the compiled dist
        by the patch session probe — node dist GovernanceBridge).
  A4    arif_init envelope carries the omega_0 contract; an envelope numeric
        WITHOUT a contract resolves LEGACY_UNCONTRACTED / NONE.
  A3    negatives: expired valid_until, out-of-expected_range, cross-unit
        arithmetic, null composite component, scope mismatch, staleness.

DECLARED STALENESS POLICY (A3 condition — one documented default, no
per-metric windows): a contract is stale when its `valid_until` has elapsed,
OR when its `observed_at` is older than DEFAULT_MAX_AGE_SECONDS = 604800
(7 days, matching the apex metrics window in
arifosmcp/runtime/apex_primitives.py:197 compute_apex_from_metrics). This
test-side resolver mirrors the compiled consumer guard in
A-FORGE/src/domain/governance/GovernanceBridge.ts
(resolveDecisionEligibility / KX010_DEFAULT_MAX_AGE_MS).
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient

from arifosmcp.runtime.floor_producers import (
    _PRODUCERS,
    collect_floor_producer_signal,
)
from arifosmcp.runtime.rest_routes.rest_routes import measurement_contract

# ── Constants ────────────────────────────────────────────────────────────────

SCHEMA_VERSION = "kx010.v1"

# Five contract fields (KX-010 acceptance test) + provenance + eligibility.
REQUIRED_CONTRACT_FIELDS = (
    "metric_name",
    "unit",
    "measurement_method",
    "monotonic_drivers",
    "falsification_test",
    "provenance_class",
    "decision_eligibility",
    "semantic_class",
    "calibration_status",
    "schema_version",
)

DECISION_ELIGIBILITY_ENUM = {
    "DISPLAY_ONLY",
    "ADVISORY",
    "ROUTING",
    "THRESHOLD_ALERT",
    "HOLD_TRIGGER",
    "AUTHORIZATION_INPUT",
    "MUTATION_GATE",
    "NONE",
}

PROVENANCE_CLASS_ENUM = {
    "MODEL_PROPOSED",
    "CLIENT_SUPPLIED",
    "TRANSPORT_DERIVED",
    "SERVER_OBSERVED",
    "POLICY_DERIVED",
    "CRYPTO_VERIFIED",
    "HUMAN_AUTHORITY",
}

# Declared default staleness window (see docstring). Mirrors the TS guard.
DEFAULT_MAX_AGE_SECONDS = 604800

# ── P5(a) DATA: CLOSED-SET ALLOWLIST ─────────────────────────────────────────
# Contracted wire paths, enumerated exhaustively.

ALLOWLIST_APEX = {
    "G",
    "C_dark",
    "A",
    "P",
    "E",
    "X",
    "W3",
    "h",
    "QDF",
    "g_task_verdict",
    "g_well_state",
    "g_authorization",
    "g_metabolism",
}

ALLOWLIST_THERMODYNAMIC = {
    "entropy_delta",
    "peace_squared",
    "vitality_index",
    "kappa_r",
    "echo_debt",
    "shadow",
    "confidence",
    "witness",  # HEURISTIC composite (tri-witness legs published verbatim)
}

ALLOWLIST_GOVERNANCE = {
    "tau_confidence_system",
    "tau_threshold_f2",
    "psi_vitality",
    "peace_squared",
}

ALLOWLIST_METRICS_JSON = {
    "entropy_delta",
    "peace_squared",
    "vitality_index",
    "echo_debt",
    "shadow",
    "confidence",
    "kappa_r",
    "tau_threshold_f2",
    "witness_human",
    "witness_ai",
    "witness_earth",
}

ALLOWLIST_LIVE_VITALS = {"G_star", "dS", "peace2", "kappa_r", "echo_debt", "psi_le"}

ALLOWLIST_LIVE_GOVERNANCE = {
    "tau_confidence_system",
    "f2_threshold",
    "psi_vitality",
    "peace2",
}

# ── P5(a) DATA: OUT-OF-SCOPE ROSTER (named debt — never retro-contracted) ────
# Every numeric leaf below is KNOWN and deliberately uncontracted by this
# patch. A leaf here is named debt, not an oversight.

ROSTER_MEASUREMENT_BASIS = {
    "event_count",
    "action_count",
    "outcome_count",
    "reversibility_count",
    "contradiction_count",
    "query_evaluated",
    "witness_sum",  # KX-011 (stale-basis class)
    "unmeasured_floors",
    "sample_size",
    "window_seconds",
    # nested block leaves (counted recursively in the scan)
    "A",
    "P",
    "E",
    "X",
    "G",
    "C_dark",
}

ROSTER_MEASUREMENT_BASIS_BLOCKS = {"f6_maruah", "f8_g_basis"}

ROSTER_EUREKA_MARGIN = {
    "n_act",
    "n_resolved",
    "phi_e",
    "contradiction_resolution_ratio",
}

# metabolic_stage — the borderline "333" leaf (verdict: executor must document
# the allowlist decision explicitly). DECISION: rostered, NOT contracted — the
# verdict's authorized_files enumerate builder sites only, and metabolic_stage
# has no authorized producer site. Named debt (A8 class).
ROSTER_THERMODYNAMIC = {"metabolic_stage"}

ROSTER_METRICS_JSON = {"metabolic_stage"}

# /api/live/all governance aggregate counters — COUNTS over the frozen
# runtime_floors_status gate math (floors_passing/failing aggregation is a
# prohibited-mutation surface; they are tallies, not physics-labelled
# scalars, so they carry no measurement contract and are named debt here).
ROSTER_LIVE_GOVERNANCE = {"floors_active", "floors_passing", "floors_failing"}

# ── Session fixtures ─────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def health_payloads() -> dict[str, dict[str, Any]]:
    """Build /health, /metrics/json and /api/live/all ONCE (live in-process)."""
    from arifosmcp.runtime.rest_routes import rest_routes as rr

    app = Starlette()
    rr.register_rest_routes(app, {})
    payloads: dict[str, dict[str, Any]] = {}
    with TestClient(app) as client:
        payloads["health"] = client.get("/health").json()
        payloads["metrics"] = client.get("/metrics/json").json()
        payloads["live_all"] = client.get("/api/live/all").json()
    return payloads


def _assert_valid_contract(contract: Any, where: str) -> None:
    assert isinstance(contract, dict), f"{where}: measurement_contract missing"
    for field in REQUIRED_CONTRACT_FIELDS:
        assert field in contract, f"{where}: contract lacks required field '{field}'"
    assert contract["schema_version"] == SCHEMA_VERSION, (
        f"{where}: schema_version {contract['schema_version']!r} != {SCHEMA_VERSION!r}"
    )
    assert contract["decision_eligibility"] in DECISION_ELIGIBILITY_ENUM, (
        f"{where}: decision_eligibility {contract['decision_eligibility']!r} not in enum"
    )
    assert contract["provenance_class"] in PROVENANCE_CLASS_ENUM, (
        f"{where}: provenance_class {contract['provenance_class']!r} not in enum"
    )
    # five-field completeness: meaning, unit, method, drivers, falsification
    assert contract["unit"], f"{where}: unit must be declared ('1' when dimensionless)"
    assert contract["measurement_method"], f"{where}: measurement_method empty"
    assert contract["metric_name"], f"{where}: metric_name (meaning) empty"
    assert contract["falsification_test"], f"{where}: falsification_test empty"


# ── P5(a): closed-set allowlist assertions ───────────────────────────────────


class TestP5AClosedSet:
    def test_apex_scalars_all_contracted(self, health_payloads) -> None:
        apex = health_payloads["health"]["apex_scalars"]
        assert apex, "apex_scalars block missing from /health"
        unknown = set(apex) - ALLOWLIST_APEX
        assert not unknown, (
            f"unclassified apex_scalars keys {sorted(unknown)} — add them to "
            f"ALLOWLIST_APEX (with contracts) or the out-of-scope roster"
        )
        for name in ALLOWLIST_APEX:
            entry = apex.get(name)
            assert entry is not None, f"apex scalar {name} missing from live wire"
            _assert_valid_contract(entry.get("measurement_contract"), f"apex_scalars.{name}")

    def test_g_authorization_is_none(self, health_payloads) -> None:
        contract = health_payloads["health"]["apex_scalars"]["g_authorization"][
            "measurement_contract"
        ]
        assert contract["decision_eligibility"] == "NONE", (
            "g_authorization must stay NONE until calibration lands via a new "
            "judged verdict (prohibited mutation #7)"
        )
        assert contract["scope"] == "g_authorization"

    def test_apex_values_untouched_by_contracts(self, health_payloads) -> None:
        """The contract never carries or edits the value (value stays beside it)."""
        for name, entry in health_payloads["health"]["apex_scalars"].items():
            contract = entry["measurement_contract"]
            assert contract["value"] is None, (
                f"apex_scalars.{name}: contract must not embed a value copy (drift)"
            )

    def test_thermodynamic_closed_set(self, health_payloads) -> None:
        thermo = health_payloads["health"]["thermodynamic"]
        contracts = thermo["measurement_contract"]
        for name in ALLOWLIST_THERMODYNAMIC:
            _assert_valid_contract(contracts.get(name), f"thermodynamic.{name}")
        # every numeric leaf classified
        numeric = {
            k for k, v in thermo.items() if isinstance(v, (int, float)) and not isinstance(v, bool)
        }
        unclassified = numeric - ALLOWLIST_THERMODYNAMIC - ROSTER_THERMODYNAMIC
        assert not unclassified, f"unclassified numeric thermodynamic leaves {sorted(unclassified)}"

    def test_governance_closed_set(self, health_payloads) -> None:
        gov = health_payloads["health"]["governance"]
        contracts = gov["measurement_contract"]
        for name in ALLOWLIST_GOVERNANCE:
            _assert_valid_contract(contracts.get(name), f"governance.{name}")
        numeric = {
            k for k, v in gov.items() if isinstance(v, (int, float)) and not isinstance(v, bool)
        }
        unclassified = numeric - ALLOWLIST_GOVERNANCE
        assert not unclassified, f"unclassified numeric governance leaves {sorted(unclassified)}"
        assert contracts["tau_confidence_system"]["decision_eligibility"] == "NONE"
        assert contracts["tau_threshold_f2"]["decision_eligibility"] == "NONE"

    def test_metrics_json_closed_set(self, health_payloads) -> None:
        metrics = health_payloads["metrics"]
        contracts = metrics["measurement_contract"]
        for name in ALLOWLIST_METRICS_JSON:
            _assert_valid_contract(contracts.get(name), f"/metrics/json.{name}")
        numeric = {
            k for k, v in metrics.items() if isinstance(v, (int, float)) and not isinstance(v, bool)
        }
        unclassified = numeric - ALLOWLIST_METRICS_JSON - ROSTER_METRICS_JSON
        assert not unclassified, f"unclassified numeric /metrics/json leaves {sorted(unclassified)}"

    def test_live_all_vitals_and_governance_closed_set(self, health_payloads) -> None:
        live = health_payloads["live_all"]
        vitals = live["vitals"]
        for name in ALLOWLIST_LIVE_VITALS:
            _assert_valid_contract(
                vitals["measurement_contract"].get(name), f"/api/live/all.vitals.{name}"
            )
        numeric_v = {
            k for k, v in vitals.items() if isinstance(v, (int, float)) and not isinstance(v, bool)
        }
        assert not (numeric_v - ALLOWLIST_LIVE_VITALS), (
            f"unclassified numeric vitals leaves {sorted(numeric_v - ALLOWLIST_LIVE_VITALS)}"
        )
        gov = live["governance"]
        for name in ALLOWLIST_LIVE_GOVERNANCE:
            _assert_valid_contract(
                gov["measurement_contract"].get(name),
                f"/api/live/all.governance.{name}",
            )
        numeric_g = {
            k for k, v in gov.items() if isinstance(v, (int, float)) and not isinstance(v, bool)
        }
        assert not (numeric_g - ALLOWLIST_LIVE_GOVERNANCE - ROSTER_LIVE_GOVERNANCE), (
            f"unclassified numeric live-governance leaves "
            f"{sorted(numeric_g - ALLOWLIST_LIVE_GOVERNANCE - ROSTER_LIVE_GOVERNANCE)}"
        )

    @staticmethod
    def _numeric_leaves(node: Any, prefix: str = "") -> list[str]:
        out: list[str] = []
        if isinstance(node, dict):
            for k, v in node.items():
                out.extend(TestP5AClosedSet._numeric_leaves(v, f"{prefix}.{k}" if prefix else k))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                out.extend(TestP5AClosedSet._numeric_leaves(v, f"{prefix}[{i}]"))
        elif isinstance(node, (int, float)) and not isinstance(node, bool):
            out.append(prefix)
        return out

    def test_measurement_basis_fully_rostered(self, health_payloads) -> None:
        """Every numeric leaf in measurement_basis is named debt, or scan fails."""
        basis = health_payloads["health"]["measurement_basis"]
        for leaf_path in self._numeric_leaves(basis):
            top = leaf_path.split(".")[0]
            assert (
                top in ROSTER_MEASUREMENT_BASIS
                or top in ROSTER_MEASUREMENT_BASIS_BLOCKS
                or leaf_path in ROSTER_MEASUREMENT_BASIS
            ), (
                f"measurement_basis leaf '{leaf_path}' is numeric but not in the "
                f"out-of-scope roster — classify it (contract or named debt)"
            )

    def test_eureka_margin_fully_rostered(self, health_payloads) -> None:
        """eureka_margin has no authorized producer site in VD-888 scope — every
        numeric leaf is named debt; a new leaf must be classified explicitly."""
        em = health_payloads["health"]["eureka_margin"]
        for leaf_path in self._numeric_leaves(em):
            top = leaf_path.split(".")[0].split("[")[0]
            assert top in ROSTER_EUREKA_MARGIN, (
                f"eureka_margin leaf '{leaf_path}' numeric and unrostered — "
                f"classify it (no authorized contract site; named debt per A8)"
            )

    def test_omega_0_value_is_immutable_on_wire(self) -> None:
        """Rollback trigger (5): omega_0 != 0.04 on the wire is a STOP."""
        from arifosmcp.runtime.megaTools.tool_01_init_anchor import init_anchor

        result = Any
        import asyncio

        result = asyncio.run(init_anchor(actor_id="kx010-omega-probe"))
        godel = result.payload["godel_lock"]
        assert godel["omega_0"] == 0.04, "omega_0 value changed — prohibited"


# ── P3 producer-wire assertions (floors) ─────────────────────────────────────


class TestP3FloorProducerContracts:
    def test_every_producer_floor_carries_unit_and_falsifier(self) -> None:
        for fid in _PRODUCERS:
            signal = collect_floor_producer_signal(fid, sources={})
            assert signal.get("unit") == "1", f"{fid}: unit label missing on producer wire"
            falsifier = signal.get("falsification_test")
            assert isinstance(falsifier, str) and falsifier, (
                f"{fid}: falsification_test missing on producer wire"
            )

    def test_no_producer_floors_carry_default_falsifier(self) -> None:
        for fid in ("F3", "F4", "F9"):
            signal = collect_floor_producer_signal(fid)
            assert signal["status"] == "UNMEASURED"
            assert signal.get("unit") == "1", f"{fid}: unit label missing"
            assert signal.get("falsification_test"), f"{fid}: falsifier missing"

    def test_a6_labels_fire_on_f3_f4_f5_f9(self) -> None:
        """a6_ruling condition 1: labels must actually fire and be asserted."""
        for fid in ("F3", "F4", "F5", "F9"):
            signal = collect_floor_producer_signal(fid)
            assert signal.get("decision_eligibility") == "NONE", (
                f"{fid}: A6 label decision_eligibility must be NONE"
            )
            contradiction = signal.get("known_contradiction", "")
            assert "KX-011" in str(contradiction), f"{fid}: A6 known_contradiction must name KX-011"

    def test_f8_falsifier_is_the_register_test(self) -> None:
        signal = collect_floor_producer_signal("F8", sources={})
        assert (
            signal["falsification_test"]
            == "contradiction_register.json contains zero active entries"
        )

    def test_labels_never_touch_status_math(self) -> None:
        """A6 condition 2: producer status/score semantics unchanged — an empty
        source bundle must still yield UNMEASURED (never PASS) for every floor."""
        for fid in _PRODUCERS:
            signal = collect_floor_producer_signal(fid, sources={})
            assert signal["status"] in ("UNMEASURED", "ERROR", "STALE"), (
                f"{fid}: empty sources produced status={signal['status']} — "
                f"labels must not change gate semantics"
            )


# ── P5(b) + A3: fail-closed resolution (test-side mirror of the TS guard) ────


def _resolve_decision_eligibility(
    replica: dict[str, Any],
    now: datetime | None = None,
    max_age_seconds: int = DEFAULT_MAX_AGE_SECONDS,
) -> str:
    """Mirror of A-FORGE resolveDecisionEligibility (see module docstring).

    Fail-closed: missing contract, missing field, expired valid_until, stale
    observed_at, out-of-expected_range, or a null declared composite component
    all resolve NONE — HOLD, not zero.
    """
    contract = replica.get("measurement_contract")
    if not isinstance(contract, dict):
        return "NONE"  # LEGACY_UNCONTRACTED
    declared = contract.get("decision_eligibility")
    if not isinstance(declared, str) or declared == "NONE":
        return "NONE"
    now = now or datetime.now(timezone.utc)
    valid_until = contract.get("valid_until")
    if isinstance(valid_until, str):
        until = datetime.fromisoformat(valid_until.replace("Z", "+00:00"))
        if now > until:
            return "NONE"
    observed_at = contract.get("observed_at")
    if isinstance(observed_at, str):
        at = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
        if (now - at).total_seconds() > max_age_seconds:
            return "NONE"
    expected_range = contract.get("expected_range")
    if (
        isinstance(expected_range, (list, tuple))
        and len(expected_range) == 2
        and all(isinstance(x, (int, float)) for x in expected_range)
    ):
        lo, hi = expected_range
        value = replica.get("value")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if value < lo or value > hi:
                return "NONE"
    components = contract.get("components")
    if isinstance(components, (list, tuple)) and components:
        present = contract.get("components_present")
        if not isinstance(present, dict):
            return "NONE"
        for name in components:
            if present.get(name) is None:
                return "NONE"
    return declared


def _replica(value: float = 0.5, contract: dict[str, Any] | None = None) -> dict[str, Any]:
    replica: dict[str, Any] = {
        "value": value,
        "status": "REPLICATED",
        "source": "arifos.health",
        "replicated_at": "2026-10-27T00:00:00Z",
    }
    if contract is not None:
        replica["measurement_contract"] = contract
    return replica


class TestP5BFailClosed:
    def test_synthetic_uncontracted_scalar_is_none(self) -> None:
        assert _resolve_decision_eligibility(_replica(0.42)) == "NONE"

    def test_uncontracted_never_renders_zero_or_pass(self) -> None:
        replica = _replica(0.99)
        replica["legacy"] = "LEGACY_UNCONTRACTED"
        eligibility = _resolve_decision_eligibility(replica)
        assert eligibility == "NONE"
        assert eligibility != "0" and replica["value"] != 0


class TestA3Negatives:
    def test_expired_valid_until_is_none(self) -> None:
        expired = (
            (datetime.now(timezone.utc) - timedelta(days=1)).isoformat().replace("+00:00", "Z")
        )
        replica = _replica(contract={"decision_eligibility": "ADVISORY", "valid_until": expired})
        assert _resolve_decision_eligibility(replica) == "NONE"

    def test_out_of_expected_range_is_none(self) -> None:
        replica = _replica(
            value=0.9,
            contract={"decision_eligibility": "ADVISORY", "expected_range": [0.0, 0.5]},
        )
        assert _resolve_decision_eligibility(replica) == "NONE"

    def test_in_range_keeps_declared_eligibility(self) -> None:
        replica = _replica(
            value=0.3,
            contract={"decision_eligibility": "ADVISORY", "expected_range": [0.0, 0.5]},
        )
        assert _resolve_decision_eligibility(replica) == "ADVISORY"

    def test_stale_observed_at_uses_declared_default_max_age(self) -> None:
        stale = (
            (datetime.now(timezone.utc) - timedelta(seconds=DEFAULT_MAX_AGE_SECONDS + 1))
            .isoformat()
            .replace("+00:00", "Z")
        )
        replica = _replica(contract={"decision_eligibility": "ADVISORY", "observed_at": stale})
        assert _resolve_decision_eligibility(replica) == "NONE"

    def test_fresh_observed_at_within_max_age_passes(self) -> None:
        fresh = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        replica = _replica(contract={"decision_eligibility": "ADVISORY", "observed_at": fresh})
        assert _resolve_decision_eligibility(replica) == "ADVISORY"

    def test_null_composite_component_is_none(self) -> None:
        replica = _replica(
            contract={
                "decision_eligibility": "ADVISORY",
                "components": ["human", "ai", "earth"],
                "components_present": {"human": 0.6, "ai": 0.7, "earth": None},
            }
        )
        assert _resolve_decision_eligibility(replica) == "NONE"

    def test_cross_unit_arithmetic_rejected(self) -> None:
        """A3(iii): cross-unit combination must be rejected, not coerced."""

        def unit_of(replica: dict[str, Any]) -> str | None:
            contract = replica.get("measurement_contract") or {}
            unit = contract.get("unit")
            return unit if isinstance(unit, str) and unit else None

        def assert_same_unit(a: dict[str, Any], b: dict[str, Any]) -> None:
            ua, ub = unit_of(a), unit_of(b)
            if ua is None or ub is None:
                raise AssertionError("KX010_UNIT_UNPROVABLE")
            if ua != ub:
                raise AssertionError(f"KX010_UNIT_MISMATCH: {ua} vs {ub}")

        ratio = _replica(contract={"decision_eligibility": "ADVISORY", "unit": "ratio"})
        one = _replica(contract={"decision_eligibility": "ADVISORY", "unit": "1"})
        legacy = _replica()  # no contract
        with pytest.raises(AssertionError, match="UNIT_MISMATCH"):
            assert_same_unit(ratio, one)
        with pytest.raises(AssertionError, match="UNIT_UNPROVABLE"):
            assert_same_unit(one, legacy)
        assert_same_unit(one, one)  # same-unit combination allowed

    def test_scope_mismatch_is_none_and_rejected(self) -> None:
        """A3(v): a named-scope read needs an exactly matching declared scope."""

        def assert_scope_allows(replica: dict[str, Any], required: str) -> None:
            contract = replica.get("measurement_contract") or {}
            scope = contract.get("scope")
            if not isinstance(scope, str) or not scope:
                raise AssertionError("KX010_SCOPE_UNDECLARED")
            if scope != required:
                raise AssertionError(f"KX010_SCOPE_MISMATCH: {scope} != {required}")

        g_auth = _replica(
            contract={
                "decision_eligibility": "NONE",
                "unit": "1",
                "scope": "g_authorization",
            }
        )
        unscoped = _replica(contract={"decision_eligibility": "ADVISORY", "unit": "1"})
        with pytest.raises(AssertionError, match="SCOPE_MISMATCH"):
            assert_scope_allows(g_auth, "g_task_verdict")
        with pytest.raises(AssertionError, match="SCOPE_UNDECLARED"):
            assert_scope_allows(unscoped, "g_authorization")
        # the A6 case: g_authorization consumption resolves NONE regardless
        assert _resolve_decision_eligibility(g_auth) == "NONE"


# ── P5(c): historical receipt JSON untouched ─────────────────────────────────


class TestP5CHistoricalReceipts:
    SEAL_CHAIN = "/root/.local/share/arifos/vault999/seal_chain.jsonl"

    @staticmethod
    def _snapshot(path: str) -> tuple[int, str] | None:
        from pathlib import Path

        p = Path(path)
        if not p.exists():
            return None
        data = p.read_bytes()
        return len(data), hashlib.sha256(data).hexdigest()

    def test_build_paths_do_not_touch_sealed_receipts(self, health_payloads) -> None:
        """P5(c): building health payloads and producer signals must not write
        history (side-effect-on-read tripwire)."""
        before = self._snapshot(self.SEAL_CHAIN)
        # more reads through the patched paths
        collect_floor_producer_signal("F8", sources={})
        collect_floor_producer_signal("F13", sources={})
        measurement_contract(
            "probe",
            semantic_class="HEURISTIC",
            unit="1",
            measurement_method="probe",
            monotonic_drivers=[],
            falsification_test="probe",
            provenance_class="SERVER_OBSERVED",
            calibration_status="PHASE_1_HEURISTIC_UNCALIBRATED",
            decision_eligibility="DISPLAY_ONLY",
            derivation_ref="test",
        )
        after = self._snapshot(self.SEAL_CHAIN)
        assert before == after, (
            f"sealed receipt file changed while only reading/building — {before} -> {after}"
        )

    def test_contract_schema_cannot_retro_promote_legacy(self) -> None:
        """No code path in this patch rewrites an existing receipt contract."""
        # The helper ALWAYS mints schema_version kx010.v1 with value=None —
        # there is no API to stamp a contract onto an old record.
        contract = measurement_contract(
            "legacy_probe",
            semantic_class="UNKNOWN",
            unit="1",
            measurement_method="probe",
            monotonic_drivers=[],
            falsification_test="probe",
            provenance_class="SERVER_OBSERVED",
            calibration_status="UNKNOWN",
            decision_eligibility="NONE",
            derivation_ref="test",
        )
        assert contract["schema_version"] == SCHEMA_VERSION
        assert contract["value"] is None


# ── P5(d): A-FORGE passthrough contract (fixture replication) ────────────────


def _aforge_extract_scalar(field: dict[str, Any]) -> dict[str, Any]:
    """Python fixture replicating GovernanceBridge.extractScalar (compiled TS).

    The REAL TS passthrough + guards were additionally probed against the
    compiled dist by the patch session (node dist probe) — this fixture pins
    the CONTRACT on the arifOS side so the wire shape cannot drift away from
    what the TS expects: measurement_contract verbatim, else LEGACY_UNCONTRACTED.
    """
    if not isinstance(field, dict) or not isinstance(field.get("value"), (int, float)):
        return {}
    replica: dict[str, Any] = {
        "value": field["value"],
        "status": "REPLICATED",
        "source": "arifos.health",
        "replicated_at": "fixture",
    }
    mc = field.get("measurement_contract")
    if isinstance(mc, dict) and not isinstance(mc, list):
        replica["measurement_contract"] = mc
    else:
        replica["legacy"] = "LEGACY_UNCONTRACTED"
    return replica


class TestP5DAForgePassthrough:
    def test_contracted_scalar_replicates_contract_verbatim(self, health_payloads) -> None:
        g = health_payloads["health"]["apex_scalars"]["G"]
        replica = _aforge_extract_scalar(g)
        assert replica["measurement_contract"] == g["measurement_contract"]
        assert "legacy" not in replica

    def test_uncontracted_scalar_surfaces_legacy(self) -> None:
        legacy_field = {"value": 0.6667, "status": "MEASURED"}
        replica = _aforge_extract_scalar(legacy_field)
        assert replica["legacy"] == "LEGACY_UNCONTRACTED"
        assert "measurement_contract" not in replica
        assert replica["value"] == 0.6667

    def test_unmeasured_scalar_replicates_as_null_entry(self) -> None:
        assert _aforge_extract_scalar({"value": None, "status": "UNMEASURED"}) == {}


# ── A4: MCP envelope path ────────────────────────────────────────────────────


class TestA4MCPEnvelope:
    def test_arif_init_omega_0_contract_present(self) -> None:
        import asyncio

        from arifosmcp.runtime.megaTools.tool_01_init_anchor import init_anchor

        result = asyncio.run(init_anchor(actor_id="kx010-a4-probe"))
        godel = result.payload["godel_lock"]
        contract = godel["measurement_contract"]
        _assert_valid_contract(contract, "arif_init.godel_lock.omega_0")
        assert contract["metric_name"] == "omega_0"
        assert contract["semantic_class"] == "POLICY_CONSTANT"
        assert contract["decision_eligibility"] == "DISPLAY_ONLY"
        assert contract["provenance_class"] == "POLICY_DERIVED"
        assert godel["omega_0"] == 0.04, "omega_0 value must stay 0.04"

    def test_envelope_numeric_without_contract_resolves_legacy_none(self) -> None:
        """Any arif_* envelope numeric that carries no contract (this patch
        authorizes none on the delta_S surface) must resolve NONE — never pass
        as if measured."""
        envelope_like = {"delta_s": 0.0}  # no measurement_contract key
        assert _resolve_decision_eligibility(envelope_like) == "NONE"


# ── Helper self-check ────────────────────────────────────────────────────────


class TestMeasurementContractHelper:
    def test_helper_emits_full_schema_field_set(self) -> None:
        contract = measurement_contract(
            "helper_check",
            semantic_class="OBSERVED",
            unit="1",
            measurement_method="direct",
            monotonic_drivers=["x"],
            falsification_test="recompute",
            provenance_class="SERVER_OBSERVED",
            calibration_status="CALIBRATED",
            decision_eligibility="DISPLAY_ONLY",
            derivation_ref="test",
        )
        _assert_valid_contract(contract, "helper")
        # 05 schema fields present
        for field in (
            "measurement_id",
            "semantic_class",
            "value",
            "unit",
            "dimension",
            "producer",
            "source_inputs",
            "derivation_ref",
            "observed_at",
            "valid_from",
            "valid_until",
            "scope",
            "population_or_system",
            "calibration_status",
            "calibration_ref",
            "uncertainty",
            "expected_range",
            "threshold_ref",
            "falsifier",
            "decision_eligibility",
            "provenance_class",
            "schema_version",
        ):
            assert field in contract, f"helper output lacks 05-schema field '{field}'"
        assert contract["value"] is None

    def test_unknown_semantic_class_still_declares(self) -> None:
        """The 05 fail_closed_rule: UNKNOWN class -> NONE is the caller's duty;
        the helper must faithfully carry whatever eligibility is passed."""
        contract = measurement_contract(
            "unknown_probe",
            semantic_class="UNKNOWN",
            unit="1",
            measurement_method="probe",
            monotonic_drivers=[],
            falsification_test="probe",
            provenance_class="SERVER_OBSERVED",
            calibration_status="UNKNOWN",
            decision_eligibility="NONE",
            derivation_ref="test",
        )
        assert contract["decision_eligibility"] == "NONE"
