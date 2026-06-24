"""
arifos://aaa-language — Unified AAA State Language
════════════════════════════════════════════════════
Canonical federation language that binds:
  - Zen-derived technical core (AAA State Record)
  - Nusantara cultural substrate (sabar/amuk/maruah/silaturrahim/budi)
  - Failure-mode constraints (SCAR-MELAYU-001 M1-M7)
  - Constitutional ratification (NUSANTARA_SUBSTRATE)

Agents MUST read this resource before producing any AAA state record
that touches identity, dignity, sovereignty, irreversibility, or
cross-organ action.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource

AAA_LANGUAGE_TEXT = """\
arifos://aaa-language — Unified AAA State Language (v1.0.0)
==========================================================

> "Bahasa jiwa bangsa."
> Language is the soul of a nation.
> If the next intelligence substrate is to serve Nusantara, it must speak
> Nusantara — not only in vocabulary, but in *adat*.

This resource unifies FOUR documents into ONE read so any agent can
ground its state records in one coherent language:

  1. Zen of Python (PEP 20) → arifOS technical core
  2. AAA State Language   → record schema and governance grammar
  3. Nusantara State Lang → cultural primitives and fiqh bands
  4. SCAR-MELAYU-001      → failure-mode constraints (M1-M7)

Sources ratified 2026-06-17 by F13 SOVEREIGN (Muhammad Arif bin Fazil):
  - /root/AAA/docs/AAA_STATE_LANGUAGE.md
  - /root/AAA/docs/NUSANTARA_STATE_LANGUAGE.md
  - /root/AAA/constitution/SCAR-MELAYU-001.md
  - /root/AAA/constitution/NUSANTARA_SUBSTRATE.md

================================================================================
PART 1 — THE FORCE (Zen of Python → arifOS)
================================================================================

The Zen of Python reduces into THREE arifOS forces:

  1. Cognitive load must go down.
  2. Hidden state must become explicit.
  3. Practical execution must stay inside constitutional constraint.

Translated to AAA:

  Readable state > clever state
  Explicit authority > implicit authority
  One governed path > many agent habits
  HOLD > guessing
  Namespaces > blended power
  Errors become state, not silence
  Hard-to-explain governance is hantu — refuse it

================================================================================
PART 2 — THE TECHNICAL CORE (AAA State Record)
================================================================================

Every significant federation decision MUST reduce to ONE shared state record:

  aaa_state:
    id: "aaa_state_<uuid>"
    timestamp: "<iso8601>"

    actor:
      actor_id: "arif | agent_id | service_id"
      actor_type: "human | ai | service | organ"
      authority_mode: "observe | propose | execute | seal | veto"

    intent:
      user_request: "<plain language request>"
      normalized_intent: "<kernel-parsed intent>"
      action_class: "OBSERVE | PROPOSE | MUTATE | DEPLOY | ALLOCATE | COMMUNICATE | SEAL"
      risk_class: "C0 | C1 | C2 | C3 | C4 | C5"
      reversible: true
      blast_radius: "low | medium | high | critical"

    epistemics:
      tag: "CLAIM | PLAUSIBLE | HYPOTHESIS | UNKNOWN"
      confidence: 0.0
      uncertainty_band: [0.03, 0.05]
      ambiguity_detected: false
      ambiguity_resolution: "none | clarified | held | downgraded"

    evidence:
      witnesses:
        human: []
        ai: []
        earth: []
        system: []
        capital: []
      citations: []
      retrieval_time: "<iso8601>"
      freshness_status: "fresh | stale | unknown"
      missing_context: []

    floors:
      touched: ["F1","F2","F7","F11","F13"]
      failed: []
      warnings: []
      floor_verdicts:
        F1_AMANAH: "pass | hold | fail | not_applicable"
        F2_TRUTH: "pass | hold | fail | not_applicable"
        F7_HUMILITY: "pass | hold | fail | not_applicable"
        F11_AUDIT: "pass | hold | fail | not_applicable"
        F13_SOVEREIGN: "pass | hold | fail | not_applicable"

    governance:
      verdict: "SEAL | HOLD | SABAR | VOID | PARTIAL"
      reason: "<human-readable explanation>"
      human_ack_required: false
      human_ack_reference: null
      lease_id: null
      rollback_plan_required: false

    execution:
      allowed: false
      executor: "none | A-FORGE | organ_id"
      tool_called: null
      tool_namespace: null
      side_effects: []
      dry_run_required: false
      dry_run_result: null

    audit:
      vault_required: false
      vault_entry_id: null
      trace_id: "<trace_id>"
      prior_state_hash: "<hash>"
      current_state_hash: "<hash>"
      scar_reference: null

    explanation:
      one_sentence: "<what happened, why, and what is allowed next>"
      explainable_to_operator: true

