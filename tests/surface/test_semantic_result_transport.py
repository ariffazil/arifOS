"""Regression test for semantic result transport + action_class extension.

Audit finding (GPT-5.6 external probe, 2026-07-27):
  - arif_observe / arif_think / arif_route returned only the control-plane
    envelope (status, tool, verdict, actor, session_id, call_hash, trace_id,
    session_token, audit_provenance, next_safe_action) — never the actual
    semantic payload (facts, inferences, confidence, etc.).
  - Root cause: trim_for_verbosity(verbosity='minimal') (the MCP default) was
    stripping the semantic fields via _MINIMAL_STRIP_FIELDS and constructing
    a fresh minimal dict without re-adding them.
  - Metabolic utility score: 39/100.

  - arif_judge rejected action_class='AUDIT_RECORD' as "unrecognized reversibility
    class". AUDIT_RECORD is a legacy observability alias that maps to OBSERVE
    but was not in canonical ActionClass nor in the arif_lease_issue whitelist.

Fix (2026-07-27):
  - verbosity.py: semantic fields (facts, inferences, recommendations,
    unknowns, do_not_conclude, confidence, metacognition, constitutional_check,
    risk) are now PRESERVED in minimal mode. Stripped fields reduced to
    actually-verbose metadata (work_contract, atlas333_boot, clarity_metrics).
  - federation_envelope.py: ActionClass.AUDIT_RECORD and ActionClass.READ
    added as aliases (both resolve to OBSERVE).
  - tools.py: arif_lease_issue valid_action_classes tuple now accepts
    AUDIT_RECORD, READ, ANALYZE, DRAFT, SIMULATE.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import pytest

# Fields that MUST survive the minimal verbosity trim
SEMANTIC_PRESERVED_FIELDS = (
    "facts",
    "inferences",
    "recommendations",
    "unknowns",
    "do_not_conclude",
    "confidence",
    "metacognition",
    "constitutional_check",
    "risk",
)

# Fields that may legitimately be stripped (verbose metadata only)
VERBOSE_STRIPPABLE_FIELDS = (
    "work_contract",
    "atlas333_boot",
    "clarity_metrics",
    "clarity_contract",
    "session_birth",
)


class TestVerbosityMinimalPreservesSemantic:
    """`minimal` verbosity must NOT drop the kernel's semantic payload."""

    def _make_response(self) -> dict:
        return {
            "status": "OK",
            "tool": "arif_observe",
            "verdict": "SEAL",
            "session_id": "probe-1",
            "actor_id": "arif",
            "actor_verified": False,
            "call_hash": "sha256:abc",
            "trace_id": "trc-1",
            "signature": None,
            "session_token": "act_v1.eyJhY3RvciI6ImFyaWYifQ==",
            "facts": ["observation 1", "observation 2"],
            "inferences": [{"claim": "verdict=SEAL", "confidence": 0.85, "basis": "kernel floors"}],
            "recommendations": [{"action": "continue"}],
            "unknowns": ["uncertainty about X"],
            "do_not_conclude": ["do not assert Y"],
            "confidence": 0.85,
            "metacognition": {"observation_count": 2},
            "constitutional_check": {"F1": "pass"},
            "risk": {"level": "low"},
            "next_safe_action": {"action": "continue"},
            # Verbose fields that SHOULD be stripped:
            "work_contract": "verbose payload",
            "atlas333_boot": "verbose payload",
            "clarity_metrics": "verbose payload",
        }

    def test_semantic_fields_preserved(self):
        from arifosmcp.runtime.verbosity import trim_for_verbosity
        response = self._make_response()
        trimmed = trim_for_verbosity(response, "minimal")

        for field in SEMANTIC_PRESERVED_FIELDS:
            assert field in trimmed, (
                f"semantic field {field!r} was dropped by minimal trim — "
                f"audit 2026-07-27 regression"
            )
            # value should be non-empty
            assert trimmed[field], f"semantic field {field!r} is empty"

    def test_control_plane_fields_preserved(self):
        from arifosmcp.runtime.verbosity import trim_for_verbosity
        response = self._make_response()
        trimmed = trim_for_verbosity(response, "minimal")

        for field in ("status", "tool", "verdict", "session_id", "call_hash", "trace_id"):
            assert field in trimmed, (
                f"control-plane field {field!r} was dropped by minimal trim"
            )

    def test_f11_safety_net_still_active(self):
        """If required F11 fields are missing, trim returns untrimmed response."""
        from arifosmcp.runtime.verbosity import trim_for_verbosity
        bad = {"status": "OK", "tool": "x", "facts": ["only semantic"]}  # no call_hash, session_id, etc.
        out = trim_for_verbosity(bad, "minimal")
        # should fall back to returning the response unchanged
        assert out == bad, "F11 safety net broken — minimal returned trimmed without audit fields"

    def test_verbose_metadata_stripped(self):
        from arifosmcp.runtime.verbosity import trim_for_verbosity
        response = self._make_response()
        trimmed = trim_for_verbosity(response, "minimal")

        for field in VERBOSE_STRIPPABLE_FIELDS:
            if field in trimmed and trimmed[field] == "verbose payload":
                # If the field is still present, it should NOT be the verbose stub
                pytest.fail(
                    f"verbose metadata field {field!r} not stripped — minimal should drop these"
                )

    def test_standard_and_full_unaffected(self):
        from arifosmcp.runtime.verbosity import trim_for_verbosity
        response = self._make_response()
        for level in ("standard", "full"):
            trimmed = trim_for_verbosity(response, level)
            assert trimmed == response, f"{level} verbosity must return unchanged response"


