"""Input-contract minimums — mode-conditional required params (2026-10-15).

Doctrine (F13 session 2026-10-15): the input contract outranks output polish.
The advertised schema stays all-optional for back-compat (every param has a
default, so nothing breaks on the wire); this module enforces per-mode
minimums at the single dispatch chokepoint (_wrap_handler). Empty or lazy
calls that previously sailed through now get an actionable rejection naming
exactly what to supply.

Exemptions preserved BY DESIGN (a read with no inputs is legitimate):
  - transport probes (canary), light sessions, vitals/compass/atlas reads
  - ledger/changelog/audit reads on arif_seal
  - arif_memory audit/metabolize maintenance sweeps

Single source of truth. Adding a mode requirement? Edit MODE_REQUIRED /
MODE_ANY_REQUIRED / ALIAS_REQUIRED here — never inline checks in handlers
(LAW 8: one owner).
"""

from __future__ import annotations

from typing import Any

# tool -> mode -> required params (all must be present AND non-empty)
MODE_REQUIRED: dict[str, dict[str, tuple[str, ...]]] = {
    "arif_init": {
        "init": ("actor_id", "intent"),
        "resume": ("session_id",),
        "validate": ("session_id",),
        "preflight": ("session_id",),
        "triage": ("session_id",),
        "epoch_open": ("epoch_id",),
        "epoch_seal": ("epoch_id",),
        # canary / light / opt_out: no minimum — deliberate empty calls
    },
    "arif_observe": {
        "search": ("query",),
        "hybrid_discovery": ("query",),
        "fetch": ("url",),
        "ingest": ("url",),
        # compass / atlas / entropy_dS / vitals: no minimum
    },
    "arif_think": {
        "reason": ("query",),
        "reflect": ("query",),
        "verify": ("query",),
        "axioms": ("query",),
        "plan": ("query",),
        "simulate": ("query",),
        "wonder": ("query",),
        "plan_review": ("plan_id",),
        "plan_approve": ("plan_id",),
        "refactor_plan": ("plan_id",),
        # metabolize / atlas: no minimum
    },
    "arif_route": {
        # route has free-form mode; requirement is alias-level, see below
    },
    "arif_memory": {
        "recall": ("query",),
        "inspect": ("memory_id",),
        "attest": ("memory_id",),
        "remember": ("content",),
        "promote": ("memory_id",),
        "revise": ("memory_id", "new_content"),
        "forget": ("memory_id",),
        # audit / metabolize: no minimum
    },
    "arif_judge": {
        "judge": ("candidate",),
        "intercept": ("candidate",),
        # validate / hold / escalate: gated by kernel auth, not input contract
    },
    "arif_forge": {
        "engineer": ("manifest",),
        "write": ("manifest",),
        "generate": ("manifest",),
        # dry_run: manifest OR query — see MODE_ANY_REQUIRED (anyOf fallback)
        "query": ("query",),
        "recall": ("query",),
        # commit: gated by seal_verdict_id downstream, not here
    },
    "arif_seal": {
        # Mode 'seal' writes a PERMANENT record: payload is the content,
        # seal_purpose is the one-sentence reason it must exist (F1 AMANAH —
        # a permanent record with no stated reason is refused). Ordered so a
        # fully-empty call reports payload first, then seal_purpose.
        "seal": ("payload", "seal_purpose"),
        # session_close is also a WRITE (permanent ledger macro): payload is
        # the closure summary. Pure reads (verify/ledger/changelog/audit)
        # stay exempt — do not over-block reads.
        "session_close": ("payload",),
    },
}

# tool -> list of alias groups; at least ONE param per group must be present
ALIAS_REQUIRED: dict[str, list[tuple[str, ...]]] = {
    "arif_route": [("intent", "task")],  # task is the legacy alias for intent
}

# tool -> mode -> anyOf groups; at least ONE param PER GROUP must be present.
# Mirrors the advertised schema's allOf/anyOf branches (public_registry) —
# the gate and the schema must say the same thing (F4 CLARITY). Fallback
# ruling 2026-10-15: "query-only allowed as an explicit fallback path" is a
# REAL carve-out for arif_forge mode=dry_run — the preview accepts a
# manifest OR a plain-language query.
MODE_ANY_REQUIRED: dict[str, dict[str, tuple[tuple[str, ...], ...]]] = {
    "arif_forge": {
        "dry_run": (("manifest", "query"),),
    },
}

