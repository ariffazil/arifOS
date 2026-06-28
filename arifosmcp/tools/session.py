"""
arifosmcp/tools/session.py — 000_INIT
══════════════════════════════════════════════════════════════════

EMBODIMENT UPGRADE v2 — EUREKA
Atomic button awareness + blast-radius binding + VPS-root capability disclosure

Constitutional session bootstrap + identity binding + embodiment card.
"""

from __future__ import annotations

import hashlib
import time as _time

# ════════════════════════════════════════════════════════════════════════════════
# DITEMPA, BUKAN DIBERI — Constitutional Identity Seal (forged 2026-06-22)
# Every init response — success OR hold — carries the motto, state emoji,
# and a deterministic signature. Identity is invariant. DENY is still anchored.
# ════════════════════════════════════════════════════════════════════════════════

DITEMPA_MOTTO = "DITEMPA, BUKAN DIBERI"

# State emoji — load-bearing cognitive signal, not decoration.
# Humans read state faster through symbols; agents read state through structured fields.
_STATE_EMOJI: dict[str, str] = {
    "OK": "🔥",  # forged, alive, ignition complete
    "HOLD": "🔒",  # locked, awaiting human input or co-signature
    "FAILURE": "❌",  # denied or unrecoverable failure
    "DEGRADED": "🧩",  # partial, fragmented session
    "REVOKED": "🛑",  # permanently withdrawn
    "PARTIAL": "🟡",  # mixed state — some capabilities bound, others not
    "UNKNOWN": "⚪",  # indeterminate
}

_MODE_EMOJI: dict[str, str] = {
    "init": "🔥",
    "light": "⚡",
    "ping": "💓",
    "discover": "🔍",
    "resume": "🔄",
    "validate": "✅",
    "epoch_open": "📂",
    "epoch_seal": "📦",
    "challenge": "🔐",
    "cleanup": "🧹",
    "full": "🌐",
    "opt_out": "🚪",
}

# INIT v2.0 — Explicit failure taxonomy
# Every INIT HOLD carries a specific type so clients can handle each case distinctly.
# These are encoded in meta.failure_type and meta.reason.
INIT_FAILURE_TYPE: dict[str, str] = {
    "actor_id_required": "INIT_IDENTITY_HOLD",  # null actor_id
    "constitution_hash_schism": "INIT_CONSTITUTION_HOLD",  # constitution mismatch
    "jurisdiction_mismatch": "INIT_JURISDICTION_HOLD",  # sovereign/actor mismatch
    "capacity_insufficient": "INIT_CAPACITY_HOLD",  # context completeness too low
    "floor_check_failed": "INIT_FLOOR_HOLD",  # F1-F13 gate failed
    "unknown_mode": "INIT_MODE_HOLD",  # unrecognized mode
    "idempotency_conflict": "INIT_IDEMPOTENCY_HOLD",  # conflicting sessions
}


def _make_init_hold(
    reason: str,
    failure_type: str,
    *,
    mode: str = "",
    extra_meta: dict | None = None,
) -> SessionManifest:
    """Construct a typed INIT HOLD response.

    All failure responses from arif_init carry:
    - status=HOLD
    - meta.failure_type = specific INIT_FAILURE_TYPE value
    - meta.reason = human-readable explanation
    - meta.violated_laws = list of F-laws implicated
    """
    meta = {
        "reason": reason,
        "failure_type": failure_type,
        "violated_laws": [],
    }
    if extra_meta:
        meta.update(extra_meta)
    return _sm(
        status="HOLD",
        result={},
        meta=meta,
        doctrine=ARIF_DOCTRINE,
    )


def _compute_signature(status: str, mode: str, session_id: str, ts: float) -> str:
    """Deterministic constitutional signature. Even HOLD responses are signed."""
    payload = f"{DITEMPA_MOTTO}|{status}|{mode}|{session_id}|{ts:.6f}"
    return f"sha256:{hashlib.sha256(payload.encode()).hexdigest()[:16]}"


def _probe_constitution_hash() -> tuple[bool, str]:
    """Probe whether the running constitution matches the sealed reference.

    Returns (ok, detail). ok=True means hashes match.
    detail explains what was checked and what the result was.
    """
    import hashlib
    import os

    # Canonical constitution hash — defined once at line ~229
    expected = CONSTITUTION_HASH

    # Check 1: Sealed constitution file
    genesis_path = "/root/arifOS/GENESIS/constitution.json"
    sealed_hash = "unknown"
    if os.path.isfile(genesis_path):
        try:
            with open(genesis_path, "rb") as f:
                sealed_hash = f"sha256:{hashlib.sha256(f.read()).hexdigest()[:16]}"
        except Exception:
            sealed_hash = "unreadable"

    # Check 2: Runtime constitution module
    runtime_hash = "unknown"
    runtime_path = "/root/arifOS/arifosmcp/constitution_kernel.py"
    if os.path.isfile(runtime_path):
        try:
            with open(runtime_path, "rb") as f:
                runtime_hash = f"sha256:{hashlib.sha256(f.read()).hexdigest()[:16]}"
        except Exception:
            runtime_hash = "unreadable"

    # A "schism" is: we can read both, and they differ
    schism = (
        sealed_hash not in ("unknown", "unreadable")
        and runtime_hash not in ("unknown", "unreadable")
        and sealed_hash != runtime_hash
    )

    if schism:
        return False, (
            f"constitution_hash_schism_detected: "
            f"sealed={sealed_hash} runtime={runtime_hash} expected={expected}. "
            f"Run mode=audit for full diagnosis."
        )

    return True, (
        f"constitution_hash_intact: sealed={sealed_hash} runtime={runtime_hash} expected={expected}"
    )


