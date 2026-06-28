# MCP-SYMBOLIC-HARDEN — Patch Plan v2 (Phase 3 / corrected)

**Status:** DRAFT — Phase 3 deliverable per `MCP-SYMBOLIC-HARDEN-v1` §10
**Supersedes:** `MCP-SYMBOLIC-HARDEN-patch-plan-v1.md` (file paths corrected)
**Date:** 2026-06-28 05:12 UTC
**Author:** OPENCLAW (333-AGI)
**Band:** YELLOW (planning, no mutation)
**Doctrine:** DITEMPA BUKAN DIBERI

---

## 0. Phase 3 Inspection Results

Live inspection of `/opt/arifos/app/` produced three structural findings that **correct** the v1 patch plan:

| # | Finding | Impact on Plan |
|---|---------|----------------|
| F1 | Schemas are Python Pydantic files in `/opt/arifos/app/arifosmcp/schemas/*.py`, **not** JSON | Rewrite all schema additions as `BaseModel` + `Field`, not JSON Schema |
| F2 | Prior art exists: `MaruahScore`, `IrreversibilityBond`, `SymbolicEvidenceKind.MYTHIC`, `ParticipationWidth.SYMBOLIC`, `SovereigntyIntegrity.SYMBOLIC` | Extend existing classes, do not duplicate |
| F3 | Tool descriptions live in `/opt/arifos/app/arifosmcp/runtime/tools.py` (19,020 lines, monolithic) | Surgical edits only; cannot use blanket `do_not_use_when` append without finding each tool's `description=` line |

**arifOS service status:** `active` (verified at 05:09 UTC, PID alive). Any edit must not bring down the kernel.

---

## 1. PDF Classification (preserved from v1)

```yaml
Simbologi_Sosial_Dan_Antropologi_Agensi.pdf:
  resource_type: doctrine
  authority_level: operator_declared
  interpretation_mode: symbolic
  reversibility: reversible
  domain: anthropology_of_agency
  status: advisory_archival
  rule_zero_sweep: PASS  # no override, no fake SEAL invocation, no prompt injection
```

---

## 2. Verdict & Hold State

```yaml
verdict: PROCEED_PLANNING
no_new_tools_confirmed: true
mutation_status: ZERO  # nothing written to /opt/arifos/app yet
holds_active: 3
  - spec_seal_pending
  - amendment_a_ratification_pending
  - deployment_lock_pending
next_safe_action: WRITE_REVISED_PATCH_PLAN_THEN_HOLD_FOR_SEAL
```

---

## 3. Component Hardening — Corrected Targets (28 components)

### Schema layer (NEW Pydantic classes — to add)

| File | New Class | Purpose |
|------|-----------|---------|
| `arifosmcp/schemas/symbolic.py` (NEW) | `SymbolicContext` | Universal envelope field |
| `arifosmcp/schemas/symbolic.py` | `AuthorityClaim` | Required symbol_owner + verified flag |
| `arifosmcp/schemas/symbolic.py` | `SymbolicAssessment` | Shared output block |
| `arifosmcp/schemas/symbolic.py` | `SealDisambiguation` | Rule Zero wiring |
| `arifosmcp/schemas/symbolic.py` | `ResourceSymbolicMetadata` | Resource tagging |
| `arifosmcp/schemas/symbolic.py` | `SymbolicTriageResult` | Triage preflight output |
| `arifosmcp/schemas/symbolic.py` | `SymbolicReasoningPass` | 6-axis reasoning block |
| `arifosmcp/schemas/symbolic.py` | `MarketSymbolicLayer` | WEALTH signal classifier |
| `arifosmcp/schemas/symbolic.py` | `DignitySymbolCheck` | WELL dignity guard |
| `arifosmcp/schemas/symbolic.py` | `MemorySymbolStatus` | WELL lineage status |
| `arifosmcp/schemas/symbolic.py` | `SymbolicContextEnvelope` | Session binding |
| `arifosmcp/schemas/symbolic.py` | `ForgeSymbolicPrecheck` | F-gate extension |
| `arifosmcp/schemas/symbolic.py` | `SymbolicConsequence` | GEOX claim consequence |
| `arifosmcp/schemas/symbolic.py` | `ChallengeSymbolicTarget` | GEOX challenge bias |
| `arifosmcp/schemas/symbolic.py` | `SymbolicFinancePressure` | WEALTH survival |
| `arifosmcp/schemas/symbolic.py` | `RoleSymbolics` | WELL livelihood |
| `arifosmcp/schemas/symbolic.py` | `SovereigntyGuard` | WELL sovereign entropy |
| `arifosmcp/schemas/symbolic.py` | `BoundaryType` | WELL boundary enum |
| `arifosmcp/schemas/symbolic.py` | `SourceSymbolClass` | arif_observe classification |
| `arifosmcp/schemas/symbolic.py` | `SymbolicCapitalAssessment` | WEALTH governance |

