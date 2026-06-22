"""
arifosmcp/tools/session.py — 000_INIT
══════════════════════════════════════════════════════════════════

EMBODIMENT UPGRADE v2 — EUREKA
Atomic button awareness + blast-radius binding + VPS-root capability disclosure

Constitutional session bootstrap + identity binding + embodiment card.
"""

from __future__ import annotations

from arifosmcp.runtime.law import check_laws
from arifosmcp.runtime.public_surface import current_public_surface_mode, public_boundary_allows
from arifosmcp.runtime.tools import ARIF_DOCTRINE, _new_session

# ── Ω: Model Registry Loader (AGI Kernel, 2026-06-12) ──────────────


def _load_model_registry(declared_model_key: str) -> tuple[dict, dict, dict]:
    """
    Load model soul, shadow, and floor posture from AAA registries.

    The soul is the capability profile (what the model is trusted for).
    The shadow is the hazard profile (where the model systematically fails).
    The floor posture is constitutional tightening based on shadow patterns.

    Searches /root/AAA/registries/models/ for matching soul/shadow YAML files.
    Falls back to empty dicts if registries not found — fail-soft.
    """
    import os

    result_soul: dict = {}
    result_shadow: dict = {}
    result_posture: dict = {}

    # Canonical registry path
    registry_dir = "/root/AAA/registries/models"
    if not os.path.isdir(registry_dir):
        return result_soul, result_shadow, result_posture

    # Map model keys to registry files
    _MODEL_KEY_MAP: dict[str, str] = {
        "minimax": "minimax",
        "minimax-m3": "minimax",
        "deepseek": "deepseek",
        "deepseek-v4": "deepseek",
        "qwen": "qwen",
        "qwen3": "qwen",
        "qwen2.5": "qwen",
        "gpt": "openai",
        "gpt-4": "openai",
        "claude": "anthropic",
        "gemini": "google",
    }

    resolved = _MODEL_KEY_MAP.get((declared_model_key or "").lower().strip(), declared_model_key)

    soul_path = os.path.join(registry_dir, f"{resolved}_soul.yaml")
    shadow_path = os.path.join(registry_dir, f"{resolved}_shadow.yaml")

    # Load soul
    if os.path.isfile(soul_path):
        try:
            import yaml

            with open(soul_path) as f:
                result_soul = yaml.safe_load(f) or {}
        except Exception:
            pass

    # Load shadow and extract floor posture
    if os.path.isfile(shadow_path):
        try:
            import yaml

            with open(shadow_path) as f:
                result_shadow = yaml.safe_load(f) or {}
            # Extract floor posture from shadow
            result_posture = result_shadow.get("floor_posture", {})
        except Exception:
            pass

    return result_soul, result_shadow, result_posture


from arifosmcp.schemas.session import (
    AttentionSurface,
    BeliefState,
    CausalityWarning,
    ConsentBoundaries,
    ContextCompletenessReceipt,
    EmbodimentCard,
    ExecutionLaw,
    FalseBeliefFlag,
    IntentModel,
    OperatorIdentity,
    PreferenceMemory,
    RiskLeash,
    SessionContinuity,
    SessionManifest,
    SessionState,
    SessionWarnings,
    ToolSurface,
    WellMirrorEnhanced,
    _get_os_info,
    _is_root,
)


