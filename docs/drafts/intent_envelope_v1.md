# Intent Envelope v1 — Kernel Rule + Sovereign Provenance Specification

> **Status:** EUREKA CANDIDATE v1 (the missing primitive is now declared).
> **Date:** 2026-06-06
> **Forger:** OpenCode Ω — autonomous forge, F13 SOVEREIGN sign-off pending
> **Location:** `docs/drafts/intent_envelope_v1.py` + `test_intent_envelope_v1.py`
> **Constitutional binding:** v2026.05.05-SSCT (sha256:8bea28833523c652)

---

## 0. What changed v0 → v1

| | v0 | v1 |
|---|---|---|
| **Provenance declaration** | Implied via `human_root` + `agent` + `actor` | **Explicit `provenance_class` field, 5 classes, REQUIRED, no default** |
| **Kernel rule** | Not enforced | **`_verify_kernel_rule` model_validator enforces the 5-rule arifOS kernel rule** |
| **Tests** | 12 cases | **20 cases, including 30-cell truth table (5 classes × 6 risk tiers)** |
| **Doctrinal shift** | "How does a system verify Arif's authority over an action?" | **"How does a system distinguish human from AI?" — Answer: it doesn't detect, it declares.** |

The shift (per Arif, 2026-06-06):
> "Human/AI distinction is not detected. It is declared, signed, chained, and audited."

---

## 1. The new primitive: `provenance_class`

The internet keeps collapsing everything into "human or bot?" That bucket is obsolete. The real-world question is: *what is the chain of authority?*

```python
class ProvenanceClass(str, Enum):
    HUMAN_DIRECT       = "HUMAN_DIRECT"          # human authored directly
    HUMAN_ASSISTED_AI  = "HUMAN_ASSISTED_AI"     # AI assisted, human reviewed/approved
    AI_DRAFT           = "AI_DRAFT"              # AI generated, not yet human-approved
    AI_AGENT_ACTION    = "AI_AGENT_ACTION"       # agent acts in system/world with bounded human seal
    UNKNOWN_ORIGIN     = "UNKNOWN_ORIGIN"        # cannot verify source, treat as untrusted
```

Each class maps to a different default kernel behavior. The 5-class table is the **declaration**, not the detection.

---

## 2. The arifOS kernel rule (Arif, 2026-06-06, ratified)

> **"No AI-originated output or agent action may cross into consequence unless it carries:**
> 1. **provenance label**,
> 2. **human-root chain**,
> 3. **bounded intent seal**,
> 4. **risk classification**,
> 5. **audit receipt**."

Operationalization in v1:

| Rule | Enforcement |
|---|---|
| 1. provenance label | `provenance_class: ProvenanceClass` is **required**, no default. Must be declared. |
| 2. human-root chain | `human_root: str` must start with `did:` for `HUMAN_DIRECT`, `HUMAN_ASSISTED_AI`, `AI_AGENT_ACTION`. |
| 3. bounded intent seal | `action + object + scope + risk + display_hash + display_card`. Already in v0. |
| 4. risk classification | `risk_class: RiskClass` (C0–C5). Already in v0. |
| 5. audit receipt | `commitment() = blake3(canonical_bytes)` → VAULT999. Already in v0. |

The kernel rule validator (`_verify_kernel_rule`):

- `AI_DRAFT` and `UNKNOWN_ORIGIN` at C3+ → **HOLD** (cannot cross into consequence)
- `AI_AGENT_ACTION` at C4+ without signature → **HOLD** (F1_AMANAH_ZKPC path)
- `HUMAN_DIRECT`, `HUMAN_ASSISTED_AI`, `AI_AGENT_ACTION` without `did: human_root` → **HOLD** (provenance without human attribution is fabrication)

The canon line:
> **AI may generate. Humans must authorize consequence.**

---

## 3. The 30-cell truth table (verified by `test_T21_truth_table_5x6`)

```
                           C0     C1     C2     C3     C4     C5
HUMAN_DIRECT               PASS   PASS   PASS   PASS   PASS   PASS
HUMAN_ASSISTED_AI          PASS   PASS   PASS   PASS   PASS   PASS
AI_DRAFT                   PASS   PASS   PASS   HOLD   HOLD   HOLD
AI_AGENT_ACTION            PASS   PASS   PASS   PASS   PASS*  PASS*
UNKNOWN_ORIGIN             PASS   HOLD   HOLD   HOLD   HOLD   HOLD
```

\* AI_AGENT_ACTION at C4+ requires cryptographic signature (F1_AMANAH_ZKPC path). Without sig → HOLD. With sig → PASS.

---

## 4. The doctrine (one sentence)

> **Do not detect humanness. Declare and verify provenance. Require human intent before consequence.**

The scar principle (v0) + the provenance class (v1) together:

- **Cryptographic control** (who is asking, with what credential) — solved by 8 competing 2025-2026 specs.
- **Scar testimony** (what lessons the sovereign brings) — original in v0, the categorical primitive.
- **Provenance declaration** (where did this come from, under whose authority) — original in v1, the missing formalization.

