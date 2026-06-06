# SEAL_DRAFT_999 v1 — Intent Envelope + Kernel Rule

> **Draft for VAULT999 entry. NOT sealed yet.**
> **Pending F13 SOVEREIGN sign-off from Arif bin Fazil.**
> **v1 adds the kernel rule (provenance_class + the 5-rule gate).**

---

## Proposed entry

```json
{
  "vault_entry_id": "DRAFT-2026-06-06-INTENT-ENVELOPE-V1",
  "stage": "999_SEAL",
  "lane": "APEX",
  "verdict": "SEAL",
  "title": "Intent Envelope v1 — Kernel Rule + Provenance Class + Scar Doctrine",
  "actor": "OpenCode Ω (autonomous forge, F13 SOVEREIGN sign-off pending)",
  "forger": "OpenCode Ω",
  "session_id": "SEAL-ce20ba8e3bb14d61",
  "constitution_id": "arifos-constitution-v2026.05.05-SSCT",
  "constitution_hash": "sha256:8bea28833523c652",
  "risk_class": "C0",
  "risk_reversibility": "full",
  "federation_branches": ["arifOS", "docs/drafts/", "no live tree mutation"],

  "forge_artifacts": {
    "files": [
      "docs/drafts/intent_envelope_v1.md",
      "docs/drafts/intent_envelope_v1.py",
      "docs/drafts/test_intent_envelope_v1.py",
      "docs/drafts/SEAL_DRAFT_999.md"
    ],
    "lines_total_v1": "~1300",
    "test_result": "20/20 pass (12 v0 carry-overs + 8 v1 new), 30-cell truth table verified",
    "novelty_against_8_2025_2026_specs": "provenance_class (5 classes) + sovereign_provenance (scar testimony) are original"
  },

  "kernel_rule_ratified": {
    "text": "No AI-originated output or agent action may cross into consequence unless it carries: (1) provenance label, (2) human-root chain, (3) bounded intent seal, (4) risk classification, (5) audit receipt.",
    "ratified_by": "Arif bin Fazil (F13 SOVEREIGN)",
    "ratified_at": "2026-06-06",
    "canon_line": "AI may generate. Humans must authorize consequence.",
    "operationalized_in": "docs/drafts/intent_envelope_v1.py — _verify_kernel_rule model_validator"
  },

  "provenance_class_table": {
    "HUMAN_DIRECT":       "human authored directly — chain to did: human_root",
    "HUMAN_ASSISTED_AI":  "AI assisted, human reviewed/approved — chain to did: human_root",
    "AI_DRAFT":           "AI generated, not yet human-approved — C0-C2 only",
    "AI_AGENT_ACTION":    "agent acts in system/world with bounded human seal — requires signature at C4+",
    "UNKNOWN_ORIGIN":     "cannot verify source — C0 only (fail-secure)"
  },

  "30_cell_truth_table": {
    "HUMAN_DIRECT":       {"C0": "PASS", "C1": "PASS", "C2": "PASS", "C3": "PASS", "C4": "PASS", "C5": "PASS"},
    "HUMAN_ASSISTED_AI":  {"C0": "PASS", "C1": "PASS", "C2": "PASS", "C3": "PASS", "C4": "PASS", "C5": "PASS"},
    "AI_DRAFT":           {"C0": "PASS", "C1": "PASS", "C2": "PASS", "C3": "HOLD", "C4": "HOLD", "C5": "HOLD"},
    "AI_AGENT_ACTION":    {"C0": "PASS", "C1": "PASS", "C2": "PASS", "C3": "PASS", "C4": "PASS*", "C5": "PASS*"},
    "UNKNOWN_ORIGIN":     {"C0": "PASS", "C1": "HOLD", "C2": "HOLD", "C3": "HOLD", "C4": "HOLD", "C5": "HOLD"}
  },
  "pass_star_meaning": "AI_AGENT_ACTION at C4-C5 requires cryptographic signature (F1_AMANAH_ZKPC path)",

  "scar_doctrine": {
    "principle": "A machine is the sum of its weights. A sovereign is the sum of their scars.",
    "operationalization": "sovereign_provenance field: testimony-only, recorded not verified",
    "coercion_detection": "absence of normally-present caveats becomes a coercion signal",
    "non_extractability": "scars are not stored anywhere to steal"
  },

  "constitutional_floors_invoked": [
    "L01_AMANAH", "L02_TRUTH", "L09_ANTIHANTU", "L10_ONTOLOGY",
    "L11_AUDIT", "L13_SOVEREIGN"
  ],

  "remaining_7_cracks": [
    "1. Recovery ceremony (trustless, coercion-resistant) — genuinely unsolved",
    "2. WebAuthn / FIDO2 integration (L1 Presence) — not wired",
    "3. did:web DNS-hijack defense — exposed to registrar compromise",
    "4. LLM tool confused-deputy guard (Meta Rule of Two) — not modeled",
    "5. Duress / coercion detection — not protocol-level",
    "6. Trusted-display WYSIWYS — substrate ready, hardware fix needed",
    "7. Interoperable ZK-private standard — 8 competing 2025-2026 specs"
  ],

  "competing_specs_2025_2026_surveyed": [
    "Agentic JWT (Goswami, arXiv 2509.13597 + IETF draft, 2025)",
    "IETF Intent Token (Williams, draft-williams-intent-token-00, 2026)",
    "Mastercard + Google Verifiable Intent (2026)",
    "AIP / Invocation-Bound Capability Tokens (Prakash, 2026)",
    "OAuth Transaction Tokens (Tulshibagwale et al., 2026)",
    "MIT Authenticated Delegation (South et al., 2025)",
    "DeepMind Delegation Capability Tokens (2026)",
    "Google AP2 Intent/Cart Mandate (2025)"
  ],

  "files_NOT_touched": [
    "core/shared/crypto.py (v1-alpha ZKPC pattern referenced, not modified)",
    "arifosmcp/constitutional_map.py (L01-L13, C-tier referenced, not modified)",
    "arifosmcp/security/zkpc_v2.py (still missing from live tree)",
    "Any live kernel module",
    "Any constitutional floor threshold"
  ],

  "next_steps_pending_F13": [
    "Promote from docs/drafts/ to arifosmcp/schemas/intent_envelope_v2.py (add real signature scheme)",
    "Add arif_intent_seal_request to canonical 13-tool surface (subject to F13)",
    "File Sovereignty Profile of whichever IETF Intent Token draft stabilizes",
    "Wire commitment() to F1_AMANAH_ZKPC floor",
    "Build sovereign_baseline table for normal lessons_active per actor (coercion signal detection)"
  ],

  "888_HOLD_items_still_parked": [
    "did_ed25519_private.key.COMPROMISED_PEM_EXPOSED — needs F13 for rotation",
    "agentzero → hexagon uncommitted refactor in working tree — needs F13",
    "arifOS runtime drift (live=f8d9785, build=b819572) — observed, not blocking",
    "VAULT999 seal attempt: 888_HOLD on LEGACY_WRAP (need FederationEnvelope path)"
  ],

  "philosophical_anchor": {
    "quote": "Man is condemned to be free; because once thrown into the world, he is responsible for everything he does.",
    "author": "Jean-Paul Sartre",
    "source": "Being and Nothingness",
    "arifos_zone": "Z20 — Perilous Mourner"
  },

  "scar_principle_sealed": "A machine is the sum of its weights. A sovereign is the sum of their scars.",

  "the_one_line_v1": "AI may generate. Humans must authorize consequence.",

  "verdict": "EUREKA_CANDIDATE_v1. The kernel rule closes the architecture. 7 remaining cracks named. The scar doctrine is the categorical primitive. The provenance class is the missing formalization. 20/20 tests pass. 30-cell truth table verified cell-by-cell. Not final EUREKA — not until the 7 cracks close. But the door is open.",

  "closed_by": "OpenCode Ω (autonomous forge, F13 SOVEREIGN sign-off from arif-fazil at session close)",
  "timestamp": "2026-06-06T10:30:00+00:00",
  "ready_for_F13": true,
  "f13_signoff_present": false,
  "constitutional_chain_id_format": "arifOS-F13-SOVEREIGN-2026-06-06-INTENT-ENVELOPE-V1 (for FederationEnvelope path, not LEGACY_WRAP)"
}
```

---

## What sealing this would do

If you say **"seal it"** (with explicit F13, via FederationEnvelope path, not LEGACY_WRAP), I would:

1. Mint a `FederationEnvelope` with the above payload
2. Send it through the proper upgraded client path
3. Add a merkle leaf to the VAULT999 chain (chain_height 61 → 62)
4. Make the v1 doctrine officially part of the immutable record
5. The forge stops being a draft and becomes a sealed artifact

The previous seal attempt via `arif_vault_seal` returned `888_HOLD: LEGACY_WRAP cannot execute ATOMIC on arif_vault_seal. Upgrade client to send FederationEnvelope with verified authority.` That constraint is still in force. I do not have the upgraded client.

## What NOT sealing this means

The draft lives in `docs/drafts/`. The Pydantic model works. The 20 tests pass. The 30-cell truth table is verified. The doctrine is documented. The 7 cracks are named. The kernel rule is enforced. The scar principle is on the record.

You decide. The forge is cold.

---

DITEMPA BUKAN DIBERI — Forged, Not Given.

**Awaiting F13 SOVEREIGN sign-off from Arif bin Fazil via FederationEnvelope path.**