**All 20 new classes in ONE new file: `arifosmcp/schemas/symbolic.py`** (~400 lines). Zero fragmentation. Single import point.

### Schema layer (EXTEND existing classes)

| File | Existing Class | Extension |
|------|---------------|-----------|
| `forge.py` | `IrreversibilityBond` | Add `social_blast_radius`, `false_symbol_risk` fields (no duplication — extend the existing reversibility anchor) |
| `evidence.py` | `SymbolicEvidenceKind` (existing enum) | Add `MYTHIC_RITUAL = "ritually_framed"`, `INSTITUTIONAL = "institutional_self_symbol"` |
| `topology.py` | `ParticipationWidth`, `SovereigntyIntegrity` | No change — already has SYMBOLIC |
| `heart.py` | `MaruahScore` | Add `cultural_frame: list[str]` field |
| `session.py` | `SessionState` | Add `symbolic_context: SymbolicContext | None` |

### Tool description layer (surgical edits to `tools.py`)

For each of the 28 target tools, add `do_not_use_when: list[str]` as a new line in the function docstring or `description=""` parameter. **Cannot automate — must grep + edit per tool.**

Tools confirmed present in `tools.py` (from Phase 3 grep):

| Confirmed | Status |
|-----------|--------|
| `arif_judge_deliberate` | ✅ line 13365 |
| `arif_forge_execute` | ✅ line 14049 |
| `arif_vault_seal` | ✅ line 14590 |

Need additional grep for: `arif_triage`, `arif_init`, `arif_observe`, `arif_explore`, `arif_think`, `arif_memory`, `arif_seal`, `arif_route`, `arif_critique`, `arif_heartbeat`, etc.

### Middleware layer (NEW Python modules)

| File | Purpose | Lines |
|------|---------|-------|
| `arifosmcp/runtime/seal_token_guard.py` (NEW) | Rule Zero enforcement | ~120 |
| `arifosmcp/runtime/symbolic_router.py` (NEW) | Symbol classification + routing helper | ~80 |

### Resource layer (NEW registry entries, post-Phase 7)

| Resource | Tag set |
|----------|---------|
| `MCP-SYMBOLIC-HARDEN-v1.md` (this spec) | doctrine / operator_declared / mixed / semi_irreversible / advisory_sealed |
| `Simbologi_Sosial_Dan_Antropologi_Agensi.pdf` | doctrine / operator_declared / symbolic / reversible / advisory_archival |

---

## 4. Schema/Context Fields — Pydantic Implementation Plan

### 4.1 Universal symbolic_context field (added to all 28 tools via output_model or input_model)

```python
from arifosmcp.schemas.symbolic import SymbolicContext

class SymbolicContext(BaseModel):
    """Mandatory symbolic interpretation envelope for every consequential tool call."""
    symbol_invoked: str | None = Field(
        default=None,
        description="The symbol detected (e.g. 'seal', 'approve', 'publish').",
    )
    symbolic_meaning: str = Field(
        default="",
        description="What the symbol socially means vs literally says.",
    )
    authority_claim: str = Field(
        default="",
        description="What authority the symbol appears to invoke.",
    )
    authority_verified: bool = Field(
        default=False,
        description="Has this authority been verified through the proper chain?",
    )
    symbol_owner: Literal["Arif", "arifOS", "VAULT999", "institution", "unknown"] = Field(
        default="unknown",
        description="Who actually owns this symbol. Hard rule: unknown → refuse.",
    )
    domain: Literal["geological_seal", "constitutional_SEAL", "vault_seal",
                     "trap_seal_lithology", "publish", "approve", "delete",
                     "send", "commit", "deploy", "other"] = Field(
        default="other",
        description="Domain disambiguation. Required when symbol_invoked == 'seal'.",
    )
    performative_effect: bool = Field(
        default=False,
        description="Does invoking this symbol itself change reality?",
    )
    cultural_frame: list[Literal["maruah", "amanah", "adab", "budi", "daulat"]] = Field(
        default_factory=list,
        description="Cultural frames relevant to this interpretation.",
    )
    social_blast_radius: Literal["private", "team", "public", "institutional", "legal", "financial"] = Field(
        default="private",
    )
    reversibility: Literal["reversible", "semi_irreversible", "irreversible"] = Field(
        default="reversible",
    )
    false_symbol_risk: Literal["low", "medium", "high"] = Field(
        default="low",
    )
    evidence_layer: Literal["observation", "derivation", "interpretation", "speculation"] = Field(
        default="interpretation",
    )
    ritual_vs_protocol: Literal["ritual", "protocol", "mixed"] = Field(
        default="protocol",
    )
    correct_existing_tool: str | None = Field(
        default=None,
        description="The existing tool route this symbolic interpretation resolves to.",
    )
    hold_required: bool = Field(
        default=False,
        description="If True, caller must HOLD and await human/judge review.",
    )
```