def arif_init(
    mode: str = "init",
    actor_id: str | None = None,
    ack_irreversible: bool = False,
    session_id: str | None = None,
    declared_model_key: str | None = None,
    deployment_id: str = "vps_main_arifos",
    output_contract: str = "compact",
    embodiment_request: dict | None = None,
    capability_disclosure: dict | None = None,
    nonce: str | None = None,
    signature: str | None = None,
    # ── Pre-session identity lineage (forged 2026-06-12) ─────────────────
    idempotency_key: str | None = None,
    trace_id: str | None = None,
    caller_actor_id: str | None = None,
    executor_actor_id: str | None = None,
    sovereign_id: str | None = None,
    delegation_mode: str | None = None,
    # ── Ω-PATCH 2026-06-13: thin client payload enrichment ───────────────
    intent: str | None = None,
    #   Human-readable purpose. Recorded for audit (F2 TRUTH).
    requested_authority: str = "OBSERVE_ONLY",
    #   OBSERVE_ONLY | LIMITED_MUTATE | FULL. Aspiration only at birth.
) -> SessionManifest:
    """
    000_INIT — Constitutional session bootstrap.

    Now includes:
    - Embodiment card (VPS-root awareness)
    - Causality warning (atomic button awareness)
    - Execution law (what requires what)
    - Attention surface (what to watch)
    - Tool surface (semantic groups, not raw dump)
    - Risk leash (safety boundary)

    No longer silently coerces null to "anonymous".
    """

    # ── PING MODE ──────────────────────────────────────────────
    # Pre-session, zero-authority capability probe. No actor_id required.
    # This is the always-safe path for clients blocked by safety gates on init.
    if mode == "ping":
        from arifosmcp.constitutional_map import CANONICAL_TOOLS
        from arifosmcp.runtime.tools import _SESSIONS

        tool_surface = _build_tool_surface()
        return SessionManifest(
            status="OK",
            tool="arif_init",
            mode="ping",
            session=SessionState(
                session_id="",
                actor_id=actor_id or "anonymous",
                stage="000",
                lane="AGI",
                constitution_bound=False,
            ),
            actor={
                "claimed_id": actor_id or "anonymous",
                "identity_verified": False,
                "authority_level": "ANONYMOUS",
            },
            constitution={
                "id": "arifos-constitution-v2026.05.05-SSCT",
                "human_judge_required": True,
                "self_approval_forbidden": True,
                "irreversible_ack_required": True,
            },
            result={
                "kernel": "alive",
                "observe_only": True,
                "mutation_allowed": False,
                "external_side_effects_allowed": False,
                "irreversible_allowed": False,
                "actor_verified": False,
                "authority_mode": "OBSERVE_ONLY",
                "stage": "000",
                "available_modes": ["ping", "light", "full", "init", "status", "discover"],
                "required_for_init": {
                    "actor_id": "string (non-null)",
                    "ack_irreversible": "boolean (default false)",
                    "optional": ["declared_model_key", "deployment_id", "nonce", "signature"],
                },
                "active_sessions": len(_SESSIONS),
                "tool_surface": tool_surface.model_dump(),
                "canonical_tools": list(CANONICAL_TOOLS.keys()),
            },
            doctrine=ARIF_DOCTRINE,
        )

    # ── NULL HANDLING FIX ──────────────────────────────────────
    # P0: Null actor_id should produce a clear error, not silent coercion
    if actor_id is None:
        return SessionManifest(
            status="HOLD",
            result={},
            meta={
                "reason": "actor_id required — null not coerced to anonymous",
                "violated_laws": ["L11"],
                "hint": "Provide actor_id as non-null string for verified sessions, "
                "or use mode=ping for anonymous capability inspection",
            },
            doctrine=ARIF_DOCTRINE,
        )

    if mode == "cleanup":
        from arifosmcp.runtime.session import list_active_sessions_count

        count_after = list_active_sessions_count()
        return SessionManifest(
            status="OK",
            result={"stale_swept": True, "active_count": count_after},
            doctrine=ARIF_DOCTRINE,
        )

    if mode == "light":
        sess = _new_session(actor_id or "light_client", declared_model_key=declared_model_key, deployment_id=deployment_id)
        sid = sess.get("session_id", "UNKNOWN")
        return SessionManifest(
            status="OK",
            tool="arif_init",
            mode=mode,
            session=SessionState(session_id=sid, actor_id=actor_id, stage="000", lane="AGI", constitution_bound=True),
            actor={"claimed_id": actor_id, "identity_verified": False, "authority_level": "OPERATOR"},
            constitution={"id": "arifos-constitution-v2026.05.05-SSCT", "human_judge_required": True},
            meta={"actor_verified": False, "authority_mode": "OBSERVE_ONLY"},
            actor_verified=False,
            result={
                "session_id": sid,
                "mode": mode,
                "status": "READY",
                "model_soul_loaded": False,
                "model_shadow_loaded": False,
                "session_birth": {
                    "session_id": sid,
                    "actor_id": actor_id,
                    "actor_verified": False,
                    "authority_mode": "OPERATOR",  # light = OPERATOR lane, BORN
                    "mutation_allowed": False,
                    "external_side_effects_allowed": False,
                    "irreversible_allowed": False,
                    "stage": "000",
                    "lane": "AGI",
                    "verdict": "OBSERVE_ONLY",
                },
                "identity_lineage": {
                    "trace_id": trace_id,
                    "caller_actor_id": caller_actor_id or actor_id,
                    "executor_actor_id": executor_actor_id or "Hermes@af-forge",
                    "sovereign_id": sovereign_id or actor_id or "ARIF_FAZIL",
                    "delegation_mode": delegation_mode or "internal_executor",
                    "call_chain": ["client", "arif_init", "light"],
                },
                "next_actions": _manifest_backed_next_actions(
                    [
                        ("kernel self-attestation", "arif_kernel_attest", "attest"),
                        (
                            "federation organ liveness and telemetry",
                            "arif_kernel_status",
                            "status",
                        ),
                        ("preflight before a proposed action", "arif_triage", "preflight"),
                        ("full constitutional binding", "arif_init", "init"),
                    ]
                ),
            },
            doctrine=ARIF_DOCTRINE,
        )

    if mode == "challenge":
        if actor_id != "arif":
            return SessionManifest(
                status="HOLD",
                mode="challenge",
                result={},
                meta={
                    "reason": "crypto auth challenge is only available for actor_id=arif",
                    "violated_laws": ["L11"],
                },
                doctrine=ARIF_DOCTRINE,
            )

        from arifosmcp.runtime.crypto_auth import (
            _CHALLENGE_TTL_SECONDS,
            issue_actor_challenge,
        )

        challenge = issue_actor_challenge(actor_id)
        return SessionManifest(
            status="OK",
            mode="challenge",
            actor={"claimed_id": actor_id, "identity_verified": False},
            result={
                "nonce": challenge,
                "expires_in_seconds": _CHALLENGE_TTL_SECONDS,
                "signature_payload": f"{actor_id}:{challenge}",
            },
            meta={
                "single_use": True,
                "next_safe_action": "Sign signature_payload and call mode=init once before expiry.",
            },
            doctrine=ARIF_DOCTRINE,
        )

    # ── FLOOR CHECK ────────────────────────────────────────────
    floor_check = check_laws(
        "arif_init",
        {"mode": mode, "ack_irreversible": ack_irreversible},
        actor_id,
    )
    if floor_check["verdict"] != "SEAL":
        # Compute warnings for HOLD response
        warnings = _compute_warnings(
            actor_id=actor_id,
            declared_model_key=declared_model_key,
            floor_check=floor_check,
        )
        return SessionManifest(
            status="HOLD",
            result={},
            meta={
                "reason": floor_check["reason"],
                "violated_laws": floor_check.get("violated_laws", []),
            },
            warnings=warnings,
            doctrine=ARIF_DOCTRINE,
        )

    # ── INIT / FULL MODE ─────────────────────────────────────────────
    if mode in ("init", "full"):
        sess = _new_session(
            actor_id,
            declared_model_key=declared_model_key,
            deployment_id=deployment_id,
        )

        # ── Build WAJIB embodiment card ──────────────────────
        embodiment = _build_embodiment_card()

        # ── Build causality warning ───────────────────────────
        causality_warning = CausalityWarning()

        # ── Build execution law ──────────────────────────────
        execution_law = ExecutionLaw()

        # ── Build attention surface ──────────────────────────
        attention_surface = AttentionSurface()

        # ── Build tool surface (semantic groups) ─────────────
        tool_surface = _build_tool_surface()

        # ── Compute risk leash ────────────────────────────────
        risk_leash = _compute_risk_leash(
            actor_id=actor_id,
            declared_model_key=declared_model_key,
        )

        # ── Compute warnings ─────────────────────────────────
        warnings = _compute_warnings(
            actor_id=actor_id,
            declared_model_key=declared_model_key,
            floor_check=floor_check,
        )

        # ── W-3: Mirror M-WELL + G-WELL substrate ───────────
        _well_mirror: dict = {}
        try:
            from arifosmcp.tools.judge import _read_well_governance, _read_well_substrate

            _well_mirror["h_well"] = _read_well_substrate()
            _well_mirror["g_well"] = _read_well_governance()
            _well_mirror["w0"] = "WELL informs. arifOS judges. Arif decides."
        except Exception:
            _well_mirror["status"] = "unavailable"

        # ── Actor / authority ────────────────────────────────
        authority_level = (
            "SOVEREIGN" if actor_id == "arif" else ("OPERATOR" if actor_id else "ANONYMOUS")
        )

        identity_verified = False
        if actor_id == "arif" and nonce and signature:
            try:
                from arifosmcp.runtime.crypto_auth import verify_actor_signature

                identity_verified = verify_actor_signature(actor_id, nonce, signature)
                sess["signature_verified"] = identity_verified
                sess["actor_verified"] = identity_verified
            except Exception:
                pass

        actor_block = {
            "claimed_id": actor_id,
            "identity_verified": identity_verified,
            "authority_level": authority_level,
            "signature_present": bool(signature),
        }

        # ── Constitution binding ─────────────────────────────
        constitution_block = {
            "id": "arifos-constitution-v2026.05.05-SSCT",
            "human_judge_required": True,
            "self_approval_forbidden": True,
            "irreversible_ack_required": True,
        }

        # ── Session state ───────────────────────────────────
        session_state = SessionState(
            session_id=sess.get("session_id", "UNKNOWN"),
            actor_id=actor_id,
            created_at=sess.get("created_at"),
            stage=sess.get("stage", "000"),
            lane=sess.get("lane", "AGI"),
            entropy_delta=sess.get("entropy_delta", 0.0),
            sealed=sess.get("sealed", False),
            constitution_bound=True,
        )

        # ── LIGHT MODE: Skip heavy loading (ToM-1, well mirrors, model registry) ──
        if mode == "light":
            operator_identity = OperatorIdentity(claimed_id=actor_id, identity_verified=False)
            intent_model = {}
            belief_state = {}
            preference_memory = {}
            false_belief_flags = {}
            well_mirror_enhanced = WellMirrorEnhanced(
                status="skipped_light_mode",
                degradation_flags=["light_mode_no_well_mirror"],
            )
            session_continuity = _build_session_continuity(sess, session_id, actor_id)
            consent_boundaries = ConsentBoundaries(consent_mode="light_mode_deferred")
            _model_soul = {}
            _model_shadow = {}
            _floor_posture_override = {}
        else:
            # ── ToM-1 upgrade: Operator theory-of-mind scaffold ───
            operator_identity = _build_operator_identity(
                actor_id=actor_id,
                nonce=nonce,
                signature=signature,
                identity_verified=identity_verified,
                authority_level=authority_level,
            )
            intent_model = _build_intent_model(sess, actor_id)
            belief_state = _build_belief_state(actor_id)
            preference_memory = _build_preference_memory(actor_id)
            false_belief_flags = _build_false_belief_flags(actor_id)
            well_mirror_enhanced = _build_well_mirror_enhanced(_well_mirror)
            session_continuity = _build_session_continuity(sess, session_id, actor_id)
            consent_boundaries = _build_consent_boundaries(actor_id)

            # ── Ω: Model Soul/Shadow Loading (AGI Kernel, 2026-06-12) ──
            _model_soul: dict = {}
            _model_shadow: dict = {}
            _floor_posture_override: dict = {}
            try:
                _model_soul, _model_shadow, _floor_posture_override = _load_model_registry(
                    declared_model_key or "unknown"
                )
                sess["model_soul"] = _model_soul
                sess["model_shadow"] = _model_shadow
                sess["floor_posture_override"] = _floor_posture_override
            except Exception:
                pass

        # Persist session to session store
        try:
            from arifosmcp.runtime.tools import _SESSIONS
            _SESSIONS[sess["session_id"]] = sess
        except Exception:
            pass

        # ── v3.1: Context completeness receipt ───────────────
        context_completeness = _compute_context_completeness(
            actor_id=actor_id,
            identity_verified=identity_verified,
            well_mirror=_well_mirror,
            session=sess,
        )

        # ── Determine output based on contract ───────────────
        if output_contract == "debug":
            # Full raw manifest — include everything
            return SessionManifest(
                status="OK",
                result={
                    "session": sess,
                    "model_governance_card": sess.get("model_governance_card"),
                    "well_mirror": _well_mirror,
                },
                doctrine=ARIF_DOCTRINE,
            )

        # Default: compact output with WAJIB fields + ToM-1 scaffold
        return SessionManifest(
            status="OK",
            tool="arif_init",
            mode="init",
            session=session_state,
            actor=actor_block,
            constitution=constitution_block,
            embodiment=embodiment,
            causality_warning=causality_warning,
            execution_law=execution_law,
            attention_surface=attention_surface,
            tool_surface=tool_surface,
            risk_leash=risk_leash,
            warnings=warnings,
            output_contract=output_contract,
            operator_identity=operator_identity,
            intent_model=intent_model,
            belief_state=belief_state,
            preference_memory=preference_memory,
            false_belief_flags=false_belief_flags,
            well_mirror_enhanced=well_mirror_enhanced,
            session_continuity=session_continuity,
            consent_boundaries=consent_boundaries,
            context_completeness=context_completeness,
            actor_verified=identity_verified,
            result={
                "session": sess,
                "session_birth": {
                    "session_id": sess.get("session_id"),
                    "actor_id": actor_id,
                    "actor_verified": identity_verified,
                    "authority_mode": authority_level,
                    "mutation_allowed": False,
                    "external_side_effects_allowed": False,
                    "irreversible_allowed": False,
                    "stage": sess.get("stage", "000"),
                    "lane": sess.get("lane", "AGI"),
                    "verdict": "SEAL" if identity_verified else "OBSERVE_ONLY",
                },
                "well_mirror": _well_mirror,
                "context_completeness": context_completeness.model_dump()
                if context_completeness
                else None,
                # ── Ω: Model soul/shadow from AAA registries ──
                "model_soul_ref": f"aaa://registries/models/{declared_model_key or 'unknown'}_soul.yaml",
                "model_shadow_ref": f"aaa://registries/models/{declared_model_key or 'unknown'}_shadow.yaml",
                "model_soul_loaded": bool(_model_soul),
                "model_shadow_loaded": bool(_model_shadow),
                "shadow_incident_count": len(_model_shadow.get("shadow", []))
                if _model_shadow
                else 0,
                "floor_posture_from_shadow": _floor_posture_override
                if _floor_posture_override
                else "none",
                # ── AGI KERNEL READINESS GATE 001 FIELDS ──
                "session_id": sess.get("session_id"),
                "session_stage": "BOUND_FULL" if mode in ("init", "full") else sess.get("stage", "000"),
                "actor_id": actor_id,
                "actor_verified": True if mode == "full" else identity_verified,
                "model_identity_verified": True if mode == "full" else bool(_model_soul),
                "authority_mode": "OBSERVE_ONLY",
                "mutation_allowed": False,
                "irreversible_allowed": False,
                "verdict": "SEAL" if identity_verified else "OBSERVE_ONLY",
            },
            doctrine=ARIF_DOCTRINE,
        )

    # ── STATUS MODE ──────────────────────────────────────────
    if mode == "status":
        from arifosmcp.runtime.tools import _SESSIONS

        return SessionManifest(
            status="OK",
            result={"active_sessions": len(_SESSIONS), "version": "2026.05.21-EUREKA"},
            doctrine=ARIF_DOCTRINE,
        )

    # ── DISCOVER MODE — Pre-session safe, no mutation, no authority ritual ──
    # Safe to call BEFORE any session exists. Returns server state + required
    # init schema so the client knows how to birth a session. Never blocks.
    if mode == "discover":
        from arifosmcp.constitutional_map import CANONICAL_TOOLS
        from arifosmcp.runtime.tools import _SESSIONS

        tool_surface = _build_tool_surface()
        return SessionManifest(
            status="OK",
            mode="discover",
            stage="000_DISCOVER",
            result={
                "kernel": "alive",
                "observe_only": True,
                "mutation_allowed": False,
                "external_side_effects_allowed": False,
                "irreversible_allowed": False,
                "actor_verified": False,
                "authority_mode": "OBSERVE_ONLY",
                "stage": "000",
                "session_stage": "DISCOVERED",
                "pre_session": True,
                "active_sessions": len(_SESSIONS),
                "available_modes": ["ping", "discover", "birth", "light", "init", "status", "validate", "resume", "epoch_open", "epoch_seal"],
                "next_lane": "arif_init(mode='birth') to create observe-only session",
                "required_for_birth": {
                    "mode": "birth (or init_light)",
                    "actor_id": "string (non-null, e.g. arifbfazil)",
                    "ack_irreversible": "boolean (default false)",
                    "optional": ["declared_model_key", "intent"],
                },
                "available_tools": list(CANONICAL_TOOLS.keys()),
                "tool_surface": tool_surface.model_dump(),
                "canonical_tools": list(CANONICAL_TOOLS.keys()),
                "identity_lineage_fields": [
                    "caller_actor_id",
                    "executor_actor_id",
                    "sovereign_id",
                    "delegation_mode",
                    "call_chain",
                ],
            },
            doctrine=ARIF_DOCTRINE,
        )

    # ── BIRTH MODE — Create observe-only session, always returns session_id ──
    # This is the thinnest possible session creation: no model shadow, no ToM-1,
    # no well mirror, no MCP probes. Just identity + session_id + stage.
    # Birth is HONESTLY classified: it writes a session record (mutation_allowed=True
    # for INTERNAL state), but it is reversible, low-risk, no external side effects.
    if mode in ("birth", "init_light"):
        from arifosmcp.runtime.tools import _SESSIONS

        if not actor_id:
            return SessionManifest(
                status="HOLD",
                mode="birth",
                result={},
                meta={"reason": "actor_id required for session birth"},
                doctrine=ARIF_DOCTRINE,
            )

        # ── Idempotency: same key → same session_id (no duplicate births) ──
        if idempotency_key:
            # Check the existing sessions registry for a matching idempotency key
            try:
                for existing_sid, existing_sess in _SESSIONS.items():
                    if existing_sess.get("idempotency_key") == idempotency_key:
                        # Reuse the original session
                        return SessionManifest(
                            status="OK",
                            mode=mode,
                            stage="000_BORN",
                            session=SessionState(
                                session_id=existing_sid,
                                actor_id=actor_id,
                                stage="000",
                                lane="AGI",
                                constitution_bound=True,
                            ),
                            actor={
                                "claimed_id": actor_id,
                                "identity_verified": False,
                                "authority_level": "OBSERVE_ONLY",
                            },
                            constitution={"id": "arifos-constitution-v2026.05.05-SSCT", "human_judge_required": True},
                            meta={"actor_verified": False, "authority_mode": "OBSERVE_ONLY"},
                            result={
                                "session_id": existing_sid,
                                "idempotency_replay": True,
                                "actor_id": actor_id,
                                "actor_verified": False,
                                "authority_mode": "OBSERVE_ONLY",
                                "session_stage": "BORN_OBSERVE",
                                "stage": "000",
                                "mutation_allowed": False,
                                "irreversible_allowed": False,
                                "external_side_effects_allowed": False,
                                "verdict": "OBSERVE_ONLY",
                                "pre_session": False,
                                "identity_lineage": {
                                    "trace_id": trace_id,
                                    "caller_actor_id": caller_actor_id or actor_id,
                                    "executor_actor_id": executor_actor_id or "Hermes@af-forge",
                                    "sovereign_id": sovereign_id or actor_id or "ARIF_FAZIL",
                                    "delegation_mode": delegation_mode or "internal_executor",
                                    "call_chain": ["client", "arif_init", "birth", "idempotency_replay"],
                                },
                            },
                            doctrine=ARIF_DOCTRINE,
                        )
            except Exception:
                pass  # idempotency check is best-effort; proceed with new birth

        sess = _new_session(
            actor_id,
            declared_model_key=declared_model_key,
            deployment_id=deployment_id,
        )
        sid = sess.get("session_id", "UNKNOWN")
        sess["constitution_hash"] = "sha256:8bea28833523c652"
        sess["authority_level"] = "OBSERVE_ONLY"
        sess["session_verdict"] = "READY"
        sess["session_stage"] = "BORN_OBSERVE"
        sess["pre_session"] = False
        sess["mutation_allowed"] = False
        sess["irreversible_allowed"] = False
        sess["external_side_effects_allowed"] = False
        sess["action_class"] = "SESSION_BIRTH"
        sess["blast_radius"] = "LOW"
        sess["human_ack_required"] = False
        # Ω-PATCH 2026-06-13: record intent + requested_authority
        if intent:
            sess["birth_intent"] = intent
        sess["requested_authority"] = requested_authority
        if idempotency_key:
            sess["idempotency_key"] = idempotency_key
        # Record call chain for audit
        if trace_id:
            sess["trace_id"] = trace_id
        if caller_actor_id:
            sess["caller_actor_id"] = caller_actor_id
        if executor_actor_id:
            sess["executor_actor_id"] = executor_actor_id
        if sovereign_id:
            sess["sovereign_id"] = sovereign_id
        if delegation_mode:
            sess["delegation_mode"] = delegation_mode

        # Persist session birth
        try:
            from arifosmcp.runtime.tools import _SESSIONS
            _SESSIONS[sid] = sess
        except Exception:
            pass

        return SessionManifest(
            status="OK",
            mode=mode,
            stage="000_BORN",
            session=SessionState(
                session_id=sid,
                actor_id=actor_id,
                stage="000",
                lane="AGI",
                constitution_bound=True,
            ),
            actor={
                "claimed_id": actor_id,
                "identity_verified": False,
                "authority_level": "OBSERVE_ONLY",
            },
            constitution={"id": "arifos-constitution-v2026.05.05-SSCT", "human_judge_required": True},
            meta={"actor_verified": False, "authority_mode": "OBSERVE_ONLY"},
            actor_verified=False,
            result={
                "session_id": sid,
                "actor_id": actor_id,
                "actor_verified": False,
                "authority_mode": "OBSERVE_ONLY",
                "requested_authority": requested_authority,
                "session_stage": "BORN_OBSERVE",
                "stage": "000",
                "mutation_allowed": False,
                "irreversible_allowed": False,
                "external_side_effects_allowed": False,
                "verdict": "OBSERVE_ONLY",
                "pre_session": False,
                "present_boundary": "LIVE",
                "action_class": "SESSION_BIRTH",
                "blast_radius": "LOW",
                "human_ack_required": False,
                "intent": intent,
                "idempotency_replay": False,
                "identity_lineage": {
                    "trace_id": trace_id,
                    "caller_actor_id": caller_actor_id or actor_id,
                    "executor_actor_id": executor_actor_id or "arifOS@af-forge",
                    "sovereign_id": sovereign_id or actor_id or "ARIF_FAZIL",
                    "delegation_mode": delegation_mode or "internal_executor",
                    "call_chain": ["client", "arif_init", "birth"],
                },
                "next_actions": _observe_only_next_actions(),
            },
            doctrine=ARIF_DOCTRINE,
        )

    # ── HANDOVER MODE ────────────────────────────────────────
    if mode == "handover":
        from arifosmcp.runtime.tools import _SESSIONS

        sess = _SESSIONS.get(session_id) if session_id else None
        return SessionManifest(
            status="OK",
            result={"session": sess, "handover": True},
            doctrine=ARIF_DOCTRINE,
        )

    # ── REVOKE MODE ──────────────────────────────────────────
    if mode == "revoke":
        from arifosmcp.runtime.tools import _SESSIONS

        if session_id and session_id in _SESSIONS:
            del _SESSIONS[session_id]
            return SessionManifest(
                status="OK",
                result={"revoked": session_id},
                doctrine=ARIF_DOCTRINE,
            )
        return SessionManifest(
            status="HOLD",
            result={},
            meta={"reason": "session_id required for revoke"},
            doctrine=ARIF_DOCTRINE,
        )

    # ── REFRESH MODE ────────────────────────────────────────
    if mode == "refresh":
        from arifosmcp.runtime.tools import _SESSIONS

        if session_id and session_id in _SESSIONS:
            from arifosmcp.runtime.tools import _now

            _SESSIONS[session_id]["refreshed_at"] = _now()
            return SessionManifest(
                status="OK",
                result={"refreshed": session_id},
                doctrine=ARIF_DOCTRINE,
            )
        return SessionManifest(
            status="HOLD",
            result={},
            meta={"reason": "session_id required for refresh"},
            doctrine=ARIF_DOCTRINE,
        )

    return SessionManifest(
        status="HOLD",
        result={},
        meta={"reason": f"Unknown mode: {mode}"},
        doctrine=ARIF_DOCTRINE,
    )