# Fallback default mode when the caller omits it entirely (matches the
# signature defaults on the public tools).
DEFAULT_MODE: dict[str, str] = {
    "arif_init": "init",
    "arif_observe": "search",
    "arif_think": "reason",
    "arif_route": "",
    "arif_memory": "recall",
    "arif_judge": "judge",
    "arif_forge": "engineer",
    "arif_seal": "seal",
}


def _is_absent(value: Any) -> bool:
    """A param is 'missing' when absent, None, or an empty string."""
    return value is None or (isinstance(value, str) and not value.strip())


def normalize_request_fields(kwargs: dict[str, Any]) -> dict[str, list[str]]:
    """Normalize and classify request input fields into distinct sets (KX-008).

    - raw_present_fields: all keys present in the raw input dictionary.
    - valid_fields: fields holding non-empty, non-null usable data.
    - invalid_fields: fields explicitly provided but null or empty.
    """
    raw_present = sorted(str(k) for k in kwargs.keys())
    valid: list[str] = []
    invalid: list[str] = []

    for k, v in kwargs.items():
        if k.startswith("_") or k == "mode":
            continue
        if _is_absent(v):
            invalid.append(str(k))
        else:
            valid.append(str(k))

    return {
        "raw_present_fields": raw_present,
        "valid_fields": sorted(valid),
        "invalid_fields": sorted(invalid),
    }


def _mode_of(tool_name: str, kwargs: dict[str, Any]) -> str:
    """Resolve the effective mode (caller-supplied or the signature default)."""
    return kwargs.get("mode") or DEFAULT_MODE.get(tool_name, "")


def missing_params(tool_name: str, kwargs: dict[str, Any]) -> list[str]:
    """Return the mode-conditional required params absent from this call.

    Empty list = the call satisfies the contract. Mirrors enforce() exactly —
    single source of truth for WHICH fields are missing, so structured error
    envelopes (meta.missing_fields) can never disagree with the prose reason.
    For a failed anyOf group (e.g. dry_run with neither manifest nor query)
    every alternative is named, in advertised-schema order — deterministic.
    """
    mode_map = MODE_REQUIRED.get(tool_name)
    if not mode_map:
        return []
    mode = _mode_of(tool_name, kwargs)
    missing: list[str] = []
    required = mode_map.get(mode)
    if required:
        missing.extend(p for p in required if _is_absent(kwargs.get(p)))
    for group in MODE_ANY_REQUIRED.get(tool_name, {}).get(mode, ()):
        if all(_is_absent(kwargs.get(p)) for p in group):
            missing.extend(p for p in group if p not in missing)
    return missing


def enforce(tool_name: str, kwargs: dict[str, Any]) -> str | None:
    """Return an actionable rejection message, or None when the call passes.

    Never raises — an input-contract bug must not take down the call path
    (fail-open to the handler, which retains all its own internal gates).
    """
    try:
        mode_map = MODE_REQUIRED.get(tool_name)
        mode = _mode_of(tool_name, kwargs)
        norm = normalize_request_fields(kwargs)
        got = norm["valid_fields"]

        if mode_map:
            # AND-requirements message from the table itself (NOT from
            # missing_params, which unions anyOf failures — an anyOf refusal
            # must carry its own "at least one of" wording).
            required = mode_map.get(mode)
            if required:
                and_missing = [p for p in required if _is_absent(kwargs.get(p))]
                if and_missing:
                    return (
                        f"MISSING_REQUIRED_INPUT: {tool_name} mode='{mode}' requires "
                        f"{', '.join(and_missing)}. State it explicitly — the kernel no "
                        f"longer infers it from silence. Params received: "
                        f"{got or ['<none>']}. Retry with the required params; this "
                        f"rejection is the input contract working, not a crash."
                    )

        for group in MODE_ANY_REQUIRED.get(tool_name, {}).get(mode, ()):
            if all(_is_absent(kwargs.get(p)) for p in group):
                return (
                    f"MISSING_REQUIRED_INPUT: {tool_name} mode='{mode}' requires at "
                    f"least one of {' or '.join(group)} — any one alternative "
                    f"satisfies the advertised schema anyOf. Params received: "
                    f"{got or ['<none>']}. Retry with the required params; this "
                    f"rejection is the input contract working, not a crash."
                )

        for group in ALIAS_REQUIRED.get(tool_name, ()):
            if all(_is_absent(kwargs.get(p)) for p in group):
                return (
                    f"MISSING_REQUIRED_INPUT: {tool_name} requires at least one of "
                    f"{' or '.join(group)} (one is the legacy alias of the other). "
                    f"A route with no intent cannot be routed."
                )
        return None
    except Exception:  # fail-open: contract check must never break dispatch
        return None