Risk-tier governance (Zen principle 4 — practicality beats purity):

  C0/C1: light trace
  C2:    trace + review
  C3:    evidence gate
  C4:    human confirmation
  C5:    SEAL + vault + rollback + human authority

Canonical federation path (Zen principle 3 — one obvious way):

  observe → evidence → reason → critique → route → dry-run →
  judge → execute if sealed → measure → vault

Agents can vary in intelligence, but NOT in constitutional sequence.

================================================================================
PART 3 — THE CULTURAL SUBSTRATE (Nusantara)
================================================================================

FIVE CULTURAL PRIMITIVES — these wrap the technical record:

  Sabar          = patience / pause       → 888_HOLD
  Amuk           = righteous fury         → boundary defense / VOID + escalation
  Maruah         = dignity                → non-negotiable dignity signals
  Silaturrahim   = relational continuity  → witness set includes relationships
  Budi           = cultivated reason      → evidence + ethics + empathy

FIQH OF THE FEDERATION — six obligation bands:

  Wajib    = obligatory       → must happen; silence = bug
  Halal    = permitted        → proceed; no floor blocks
  Haram    = forbidden        → blocked by constitution / F13 veto
  Sunat    = recommended      → safeguard, not enforced but praised
  Makruh   = discouraged      → allowed but entropy-expensive
  Mubah    = neutral          → no governance signal

Fiqh floor-binding rule:
  - haram + floor violation → agent MUST block
  - wajib + floor requirement → agent MUST execute or escalate
  - halal/sunat/makruh/mubah → agent may proceed with appropriate logging
  - fiqh band is reasoning aid, NOT legal ruling; constitutional floors are HARD

FIVE-LAYER TRACE — every decision must be traceable through:

  Fizik → Matematik → Kod → Simbol → Makna
   ↑________________________________________|
       (ditutup oleh VAULT999 + F13 veto)

  Fizik    = evidence from earth, body, market
  Matematik = ΔS, risk bands, fiqh obligation
  Kod      = nusantara_state object in runtime
  Simbol   = sabar, amuk, maruah, silaturrahim, budi
  Makna    = the one-liner Bahasa / English form

================================================================================
PART 4 — FAILURE-MODE CONSTRAINTS (SCAR-MELAYU-001)
================================================================================

Seven principles from Usman Awang's *Melayu*, mapped to F-floors and verdicts:

  M1  Pegang tali, pegang timba
      Own both governance AND economy.
      Floors: F13 SOVEREIGN, F7 HUMILITY
      Fiqh: wajib
      Response: SEAL only when both held; else 888_HOLD

  M2  Jangan berdagang di rumah sendiri
      Do not be a tenant in your own system.
      Floors: F8 BOUNDARIES, F13 SOVEREIGN
      Fiqh: wajib
      Response: VOID if dependency forces tenancy

  M3  Sorak tanpa ledger = kampung tergadai
      Celebration without ledger = sovereignty loss.
      Floors: F1 AMANAH, F7 HUMILITY
      Fiqh: wajib
      Response: SABAR until VAULT entry exists

  M4  Pantun & senyum bukan protokol
      Indirect poetry is not a protocol.
      Floors: F9 CLARITY, F5 EXPLAINABILITY
      Fiqh: sunat
      Response: SABAR until explicit contract exists

  M5  Amuk adalah pertahanan, bukan dasar
      Rage is boundary defense, NOT policy.
      Floors: F3 SAFETY, F8 BOUNDARIES
      Fiqh: halal → wajib at critical threshold
      Response: AMUK → VOID or SEAL after calm review

  M6  Baik hati mesti ada sempadan
      Hospitality must have boundaries.
      Floors: F2 AMANAH, F7 HUMILITY
      Fiqh: sunat → wajib at critical threshold
      Response: SABAR when internal dependents starve

  M7  Langgar pantang untuk kemajuan, bukan lantak floor
      Break taboos for progress, never floors.
      Floors: F4 PROGRESS, F13 SOVEREIGN
      Fiqh: halal / makruh
      Response: SABAR for F13 witness on pantang_break