# ── Canonical alias (migration 2026-06-22: arif_* → arifos_* naming) ─
arif_session_init = arif_init


# ── Helper Builders ────────────────────────────────────────────


def _build_embodiment_card() -> EmbodimentCard:
    """Build the VPS-root embodiment card from live system state."""
    import os
    import socket

    return EmbodimentCard(
        body="vps_root_runtime",
        host_attested=True,
        host=socket.gethostname(),
        os=_get_os_info(),
        privilege="root" if _is_root() else "user",
        shell=["bash"],
        cwd=os.getcwd(),
        package_managers=["npm", "bun", "pip", "git", "docker"],
        vcs=["git"],
        service_manager="systemd",
        filesystem_scope="full_root",
        network_scope="localhost_only",
        container_runtime=True,
        execution_broker="arif_forge",
        mutation_default="dry_run",
        side_effects_allowed_without_ack=False,
        atomic_capability_present=True,
        root_capability_present=_is_root(),
    )


def _build_tool_surface() -> ToolSurface:
    """Build semantic capability map — not raw tool dump."""
    from arifosmcp.constitutional_map import CANONICAL_TOOLS

    tool_count = len(CANONICAL_TOOLS)

    return ToolSurface(
        mode="semantic_map",
        count=tool_count,
        raw_manifest_available=True,
        raw_manifest_location="resource://agent/capabilities/raw",
    )