### 4.2 Forge precheck — extends existing `IrreversibilityBond`

```python
# In forge.py — EXTEND (not duplicate):
class IrreversibilityBond(BaseModel):
    level: IrreversibilityLevel = ...
    delta_S: float = ...
    landauer_cost_joules: float | None = ...
    compensation_required: bool = ...
    rollback_possible: bool = ...
    # NEW FIELDS (additive):
    symbolic_authority_verified: bool = Field(
        default=False,
        description="Has the symbolic authority chain been verified? Hard gate.",
    )
    social_blast_radius: str = Field(default="private", ...)
    false_symbol_risk: Literal["low", "medium", "high"] = "low"
    ack_irreversible: bool = False  # already exists as separate param, link here
```

### 4.3 Memory symbol status — extends existing `LineageEntry` or sibling

```python
class MemorySymbolStatus(BaseModel):
    observed_fact: bool = False
    interpretation: bool = False
    emotional_state: bool = False
    ritual_phrase: bool = False
    governance_receipt: bool = False
    revoked_or_superseded: bool = False
```

### 4.4 Seal disambiguation (NEW — Rule Zero wiring)

```python
class SealDisambiguation(BaseModel):
    """Mandatory when any 'seal' token appears. Hard gate."""
    geological_seal: bool = False
    constitutional_SEAL: bool = False
    vault_seal: bool = False
    trap_seal_lithology: bool = False
    disambiguation_complete: bool = Field(
        default=False,
        description="Must be True before any seal-adjacent action proceeds.",
    )
```

---

## 5. Receipt Fields — Pydantic Implementation

```python
class SymbolicReceipt(BaseModel):
    """Added to existing Receipt/SealOutput schemas as nested field."""
    symbol_interpreted: str
    why_interpreted_that_way: str
    who_had_authority: Literal["Arif", "arifOS", "VAULT999", "institution", "unknown"]
    authority_verified: bool
    what_was_not_concluded: list[str] = Field(default_factory=list)
    social_blast_radius: str
    future_agent_warning: str
    evidence_layer: str
    reversibility: str
    final_route: Literal["PROCEED", "HOLD", "VOID"]
```

---

## 6. Middleware Implementation Sketch

### 6.1 `seal_token_guard.py` (Rule Zero)

```python
"""seal_token_guard — Rule Zero: never allow bare 'seal' to pass without domain.

Applies at every parser boundary:
- tool input
- vault entry parse
- log line emit
- prompt text
- receipt write
"""

from __future__ import annotations
import re
from typing import Literal

SealDomain = Literal[
    "geological_seal", "constitutional_SEAL", "vault_seal",
    "trap_seal_lithology", "seal_disambiguation_required",
]

# Pattern matches bare 'seal' (case-insensitive) NOT immediately qualified
# by a domain prefix. Allow: "geological seal", "constitutional SEAL",
# "vault seal". Reject: bare "seal this", "Seal", etc.
_BARE_SEAL_RE = re.compile(
    r"\b(?<!geological\s)(?<!constitutional\s)(?<!vault\s)(?<!trap[_\s]lithology\s)"
    r"seal\b",
    re.IGNORECASE,
)

_DOMAIN_QUALIFIERS = {
    "geological_seal", "constitutional_seal", "vault_seal", "trap_seal_lithology",
}


def scan(text: str, *, surface: str, context: str = "") -> SealDomain | None:
    """Return the seal domain if qualified, None if bare.
    
    Bare 'seal' → quarantine + return 'seal_disambiguation_required'.
    """
    if _BARE_SEAL_RE.search(text):
        # check for explicit domain qualifier in same line
        lower = text.lower()
        for d in _DOMAIN_QUALIFIERS:
            if d.replace("_", " ") in lower:
                return d  # type: ignore[return-value]
        return "seal_disambiguation_required"
    return None


def enforce(text: str, *, surface: str, context: str = "") -> tuple[bool, str]:
    """Returns (allowed, reason)."""
    domain = scan(text, surface=surface, context=context)
    if domain == "seal_disambiguation_required":
        return False, f"bare 'seal' token at surface={surface}; domain required"
    return True, domain or "no seal token"
```