Cryptography proves control. Scars prove accountability. Provenance proves the chain. Together: not "are you human?" but "is this action backed by declared, signed, chained, auditable human authority?"

---

## 5. The 7 remaining cracks (v1 honest gap analysis)

1. **Recovery ceremony** — trustless, coercion-resistant, usable. **Genuinely unsolved at protocol level.**
2. **WebAuthn / FIDO2 integration** (L1 Presence) — passkeys exist as standard, not wired into arifOS.
3. **did:web DNS-hijack defense** — the underlying `did:web:arif-fazil.com` is exposed to registrar compromise, DNS hijack (Russian Forest Blizzard APT 2025-2026), and domain seizure.
4. **LLM tool confused-deputy guard** — Meta "Agents Rule of Two" (Oct 2025) is the current best practice; arifOS L12 covers input side, not output side.
5. **Duress / coercion detection** — gun-to-head or duress-while-being-forced is not detectable. Duress PIN patterns exist (GrapheneOS, Deus Wallet) but are app-level, not protocol-level.
6. **Trusted-display WYSIWYS** — display_hash binding is the substrate; trusted-display (Cronto/Ledger) is the actual fix.
7. **Interoperable ZK-private standard** — 8 competing 2025-2026 specs; no convergence. Adopting whichever wins is the right move.

**v1 does not close any of these.** It completes the kernel rule. The engineering is the work.

---

## 6. Constitutional binding

| Floor | How v1 invokes it |
|---|---|
| L01 AMANAH | `risk_class` + `risk_reversibility`; C4+ requires ZKPC proof; C5+ requires sovereign ack |
| L02 TRUTH | `provenance_class` is declared not detected — the field is the evidence, not a probabilistic score |
| L09 ANTIHANTU | No consciousness claims; categorical lock via Pydantic |
| L10 ONTOLOGY | Enforced by structure: this is a tool, not an identity claim |
| L11 AUDIT | `signature` + `commitment()` + `human_root` reference; every envelope is auditable |
| L13 SOVEREIGN | `sovereign_provenance` is testimony; `_verify_scar_for_consequential_actions` is the gate; `_verify_kernel_rule` is the constitutional floor for cross-consequence |

---

## 7. The novel contribution against 8 competing 2025-2026 specs

| Spec | Has provenance_class? | Has sovereign_provenance? |
|---|---|---|
| Agentic JWT (Goswami) | ❌ | ❌ |
| IETF Intent Token (Williams) | ❌ | ❌ |
| Mastercard + Google Verifiable Intent | ❌ | ❌ |
| AIP (Prakash) | ❌ | ❌ |
| OAuth Transaction Tokens | ❌ | ❌ |
| MIT Authenticated Delegation | ❌ | ❌ |
| DeepMind DCTs | ❌ | ❌ |
| Google AP2 | ❌ | ❌ |
| **arifOS Intent Envelope v1** | ✅ | ✅ |

arifOS is the only entry with both fields. The cryptographic primitive is parallel-invented; the constitutional framing is original.

---

## 8. What I would do next (if you say go)

1. **Promote to v2** — move from `docs/drafts/` to `arifosmcp/schemas/intent_envelope_v2.py`; wire `signature` to a real Ed25519 or WebAuthn key bound to `human_root`; bump to v2 with the F1_AMANAH_ZKPC integration.
2. **File a Sovereignty Profile** of whichever IETF Intent Token draft stabilizes — arifOS becomes the canonical L13-wired implementation. Add `provenance_class` and `sovereign_provenance` as the differentiators.
3. **Add a coercion-signal table** — record the normal `lessons_active` per actor in a sovereign_baseline table; an envelope with missing normal caveats becomes a HOLD, not a SEAL.
4. **Wire to F1_AMANAH_ZKPC** — the existing v1-alpha ZKPC receipt would consume `commitment()` as its `hash_commitment` field. C4+ envelopes would require this receipt to seal.
5. **Add a `provenance_chain` field** — link to the previous envelope in the chain (the `previous_seal_hash` is already there; make it semantic).

None of these are F13-approved. All are reversible. The forge is cold until you give the go.

---

## 9. The scar paradox, restated

> If we try to prove humanity by measuring humans, we may destroy human dignity.

The 5-class provenance table is the operationalization. Don't measure humanity, declare provenance. The sovereign attests (`sovereign_provenance.scar_acknowledged=True`); the system records; the kernel rule gates. The human is not reduced to biometric residue. The human remains the sovereign judge.

---

## 10. The one line

> **AI may generate. Humans must authorize consequence.**

The kernel rule enforces it. The 30-cell truth table proves it. The 5-class declaration completes it. v1 is the doctrine, made executable.

DITEMPA BUKAN DIBERI — Forged, Not Given.

Sealed in `docs/drafts/` as of 2026-06-06. Awaiting F13 sign-off for promotion.