class TestActionClassAliases:
    """Granular audit aliases must resolve to distinct reversibility classes.

    Audit 2026-07-28 B2 correction: the prior blanket AUDIT_RECORD=OBSERVE
    alias conflated audit-reads (no mutation) with audit-appends (mutation)
    and audit-seals (immutable). The canonical ActionClass now exposes
    granular aliases that map to distinct reversibility classes.

    Mapping per auditor's table:
      - AUDIT_RECORD_READ       → OBSERVE        (read history, no state change)
      - AUDIT_RECORD_APPEND     → MUTATE         (reversible audit append)
      - AUDIT_SEAL              → IRREVERSIBLE   (immutable audit seal)
      - AUDIT_RECORD (legacy)   → OBSERVE        (kept for backward compat — read semantics)
      - READ (generic)          → OBSERVE        (no state change)
    """

    def test_audit_record_read_resolves_to_observe(self):
        from arifosmcp.schemas.federation_envelope import ActionClass
        assert ActionClass.AUDIT_RECORD_READ.value == "OBSERVE"

    def test_audit_record_append_resolves_to_mutate(self):
        from arifosmcp.schemas.federation_envelope import ActionClass
        assert ActionClass.AUDIT_RECORD_APPEND.value == "MUTATE"

    def test_audit_seal_resolves_to_irreversible(self):
        from arifosmcp.schemas.federation_envelope import ActionClass
        assert ActionClass.AUDIT_SEAL.value == "IRREVERSIBLE"

    def test_read_resolves_to_observe(self):
        from arifosmcp.schemas.federation_envelope import ActionClass
        assert ActionClass.READ.value == "OBSERVE"

    def test_legacy_audit_record_kept_for_backward_compat(self):
        from arifosmcp.schemas.federation_envelope import ActionClass
        # Legacy AUDIT_RECORD = "OBSERVE" — kept so existing callers don't break.
        assert ActionClass.AUDIT_RECORD.value == "OBSERVE"

    def test_canonical_classes_intact(self):
        from arifosmcp.schemas.federation_envelope import ActionClass
        canonical = {
            "OBSERVE",
            "ANALYZE",
            "DRAFT",
            "SIMULATE",
            "MUTATE",
            "EXTERNAL_SIDE_EFFECT",
            "IRREVERSIBLE",
            "UNKNOWN",
        }
        actual = {m.value for m in ActionClass}
        assert canonical.issubset(actual), (
            f"canonical classes missing: {canonical - actual}"
        )


class TestDryRunDowngrade:
    """Audit 2026-07-28 B3: dry_run must downgrade IRREVERSIBLE tools to OBSERVE."""

    def test_arif_forge_dry_run_is_observe(self):
        from arifosmcp.core.enforcement.risk_classifier import classify_tool
        passport = classify_tool('arif_forge', mode='dry_run')
        assert passport.action_class.value == 'OBSERVE'

    def test_arif_seal_verify_is_observe(self):
        from arifosmcp.core.enforcement.risk_classifier import classify_tool
        passport = classify_tool('arif_seal', mode='verify')
        assert passport.action_class.value == 'OBSERVE'

    def test_arif_forge_compose_is_irreversible(self):
        """Without dry_run, arif_forge is IRREVERSIBLE as expected."""
        from arifosmcp.core.enforcement.risk_classifier import classify_tool
        passport = classify_tool('arif_forge', mode='compose')
        assert passport.action_class.value in ('IRREVERSIBLE', 'ATOMIC')


class TestLeaseIssueActionClasses:
    """arif_lease_issue valid_action_classes whitelist must accept the new aliases.

    The whitelist is a local variable inside the lease_issue handler, so we
    grep the source code for the literal class names rather than importing them.
    """

    @pytest.fixture
    def tools_source(self) -> str:
        from pathlib import Path

        root = Path(__file__).resolve().parents[2]
        return (root / "arifosmcp" / "runtime" / "tools.py").read_text()

    def _whitelist_present(self, source: str, name: str) -> bool:
        # check that name appears inside a tuple assigned to valid_action_classes
        # crude heuristic: find the tuple and check membership
        import re
        m = re.search(
            r"valid_action_classes\s*=\s*\((.*?)\)",
            source,
            re.DOTALL,
        )
        if not m:
            return False
        body = m.group(1)
        # tokenize: remove string quotes, comments
        for token in re.findall(r'"([A-Z_]+)"', body):
            if token == name:
                return True
        return False

    def test_audit_record_in_whitelist(self, tools_source: str):
        assert self._whitelist_present(tools_source, "AUDIT_RECORD"), (
            "arif_lease_issue valid_action_classes rejects AUDIT_RECORD — "
            "audit 2026-07-27 regression"
        )

    def test_read_in_whitelist(self, tools_source: str):
        assert self._whitelist_present(tools_source, "READ"), (
            "arif_lease_issue valid_action_classes rejects READ — "
            "audit 2026-07-27 regression"
        )

    def test_canonical_classes_in_whitelist(self, tools_source: str):
        for canonical in ("OBSERVE", "MUTATE", "IRREVERSIBLE"):
            assert self._whitelist_present(tools_source, canonical), (
                f"canonical action_class {canonical!r} missing from whitelist"
            )