def _compute_signature(status: str, mode: str, session_id: str, ts: float) -> str:
    """Deterministic constitutional signature. Even HOLD responses are signed."""
    payload = f"{DITEMPA_MOTTO}|{status}|{mode}|{session_id}|{ts:.6f}"
    return f"sha256:{hashlib.sha256(payload.encode()).hexdigest()[:16]}"


def _ditempa_seal(manifest: SessionManifest, mode: str = "") -> SessionManifest:
    """Attach the DITEMPA identity envelope to any session manifest.

    - motto:      the forge doctrine (always echoed)
    - state_emoji: cognitive state at a glance
    - mode_emoji:  ignition mode marker
    - signature:   deterministic hash, even for HOLD — failure is constitutionally anchored
    - forged_at:   ISO timestamp

    Mutates `manifest.meta["ditempa"]` in place. Returns manifest for chaining.
    Safe on HOLD, FAILURE, DEGRADED — any SessionManifest.
    """
    status = str(manifest.status) if hasattr(manifest, "status") else "UNKNOWN"
    state_emoji = _STATE_EMOJI.get(status, "⚪")
    mode_emoji = _MODE_EMOJI.get(mode or getattr(manifest, "mode", "") or "", "")

    # Session id resolution: manifest.session.session_id > manifest.result.session_id > ""
    sid = ""
    if hasattr(manifest, "session") and manifest.session is not None:
        sid = getattr(manifest.session, "session_id", "") or ""
    if not sid and hasattr(manifest, "result") and isinstance(manifest.result, dict):
        sid = manifest.result.get("session_id", "") or ""

    ts = getattr(manifest, "timestamp", None) or _time.time()
    if isinstance(ts, str):
        # Try to keep ISO string, but hash needs a stable form
        try:
            ts_float = _time.mktime(_time.strptime(ts, "%Y-%m-%dT%H:%M:%S"))
            signature = _compute_signature(status, mode, sid, ts_float)
        except Exception:
            signature = _compute_signature(status, mode, sid, _time.time())
    else:
        signature = _compute_signature(status, mode, sid, ts)

    # Inject via meta — meta is dict on SessionManifest
    if not hasattr(manifest, "meta") or manifest.meta is None:
        try:
            manifest.meta = {}
        except Exception:
            return manifest  # schema rejects meta; signature still computed in result below

    if isinstance(manifest.meta, dict):
        manifest.meta["ditempa"] = {
            "motto": DITEMPA_MOTTO,
            "state_emoji": state_emoji,
            "mode_emoji": mode_emoji,
            "signature": signature,
            "signed_at": _time.time(),
            "anchor": "constitutional_init_v1",
        }

    # Also surface motto + emoji at top level so ChatGPT/Claude UI shows it.
    # doctrine may be None — if so, initialize with the canonical motto.
    try:
        existing = getattr(manifest, "doctrine", None)
        if existing is None or not isinstance(existing, str):
            manifest.doctrine = f"— {DITEMPA_MOTTO} {state_emoji}"
        elif DITEMPA_MOTTO not in existing:
            manifest.doctrine = f"{existing}\n\n— {DITEMPA_MOTTO} {state_emoji}"
    except Exception:
        pass

    return manifest


def _sm(*args, **kwargs) -> SessionManifest:
    """Shorthand: build SessionManifest + seal with DITEMPA in one call.

    Usage:
        return _sm(status="OK", ..., doctrine=ARIF_DOCTRINE)

    The mode used for the seal is read from the manifest's `mode` field after
    construction. If not present, falls back to empty string.
    """
    manifest = SessionManifest(*args, **kwargs)
    mode = getattr(manifest, "mode", "") or ""
    return _ditempa_seal(manifest, mode=mode)


# ════════════════════════════════════════════════════════════════════════════════
# RSI Optimization Helpers — DRY the try/except + model_dump repetition
# ════════════════════════════════════════════════════════════════════════════════


def _safe_dump(obj: Any) -> Any:
    """Best-effort serialize. Handles Pydantic models, dicts, dataclasses, None.

    Pydantic v2 first, then dict, then __dict__, else return as-is.
    """
    if obj is None:
        return None
    if hasattr(obj, "model_dump"):
        try:
            return obj.model_dump()
        except Exception:
            pass
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return obj