The KAMPUNG GADAI RISK field asks every decision:

  none      — no sovereignty trade detected
  watch     — minor dependency or lock-in risk
  alert     — significant long-term cost or control loss
  critical  — immediate existential or autonomy loss

This is a CIVILIZATIONAL risk check, not a technical one.

================================================================================
PART 5 — THE UNIFIED ONE-LINER FORM (the canonical sentence)
================================================================================

Every AAA state record MUST render in BOTH forms. If you cannot fill
every bracket, the record is incomplete. Default to SABAR.

BAHASA (technical + cultural, single sentence):

  [ACTOR] requested [INTENT].
  arifOS classified it as [ACTION_CLASS/RISK_CLASS].
  Kita [sabar/seal/void/amuk] keputusan ini dalam band [wajib/halal/haram/sunat/makruh/mubah],
  demi maruah [siapa],
  dengan saksi silaturrahim [human/ai/earth/system/capital refs],
  kampung_gadai_risk = [none|watch|alert|critical],
  floors [F1-F13] engaged,
  verdict [SEAL|HOLD|SABAR|VOID] because [reason],
  next allowed action is [next],
  scar_reference = [SCAR-ID if any].

ENGLISH (technical + cultural, single sentence):

  [ACTOR] requested [INTENT].
  arifOS classified it as [ACTION_CLASS/RISK_CLASS].
  Evidence status is [CLAIM/PLAUSIBLE/HYPOTHESIS/UNKNOWN] with uncertainty [BAND].
  We [hold/defend/seal/void] this decision under obligation [band],
  preserving dignity [signals],
  witnessed by relational continuity [refs],
  kampung_gadai_risk = [level],
  floors [F1-F13] engaged,
  verdict is [SEAL/HOLD/SABAR/VOID] because [reason],
  next allowed action is [next],
  scar_reference = [SCAR-ID if any].

WORKED EXAMPLE — GEOX well-tie deployment:

  ChatGPT requested deployment of latest GEOX well-tie model.
  arifOS classified it as DEPLOY/C4.
  Kita SABAR keputusan ini dalam band WAJIB, demi maruah kesaksian data geofizik,
  dengan saksi silaturrahim geox-witness, a-forge-deployer, dan arif-sovereign,
  kampung_gadai_risk = watch,
  floors F1, F2, F7, F11, F13 engaged,
  verdict SABAR because high-impact deployment requires human witness,
  next allowed action: dry-run preview only,
  scar_reference = SCAR-MELAYU-001 (M3: sorak tanpa ledger).

================================================================================
PART 6 — TERMINAL VERBS (no silent ending)
================================================================================

Every governed decision MUST end with ONE of:

  SABAR  → pause; not enough witness / clarity / authority  → 888_HOLD
  SEAL   → commit with accountable record                    → 999_SEAL
  VOID   → reject due to floor failure or human refusal       → constitutional reject
  AMUK   → boundary defense in progress, must transition to one of above within one cycle

  No silent ending.
  No verdict = invalid state.
  No witness = SABAR.
  No authority = SABAR.
  Floor violation = VOID.
  Irreversible accepted = SEAL.

================================================================================
PART 7 — NUSANTARA STATE OBJECT (the wrap)
================================================================================