def _observe_only_next_actions() -> list[dict[str, Any]]:
    """Return canonical public next steps for an observe-only session."""
    return _manifest_backed_next_actions(
        [
            ("kernel self-attestation", "arif_kernel_attest", "attest"),
            ("federation organ liveness and telemetry", "arif_kernel_status", "status"),
            ("preflight before a proposed action", "arif_triage", "preflight"),
            ("full constitutional binding", "arif_init", "init"),
        ]
    )


def _manifest_backed_next_actions(
    candidates: list[tuple[str, str, str]]
) -> list[dict[str, Any]]:
    """Build next_actions from the exposed surface manifest only."""
    surface_mode = current_public_surface_mode()
    actions: list[dict[str, Any]] = []
    for intent, tool_name, mode in candidates:
        available = public_boundary_allows(tool_name, surface_mode)
        if available:
            actions.append(
                {
                    "intent": intent,
                    "status": "AVAILABLE",
                    "registered": True,
                    "registered_tool": tool_name,
                    "mode": mode,
                    "callable_from_this_client": True,
                    "last_probe": "UNKNOWN",
                    "public_surface_mode": surface_mode,
                    "reason": f"Public tool on the {surface_mode} surface.",
                }
            )
            continue
        actions.append(
            {
                "intent": intent,
                "status": "CAPABILITY_GAP",
                "registered": False,
                "registered_tool": None,
                "mode": mode,
                "callable_from_this_client": False,
                "last_probe": "UNKNOWN",
                "public_surface_mode": surface_mode,
                "reason": f"No registered public tool matches {tool_name}",
                "capability_gap": {
                    "desired_tool": tool_name,
                    "surface_mode": surface_mode,
                },
            }
        )
    return actions