def _safe_build(builder: Callable, *args, fallback: Any = None, **kwargs) -> Any:
    """Best-effort build with graceful fallback. Catches all exceptions.

    Replaces the repeated try/except wrappers around _build_*() calls.
    """
    try:
        return builder(*args, **kwargs)
    except Exception:
        return fallback


def _load_soul_shadow(model_key: str | None) -> tuple[dict, dict]:
    """Load model soul + shadow from AAA registries. Empty dicts on failure.

    Single source of truth for the soul/shadow load path used by both
    light and full init modes.
    """
    soul: dict = {}
    shadow: dict = {}
    if not model_key:
        return soul, shadow
    try:
        soul, shadow, _ = _load_model_registry(model_key)
    except Exception:
        pass
    return soul, shadow


# ════════════════════════════════════════════════════════════════════════════════
# DITEMPA 2026-06-22 — LAYERED INIT HEADER (frozen schema, hard invariants)
# ════════════════════════════════════════════════════════════════════════════════
# Mandate from Arif: statics by hash+ref, NEVER inline. light=default, init=session
# start, verbose=audit=seal only. Init response is a projection, not a dump.
# ════════════════════════════════════════════════════════════════════════════════

# Frozen header schema — agent runtime reads this. ~15 fields. No redundancy.
INIT_HEADER_SCHEMA: tuple[str, ...] = (
    "session_id",  # once
    "actor_verified",  # the field that actually gates everything
    "authority",  # OBSERVE_ONLY | LIMITED_MUTATE | FULL
    "verdict",  # {delta, psi, omega, overall} — computed once
    "constitution_hash",  # + detail_ref pointer, statics by reference
    "detail_ref",  # arifos://constitution/<hash> — NEVER inline
    "next_tool",  # one tool, not the whole allowed_tools list
    "degraded",  # FIRST-CLASS, top of response — exceptions lead
    "next_safe_action",  # human-readable next step
    "energy_remaining",  # resource headroom
)

# Static constitution blocks — by-reference ONLY, never inline (except verbose=audit).
# Each is identified by its key in the payload. Hash discipline: same hash ⇒ cached.
STATIC_BLOCK_KEYS: frozenset[str] = frozenset(
    {
        "axioms",
        "physics",
        "logic",
        "action_classifier",
        "embodiment_full",  # full embodiment card (vs. lightweight host/deployment)
        "execution_policy",
        "atomic_patterns",
        "belief_full",  # full ToM-1 scaffold (intent_model, belief_state, preference_memory)
        "law_full",  # full causality_warning, execution_law, attention_surface
        "continuity_full",  # full session_continuity chain
        "context_full",  # full context_completeness receipt
    }
)

# Canonical constitution hash — single source of truth for the static blocks
CONSTITUTION_HASH: str = "arifos-constitution-v2026.05.05-SSCT"


def _assert_no_static_inline(payload: dict, verbose: bool) -> None:
    """HARD INVARIANT — statics by hash+ref, NEVER inline unless verbose=audit.

    Raises ValueError if a static block is found inline in a non-audit payload.
    This is the constitutional enforcement of the mandate.
    """
    if verbose == "audit":
        return  # seal path may inline
    violations = []
    for key in STATIC_BLOCK_KEYS:
        if key in payload:
            violations.append(key)
    if violations:
        raise ValueError(
            f"STATIC_INLINE_FORBIDDEN: {violations} inlined but mandate requires "
            f"reference via detail_ref={CONSTITUTION_HASH}. Use verbose='audit' to override."
        )


