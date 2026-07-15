"""
Constitutional Tests — Pre-Execution Floor Gate for arif_memory (P0-01a)
═══════════════════════════════════════════════════════════════════════════

Issue #598: arif_memory (555_MEMORY v4) had no pre-execution constitutional
gate. material mutation class operation could execute without F1/F11/F13
authority. This file gates the canonical entry points with the floor
contract specified in TASK-P0-01a.

Floor contract under test:
  F1  AMANAH       — session_id binding required (else SABAR)
  F2  TRUTH        — verdict returns SPECIFIC floor citation, not generic
  F9  ANTI-HANTU   — SABAR returns empty result; NEVER fabricates memory
  F11 AUDIT        — actor_id required; OBSERVE_ONLY blocks MUTATE
  F13 SOVEREIGN    — forget/prune requires prior arif_judge trace

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

# ═══════════════════════════════════════════════════════════════════════════
# Gate-level unit tests (no live session; mock get_session_identity)
# ═══════════════════════════════════════════════════════════════════════════


class TestMemoryFloorGateUnit:
    """Direct tests of pre_execution_floor_gate() in isolation.

    Patches get_session_identity so the gate's authority/judge-trace checks
    can be exercised without a real bound session.
    """

    def test_forget_without_session_id_returns_sabar_f1(self, monkeypatch):
        """F1: forget without session_id must be SABAR (never execute forget).
        F9: empty result, no fabricated memory.
        """
        from arifosmcp.runtime.memory_gate import pre_execution_floor_gate

        result = pre_execution_floor_gate(
            mode="forget", session_id=None, actor_id="arif", memory_id="mem-123"
        )

        assert result["verdict"] == "SABAR"
        assert result["floor_violation"] == "F1"
        assert "F1" in result["violated_laws"]
        # F2: reason must be SPECIFIC, not generic — must cite floor + rule.
        assert "F1 AMANAH" in result["reason"], (
            "F2 TRUTH violation: reason must specifically cite F1 AMANAH "
            f"(got: {result['reason']!r})"
        )
        assert "session_id" in result["reason"].lower()
        # F9: no fabricated content; operation_class should be IRREVERSIBLE.
        assert result["operation_class"] == "IRREVERSIBLE"
        # F11: actor_token must be a fingerprint, never plaintext.
        assert result["actor_token"] == "actor:sha256:" + ("0" * 16) or result[
            "actor_token"
        ].startswith("actor:sha256:")
        # Plaintext actor is not echoed in the verdict.
        assert "arif" not in (result["actor_token"] or "")

    def test_remember_without_session_id_returns_sabar_f1(self):
        """F1: remember (= store) without session_id must be SABAR."""
        from arifosmcp.runtime.memory_gate import pre_execution_floor_gate

        result = pre_execution_floor_gate(
            mode="store", session_id=None, actor_id="arif", memory_id=None
        )

        assert result["verdict"] == "SABAR"
        assert result["floor_violation"] == "F1"
        assert result["operation_class"] == "MUTATE"

    def test_revise_without_session_id_returns_sabar_f1(self):
        """F1: revise (= update) without session_id must be SABAR."""
        from arifosmcp.runtime.memory_gate import pre_execution_floor_gate

        result = pre_execution_floor_gate(
            mode="update", session_id=None, actor_id="arif", memory_id="mem-xyz"
        )

        assert result["verdict"] == "SABAR"
        assert result["floor_violation"] == "F1"
        assert result["operation_class"] == "MUTATE"

    def test_remember_without_actor_id_returns_sabar_f11(self):
        """F11: remember (= store) without actor_id must be SABAR F11."""
        from arifosmcp.runtime.memory_gate import pre_execution_floor_gate

        result = pre_execution_floor_gate(
            mode="store", session_id="sid-001", actor_id=None, memory_id=None
        )

        assert result["verdict"] == "SABAR"
        assert result["floor_violation"] == "F11"
        assert "F11" in result["violated_laws"]
        # F2: SPECIFIC citation
        assert "F11 AUDIT" in result["reason"]
        assert "actor_id" in result["reason"].lower()

    def test_anonymous_actor_treated_as_missing(self):
        """F11: 'anonymous' is the literal sentinel for missing actor.

        Per arif_memory convention the string 'anonymous' is treated as if
        no actor was provided (covers legacy F11 AUTH behavior).
        """
        from arifosmcp.runtime.memory_gate import pre_execution_floor_gate

        result = pre_execution_floor_gate(
            mode="store", session_id="sid-001", actor_id="anonymous", memory_id=None
        )

        assert result["verdict"] == "SABAR"
        assert result["floor_violation"] == "F11"

    def test_remember_observe_only_session_returns_void_f11(self, monkeypatch):
        """F11: remember (= store) on OBSERVE_ONLY session must be VOID."""
        from arifosmcp.runtime import memory_gate
        from arifosmcp.runtime.memory_gate import pre_execution_floor_gate

        # Mock get_session_identity to return OBSERVE_ONLY authority.
        def fake_get_session_identity(session_id: str) -> dict | None:
            return {
                "session_id": session_id,
                "actor_id": "arif",
                "authority": "OBSERVE_ONLY",
                "authority_level": "L4_WARGA",
                "activity": {"history": []},
            }

        monkeypatch.setattr(
            memory_gate, "_is_observe_only", lambda sid: True
        )

        result = pre_execution_floor_gate(
            mode="store", session_id="sid-L4-warga", actor_id="arif", memory_id=None
        )

        assert result["verdict"] == "VOID"
        assert result["floor_violation"] == "F11"
        assert "F11" in result["violated_laws"]
        # F2: SPECIFIC citation — must cite OBSERVE_ONLY and operation_class.
        assert "OBSERVE_ONLY" in result["reason"]
        assert "MUTATE" in result["reason"]
        # Operation class should be MUTATE (store = remember).
        assert result["operation_class"] == "MUTATE"

    def test_forget_without_judge_trace_returns_888_hold_f13(self, monkeypatch):
        """F13: forget without prior arif_judge trace must be 888_HOLD.

        This is the critical F13-SOVEREIGN boundary: the gate must NOT
        execute the forget; it must emit a HOLD verdict with F13 floor
        citation. The downstream memory_forget() function must not run.
        """
        from arifosmcp.runtime import memory_gate
        from arifosmcp.runtime.memory_gate import pre_execution_floor_gate

        monkeypatch.setattr(memory_gate, "_is_observe_only", lambda sid: False)
        monkeypatch.setattr(memory_gate, "_has_judge_trace", lambda sid: False)

        result = pre_execution_floor_gate(
            mode="forget",
            session_id="sid-mut-001",
            actor_id="arif",
            memory_id="mem-target",
        )

        assert result["verdict"] == "888_HOLD"
        assert result["floor_violation"] == "F13"
        assert "F13" in result["violated_laws"]
        # Reversibility: F1 is also cited because forget is irreversible.
        assert "F1" in result["violated_laws"]
        # F2: SPECIFIC citation
        assert "F13 SOVEREIGN" in result["reason"]
        assert "IRREVERSIBLE" in result["reason"]
        assert "arif_judge" in result["reason"].lower()
        assert result["operation_class"] == "IRREVERSIBLE"
        # Memory id should be carried in the receipt for audit.
        assert result["memory_id"] == "mem-target"

    def test_forget_with_judge_trace_proceeds_seal(self, monkeypatch):
        """Forget with prior arif_judge trace must proceed (SEAL verdict).

        The gate clears; downstream check_laws() and forget execution run.
        """
        from arifosmcp.runtime import memory_gate
        from arifosmcp.runtime.memory_gate import pre_execution_floor_gate

        monkeypatch.setattr(memory_gate, "_is_observe_only", lambda sid: False)
        monkeypatch.setattr(memory_gate, "_has_judge_trace", lambda sid: True)

        result = pre_execution_floor_gate(
            mode="forget",
            session_id="sid-jdg-001",
            actor_id="arif",
            memory_id="mem-target",
        )

        assert result["verdict"] == "SEAL"
        assert result["floor_violation"] is None
        assert result["violated_laws"] == []
        assert result["operation_class"] == "IRREVERSIBLE"
        # F11: actor fingerprint is sha256, never plaintext.
        assert result["actor_token"].startswith("actor:sha256:")
        assert "arif" not in result["actor_token"]

    def test_prune_without_judge_trace_returns_888_hold(self, monkeypatch):
        """prune (DEPRECATED → forget) also gets F13 888_HOLD treatment."""
        from arifosmcp.runtime import memory_gate
        from arifosmcp.runtime.memory_gate import pre_execution_floor_gate

        monkeypatch.setattr(memory_gate, "_is_observe_only", lambda sid: False)
        monkeypatch.setattr(memory_gate, "_has_judge_trace", lambda sid: False)

        result = pre_execution_floor_gate(
            mode="prune",
            session_id="sid-mut-002",
            actor_id="arif",
            memory_id="mem-stale",
        )

        assert result["verdict"] == "888_HOLD"
        assert result["floor_violation"] == "F13"
        assert result["operation_class"] == "IRREVERSIBLE"

    def test_revise_with_valid_mutate_session_proceeds_seal(self, monkeypatch):
        """Revise (= update) with MUTATE-eligible session must proceed.

        Floor verdict must be SEAL; check_laws() is the downstream gate.
        """
        from arifosmcp.runtime import memory_gate
        from arifosmcp.runtime.memory_gate import pre_execution_floor_gate

        monkeypatch.setattr(memory_gate, "_is_observe_only", lambda sid: False)

        result = pre_execution_floor_gate(
            mode="update",
            session_id="sid-mut-003",
            actor_id="arif",
            memory_id="mem-789",
        )

        assert result["verdict"] == "SEAL"
        assert result["floor_violation"] is None
        assert result["violated_laws"] == []
        assert result["operation_class"] == "MUTATE"

    def test_recall_without_session_returns_sabar_f1(self):
        """Recall (= read) without session_id also returns SABAR F1.

        Even read paths require session binding for F11 audit traceability.
        F9 anti-hantu: no fabricated memory content from bound recall.
        """
        from arifosmcp.runtime.memory_gate import pre_execution_floor_gate

        result = pre_execution_floor_gate(
            mode="recall", session_id=None, actor_id="arif", memory_id="mem-r"
        )

        assert result["verdict"] == "SABAR"
        assert result["floor_violation"] == "F1"
        assert result["operation_class"] == "READ"

    def test_recall_observe_only_proceeds_for_read(self, monkeypatch):
        """Read operations on OBSERVE_ONLY sessions are allowed (recall is read)."""
        from arifosmcp.runtime import memory_gate
        from arifosmcp.runtime.memory_gate import pre_execution_floor_gate

        monkeypatch.setattr(memory_gate, "_is_observe_only", lambda sid: True)

        result = pre_execution_floor_gate(
            mode="recall", session_id="sid-L4-warga", actor_id="arif", memory_id="mem-r"
        )

        assert result["verdict"] == "SEAL"
        assert result["operation_class"] == "READ"

    def test_unknown_mode_defaults_to_mutate_class(self):
        """Unknown modes default to MUTATE (conservative; F1 reversibility)."""
        from arifosmcp.runtime.memory_gate import classify_operation

        # Known classifications
        assert classify_operation("forget") == "IRREVERSIBLE"
        assert classify_operation("prune") == "IRREVERSIBLE"
        assert classify_operation("store") == "MUTATE"
        assert classify_operation("update") == "MUTATE"
        assert classify_operation("seal") == "MUTATE"
        assert classify_operation("recall") == "READ"
        assert classify_operation("audit") == "READ"
        assert classify_operation("list") == "READ"
        # Unknown defaults to MUTATE (conservative).
        assert classify_operation("unknown_mode_xyz") == "MUTATE"


# ═══════════════════════════════════════════════════════════════════════════
# Gate-to-envelope tests
# ═══════════════════════════════════════════════════════════════════════════


class TestMemoryFloorGateEnvelope:
    """gate_to_envelope translates verdict into the canonical _hold/_sabar shape."""

    def test_seal_returns_none_caller_proceeds(self):
        """SEAL envelope is None — caller proceeds to check_laws() + execution."""
        from arifosmcp.runtime.memory_gate import gate_to_envelope

        envelope = gate_to_envelope(
            {"verdict": "SEAL", "floor_violation": None}, tool="arif_memory_recall"
        )
        assert envelope is None

    def test_void_returns_hold_with_f11_citation(self):
        """VOID → _hold response, floors=['F11'], specific reason."""
        from arifosmcp.runtime.memory_gate import gate_to_envelope

        envelope = gate_to_envelope(
            {
                "verdict": "VOID",
                "floor_violation": "F11",
                "violated_laws": ["F11"],
                "reason": "F11: OBSERVE_ONLY session on MUTATE blocked",
                "next_safe_action": "Promote session authority",
                "operation_class": "MUTATE",
                "mode": "store",
                "actor_token": "actor:sha256:abcdef1234567890",
                "session_id": "sid-x",
                "memory_id": None,
            },
            tool="arif_memory_recall",
        )
        assert envelope is not None
        # _hold returns a structured envelope with status='HOLD'
        assert envelope["status"] == "HOLD"
        meta = envelope["meta"]
        assert "F11" in meta["violated_laws"]
        assert "F11" in meta["reason"]
        # Floor receipt carries the per-floor pre-execution gate detail.
        gate_meta = meta["pre_execution_gate"]
        assert gate_meta["floor_violation"] == "F11"

    def test_888_hold_returns_hold_with_f13_citation(self):
        """888_HOLD → _hold response, floors=['F13', 'F1'], specific reason."""
        from arifosmcp.runtime.memory_gate import gate_to_envelope

        envelope = gate_to_envelope(
            {
                "verdict": "888_HOLD",
                "floor_violation": "F13",
                "violated_laws": ["F13", "F1"],
                "reason": "F13 SOVEREIGN: forget without judge trace",
                "next_safe_action": "Call arif_judge first",
                "operation_class": "IRREVERSIBLE",
                "mode": "forget",
                "actor_token": "actor:sha256:abcdef1234567890",
                "session_id": "sid-y",
                "memory_id": "mem-z",
            },
            tool="arif_memory_recall",
        )
        assert envelope is not None
        assert envelope["status"] == "HOLD"
        meta = envelope["meta"]
        assert "F13" in meta["violated_laws"]
        assert "F1" in meta["violated_laws"]
        assert "F13 SOVEREIGN" in meta["reason"]

    def test_sabar_emits_empty_result_no_fabricated_memory(self):
        """SABAR -> _sabar envelope with no fabricated memory content (F9 anti-hantu).

        The envelope's verdict must be SABAR; status must be SABAR.
        The envelope may carry verdict metadata (status, meta, reasons,
        nine_signal, call_hash) but must NOT carry any fabricated memory
        content (no 'content', no 'text', no 'memory_data', no 'records',
        no 'summary', no 'entries'). F9 ANTI-HANTU: never fabricate memory
        out of thin air.
        """
        from arifosmcp.runtime.memory_gate import gate_to_envelope

        envelope = gate_to_envelope(
            {
                "verdict": "SABAR",
                "floor_violation": "F1",
                "violated_laws": ["F1"],
                "reason": "F1 AMANAH: missing session_id",
                "next_safe_action": "Bind session",
                "operation_class": "MUTATE",
                "mode": "store",
                "actor_token": "actor:sha256:abcdef1234567890",
                "session_id": None,
                "memory_id": None,
            },
            tool="arif_memory_recall",
        )
        assert envelope is not None
        # Status / verdict must be SABAR.
        assert envelope["status"] == "SABAR"
        # F9 anti-hantu: NO fabricated memory-data fields in the envelope.
        result = envelope.get("result", {})
        assert isinstance(result, dict)
        # These would be a hallucinated memory; assert NONE present.
        forbidden = {"content", "text", "memory_data", "records", "entries"}
        leaked = forbidden & set(result.keys())
        assert not leaked, (
            f"F9 ANTI-HANTU violated: SABAR envelope must carry no fabricated "
            f"memory content, but found: {leaked}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# Specific floor citation tests (F2 TRUTH: no generic errors)
# ═══════════════════════════════════════════════════════════════════════════


class TestFloorCitationSpecificity:
    """Per F2 TRUTH: every floor violation must cite a SPECIFIC floor.

    No naked "error" string. No "unknown" reason. No generic message.
    """

    def test_f1_citation_includes_specific_phrase(self):
        from arifosmcp.runtime.memory_gate import pre_execution_floor_gate

        result = pre_execution_floor_gate(
            mode="store", session_id=None, actor_id="arif", memory_id=None
        )
        assert "F1 AMANAH" in result["reason"]
        # And the next_safe_action must also be specific, not generic.
        assert "session_id" in result["next_safe_action"].lower()

    def test_f11_citation_includes_specific_phrase(self):
        from arifosmcp.runtime.memory_gate import pre_execution_floor_gate

        result = pre_execution_floor_gate(
            mode="store", session_id="sid-001", actor_id=None, memory_id=None
        )
        assert "F11 AUDIT" in result["reason"]
        assert "actor_id" in result["reason"].lower()

    def test_f11_observe_only_citation_includes_specific_phrase(self, monkeypatch):
        from arifosmcp.runtime import memory_gate
        from arifosmcp.runtime.memory_gate import pre_execution_floor_gate

        monkeypatch.setattr(memory_gate, "_is_observe_only", lambda sid: True)
        result = pre_execution_floor_gate(
            mode="store", session_id="sid-002", actor_id="arif", memory_id=None
        )
        assert "F11 AUDIT" in result["reason"]
        assert "OBSERVE_ONLY" in result["reason"]
        assert "MUTATE" in result["reason"]

    def test_f13_citation_includes_specific_phrase(self, monkeypatch):
        from arifosmcp.runtime import memory_gate
        from arifosmcp.runtime.memory_gate import pre_execution_floor_gate

        monkeypatch.setattr(memory_gate, "_is_observe_only", lambda sid: False)
        monkeypatch.setattr(memory_gate, "_has_judge_trace", lambda sid: False)
        result = pre_execution_floor_gate(
            mode="forget", session_id="sid-003", actor_id="arif", memory_id="m"
        )
        assert "F13 SOVEREIGN" in result["reason"]
        assert "IRREVERSIBLE" in result["reason"]
        assert "arif_judge" in result["reason"].lower()


# ═══════════════════════════════════════════════════════════════════════════
# F11 audit hygiene — actor plaintext never echoed
# ═══════════════════════════════════════════════════════════════════════════


class TestF11ActorHygiene:
    """actor_token is SHA-256 fingerprint; plaintext actor_id never appears."""

    def test_actor_token_uses_sha256_fingerprint(self):
        from arifosmcp.runtime.memory_gate import _tokenize_actor

        token = _tokenize_actor("arif.verified@example.com")
        assert token.startswith("actor:sha256:")
        assert "arif" not in token
        assert "@" not in token
        assert ".com" not in token

    def test_empty_actor_yields_actor_none_sentinel(self):
        from arifosmcp.runtime.memory_gate import _tokenize_actor

        assert _tokenize_actor(None) == "actor:none"
        assert _tokenize_actor("") == "actor:none"
        assert _tokenize_actor("   ") == "actor:none"

    def test_plaintext_actor_never_in_verdict(self):
        """Verdict payloads must not contain the plaintext actor_id."""
        from arifosmcp.runtime.memory_gate import pre_execution_floor_gate

        secret_actor = "arif.secret@sovereign-key-2026"
        result = pre_execution_floor_gate(
            mode="store",
            session_id="sid-h",
            actor_id=secret_actor,
            memory_id=None,
        )
        # Serialize the verdict and check no plaintext leaks.
        serialized = str(result).lower()
        assert "secret" not in serialized
        assert "sovereign-key-2026" not in serialized
        # SHA-256 fingerprint should be present.
        assert "actor:sha256:" in serialized


# ═══════════════════════════════════════════════════════════════════════════
# Judge-trace detection
# ═══════════════════════════════════════════════════════════════════════════


class TestJudgeTraceDetection:
    """_has_judge_trace checks session.activity.history for arif_judge."""

    def test_no_judge_trace_returns_false(self, monkeypatch):
        """Empty / missing history -> no judge trace -> False."""
        from arifosmcp.runtime import memory_gate
        from arifosmcp.runtime.memory_gate import _has_judge_trace

        # Patch the module-level binding (imported at module load time).
        def fake_get(sid):
            return {"session_id": sid, "actor_id": "x", "activity": {}}

        monkeypatch.setattr(memory_gate.get_session_identity, "__defaults__", (None,))
        monkeypatch.setattr(memory_gate, "get_session_identity", fake_get)
        assert _has_judge_trace("sid-no-judge") is False

    def test_judge_trace_present_returns_true(self, monkeypatch):
        """activity.history contains arif_judge -> True."""
        from arifosmcp.runtime import memory_gate
        from arifosmcp.runtime.memory_gate import _has_judge_trace

        def fake_get(sid):
            return {
                "session_id": sid,
                "actor_id": "x",
                "activity": {
                    "history": [
                        {"tool": "arif_init", "verdict": "SEAL"},
                        {"tool": "arif_judge", "verdict": "SEAL"},
                    ]
                },
            }

        monkeypatch.setattr(memory_gate, "get_session_identity", fake_get)
        assert _has_judge_trace("sid-with-judge") is True

    def test_judge_deliberate_trace_also_counts(self, monkeypatch):
        """activity.history contains arif_judge_deliberate -> True."""
        from arifosmcp.runtime import memory_gate
        from arifosmcp.runtime.memory_gate import _has_judge_trace

        def fake_get(sid):
            return {
                "session_id": sid,
                "actor_id": "x",
                "activity": {
                    "history": [{"tool": "arif_judge_deliberate", "verdict": "SEAL"}]
                },
            }

        monkeypatch.setattr(memory_gate, "get_session_identity", fake_get)
        assert _has_judge_trace("sid-with-deliberate") is True

    def test_missing_session_returns_false(self, monkeypatch):
        from arifosmcp.runtime import memory_gate
        from arifosmcp.runtime.memory_gate import _has_judge_trace

        monkeypatch.setattr(memory_gate, "get_session_identity", lambda sid: None)
        assert _has_judge_trace("sid-missing") is False