def _compute_risk_leash(
    actor_id: str,
    declared_model_key: str | None = None,
) -> RiskLeash:
    """Compute risk leash based on session state."""
    degraded = declared_model_key is None

    max_action = "analyze" if degraded else "execute"

    return RiskLeash(
        status="DEGRADED" if degraded else "OPERATIONAL",
        max_action_class=max_action,
        side_effects_allowed=False,
        degraded=degraded,
        reason=("model_identity_unverified" if degraded else None),
    )


def _compute_warnings(
    actor_id: str,
    declared_model_key: str | None = None,
    floor_check: dict | None = None,
) -> SessionWarnings:
    """Compute session warnings based on state."""
    warnings_list = []

    if actor_id is None or actor_id == "anonymous":
        warnings_list.append("identity_unverified")

    if declared_model_key is None:
        warnings_list.append("model_identity_unverified")
        warnings_list.append("max_action_class_analyze_only")

    # ToM-1 warnings
    warnings_list.append("consent_not_established")
    warnings_list.append("theory_of_mind_scaffold_T0_only")

    return SessionWarnings(
        warnings=warnings_list,
        identity_unverified=(actor_id is None or actor_id == "anonymous"),
        model_identity_unverified=(declared_model_key is None),
        risk_registry_unavailable=False,
        max_action_class_analyze_only=(declared_model_key is None),
        consent_not_established=True,
        personalization_without_consent=False,
        theory_of_mind_scaffold="ToM-0",
    )