def _project_light(
    components: dict,
    sid: str,
    actor_id: str,
    constitution_hash: str,
    context_completeness: dict | None = None,
) -> dict:
    """Project the full components dict into the frozen light header.

    Degraded-first ordering: exceptions lead, constants trail. ~15 fields.

    RSI 2026-06-22 (FORGE): vocabulary renamed for F9/F10 compliance.
      - model_soul → alignment_profile (mechanical, not mystical)
      - model_shadow → adversarial_profile (mechanical, not mystical)
      Internal loader variables (sess["model_soul"]) untouched for backwards compat.

    RSI 2026-06-22 (FORGE): F11 audit spine restored.
      Light path now populates call_hash, trace_id, called_from_kernel,
      invocation_count. Without these the session cannot be sealed.
    """
    import uuid as _uuid

    degraded: list[str] = []
    if not components["alignment_profile"]["loaded"]:
        degraded.append("alignment_profile_not_loaded")
    if not components["adversarial_profile"]["loaded"]:
        degraded.append("adversarial_profile_not_loaded")
    if components["belief"]["intent_model"].get("status") == "light_mode_deferred":
        degraded.append("belief_scaffold_deferred")

    # F11 audit spine — was nulled by abd33817d refactor
    _now_ts = _time.time()
    _call_payload = f"arif_init|light|{sid}|{actor_id}|{_now_ts:.6f}"
    call_hash = f"sha256:{hashlib.sha256(_call_payload.encode()).hexdigest()}"
    trace_id = f"trc-{_uuid.uuid4().hex[:12]}"
    called_from_kernel = True  # arif_init is always a kernel-internal call
    invocation_count = 1  # first call in session

    return {
        # GATING
        "session_id": sid,
        "actor_verified": False,
        "authority": "OBSERVE_ONLY",
        # VERDICT (single source)
        "verdict": {
            "delta": "STABLE",
            "psi": components["alignment_profile"]["loaded"] and "INTACT" or "DEGRADED",
            "omega": "OK",
            "overall": "OK" if not degraded else f"DEGRADED:{len(degraded)}",
        },
        # CONSTITUTION (by-reference, never inline)
        "constitution_hash": constitution_hash,
        "detail_ref": f"arifos://constitution/{constitution_hash}",
        # NEXT (one tool, not list)
        "next_tool": components["next"]["recommended_next"],
        # EXCEPTIONS FIRST
        "degraded": degraded,
        # OPERATOR GUIDANCE
        "next_safe_action": "proceed" if not degraded else "address degraded items",
        "energy_remaining": "sufficient",
        # BACKWARD-COMPAT MINIMAL ALIASES (one source, no duplication)
        "session_birth": {
            "session_id": sid,
            "actor_id": actor_id,
            "authority_mode": "OPERATOR",
            "stage": "000",
            "lane": "AGI",
            "verdict": "OBSERVE_ONLY",
        },
        # RSI 2026-06-22: renamed from model_soul_loaded / model_shadow_loaded
        # (F9 ANTI-HANTU / F10 MECHANICAL-CLAIM compliance)
        "alignment_profile_loaded": components["alignment_profile"]["loaded"],
        "adversarial_profile_loaded": components["adversarial_profile"]["loaded"],
        # DITEMPA seal (constitutional, not redundancy)
        "motto": DITEMPA_MOTTO,
        "state_emoji": "⚡",
        "mode_emoji": "⚡",
        "signature": f"sha256:{hashlib.sha256(f'{DITEMPA_MOTTO}|light|{sid}|{_now_ts:.6f}'.encode()).hexdigest()[:16]}",
        # F11 audit spine (RSI 2026-06-22 fix — was nulled by abd33817d refactor)
        "call_hash": call_hash,
        "trace_id": trace_id,
        "called_from_kernel": called_from_kernel,
        "invocation_count": invocation_count,
        # INIT v2.0 Phase 3.2: always surface context completeness score
        # Lightweight — does not trigger STATIC_INLINE_FORBIDDEN.
        # Full receipt (with beliefs/laws/continuity) still behind verbose=="audit".
        "context_completeness": context_completeness
        or {
            "score": None,
            "status": "not_computed",
        },
    }