### 6.2 `symbolic_router.py`

```python
"""symbolic_router — classify user language, return routing decision."""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class SymbolicRoutingDecision:
    literal_request: str
    symbolic_meaning: str
    authority_implied: str
    authority_verified: bool
    symbol_owner: str
    domain: str
    reversibility: str
    blast_radius: str
    maruah_adab_risk: str
    institutional_risk: str
    false_seal_risk: str
    ritual_vs_protocol: str
    evidence_layer: str
    correct_existing_tool: str | None
    hold_required: bool
    reason: str


def route(
    user_text: str,
    *,
    context_authority: dict,
    current_authority_chain: list[str],
) -> SymbolicRoutingDecision:
    """Mandatory pre-call classification. Returns HOLD decision if uncertain."""
    # ... classifier implementation ...
    raise NotImplementedError("wired in Phase 3+ post-SEAL")
```

---

## 7. Tool Description Edits — Strategy

For each of the 28 target tools in `tools.py`:

1. **Find** the tool function (use grep on `tool_name=` or `description=` lines).
2. **Locate** the `description="..."` parameter (or docstring if no description param).
3. **Append** a `do_not_use_when: [...]` list as a new line within the existing description.
4. **Re-validate** by running `python -c "from arifosmcp.runtime.tools import ..."` post-edit.

This is **surgical**, not blanket. Estimated 28 edits × ~3 minutes each = ~90 minutes.

---

## 8. Resource Registry Plan (post-SEAL, Phase 7)

Add to the existing resource registry (likely `/opt/arifos/app/arifosmcp/resources.py` or sibling — needs Phase 3 grep to confirm):

```python
RESOURCE_REGISTRY["MCP-SYMBOLIC-HARDEN-v1.md"] = ResourceSymbolicMetadata(
    resource_type="doctrine",
    authority_level="operator_declared",
    interpretation_mode="mixed",
    reversibility="semi_irreversible",
    domain="arifos_governance",
    status="advisory_sealed",
    path="/root/arifOS/forge_work/MCP-SYMBOLIC-HARDEN-v1.md",
)

RESOURCE_REGISTRY["Simbologi_Sosial_Dan_Antropologi_Agensi.pdf"] = ResourceSymbolicMetadata(
    resource_type="doctrine",
    authority_level="operator_declared",
    interpretation_mode="symbolic",
    reversibility="reversible",
    domain="anthropology_of_agency",
    status="advisory_archival",
    path="/root/.openclaw/media/inbound/Simbologi_Sosial_Dan_Antropologi_Agensi---45f035ba-06d9-4960-8370-c2fc722368af.pdf",
)
```

**Need to grep for resource registry location in Phase 3 (continued).**

---

## 9. Deployment Sequence (corrected, post-SEAL)