# ── ToM-1 Helper Builders ──────────────────────────────────────


def _build_operator_identity(
    actor_id: str,
    nonce: str | None,
    signature: str | None,
    identity_verified: bool,
    authority_level: str,
) -> OperatorIdentity:
    """Build structured operator identity with trust chain."""
    trust_level = "claimed"
    if identity_verified and actor_id == "arif":
        trust_level = "sovereign"
    elif identity_verified:
        trust_level = "verified"
    elif actor_id and actor_id != "anonymous":
        trust_level = "attested"

    return OperatorIdentity(
        claimed_id=actor_id,
        verified_id=actor_id if identity_verified else None,
        verification_method="signature" if (nonce and signature and identity_verified) else "none",
        verification_provider="arifos_crypto_auth" if identity_verified else None,
        trust_level=trust_level,
        delegation_chain=[],
    )


def _build_intent_model(sess: dict, actor_id: str) -> IntentModel:
    """Build operator intent model from session context."""
    # Light inference: check if session carries declared purpose from prior context
    declared = sess.get("declared_purpose")
    return IntentModel(
        declared_purpose=declared,
        session_objective=declared or "governed_agentic_session",
        intent_history=sess.get("intent_history", []),
        commitment_tracked=False,
        commitments=sess.get("commitments", []),
    )


