"""
identity_resolver.py — Identity Interceptor Gate (kata nama am vs kata nama khas)
═════════════════════════════════════════════════════════════════════════════════

THE PAGAR, NOT THE PETA.

`registry/routing/identity_continuity.yaml` is doctrine. This module is the
mechanism that enforces it at the execution boundary: no T2I, biometric, or
identity-bound capability may run until the subject string has been resolved
against `named_actors` (kata nama khas) and `ambiguous_categories` (kata nama am).

SCAR-2026-09-15-001 — a descriptive category ("abang sado") was hard-welded to a
single identity because it appeared as a Telegram display name. Mesin resolved
the token literally, killed contextual judgement, and the collapse propagated
across sessions. Doctrine was written and made no difference until this gate
existed, because a registry no process reads is a manifesto.

LAW
    Kata nama khas (proper noun)  → MAY bind to an identity card.
    Kata nama am   (common noun)  → MUST NOT bind. DISAMBIGUATE or HOLD.

FAIL-SAFE (F1 > F2)
    Registry missing, unreadable, or unparseable → HOLD. Never PASS.
    An agent that cannot read the law does not get to guess at it.

Usage:
    from arifos.identity.identity_resolver import guard, identity_bound

    result = guard("abang sado", capability="t2i")
    # result.verdict == Verdict.REQUIRE_DISAMBIGUATION

    @identity_bound(capability="biometric")
    def enroll(subject: str, ...): ...

Forged: 2026-09-15 · F13 order ("Jalan Option (a)") · DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import functools
import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Iterable

try:  # PyYAML is present across the federation images; absence is a HOLD condition.
    import yaml
except Exception:  # pragma: no cover - exercised only on a broken image
    yaml = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────────────────────

REGISTRY_PATH = Path(
    os.environ.get(
        "IDENTITY_CONTINUITY_REGISTRY",
        "/root/AAA/registry/routing/identity_continuity.yaml",
    )
)
LEDGER_PATH = Path(
    os.environ.get(
        "IDENTITY_INTERCEPT_LEDGER",
        "/root/AAA/registry/routing/intercept_log.jsonl",
    )
)

# Capabilities whose execution binds a real person's identity.
IDENTITY_BOUND_CAPABILITIES: frozenset[str] = frozenset(
    {
        "t2i",  # text-to-image on a named actor — FORBIDDEN, route to I2I
        "identity_bound",
        "biometric",
        "face_enroll",
        "face_match",
        "subject_ref",
    }
)
# T2I on a named actor is forbidden outright (routing_law ICL-2.0).
T2I_CAPABILITIES: frozenset[str] = frozenset({"t2i", "text_to_image"})


#: Distinguishes "caller did not supply a registry" (load the default) from
#: "caller supplied an unusable registry" (HOLD). None is a HOLD, never a reload.
_UNSET: Any = object()


class Verdict(Enum):
    """Outcome of an identity resolution."""

    PASS = "PASS"                                  # no identity claim, or a clean instance
    PASS_INSTANCE = "PASS_INSTANCE"                # kata nama khas resolved to one actor
    REQUIRE_DISAMBIGUATION = "REQUIRE_DISAMBIGUATION"  # kata nama am — do not blind-resolve
    DENY_T2I = "DENY_T2I"                          # T2I on a named actor — route to I2I
    HOLD_REGISTRY_UNREADABLE = "HOLD_REGISTRY_UNREADABLE"  # fail-safe (F1 > F2)
    HOLD_UNKNOWN_VERDICT = "HOLD_UNKNOWN_VERDICT"  # defensive default

    @property
    def blocks_execution(self) -> bool:
        return self is not Verdict.PASS and self is not Verdict.PASS_INSTANCE


class IdentityHold(RuntimeError):
    """Raised by @identity_bound when the gate refuses to let a call through."""

    def __init__(self, result: "GuardResult"):
        self.result = result
        super().__init__(
            f"identity gate {result.verdict.value}: {result.reason} "
            f"(capability={result.capability!r}, subject={result.subject!r})"
        )


# ── Data ─────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class LegacyRule:
    string: str
    resolution: str
    on_parse: str


@dataclass
class Registry:
    """Parsed identity_continuity.yaml, compiled to regex."""

    named_actor_patterns: list[re.Pattern[str]] = field(default_factory=list)
    ambiguous_patterns: list[re.Pattern[str]] = field(default_factory=list)
    legacy_rules: list[LegacyRule] = field(default_factory=list)
    actor_cards: dict[str, str] = field(default_factory=dict)
    loaded_at: float = 0.0

    @property
    def is_empty(self) -> bool:
        return not (
            self.named_actor_patterns or self.ambiguous_patterns or self.legacy_rules
        )


@dataclass
class GuardResult:
    subject: str
    capability: str
    verdict: Verdict
    reason: str
    instances: list[str] = field(default_factory=list)   # kata nama khas matched
    classes: list[str] = field(default_factory=list)     # kata nama am matched
    legacy_hits: list[str] = field(default_factory=list)
    resolved_actor: str | None = None
    registry_loaded: bool = False

    @property
    def blocked(self) -> bool:
        return self.verdict.blocks_execution

    def as_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "capability": self.capability,
            "verdict": self.verdict.value,
            "reason": self.reason,
            "instances": self.instances,
            "classes": self.classes,
            "legacy_hits": self.legacy_hits,
            "resolved_actor": self.resolved_actor,
            "registry_loaded": self.registry_loaded,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }


# ── Registry loading (fail-safe) ─────────────────────────────────────────────

_REGISTRY: Registry | None = None
_REGISTRY_MTIME: float = -1.0


def _compile(raw: str) -> re.Pattern[str]:
    return re.compile(raw, re.IGNORECASE)


def _parse_registry(doc: dict[str, Any]) -> Registry:
    patterns = doc.get("self_reference_patterns") or {}

    named = [_compile(p) for p in (patterns.get("named_actors") or []) if isinstance(p, str)]

    amb = patterns.get("ambiguous_categories") or {}
    amb_raw: list[str] = []
    if isinstance(amb, dict):
        amb_raw = [p for p in (amb.get("patterns") or []) if isinstance(p, str)]
    elif isinstance(amb, list):  # tolerate the legacy flat shape
        amb_raw = [p for p in amb if isinstance(p, str)]

    legacy_entries = (doc.get("legacy_handling") or {}).get("entries") or []
    legacy = [
        LegacyRule(
            string=str(e.get("string", "")),
            resolution=str(e.get("resolution", "")),
            on_parse=str(e.get("on_parse", "")),
        )
        for e in legacy_entries
        if isinstance(e, dict) and e.get("string")
    ]

    cards: dict[str, str] = {}
    for actor, spec in (doc.get("default_actor_resolution") or {}).items():
        if isinstance(spec, dict) and spec.get("identity_card"):
            cards[actor] = str(spec["identity_card"])

    return Registry(
        named_actor_patterns=named,
        ambiguous_patterns=[_compile(p) for p in amb_raw],
        legacy_rules=legacy,
        actor_cards=cards,
        loaded_at=time.time(),
    )


def load_registry(path: Path | str | None = None, force: bool = False) -> Registry | None:
    """Load + cache the registry. Returns None when it cannot be trusted.

    A None return is a HOLD condition, never a licence to continue.
    """
    global _REGISTRY, _REGISTRY_MTIME

    p = Path(path or REGISTRY_PATH)

    if yaml is None:
        logger.error("identity gate: PyYAML unavailable — HOLD (F1 > F2)")
        return None

    try:
        mtime = p.stat().st_mtime
    except OSError as exc:
        logger.error("identity gate: registry unreadable at %s — HOLD (%s)", p, exc)
        return None

    if not force and _REGISTRY is not None and mtime == _REGISTRY_MTIME:
        return _REGISTRY

    try:
        doc = yaml.safe_load(p.read_text(encoding="utf-8"))
        if not isinstance(doc, dict):
            raise ValueError("registry root is not a mapping")
        reg = _parse_registry(doc)
        if reg.is_empty:
            raise ValueError("registry parsed but carried zero patterns")
    except Exception as exc:  # parse error, permission error, anything
        logger.error("identity gate: registry parse failed at %s — HOLD (%s)", p, exc)
        return None

    _REGISTRY, _REGISTRY_MTIME = reg, mtime
    return reg


def _reset_cache() -> None:
    """Test hook — force the next load to re-read from disk."""
    global _REGISTRY, _REGISTRY_MTIME
    _REGISTRY, _REGISTRY_MTIME = None, -1.0


# ── Ledger ───────────────────────────────────────────────────────────────────


def _log_receipt(result: GuardResult) -> None:
    """Append one JSONL line. Ledger failure must never open the gate."""
    try:
        LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LEDGER_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result.as_dict(), ensure_ascii=False) + "\n")
    except Exception as exc:  # pragma: no cover - disk-full-style edge
        logger.warning("identity gate: ledger append failed (%s)", exc)


# ── The gate ─────────────────────────────────────────────────────────────────


def resolve(
    text: str,
    capability: str = "identity_bound",
    registry: Registry | None | Any = _UNSET,
) -> GuardResult:
    """Resolve a subject string. Never raises — every failure path is a HOLD.

    `registry` omitted → the canonical registry is loaded (cached).
    `registry=None`   → the caller has no usable registry → HOLD (fail-safe).
    """
    subject = text or ""
    reg = load_registry() if registry is _UNSET else registry

    if reg is None:
        return GuardResult(
            subject=subject,
            capability=capability,
            verdict=Verdict.HOLD_REGISTRY_UNREADABLE,
            reason="identity registry unreadable/unparseable — fail-safe HOLD (F1 > F2)",
            registry_loaded=False,
        )

    instances = sorted({p.pattern for p in reg.named_actor_patterns if p.search(subject)})
    classes = sorted({p.pattern for p in reg.ambiguous_patterns if p.search(subject)})
    legacy_hits = [r.string for r in reg.legacy_rules if r.string and r.string.lower() in subject.lower()]

    resolved_actor: str | None = None
    if len(instances) == 1:
        # strip the regex decoration to name the actor
        resolved_actor = re.sub(r"\\b|\^|\$", "", instances[0]).strip().lower()

    result = GuardResult(
        subject=subject,
        capability=capability,
        verdict=Verdict.PASS,
        reason="no identity claim present",
        instances=instances,
        classes=classes,
        legacy_hits=legacy_hits,
        resolved_actor=resolved_actor,
        registry_loaded=True,
    )

    # 1. Legacy collapsed strings — the unconformity. Dual-evaluate, never blind-resolve.
    if legacy_hits:
        result.verdict = Verdict.REQUIRE_DISAMBIGUATION
        result.reason = (
            f"legacy collapsed form {legacy_hits!r}: evaluate as INSTANCE + CLASS, "
            "do not route exclusively to one actor"
        )
        return result

    # 2. Kata nama am with no kata nama khas — the core SCAR. DISAMBIGUATE.
    if classes and not instances:
        result.verdict = Verdict.REQUIRE_DISAMBIGUATION
        result.reason = (
            f"common noun {classes!r} matched with no proper noun — a category must not "
            "bind to an identity; ask which person, or hold"
        )
        return result

    # 3. T2I on a named actor is forbidden (ICL-2.0) — route to I2I subject_ref.
    if instances and capability in T2I_CAPABILITIES:
        result.verdict = Verdict.DENY_T2I
        result.reason = (
            "T2I FORBIDDEN on a named actor — use I2I with subject_ref from the identity card"
        )
        return result

    # 4. Clean proper noun.
    if instances:
        result.verdict = Verdict.PASS_INSTANCE
        card = reg.actor_cards.get(resolved_actor or "", "")
        result.reason = f"kata nama khas {instances!r} resolved" + (f" → {card}" if card else "")
        if classes:
            # e.g. "Syed — an abang sado node": two facts, not one.
            result.reason += (
                f"; class {classes!r} also present — record as INSTANCE of CLASS, do not collapse"
            )
        return result

    return result


def guard(text: str, capability: str = "identity_bound", *, registry: Registry | None | Any = _UNSET,
          log: bool = True) -> GuardResult:
    """Public entry point. Resolves, records a receipt, returns the verdict."""
    result = resolve(text, capability=capability, registry=registry)
    if log:
        _log_receipt(result)
    if result.blocked:
        logger.warning("identity gate BLOCK %s: %s", result.verdict.value, result.reason)
    return result


def assert_clear(text: str, capability: str = "identity_bound", *, registry: Registry | None | Any = _UNSET) -> GuardResult:
    """Same as guard(), but raises IdentityHold when the gate refuses."""
    result = guard(text, capability=capability, registry=registry)
    if result.blocked:
        raise IdentityHold(result)
    return result


def identity_bound(capability: str = "identity_bound", subject_arg: str = "subject") -> Callable:
    """Decorator: the choke point. No identity-bound capability runs un-gated."""

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            subject = kwargs.get(subject_arg)
            if subject is None and args:
                subject = args[0]
            result = guard(str(subject or ""), capability=capability)
            if result.blocked:
                raise IdentityHold(result)
            return fn(*args, **kwargs)

        wrapper.__identity_gate__ = {"capability": capability, "subject_arg": subject_arg}  # type: ignore[attr-defined]
        return wrapper

    return decorator


# ── CLI (receipt surface) ────────────────────────────────────────────────────

if __name__ == "__main__":  # pragma: no cover
    import argparse

    ap = argparse.ArgumentParser(description="Identity interceptor gate — check a subject string.")
    ap.add_argument("subject", nargs="+", help="text carrying a possible identity claim")
    ap.add_argument("--capability", "-c", default="identity_bound")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-log", action="store_true")
    ns = ap.parse_args()

    res = guard(" ".join(ns.subject), capability=ns.capability, log=not ns.no_log)
    if ns.json:
        print(json.dumps(res.as_dict(), ensure_ascii=False, indent=2))
    else:
        print(f"{res.verdict.value}: {res.reason}")
    raise SystemExit(1 if res.blocked else 0)