# ── G3 INVALID-MODE GUARD (Arif ratified 2026-10-29) ─────────────────────
# An undeclared `mode` is an INPUT VALIDATION ERROR. MCP SEP-1303
# ("Input Validation Errors as Tool Execution Errors", Final) requires it to be
# reported as a TOOL EXECUTION ERROR — isError:true, with an actionable message
# — so the calling model can read the error and self-correct.
#
# It must NOT fall through to a default branch. Failure class observed
# 2026-08-12 and re-measured on this tree 2026-10-29:
#   arif_observe(mode=<undeclared>) → UnboundLocalError (crash, not actionable)
#   arif_judge(mode=<undeclared>)   → silently entered the judgment path
#
# The allowed set is read from constitutional_map CANONICAL_TOOLS/DIAGNOSTIC_TOOLS
# — the SAME lists that generate the advertised input_schema enum — and is
# filtered by the handler's __dispatch_modes__ exactly as register_tools filters
# the wire enum. Schema and guard read one source, so they cannot drift
# (LAW 8: one owner).
#
# Scope (Arif, 2026-10-29): arif_observe + arif_judge only.
GUARDED_TOOLS: frozenset[str] = frozenset({"arif_observe", "arif_judge"})


def _guard_enabled() -> bool:
    """Guard is ON by default (the ratified doctrine must be in force).

    Kill-switch: ARIFOS_MODE_GUARD=0|off|false|no disables it without a code
    change — reversible at deploy time (F1 AMANAH).
    """
    import os

    return os.environ.get("ARIFOS_MODE_GUARD", "1").strip().lower() not in {
        "0",
        "off",
        "false",
        "no",
    }


def allowed_modes(tool_name: str, handler: Any = None) -> tuple[str, ...]:
    """The modes this tool accepts — the set the wire advertises.

    Mirrors register_tools' MODE ENUM GUARD: declared modes ∩ the handler's
    dispatchable universe. Never invents a mode the wire does not offer.
    """
    try:
        from arifosmcp.constitutional_map import CANONICAL_TOOLS, DIAGNOSTIC_TOOLS

        spec = {**CANONICAL_TOOLS, **DIAGNOSTIC_TOOLS}.get(tool_name) or {}
        modes = list(spec.get("modes") or [])
        universe = getattr(handler, "__dispatch_modes__", None)
        if universe is not None:
            modes = [m for m in modes if m in universe]
        return tuple(modes)
    except Exception:  # fail-open: a guard bug must never break dispatch
        return ()


def invalid_mode(tool_name: str, kwargs: dict[str, Any], handler: Any = None) -> str | None:
    """Return the offending mode, or None when the call is admissible.

    A tool with no declared mode set (arif_route: "modes": []) is not guarded —
    its modes are declared by the individual adapted tools, not by the verb.
    """
    if tool_name not in GUARDED_TOOLS or not _guard_enabled():
        return None
    modes = allowed_modes(tool_name, handler)
    if not modes:
        return None
    mode = _mode_of(tool_name, kwargs)
    if mode in modes:
        return None
    return str(mode)


def invalid_mode_message(tool_name: str, mode: str) -> str:
    """Actionable rejection text — the model must be able to fix the call."""
    modes = allowed_modes(tool_name)
    return (
        f"INVALID_MODE: {tool_name} does not accept mode='{mode}'. "
        f"Valid modes: {', '.join(modes) if modes else '<none declared>'}. "
        f"No work was executed and no state was changed. "
        f"Retry with one of the valid modes."
    )