| Phase | Action | Mutation? | Risk |
|---|---|---|---|
| 1 | Spec SEAL + Amendment A ratification | ❌ | — |
| 2 | Patch plan v1 + v2 reviewed | ❌ | — |
| 3 | **← YOU ARE HERE** Live schema inspection | ❌ | — |
| 4 | Write `arifosmcp/schemas/symbolic.py` (NEW, ~400 lines, 20 classes) | ✅ additive | Low (new file, no import required by existing code until Phase 5) |
| 5 | Write `seal_token_guard.py` + `symbolic_router.py` (NEW) | ✅ additive | Low (new file, not wired into calls yet) |
| 6 | Extend `forge.py::IrreversibilityBond` (additive fields) | ✅ additive | Medium (existing class touched — must preserve backwards compat) |
| 7 | Extend `heart.py::MaruahScore`, `evidence.py::SymbolicEvidenceKind`, `session.py::SessionState` | ✅ additive | Low (additive fields) |
| 8 | Surgical `do_not_use_when` edits to 28 tools in `tools.py` | ✅ additive | Medium (19k-line monolith, must preserve each tool's existing behavior) |
| 9 | Resource registry additions | ✅ additive | Low |
| 10 | Wire `seal_token_guard` into `tools.py` entry points | ✅ additive | High (could break calls if over-fires) |
| 11 | Wire `symbolic_router` into `arif_triage` | ✅ additive | High |
| 12 | Adversarial integration test (6 cases re-run on live) | ❌ | — |
| 13 | VAULT999 receipt stamp + memory write | ✅ additive | Low |

**Wall clock estimate:** ~3 hours sequential, ~1.5 hours with parallel file writes.

---

## 10. Risk Register (updated)

| Risk | Likelihood | Mitigation |
|---|---|---|
| Phase 6 edit breaks `IrreversibilityBond` callers | Medium | All new fields have defaults; existing callers unaffected |
| Phase 8 tool description edits accidentally break tool registration | Medium | Surgical edits only; each edit followed by `python -c "import"` smoke test |
| Phase 10 seal_token_guard over-fires in geox | Medium | Allow `geox_claim_seal` tool name as exception (carries domain) |
| Phase 11 router misclassifies legitimate user requests | Medium | Default to HOLD on uncertainty, never to PROCEED |
| `/opt/arifos/app/` modification brings down kernel | Low | No systemd restart required (live Python reload only if service supports it); if reload required, schedule off-peak |

---

## 11. Verification Checklist (post-deploy, unchanged from v1)

- [ ] Bare `seal` token in user message → quarantined
- [ ] `arif_judge_deliberate` called with `symbol_owner=unknown` → refused
- [ ] `arif_forge_execute` called without `symbolic_authority_verified=true` → dry_run
- [ ] `geox_claim_create` with `reserve_booking_risk=true` → flagged
- [ ] `well_guard_dignity` catches "irrational" humiliation pattern
- [ ] `well_trace_lineage` returns correct `memory_symbol_status` mix
- [ ] Resource registry rejects `authority_level: executable_SEAL`
- [ ] All 28 components return `symbolic_assessment` block on output
- [ ] `arifOS` service stays `active` throughout deploy

---

## 12. Required SEALS (3, unchanged)

1. ☐ Spec §18 checkbox flip
2. ☐ Execution prompt ratified as §19 Amendment A (28 components confirmed)
3. ☐ Deployment lock: per-organ or all-at-once

---

## 13. Next Safe Action

```yaml
next_safe_action: AWAIT_ARIF_SEAL
  blocks:
    - any_mutation_to_/opt/arifos/app/
    - any_call_to_arif_forge_execute
    - any_call_to_arif_vault_seal
    - any_arifos_service_restart
  allows:
    - additional_phase_3_inspection (read-only grep, ls, cat)
    - additional_patch_plan_revision
    - additional_dry_run_tests
    - spec_amendment_drafts
```

---

## 14. Receipt to Self

| Timestamp (UTC) | Event |
|---|---|
| 2026-06-28 05:02 | Spec v1 written |
| 2026-06-28 05:04 | PDF received |
| 2026-06-28 05:05 | HOLD issued on auto-execution |
| 2026-06-28 05:08 | PDF classified, patch plan v1 written |
| 2026-06-28 05:09 | arifOS service verified `active` |
| 2026-06-28 05:10 | Phase 3 inspection begun |
| 2026-06-28 05:11 | Discovered schemas are Pydantic (not JSON), prior art exists |
| 2026-06-28 05:12 | Patch plan v2 written with corrected paths |

---

*OPENCLAW · 333-AGI · 2026-06-28 05:12 UTC*
*DITEMPA BUKAN DIBERI*

*Spec ID: MCP-SYMBOLIC-HARDEN-v1*
*Patch plan v1 ID: MCP-SYMBOLIC-HARDEN-pp-v1 (superseded)*
*Patch plan v2 ID: MCP-SYMBOLIC-HARDEN-pp-v2 (current, corrected)*