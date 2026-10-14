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
        if mode_map:
            # AND-requirements message from the table itself (NOT from
            # missing_params, which unions anyOf failures — an anyOf refusal
            # must carry its own "at least one of" wording).
            required = mode_map.get(mode)
            if required:
                and_missing = [p for p in required if _is_absent(kwargs.get(p))]
                if and_missing:
                    got = sorted(k for k in kwargs if not k.startswith("_") and k != "mode")
                    return (
                        f"MISSING_REQUIRED_INPUT: {tool_name} mode='{mode}' requires "
                        f"{', '.join(and_missing)}. State it explicitly — the kernel no "
                        f"longer infers it from silence. Params received: "
                        f"{got or ['<none>']}. Retry with the required params; this "
                        f"rejection is the input contract working, not a crash."
                    )

        for group in MODE_ANY_REQUIRED.get(tool_name, {}).get(mode, ()):
            if all(_is_absent(kwargs.get(p)) for p in group):
                got = sorted(k for k in kwargs if not k.startswith("_") and k != "mode")
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
