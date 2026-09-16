"""resolve.py — task-scoped capability projection for the capability fabric.

D2 of the F13-ratified decision packet (2026-09-17, D1–D5 APPROVE):
the ONE real build of the capability-fabric program. Extend-only — no new
registry, no new schema files; this module projects CapabilityRecords that
already exist (seed / CAPABILITY_INDEX.json / Qdrant) into a task-scoped
manifest of eager / deferred / hidden capability sets.

Precedent: Qwen Code tool_search deferred-loading + Hermes deferred discovery.
The agent never asks the sovereign — it receives its action surface from the
task envelope (automatic capability projection, not HITL).

Policy axes (all pre-existing fields on CapabilityRecord):
  • effective_class  → role allowance (OBSERVE/GOVERN/MUTATE/SEAL)
  • epistemic_tag    → eager requires CLAIM (high-evidence tools only)
  • risk_tier        → eager requires low
  • tags/server      → task-domain matching

Fail-closed (RSI kernel invariant 10): unknown role ⇒ zero capability grant,
every record hidden with reason. Authority ambiguity never widens a surface.

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Sequence

from capability_index.models import CapabilityRecord

RESOLVER_VERSION = "capability-fabric.resolve.v1"

# Role → allowed effective classes. Mirrors kernel verbs / APEX-ZEN lanes:
# a forge cell may act; a judge reads and verdicts but never mutates; only the
# seal tier (F13/888-lane) may touch SEAL-class tools. observe is the floor.
ROLE_ALLOWANCE: dict[str, frozenset[str]] = {
    "observe": frozenset({"OBSERVE"}),
    "route": frozenset({"OBSERVE", "GOVERN"}),
    "forge": frozenset({"OBSERVE", "GOVERN", "MUTATE"}),
    "judge": frozenset({"OBSERVE", "GOVERN"}),
    "seal": frozenset({"OBSERVE", "GOVERN", "MUTATE", "SEAL"}),
}

# Task-domain → server/tag aliases. Lexical, deterministic, cheap. Extend by
# appending; never remove an alias another lane may depend on.
DOMAIN_ALIASES: dict[str, tuple[str, ...]] = {
    "code": ("aforge", "forge", "code", "repo", "git", "test", "patch"),
    "geoscience": ("geox", "geology", "seismic", "basin", "well", "petrophys"),
    "research": ("search", "web", "reader", "firecrawl", "context7", "deepwiki", "zread", "zai"),
    "capital": ("wealth", "market", "capital", "trade", "xauusd"),
    "wellbeing": ("well", "vitality", "homeostasis", "substrate"),
    "federation": ("arifos", "ariflow", "fed", "aaa", "frame", "registry", "memory"),
    "communication": ("hermes", "telegram", "message", "a2a"),
}

DEFAULT_EAGER_MAX = 12
LOW_CONTEXT_EAGER_MAX = 6
LOW_CONTEXT_THRESHOLD = 4000  # tokens — under this, halve the eager surface


def _match_domains(rec: CapabilityRecord, domains: Optional[Sequence[str]]) -> bool:
    """True if the record belongs to at least one requested task domain."""
    if not domains:
        return True  # no domain filter ⇒ domain-agnostic match
    hay = " ".join([rec.server.lower()] + [t.lower() for t in rec.tags] + [rec.tool_name.lower()])
    for domain in domains:
        aliases = DOMAIN_ALIASES.get(domain.strip().lower(), (domain.strip().lower(),))
        if any(alias in hay for alias in aliases):
            return True
    return False


def _eager_admissible(rec: CapabilityRecord, domains: Optional[Sequence[str]]) -> bool:
    """Eager = small, high-frequency, task-critical, safe.

    OBSERVE-only, high-evidence (CLAIM), low risk, domain-matched. Everything
    else that the role may use stays discoverable-but-deferred.
    """
    return (
        rec.effective_class == "OBSERVE"
        and rec.epistemic_tag == "CLAIM"
        and rec.risk_tier == "low"
        and _match_domains(rec, domains)
    )


def resolve_capabilities(
    records: Sequence[CapabilityRecord],
    agent_id: str,
    role: str,
    task_domains: Optional[Sequence[str]] = None,
    context_budget: int = 0,
    eager_max: int = DEFAULT_EAGER_MAX,
) -> dict:
    """Project the full capability index into a task-scoped manifest.

    Returns a JSON-serialisable manifest:
      eager    — load now (small, safe, high-evidence, task-critical)
      deferred — allowed, discoverable on demand (capability_search)
      hidden   — outside the role's authority ceiling, with reason
    """
    manifest = {
        "resolver_version": RESOLVER_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "agent_id": agent_id,
        "role": role,
        "task_domains": list(task_domains or []),
        "policy": {r: sorted(c) for r, c in ROLE_ALLOWANCE.items()},
        "eager": [],
        "deferred": [],
        "hidden_count": 0,
        "hidden_by_reason": {},
        "error": None,
    }

    # Fail-closed on unknown role: authority ambiguity never widens a surface.
    allowed = ROLE_ALLOWANCE.get(role)
    if allowed is None:
        manifest["error"] = (
            f"unknown role {role!r} — fail-closed, zero capability grant. "
            f"Valid roles: {sorted(ROLE_ALLOWANCE)}"
        )
        manifest["hidden_count"] = len(records)
        manifest["hidden_by_reason"] = {"unknown_role": len(records)}
        return manifest

    if context_budget and 0 < context_budget < LOW_CONTEXT_THRESHOLD:
        eager_max = min(eager_max, LOW_CONTEXT_EAGER_MAX)

    eager, deferred = [], []
    hidden_reasons: dict[str, int] = {}

    for rec in records:
        if rec.effective_class not in allowed:
            reason = f"class_{rec.effective_class}_above_role_{role}_ceiling"
            hidden_reasons[reason] = hidden_reasons.get(reason, 0) + 1
            continue

        # Task-scoping: domains narrow the READ surface (the long tail of
        # search/observation tools); the ACTUATION substrate (GOVERN/MUTATE/
        # SEAL) stays domain-exempt — a forge cell cannot lose its hands
        # because the task domain is geoscience rather than code.
        if task_domains and rec.effective_class == "OBSERVE" and not _match_domains(rec, task_domains):
            reason = "domain_out_of_task_scope"
            hidden_reasons[reason] = hidden_reasons.get(reason, 0) + 1
            continue

        entry = {
            "tool_name": rec.tool_name,
            "server": rec.server,
            "effective_class": rec.effective_class,
            "epistemic_tag": rec.epistemic_tag,
            "risk_tier": rec.risk_tier,
            "authority_ceiling": rec.authority_ceiling,
            "description": rec.description[:160],
            "tags": rec.tags[:6],
        }

        if _eager_admissible(rec, task_domains) and len(eager) < eager_max:
            entry["load"] = "eager"
            eager.append(entry)
        else:
            entry["load"] = "deferred"
            entry["discover_via"] = "capability_search"
            deferred.append(entry)

    manifest["eager"] = eager
    manifest["deferred"] = deferred
    manifest["hidden_count"] = sum(hidden_reasons.values())
    manifest["hidden_by_reason"] = hidden_reasons
    return manifest
