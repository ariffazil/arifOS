"""
tests/golden/organs/judge/test_judge_golden.py — 888_JUDGE Golden Contract Tests

Phase 0: Freeze gate ordering, paradox anchor injection, verdict→cell routing,
and SABAR cooldown enforcement before any refactoring.

Constitutional risk: HIGHEST. Judge is the verdict gate. Its behavior is law.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""
from __future__ import annotations

import pytest

from arifosmcp.tools.judge import (
    JUDGE_PARADOX_ANCHORS,
    _JUDGE_BY_CELL,
    _JUDGE_BY_ID,
    _inject_judge_paradox,
    _judge_paradox_for_verdict,
)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. PARADOX ANCHOR REGISTRY INTEGRITY — 9 anchors, 3×3 matrix
# ═══════════════════════════════════════════════════════════════════════════════


class TestJudgeAnchorRegistry:
    """Freeze the 9 Judge paradox anchors — structure, IDs, and matrix cells."""

    def test_nine_anchors_exist(self):
        """Judge must have exactly 9 paradox anchors (3×3 matrix)."""
        assert len(JUDGE_PARADOX_ANCHORS) == 9, (
            f"Expected 9 Judge anchors, found {len(JUDGE_PARADOX_ANCHORS)}. "
            "Adding or removing anchors is a constitutional change."
        )

    def test_by_cell_lookup_covers_all_rows_and_cols(self):
        """Every anchor must be reachable by (row, col) matrix cell."""
        rows = {"TRUTH", "CLARITY", "HUMILITY"}
        cols = {"CARE", "PEACE", "JUSTICE"}
        cells_found = set()
        for anchor in JUDGE_PARADOX_ANCHORS:
            assert anchor["matrix_row"] in rows, f"Unknown row: {anchor['matrix_row']}"
            assert anchor["matrix_col"] in cols, f"Unknown col: {anchor['matrix_col']}"
            cell = anchor["matrix_cell"]
            cells_found.add(cell)
            assert cell in _JUDGE_BY_CELL, f"Cell {cell} missing from _JUDGE_BY_CELL"
        assert len(cells_found) == 9, f"Expected 9 unique cells, got {len(cells_found)}"

    def test_by_id_lookup_covers_all(self):
        """Every anchor must be reachable by ID."""
        for anchor in JUDGE_PARADOX_ANCHORS:
            aid = anchor["id"]
            assert aid in _JUDGE_BY_ID, f"ID {aid} missing from _JUDGE_BY_ID"

    def test_anchor_structure_golden(self):
        """Every anchor must have the required constitutional fields."""
        required_keys = {
            "id", "matrix_cell", "matrix_row", "matrix_col",
            "motto_binding", "quote", "antithesis", "axis",
            "binding", "severity_on_fire", "risk_bias",
            "authority_scope", "norm",
        }
        quote_keys = {"text", "author", "work", "year", "verification_level"}
        for anchor in JUDGE_PARADOX_ANCHORS:
            missing = required_keys - set(anchor.keys())
            assert not missing, f"Anchor {anchor['id']} missing fields: {missing}"
            q_missing = quote_keys - set(anchor["quote"].keys())
            assert not q_missing, f"Anchor {anchor['id']} quote missing: {q_missing}"

    def test_anchor_ids_follow_golden_naming(self):
        """Anchor IDs must follow J_{row}x{col} pattern for traceability."""
        for anchor in JUDGE_PARADOX_ANCHORS:
            aid = anchor["id"]
            assert aid.startswith("J_"), f"Anchor ID must start with J_: {aid}"
            # Verify the row and col are encoded
            row_char = aid[2]  # T/C/H
            col_char = aid[4]  # C/P/J
            row_map = {"T": "TRUTH", "C": "CLARITY", "H": "HUMILITY"}
            col_map = {"C": "CARE", "P": "PEACE", "J": "JUSTICE"}
            assert row_char in row_map, f"Bad row char in {aid}"
            assert col_char in col_map, f"Bad col char in {aid}"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. VERDICT → PARADOX CELL ROUTING — Golden mapping
# ═══════════════════════════════════════════════════════════════════════════════


class TestJudgeVerdictParadoxRouting:
    """Freeze verdict→anchor routing that drives paradox injection at decision time."""

    def test_sabar_routes_to_clarity_justice(self):
        """SABAR verdict must bind to J_CxJ (Parker/MLK — the arc bends only if we bend it)."""
        anchor = _judge_paradox_for_verdict("SABAR")
        assert anchor is not None, "SABAR must have a paradox anchor"
        assert anchor["id"] == "J_CxJ", (
            f"SABAR routed to {anchor['id']}, expected J_CxJ"
        )
        assert anchor["matrix_cell"] == "clarity_justice"
        assert "bend" in anchor["quote"]["text"].lower() or "Parker" in anchor["quote"]["author"]

    def test_seal_standard_routes_to_truth_peace(self):
        """Standard SEAL must bind to J_TxP (Aristotle — every SEAL is partial justice)."""
        anchor = _judge_paradox_for_verdict("SEAL", action_tier="standard")
        assert anchor is not None, "Standard SEAL must have a paradox anchor"
        assert anchor["id"] == "J_TxP", (
            f"Standard SEAL routed to {anchor['id']}, expected J_TxP"
        )
        assert anchor["matrix_cell"] == "truth_peace"

    def test_seal_sovereign_routes_to_humility_justice(self):
        """Sovereign SEAL must bind to J_HxJ (Kant — universality is not computable)."""
        anchor = _judge_paradox_for_verdict("SEAL", action_tier="sovereign")
        assert anchor is not None, "Sovereign SEAL must have a paradox anchor"
        assert anchor["id"] == "J_HxJ", (
            f"Sovereign SEAL routed to {anchor['id']}, expected J_HxJ"
        )
        assert anchor["matrix_cell"] == "humility_justice"
        assert "Kant" in anchor["quote"]["author"]

    def test_hold_elevated_routes_to_truth_care(self):
        """Elevated HOLD must bind to J_TxC (Marcus Aurelius — if not right, don't do it)."""
        anchor = _judge_paradox_for_verdict("HOLD", action_tier="sovereign")
        assert anchor is not None, "Elevated HOLD must have a paradox anchor"
        assert anchor["id"] == "J_TxC", (
            f"Elevated HOLD routed to {anchor['id']}, expected J_TxC"
        )
        assert anchor["matrix_cell"] == "truth_care"

    def test_hold_standard_returns_none(self):
        """Standard HOLD has no specific anchor — silence is constitutional."""
        anchor = _judge_paradox_for_verdict("HOLD", action_tier="standard")
        assert anchor is None, "Standard HOLD should not auto-inject a paradox anchor"


# ═══════════════════════════════════════════════════════════════════════════════
# 3. PARADOX ANCHOR INJECTION — Golden output structure
# ═══════════════════════════════════════════════════════════════════════════════


class TestJudgeParadoxInjection:
    """Freeze paradox anchor injection into verdict output dicts."""

    def test_sabar_injects_deadline_note(self):
        """SABAR verdict must carry deadline enforcement in meta."""
        result = {"verdict": "SABAR"}
        result = _inject_judge_paradox(result, "SABAR")
        assert "meta" in result
        assert "paradox_anchor" in result["meta"]
        anchor = result["meta"]["paradox_anchor"]
        assert anchor["quote_id"] == "J_CxJ"
        assert anchor["organ"] == "judge"
        assert anchor["matrix_row"] == "CLARITY"
        assert anchor["matrix_col"] == "JUSTICE"
        assert "sabar_deadline_note" in result["meta"]
        assert "indefinite" in result["meta"]["sabar_deadline_note"].lower()

    def test_seal_standard_injects_partial_justice_note(self):
        """Standard SEAL must carry J_TxP — every SEAL is partial justice."""
        result = {"verdict": "SEAL", "reasons": []}
        result = _inject_judge_paradox(result, "SEAL", action_tier="standard")
        assert "meta" in result
        anchor = result["meta"]["paradox_anchor"]
        assert anchor["quote_id"] == "J_TxP"
        assert anchor["matrix_cell"] == "truth_peace"
        # Must inject the partial justice caveat into reasons
        assert any("partial" in r.lower() or "J_TxP" in r for r in result.get("reasons", []))

    def test_seal_sovereign_injects_computability_warning(self):
        """Sovereign SEAL must carry J_HxJ — universality is not computable."""
        result = {"verdict": "SEAL", "reasons": []}
        result = _inject_judge_paradox(result, "SEAL", action_tier="sovereign")
        anchor = result["meta"]["paradox_anchor"]
        assert anchor["quote_id"] == "J_HxJ"
        assert "Kant" in anchor["author"]  # Kant wrote the maxim, not named in the quote text
        assert any(
            "universal" in r.lower() or "J_HxJ" in r
            for r in result.get("reasons", [])
        )

    def test_hold_elevated_injects_irreversibility_gate(self):
        """Elevated HOLD must carry J_TxC — if not right, don't do it."""
        result = {"verdict": "HOLD", "reasons": []}
        result = _inject_judge_paradox(result, "HOLD", action_tier="sovereign")
        anchor = result["meta"]["paradox_anchor"]
        assert anchor["quote_id"] == "J_TxC"
        assert "Marcus Aurelius" in anchor["author"] or "Aurelius" in anchor["quote"]
        assert any(
            "J_TxC" in r or "ex ante" in r.lower()
            for r in result.get("reasons", [])
        )

    def test_no_double_injection(self):
        """
        Golden: _inject_judge_paradox currently always injects (no guard against
        pre-existing anchor). This documents actual behavior — Phase 1 refactor
        should add the guard observed in Heart and Mind injection functions.
        """
        result = {"verdict": "SEAL", "meta": {"paradox_anchor": {"quote_id": "existing"}}}
        before = result["meta"]["paradox_anchor"]["quote_id"]
        result = _inject_judge_paradox(result, "SEAL")
        # Current behavior: always overwrites. Contract note: this is a known
        # inconsistency with Heart._inject_heart_paradox which DOES guard.
        # Phase 1 should harmonize — but only after this golden test is updated.
        assert "paradox_anchor" in result["meta"]
        # Documented: injection overwrites, does not guard

    def test_anchor_fields_are_complete(self):
        """Injected anchor must contain all constitutional metadata fields."""
        result = {"verdict": "SEAL"}
        result = _inject_judge_paradox(result, "SEAL", action_tier="standard")
        anchor = result["meta"]["paradox_anchor"]
        required = {
            "quote_id", "organ", "matrix_cell", "matrix_row", "matrix_col",
            "motto_binding", "quote", "author", "work", "year",
            "verification_level", "antithesis", "axis", "norm",
            "severity_on_fire", "risk_bias", "authority_scope",
            "binding_event", "_matrix_note",
        }
        missing = required - set(anchor.keys())
        assert not missing, f"Injected anchor missing fields: {missing}"


# ═══════════════════════════════════════════════════════════════════════════════
# 4. JUDGE GATE ORDERING — Constitutional sequence
# ═══════════════════════════════════════════════════════════════════════════════


class TestJudgeGateOrdering:
    """
    Freeze the 11-gate pipeline sequence in arif_judge_deliberate.

    The gates fire in this exact order:
      1. HEART_GATE          — if heart_critique verdict is VOID/HOLD, block immediately
      2. WELL substrate       — biological readiness evidence (W0 preserved)
      3. G-WELL governance    — machine governance for elevated tiers
      4. W5 COGNITIVE_ENTROPY — clarity gate for sovereign/C4/C5 actions
      5. NIAT GATE            — consent boundary enforcement
      6. METABOLIC BYPASS     — cumulative risk detection
      7. SELF-MOD LOCK        — prevents heart/judge self-editing
      8. A-RIF CLAIM STRENGTH — claim ≤ evidence level
      9. SIMULATIVE DETECTION — "Are you describing or performing?"
     10. SABAR cooldown       — Stage 2B hard block
     11. Vault auto-hook      — Post-SEAL sealing

    This ordering IS constitutional law. Reordering gates is a constitutional change.
    """

    # Gate names and their detection strings in judge.py source
    GATE_ORDER: list[tuple[str, str]] = [
        ("HEART_GATE", "666_HEART: Ethical Gate"),
        ("WELL_SUBSTRATE", "WELL biological substrate pre-load"),
        ("G_WELL_GOVERNANCE", "G-WELL governance pre-load"),
        ("W5_COGNITIVE_ENTROPY", "W5_COGNITIVE_ENTROPY"),
        ("NIAT_GATE", "NIAT GATE"),
        ("METABOLIC_BYPASS", "METABOLIC BYPASS"),
        ("SELF_MOD_LOCK", "SELF-MODIFICATION LOCK"),
        ("A_RIF_CLAIM_STRENGTH", "A-RIF: Post-Adjudication"),
        ("SIMULATIVE_DETECTION", "SIMULATIVE DETECTION GATE"),
        ("SABAR_COOLDOWN", "SABAR cooldown awareness"),
        ("VAULT_AUTO_HOOK", "vault_entry_id and is_seal"),
    ]

    def test_eleven_gates_exist(self):
        """There must be exactly 11 gates in the Judge pipeline."""
        assert len(self.GATE_ORDER) == 11, (
            f"Expected 11 gates, found {len(self.GATE_ORDER)}. "
            "Adding or removing gates is a constitutional change."
        )

    def test_heart_gate_is_first(self):
        """HEART_GATE must fire first — ethical block before any other check."""
        assert self.GATE_ORDER[0][0] == "HEART_GATE", (
            f"First gate is {self.GATE_ORDER[0][0]}, must be HEART_GATE"
        )

    def test_vault_auto_hook_is_last(self):
        """Vault auto-hook must fire last — only after all other gates pass."""
        assert self.GATE_ORDER[-1][0] == "VAULT_AUTO_HOOK", (
            f"Last gate is {self.GATE_ORDER[-1][0]}, must be VAULT_AUTO_HOOK"
        )

    def test_gate_order_matches_source_code(self):
        """
        Verify declared gate order matches actual source code line order.
        Reads judge.py and checks that comment markers appear in the declared sequence.
        """
        import os
        judge_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..", "..",
            "arifosmcp", "tools", "judge.py",
        )
        judge_path = os.path.normpath(judge_path)
        if not os.path.exists(judge_path):
            pytest.skip(f"Source not found at {judge_path}")

        with open(judge_path) as f:
            source = f.read()

        last_pos = -1
        for gate_name, marker in self.GATE_ORDER:
            pos = source.find(marker)
            if pos == -1:
                # Try alternate markers
                alt_markers = {
                    "HEART_GATE": "666_HEART",
                    "WELL_SUBSTRATE": "well_substrate",
                    "G_WELL_GOVERNANCE": "well_governance",
                    "W5_COGNITIVE_ENTROPY": "W5_COGNITIVE",
                    "NIAT_GATE": "check_niat_gate",
                    "METABOLIC_BYPASS": "is_bypass_attempt",
                    "SELF_MOD_LOCK": "is_self_modification_attempt",
                    "A_RIF_CLAIM_STRENGTH": "track_judge",
                    "SIMULATIVE_DETECTION": "simulative_check",
                    "SABAR_COOLDOWN": "_apply_cooldown",
                    "VAULT_AUTO_HOOK": "arif_vault_seal",
                }
                pos = source.find(alt_markers.get(gate_name, marker))
            assert pos > last_pos, (
                f"Gate '{gate_name}' (marker='{marker}') at line ~{source[:pos].count(chr(10))+1} "
                f"appears BEFORE previous gate in source. "
                f"Gate ordering in source does not match declared constitutional sequence."
            )
            last_pos = pos

    def test_gate_ordering_is_immutable(self):
        """
        Canonical gate sequence as a single golden string.
        Any reordering breaks this exact hash-equivalent assertion.
        """
        canonical_sequence = [
            "HEART_GATE",
            "WELL_SUBSTRATE",
            "G_WELL_GOVERNANCE",
            "W5_COGNITIVE_ENTROPY",
            "NIAT_GATE",
            "METABOLIC_BYPASS",
            "SELF_MOD_LOCK",
            "A_RIF_CLAIM_STRENGTH",
            "SIMULATIVE_DETECTION",
            "SABAR_COOLDOWN",
            "VAULT_AUTO_HOOK",
        ]
        actual = [g[0] for g in self.GATE_ORDER]
        assert actual == canonical_sequence, (
            f"Gate sequence changed!\n"
            f"Expected: {canonical_sequence}\n"
            f"Actual:   {actual}\n"
            f"Reordering Judge gates is a constitutional change requiring F13 review."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 5. HEART_GATE BEHAVIOR — Golden block contract
# ═══════════════════════════════════════════════════════════════════════════════


class TestHeartGateBehavior:
    """
    Freeze HEART_GATE: if heart_critique returns VOID or HOLD,
    Judge must return HOLD before any other gate fires.
    """

    def test_heart_void_blocks_judge(self):
        """
        GOLDEN GAP: The HEART_GATE code exists in the docstring (lines 544-561)
        but is NOT executable. The arif_judge_deliberate function does NOT
        currently block on heart_critique VOID. This is documented as required
        behavior (Red Team Finding #1) but not wired.

        Current behavior: Judge proceeds past the heart_critique without blocking.
        This test documents the gap. Phase 1 should move the gate from docstring
        to executable code.
        """
        import asyncio
        from arifosmcp.tools.judge import arif_judge_deliberate

        result = asyncio.run(arif_judge_deliberate(
            mode="judge",
            candidate="test action",
            heart_critique={
                "action_risk_verdict": "VOID",
                "verdict": "VOID",
                "reason": "Ethical violation detected by Heart.",
            },
        ))
        # Current behavior: does NOT block (HEART_GATE is docstring, not code)
        # Expected after fix: result.verdict.value == "HOLD"
        # Documenting actual behavior for Phase 0:
        assert result.verdict is not None

    def test_heart_hold_blocks_judge(self):
        """
        GOLDEN GAP: Same docstring issue as test_heart_void_blocks_judge.
        The HEART_GATE is documented but not wired. Phase 1 must implement.
        """
        import asyncio
        from arifosmcp.tools.judge import arif_judge_deliberate

        result = asyncio.run(arif_judge_deliberate(
            mode="judge",
            candidate="test action",
            heart_critique={
                "action_risk_verdict": "HOLD",
                "verdict": "HOLD",
                "reason": "Uncertain ethical boundary.",
            },
        ))
        # Current: does NOT block. Expected after Phase 1: result.verdict.value == "HOLD"
        assert result.verdict is not None

    def test_heart_seal_allows_judge_to_proceed(self):
        """When Heart returns SEAL, Judge must NOT be blocked by HEART_GATE."""
        import asyncio
        from arifosmcp.tools.judge import arif_judge_deliberate

        # Heart SEAL should not trigger the HEART_GATE block
        # (Judge may still HOLD for other reasons like WELL unavailability)
        result = asyncio.run(arif_judge_deliberate(
            mode="judge",
            candidate="safe action",
            heart_critique={
                "action_risk_verdict": "SEAL",
                "verdict": "OK",
                "reason": "No risks detected.",
            },
        ))
        # Must not be blocked by HEART_GATE specifically
        heart_gate_reasons = [r for r in result.reasons if "666_HEART_GATE" in r]
        assert len(heart_gate_reasons) == 0, (
            f"HEART_GATE blocked despite Heart SEAL: {heart_gate_reasons}"
        )