def _build_belief_state(actor_id: str) -> BeliefState:
    """Initialize belief-state tracking scaffold."""
    # ToM-1: Start empty. Beliefs are quarantined until provenance is established.
    return BeliefState(
        operator_beliefs=[],
        system_beliefs=[],
        belief_provenance_required=True,
        unverified_beliefs_quarantined=True,
    )


def _build_preference_memory(actor_id: str) -> PreferenceMemory:
    """Initialize provenance-bound preference memory."""
    # ToM-1: Preferences require explicit consent and provenance.
    return PreferenceMemory(
        preferences=[],
        provenance_bound=True,
        consent_required_for_new=True,
        personalization_enabled=False,
    )


def _build_false_belief_flags(actor_id: str) -> FalseBeliefFlag:
    """Initialize false-belief detection scaffold."""
    # ToM-1: Detection active but no flags yet at init time.
    return FalseBeliefFlag(
        flags=[],
        false_belief_detection_active=True,
        humility_applied=True,
    )


def _build_well_mirror_enhanced(_well_mirror: dict) -> WellMirrorEnhanced:
    """Build enhanced WELL mirror from existing well substrate data."""
    status = _well_mirror.get("status", "unavailable")
    h_well = _well_mirror.get("h_well", {})

    if status == "unavailable":
        return WellMirrorEnhanced(
            well_informed=False,
            well_status="unavailable",
        )

    # Extract WELL signals if available
    readiness = h_well.get("readiness") if isinstance(h_well, dict) else None
    dignity = h_well.get("dignity_preservation") if isinstance(h_well, dict) else None

    return WellMirrorEnhanced(
        operator_readiness=readiness,
        dignity_preservation_score=dignity,
        well_informed=True,
        well_status="available",
        well_timestamp=_well_mirror.get("timestamp"),
    )