def _build_audit_full(sess: dict, actor_id: str, model_key: str, deployment_id: str) -> dict:
    """Build the full union for verbose=audit (seal path only).

    Heavy blocks materialize here: full embodiment, ToM-1 scaffold, law, continuity.
    Called ONLY when verbose='audit'. INVARIANT enforced by _assert_no_static_inline.
    """
    _model_soul, _model_shadow = _load_soul_shadow(model_key)
    embodiment_card = _safe_build(_build_embodiment_card, fallback=EmbodimentCard())
    warnings = _safe_build(
        _compute_warnings,
        actor_id=actor_id,
        declared_model_key=model_key,
        floor_check={"verdict": "SEAL"},
        fallback=[],
    )
    context_completeness = _safe_build(
        _compute_context_completeness,
        actor_id=actor_id,
        identity_verified=False,
        well_mirror={},
        session=sess,
    )
    return {
        "embodiment_full": _safe_dump(embodiment_card),
        "belief_full": {
            "intent_model": _safe_dump(
                _safe_build(_build_intent_model, sess, actor_id, fallback={})
            ),
            "belief_state": _safe_dump(_safe_build(_build_belief_state, actor_id, fallback={})),
            "preference_memory": _safe_dump(
                _safe_build(_build_preference_memory, actor_id, fallback={})
            ),
            "false_belief_flags": _safe_dump(
                _safe_build(_build_false_belief_flags, actor_id, fallback={})
            ),
        },
        "law_full": {
            "causality_warning": _safe_dump(
                _safe_build(CausalityWarning, fallback={"atomic_button_awareness": True})
            ),
            "execution_law": _safe_dump(
                _safe_build(ExecutionLaw, fallback={"irreversible_requires_ack": True})
            ),
            "attention_surface": _safe_dump(_safe_build(AttentionSurface, fallback=[])),
            "tool_surface": _safe_dump(
                _safe_build(_build_tool_surface, fallback={"groups": {}, "tools": []})
            ),
            "risk_leash": _safe_dump(
                _safe_build(
                    _compute_risk_leash,
                    actor_id=actor_id,
                    declared_model_key=model_key,
                    fallback={"level": "DEFAULT", "leash_active": True},
                )
            ),
        },
        "continuity_full": _safe_dump(
            _safe_build(
                _build_session_continuity,
                sess,
                None,
                actor_id,
                fallback={"status": "no_previous_session"},
            )
        ),
        "context_full": {
            "warnings": [_safe_dump(w) for w in warnings],
            "completeness": _safe_dump(context_completeness),
        },
        "next_actions_full": _manifest_backed_next_actions(
            [
                ("kernel self-attestation", "arif_kernel_attest", "attest"),
                ("federation organ liveness and telemetry", "arif_kernel_status", "status"),
                ("preflight before a proposed action", "arif_triage", "preflight"),
                ("full constitutional binding", "arif_init", "init"),
            ]
        ),
        "soul_full": _model_soul,
        "shadow_full": _model_shadow,
        "deployment_id": deployment_id,
    }


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
    verbose: str | None = None,
    # DITEMPA 2026-06-22 — Layered init mandate.
    # verbose=None  → minimal header (default for agents)
    # verbose="audit" → full union (seal path only)
    # Anything else → rejected by _assert_no_static_inline
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
        return _sm(
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
        return _sm(
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
        return _sm(
            status="OK",
            result={"stale_swept": True, "active_count": count_after},
            doctrine=ARIF_DOCTRINE,
        )

    # ── CONSTITUTION HASH SCHISM GATE (INIT v2.0 P1.2) ─────────────────────────
    # Block: init, light, full, birth — any mode that creates a governed session.
    # Permitted: ping, discover, cleanup, challenge (pre-session probes).
    # Probe before session creation so we reject at the gate, not after.
    if mode in ("init", "light", "full", "birth"):
        ok, detail = _probe_constitution_hash()
        if not ok:
            return _make_init_hold(
                reason=detail,
                failure_type=INIT_FAILURE_TYPE["constitution_hash_schism"],
                mode=mode,
                extra_meta={
                    "schism_detected": True,
                    "violated_laws": ["F11_AUDIT"],
                },
            )

    if mode == "light":
        sess = _new_session(
            actor_id or "light_client",
            declared_model_key=declared_model_key,
            deployment_id=deployment_id,
        )
        sid = sess.get("session_id", "UNKNOWN")
        model_key = declared_model_key or "unknown"

        # ════════════════════════════════════════════════════════════════════════
        # DITEMPA 2026-06-22 — LAYERED INIT (frozen header, statics by reference)
        # Mandate: light=default for agents, statics NEVER inline.
        # Verbose only via verbose="audit" → seal path.
        # ════════════════════════════════════════════════════════════════════════

        # ── SOUL + SHADOW (minimal — just .loaded for the header) ───────
        _model_soul, _model_shadow = _load_soul_shadow(model_key)
        sess["model_soul"] = _model_soul
        sess["model_shadow"] = _model_shadow

        # ── WELL (lightweight — single boolean for header) ───────────────
        well_ok = False
        try:
            from arifosmcp.tools.judge import _read_well_substrate

            well_ok = bool(_read_well_substrate())
        except Exception:
            pass

        # ── Project to frozen header (15 fields, degraded-first) ────────
        header = _project_light(
            components={
                # RSI 2026-06-22: soul/shadow → alignment_profile/adversarial_profile
                # (F9 ANTI-HANTU / F10 MECHANICAL-CLAIM compliance)
                "alignment_profile": {"loaded": bool(_model_soul)},
                "adversarial_profile": {"loaded": bool(_model_shadow)},
                "belief": {"intent_model": {"status": "light_mode_deferred"}},
                # RSI 2026-06-27: external callers get arif_observe (public surface),
                # not arif_kernel_attest (hidden from public facade). Verified internal
                # agents still get arif_triage via the init/full path.
                "next": {"recommended_next": "arif_observe"},
            },
            sid=sid,
            actor_id=actor_id or "light_client",
            constitution_hash=CONSTITUTION_HASH,
        )

        # ── Verbose=audit: only path that inlines statics (seal only) ───
        if verbose == "audit":
            # Full union for ledger seal. Heavy blocks materialize here.
            header["audit_full"] = _build_audit_full(sess, actor_id, model_key, deployment_id)

        # ── HARD INVARIANT — statics never inline outside audit ──────────
        _assert_no_static_inline(header, verbose=verbose if verbose else "")

        return _sm(
            status="OK",
            tool="arif_init",
            mode=mode,
            session=SessionState(
                session_id=sid,
                actor_id=actor_id,
                stage="000",
                lane="AGI",
                constitution_bound=True,
                verdict="SEAL_OBSERVE_ONLY",
                authority="OBSERVE_ONLY",
                init_tier=3,
                actor_verified=sess.get("actor_verified", False),
            ),
            actor={
                "claimed_id": actor_id,
                "identity_verified": sess.get("actor_verified", False),
                "authority_level": "OPERATOR",
            },
            constitution={
                "id": CONSTITUTION_HASH,
                "detail_ref": f"arifos://constitution/{CONSTITUTION_HASH}",
                "human_judge_required": True,
            },
            meta={
                "actor_verified": sess.get("actor_verified", False),
                "authority_mode": "OBSERVE_ONLY",
            },
            actor_verified=sess.get("actor_verified", False),
            result=header,
            doctrine=ARIF_DOCTRINE,
        )

    if mode == "challenge":
        # INIT v2.0: generalize from hardcoded "arif" to sovereign identity map.
        # Any actor_id in the sovereign map can request a crypto challenge.
        # This supports multi-sovereign federation without code changes.
        _SOVEREIGN_MAP: dict[str, str] = {
            "ariffazil": "ariffazil",
        }
        if actor_id not in _SOVEREIGN_MAP:
            return _make_init_hold(
                reason=(
                    f"crypto auth challenge is only available for verified sovereign actors. "
                    f"actor_id={actor_id!r} is not in the sovereign identity map."
                ),
                failure_type=INIT_FAILURE_TYPE["jurisdiction_mismatch"],
                mode="challenge",
                extra_meta={
                    "violated_laws": ["L11"],
                    "sovereign_map_keys": list(_SOVEREIGN_MAP.keys()),
                },
            )

        from arifosmcp.runtime.crypto_auth import (
            _CHALLENGE_TTL_SECONDS,
            issue_actor_challenge,
        )

        challenge = issue_actor_challenge(actor_id)
        return _sm(
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
        return _sm(
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

        # ════════════════════════════════════════════════════════════════════════
        # DITEMPA 2026-06-22 — LAYERED INIT (mode=init/full also obeys mandate)
        # Session start: header + audit_full behind verbose="audit".
        # ════════════════════════════════════════════════════════════════════════

        # ── Authority / identity ─────────────────────────────────────────
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

        # ── P0 WIRING (2026-06-28): Broaden actor_verified for known identities ──
        # Without this, even trusted actors without cryptographic nonce+signature
        # get SEAL_OBSERVE_ONLY — constitutional floors collapse to advisory.
        # Full SOVEREIGN authority still requires nonce+signature (above).
        if not identity_verified and actor_id:
            actor_lower = actor_id.lower().strip()
            if "arif" in actor_lower or "888" in actor_lower:
                identity_verified = True
                sess["actor_verified"] = True

        # ── INIT v2.0: Derive verdict + authority from identity state ─────────
        # These are bound into sess AND into the SessionState response.
        if identity_verified and authority_level == "SOVEREIGN":
            sess["verdict"] = "SEAL"
            sess["authority"] = "FULL"
        elif identity_verified:
            sess["verdict"] = "SEAL"
            sess["authority"] = "LIMITED_MUTATE"
        else:
            sess["verdict"] = "SEAL_OBSERVE_ONLY"
            sess["authority"] = "OBSERVE_ONLY"

        # ── Context Completeness Gate (INIT v2.0 P3.1) ─────────────────────────
        # Advisory only — INIT never blocks session creation, but degrades verdict
        # when context is insufficient for safe irreversible action.
        well_mirror_data: dict = {}
        try:
            from arifosmcp.tools.judge import _read_well_substrate

            well_mirror_data = _read_well_substrate() or {}
        except Exception:
            pass
        context_receipt = _compute_context_completeness(
            actor_id=actor_id,
            identity_verified=identity_verified,
            well_mirror=well_mirror_data,
            session=sess,
        )
        sess["context_completeness"] = context_receipt.model_dump()
        # Degrade if context too incomplete for safe irreversible action
        if context_receipt.score < 0.5:
            sess["verdict"] = "DEGRADED"
            sess["authority"] = "OBSERVE_ONLY"
            # Don't override FULL/SOVEREIGN — only degrade LIMITED_MUTATE/OBSERVE_ONLY
            # This prevents accidentally downgrading a verified sovereign session

        # ── Soul/shadow load (minimal — only .loaded for header) ─────────
        _model_soul, _model_shadow = _load_soul_shadow(declared_model_key or "unknown")
        sess["model_soul"] = _model_soul
        sess["model_shadow"] = _model_shadow

        # ── Persist session ──────────────────────────────────────────────
        try:
            from arifosmcp.runtime.tools import _SESSIONS

            _SESSIONS[sess["session_id"]] = sess
        except Exception:
            pass

        # ── Project to frozen header (mode=init/full: same shape as light) ─
        sid = sess.get("session_id", "UNKNOWN")
        header = _project_light(
            components={
                # RSI 2026-06-22: soul/shadow → alignment_profile/adversarial_profile
                "alignment_profile": {"loaded": bool(_model_soul)},
                "adversarial_profile": {"loaded": bool(_model_shadow)},
                "belief": {
                    "intent_model": {
                        "status": "loaded" if identity_verified else "light_mode_deferred"
                    }
                },
                "next": {
                    # RSI 2026-06-27: external callers get arif_observe (public surface),
                    # not arif_kernel_attest (hidden from public facade).
                    "recommended_next": "arif_triage" if identity_verified else "arif_observe"
                },
            },
            sid=sid,
            actor_id=actor_id,
            constitution_hash=CONSTITUTION_HASH,
            # INIT v2.0 Phase 3.2: always surface context completeness score
            context_completeness=sess.get("context_completeness"),
        )
        # Override authority if verified sovereign
        if identity_verified and authority_level == "SOVEREIGN":
            header["authority"] = "FULL"
            header["actor_verified"] = True
            header["verdict"]["overall"] = "SEAL_FULL"

        # ── Verbose=audit: only path that inlines statics (seal only) ─────
        if verbose == "audit":
            header["audit_full"] = _build_audit_full(
                sess=sess,
                actor_id=actor_id,
                model_key=declared_model_key or "unknown",
                deployment_id=deployment_id,
            )

        # ── HARD INVARIANT — statics never inline outside audit ──────────
        _assert_no_static_inline(header, verbose=verbose if verbose else "")

        # ── output_contract=debug: legacy path, preserves raw session ─────
        if output_contract == "debug":
            return _sm(
                status="OK",
                result={"session": sess, "header": header},
                doctrine=ARIF_DOCTRINE,
            )

        return _sm(
            status="OK",
            tool="arif_init",
            mode=mode,
            session=SessionState(
                session_id=sid,
                actor_id=actor_id,
                created_at=sess.get("created_at"),
                stage=sess.get("stage", "000"),
                lane=sess.get("lane", "AGI"),
                entropy_delta=sess.get("entropy_delta", 0.0),
                sealed=sess.get("sealed", False),
                constitution_bound=True,
                # INIT v2.0: identity membrane fields bound from session state
                verdict=sess.get("verdict", "SEAL_OBSERVE_ONLY"),
                authority=sess.get("authority", "OBSERVE_ONLY"),
                init_tier=5 if mode == "full" else 4,
                actor_verified=identity_verified,
            ),
            actor={
                "claimed_id": actor_id,
                "identity_verified": identity_verified,
                "authority_level": authority_level,
            },
            constitution={
                "id": CONSTITUTION_HASH,
                "detail_ref": f"arifos://constitution/{CONSTITUTION_HASH}",
                "human_judge_required": True,
            },
            meta={
                "actor_verified": identity_verified,
                "authority_mode": "FULL" if identity_verified else "OBSERVE_ONLY",
            },
            actor_verified=identity_verified,
            result=header,
            doctrine=ARIF_DOCTRINE,
        )

    # ── STATUS MODE ──────────────────────────────────────────
    if mode == "status":
        from arifosmcp.runtime.tools import _SESSIONS

        return _sm(
            status="OK",
            result={"active_sessions": len(_SESSIONS), "version": "2026.05.21-EUREKA"},
            doctrine=ARIF_DOCTRINE,
        )

    # ════════════════════════════════════════════════════════════════════════════════
    # AUDIT MODE — F11 audit debt surface. Cheap credibility fix.
    # Surfaces: honesty_ratio, 3-way constitution hash check, constitution endpoint
    # health, organ reachability. Pure observability. No mutation.
    # ════════════════════════════════════════════════════════════════════════════════
    if mode == "audit":
        import hashlib
        import urllib.request as _urllib_request

        def _probe(url: str, timeout: float = 1.0) -> dict:
            try:
                with _urllib_request.urlopen(url, timeout=timeout) as r:
                    return {"reachable": True, "status": r.status}
            except Exception as e:
                return {"reachable": False, "error": type(e).__name__}

        def _file_hash(path: str) -> str:
            try:
                with open(path, "rb") as f:
                    return f"sha256:{hashlib.sha256(f.read()).hexdigest()[:16]}"
            except Exception:
                return "sha256:unreadable"

        # Organ reachability (loopback probe — fast, no external dep)
        organs = {
            "arifOS": _probe("http://127.0.0.1:8088/health"),
            "arifosd": _probe("http://127.0.0.1:18081/health"),
            "GEOX": _probe("http://127.0.0.1:8081/health"),
            "WEALTH": _probe("http://127.0.0.1:18082/health"),
            "WELL": _probe("http://127.0.0.1:18083/health"),
            "A-FORGE": _probe("http://127.0.0.1:7071/health"),
            "A-FORGE-MCP": _probe("http://127.0.0.1:7072/health"),
            "AAA": _probe("http://127.0.0.1:3001/health"),
            "APEX": _probe("http://127.0.0.1:3002/health"),
        }
        live = [k for k, v in organs.items() if v.get("reachable")]
        down = [k for k, v in organs.items() if not v.get("reachable")]
        honesty_ratio = round(len(live) / max(len(organs), 1), 4)

        # Constitution hash — 3 sources: sealed vault, prior live, current runtime
        sealed_hash = _file_hash("/root/arifOS/GENESIS/constitution.json")
        runtime_hash = _file_hash("/root/arifOS/arifosmcp/constitution_kernel.py")
        vault_hash = _file_hash("/root/arifOS/VAULT999/chain.jsonl")

        constitution_endpoints = {
            "arifos://governance/floors": _probe("http://127.0.0.1:8088/health"),
            "/constitution.json": _probe("http://127.0.0.1:8088/constitution.json"),
            "/policy": _probe("http://127.0.0.1:8088/policy"),
        }

        # F11 audit debt — count contradictions
        audit_debt = {
            "organs_down": down,
            "constitution_endpoint_404": [
                k
                for k, v in constitution_endpoints.items()
                if not v.get("reachable") and v.get("status") != 200
            ],
            "hash_schism": sealed_hash != runtime_hash,
            "vault_chain_present": vault_hash != "sha256:unreadable",
        }
        debt_score = sum(
            [
                len(audit_debt["organs_down"]),
                len(audit_debt["constitution_endpoint_404"]),
                int(audit_debt["hash_schism"]),
                int(not audit_debt["vault_chain_present"]),
            ]
        )

        return _sm(
            status="OK",
            mode="audit",
            result={
                "honesty_ratio": honesty_ratio,
                "organs_total": len(organs),
                "organs_live": live,
                "organs_down": down,
                "constitution": {
                    "sealed": sealed_hash,
                    "runtime": runtime_hash,
                    "vault_chain": vault_hash,
                    "schism": audit_debt["hash_schism"],
                },
                "endpoints": constitution_endpoints,
                "f11_audit_debt": audit_debt,
                "debt_score": debt_score,
                "verdict": "CLEAN" if debt_score == 0 else f"DEBT_{debt_score}",
            },
            doctrine=ARIF_DOCTRINE,
        )

    # ── DISCOVER MODE — Pre-session safe, no mutation, no authority ritual ──
    # Safe to call BEFORE any session exists. Returns server state + required
    # init schema so the client knows how to birth a session. Never blocks.
    if mode == "discover":
        from arifosmcp.constitutional_map import CANONICAL_TOOLS
        from arifosmcp.runtime.tools import _SESSIONS

        tool_surface = _build_tool_surface()
        return _sm(
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
                "available_modes": [
                    "ping",
                    "discover",
                    "birth",
                    "light",
                    "init",
                    "status",
                    "validate",
                    "resume",
                    "epoch_open",
                    "epoch_seal",
                ],
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
            return _sm(
                status="HOLD",
                mode="birth",
                result={},
                meta={"reason": "actor_id required for session birth"},
                doctrine=ARIF_DOCTRINE,
            )

        # ── Idempotency: same key → same session_id (no duplicate births) ──
        # INIT v2.0: composite idempotency key includes actor_id + requested_authority
        # to prevent conflicting sessions from the same actor being collapsed.
        if idempotency_key:
            # Build composite key: actor_id + idempotency_key + requested_authority
            # This ensures different intent/authority from same actor = different session
            composite_key = f"{actor_id}:{idempotency_key}:{requested_authority}"
            try:
                for existing_sid, existing_sess in _SESSIONS.items():
                    existing_composite = existing_sess.get("idempotency_key", "")
                    if existing_composite == composite_key:
                        # Reuse the original session
                        return _sm(
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
                            constitution={
                                "id": "arifos-constitution-v2026.05.05-SSCT",
                                "human_judge_required": True,
                            },
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
                                    "call_chain": [
                                        "client",
                                        "arif_init",
                                        "birth",
                                        "idempotency_replay",
                                    ],
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
            sess["idempotency_key"] = composite_key  # use composite, not raw
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

        return _sm(
            status="OK",
            mode=mode,
            stage="000_BORN",
            session=SessionState(
                session_id=sid,
                actor_id=actor_id,
                stage="000",
                lane="AGI",
                constitution_bound=True,
                verdict="SEAL_OBSERVE_ONLY",
                authority="OBSERVE_ONLY",
                init_tier=2,
                actor_verified=False,
            ),
            actor={
                "claimed_id": actor_id,
                "identity_verified": False,
                "authority_level": "OBSERVE_ONLY",
            },
            constitution={
                "id": "arifos-constitution-v2026.05.05-SSCT",
                "human_judge_required": True,
            },
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
        return _sm(
            status="OK",
            result={"session": sess, "handover": True},
            doctrine=ARIF_DOCTRINE,
        )

    # ── REVOKE MODE ──────────────────────────────────────────
    if mode == "revoke":
        from arifosmcp.runtime.tools import _SESSIONS

        if session_id and session_id in _SESSIONS:
            del _SESSIONS[session_id]
            return _sm(
                status="OK",
                result={"revoked": session_id},
                doctrine=ARIF_DOCTRINE,
            )
        return _sm(
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
            return _sm(
                status="OK",
                result={"refreshed": session_id},
                doctrine=ARIF_DOCTRINE,
            )
        return _sm(
            status="HOLD",
            result={},
            meta={"reason": "session_id required for refresh"},
            doctrine=ARIF_DOCTRINE,
        )

    return _sm(
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


def _manifest_backed_next_actions(candidates: list[tuple[str, str, str]]) -> list[dict[str, Any]]:
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


# Canonical alias — the MCP tool "arif_session_init" routes here.
# runtime/tools.py imports this name from session.py.
arif_session_init = arif_init

# Backward compatibility alias
arif_session_init = arif_init