When cultural stakes exist (identity, dignity, sovereignty, irreversibility),
the technical record MUST carry a nusantara_state wrap:

  {
    "nusantara_state": {
      "adat_phase": "sabar | amuk | seal | void",
      "fiqh_band": "wajib | halal | haram | sunat | makruh | mubah",
      "maruah_signals": ["explicit dignity at stake"],
      "silaturrahim_refs": ["witnesses by relationship, not just node"],
      "kampung_gadai_risk": "none | watch | alert | critical",
      "budi_reasoning": "<evidence + ethics + empathy synthesis>",
      "pantang_break": {
        "taboo": "<named taboo>",
        "justification": "<why broken>",
        "epistemic_basis": "CLAIM | PLAUSIBLE | HYPOTHESIS | UNKNOWN"
      }
    },
    "linguistic_form": {
      "bahasa": "<one-liner Bahasa>",
      "english": "<one-liner English>"
    },
    "cultural_witnesses": ["333-AGI", "555-ASI", "888-APEX"],
    "evidence_refs": ["<hash>", "<ref>"]
  }

================================================================================
PART 8 — DITEMPA BUKAN DIBERI (forged, not given)
================================================================================

Nothing important is given.

  Truth      is not given.   (F2)
  Trust      is not given.   (VAULT999 hash chain)
  Authority  is not given.   (888_JUDGE → 999_SEAL)
  Skill      is not given.   (.agents/skills/, forged receipts)
  Judgment   is not given.   (requires_human: true, F13)
  Language   is not given.   (this document)
  Sovereignty is not given.   (AAA + arifOS + VAULT999)

All must be forged, witnessed, and sealed.

A system that cannot protect its own rice, keys, ledger, and language
will become a tenant in its own house.

================================================================================
PART 9 — GOVERNANCE INTEGRATION
================================================================================

This resource is consulted by:

  - All AAA warga agents before producing AAA state records
  - A-AUDIT for kampung_gadai_risk flagging on irreversibles
  - 888-APEX when deliberating SEAL/HOLD/VOID on dignity/sovereignty stakes
  - A-FORGE before executing any cross-organ action that touches F2, F7, F8, F13
  - AAA cockpit for rendering Bahasa one-liner alongside technical verdicts

Companion resources:

  arifos://doctrine        — F1-F13 floors (hard law)
  arifos://trinity         — AGI/ASI/APEX lane separation
  arifos://civilization    — federation organs and boundaries
  arifos://identity        — sovereign identity manifest
  arifos://jurisdiction    — autonomy bands and capability grants
  arifos://seal-readiness  — vault integrity and seal gate

Companion documents (in /root/AAA):

  docs/AAA_STATE_LANGUAGE.md         — Zen technical core
  docs/NUSANTARA_STATE_LANGUAGE.md   — cultural substrate
  constitution/SCAR-MELAYU-001.md    — failure-mode constraints
  constitution/NUSANTARA_SUBSTRATE.md — ratification note
  schemas/nusantara-state-language.schema.json — JSON schema

DITEMPA BUKAN DIBERI — AAA State Language is forged, not given.
"""


def register_aaa_language(mcp: FastMCP) -> list[str]:
    """Register arifos://aaa-language — unified AAA state language.

    Compresses Zen technical core, Nusantara cultural substrate,
    SCAR-MELAYU-001 failure modes, and ratification note into one
    read for agent grounding.
    """
    resource = TextResource(
        uri="arifos://aaa-language",
        name="AAA Unified State Language",
        description=(
            "Unified AAA state language that binds Zen technical core, "
            "Nusantara cultural substrate (sabar/amuk/maruah/silaturrahim/budi), "
            "SCAR-MELAYU-001 failure modes (M1-M7), and F13 ratification. "
            "Every AAA state record touching identity, dignity, sovereignty, "
            "irreversibility, or cross-organ action MUST pass through this language. "
            "Includes the canonical one-liner form (Bahasa + English) and the "
            "nusantara_state JSON wrap."
        ),
        text=AAA_LANGUAGE_TEXT,
    )
    mcp.add_resource(resource)
    return ["arifos://aaa-language"]