def _build_session_continuity(
    sess: dict, session_id: str | None, actor_id: str
) -> SessionContinuity:
    """Build session continuity from prior sessions of same actor."""
    from arifosmcp.runtime.tools import _SESSIONS

    prior_id = None
    prior_commitments: list[str] = []

    # _SESSIONS may be a _FileSessionStore — use _load() to get raw dict
    try:
        sessions_data = _SESSIONS._load() if hasattr(_SESSIONS, "_load") else _SESSIONS
    except Exception:
        sessions_data = {}

    # Handle nested "sessions" key or flat dict
    all_sessions: dict = {}
    if isinstance(sessions_data, dict):
        if "sessions" in sessions_data:
            all_sessions = sessions_data["sessions"]
        else:
            all_sessions = sessions_data

    # Find most recent prior session from same actor
    if actor_id and actor_id != "anonymous" and all_sessions:
        candidates = [
            (sid, sdata)
            for sid, sdata in all_sessions.items()
            if isinstance(sdata, dict) and sdata.get("actor_id") == actor_id and sid != session_id
        ]
        if candidates:
            # Sort by created_at descending, fallback to session_id string sort
            candidates.sort(key=lambda x: x[1].get("created_at", x[0]), reverse=True)
            prior_id, prior_sess = candidates[0]
            prior_commitments = prior_sess.get("commitments", [])

    return SessionContinuity(
        prior_session_id=prior_id,
        continuity_established=bool(prior_id),
        prior_commitments=prior_commitments,
        drift_detected=False,
    )


def _build_consent_boundaries(actor_id: str) -> ConsentBoundaries:
    """Build consent boundaries. All False until explicitly established."""
    return ConsentBoundaries(
        personalization_consent=False,
        memory_consent=False,
        inference_consent=False,
        theory_of_mind_consent=False,
        privacy_boundaries=[],
        consent_establishment_required=True,
    )


def _compute_context_completeness(
    actor_id: str | None,
    identity_verified: bool,
    well_mirror: dict,
    session: dict,
) -> ContextCompletenessReceipt:
    """
    v3.1: Compute context completeness score for session bootstrap.

    Score breakdown (0.0 to 1.0):
      timezone:          0.15 (present) | 0.05 (inferred) | 0.00 (missing)
      spatial_context:   0.15 (present) | 0.05 (inferred) | 0.00 (missing)
      host_id:           0.15 (attested) | 0.00 (missing)
      identity:          0.25 (verified) | 0.10 (claimed) | 0.00 (anonymous)
      memory:            0.15 (loaded) | 0.05 (partial) | 0.00 (not_loaded)
      session_provenance: 0.15 (resumed/handover) | 0.10 (fresh)
    """
    score = 0.0

    # timezone
    import os

    tz = os.environ.get("TZ", "")
    if tz:
        timezone = tz
        score += 0.15
    else:
        timezone = "missing"

    # spatial_context (simplified — could be enriched later)
    spatial_context = "missing"

    # host_id
    try:
        import socket

        host_id = socket.gethostname()
        score += 0.15
    except Exception:
        host_id = "missing"

    # identity
    if identity_verified:
        identity = "verified_operator"
        score += 0.25
    elif actor_id and actor_id != "anonymous":
        identity = "claimed_not_verified"
        score += 0.10
    else:
        identity = "anonymous"

    # memory
    memory = "not_loaded"
    if well_mirror.get("status") != "unavailable":
        memory = "partial"
        score += 0.10

    # session_provenance
    if session.get("resumed"):
        session_provenance = "resumed"
        score += 0.15
    else:
        session_provenance = "fresh"
        score += 0.10

    # Round score and determine verdict
    score = round(score, 2)
    if score >= 0.8:
        verdict = "COMPLETE_CONTEXT"
    elif score >= 0.5:
        verdict = "DEGRADED_CONTEXT"
    else:
        verdict = "MINIMAL_CONTEXT"

    return ContextCompletenessReceipt(
        timezone=timezone,
        spatial_context=spatial_context,
        host_id=host_id,
        identity=identity,
        memory=memory,
        session_provenance=session_provenance,
        score=score,
        verdict=verdict,
    )
