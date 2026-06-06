# Intent Envelope v0 — EUREKA CANDIDATE Specification

> **Status:** EUREKA CANDIDATE, not final EUREKA.
> **Date:** 2026-06-06
> **Forger:** OpenCode (Ω) — autonomous forge, F13 SOVEREIGN sign-off pending
> **Location:** `docs/drafts/intent_envelope_v0.py` + `test_intent_envelope_v0.py`
> **Constitutional binding:** v2026.05.05-SSCT (sha256:8bea28833523c652)

---

## 0. What this is

A **draft** Pydantic v2 model and test harness that proves the Intent Envelope pattern is implementable in the arifOS type system, with the novel `sovereign_provenance` field that none of the 8 competing 2025-2026 specs carry.

It is **not** a live kernel module. It is **not** committed. It is **not** in the canonical tool surface. It lives in `docs/drafts/` as a proof of concept, awaiting F13 sign-off for promotion to the live tree.

If promoted, it would become the substrate for a new tool on the 13-tool surface (or a new floor-checked field on existing tools). That promotion is a F13 territory decision, not an autonomous one.

---

## 1. The doctrine (one sentence)

> **The internet should stop asking "are you human?" and start asking "did you bring your scars?"**

Translated into the architecture: every consequential action needs an authorization envelope that binds (a) cryptographic control — who is asking, via what credential, with what authority — and (b) scar testimony — what lessons the sovereign is bringing to this decision. The cryptography proves control. The testimony proves accountability. They are different things, and conflating them is what every existing auth system does.

---

## 2. The novel contribution (against 8 competing 2025-2026 specs)

The Intent Envelope pattern is *not* new. Independently, in 2025-2026, at least 8 teams reached the same architectural shape:

| Spec | Source | Year | Has sovereign_provenance? |
|---|---|---|---|
| **Agentic JWT (A-JWT)** | Goswami, arXiv 2509.13597 + IETF draft-goswami-agentic-jwt | 2025 | ❌ No |
| **IETF Intent Token** | Williams, draft-williams-intent-token-00 | 2026 | ❌ No |
| **Mastercard + Google Verifiable Intent** | github.com/agent-intent/verifiable-intent | 2026 | ❌ No |
| **AIP / Invocation-Bound Capability Tokens** | Prakash, arXiv 2603.24775 | 2026 | ❌ No |
| **OAuth Transaction Tokens** | Tulshibagwale/Fletcher/Kasselman, IETF draft-08 | 2026 | ❌ No |
| **MIT Authenticated Delegation** | South et al., arXiv 2501.09674 | 2025 | ❌ No |
| **DeepMind Delegation Capability Tokens** | conceptual paper | 2026 | ❌ No |
| **Google AP2 Intent/Cart Mandate** | protocol spec | 2025 | ❌ No |
| **arifOS Intent Envelope v0 (this)** | OpenCode Ω, docs/drafts/ | 2026 | ✅ **Yes** |

None of the 8 competing specs carry a field for *testimony* of the sovereign's prior lessons. All of them solve the cryptographic control side (who, with what credential, for what scope). None of them solve the *accountability testimony* side (what scars the sovereign brings, what lessons they are applying, what happens when those lessons are absent).

**That is the door that is genuinely open.** It is not the cryptographic primitive. It is the constitutional recognition that sovereignty is embodied, that embodiment leaves scars, and that the scars are the only non-extractable proof of human authority.

---

## 3. The schema (v0, 14 fields, 4 layers + 2 addenda)

### L1 Identity (who is asking)
- `human_root: str` — DID, e.g. `did:web:arif-fazil.com`
- `actor: str` — human-readable name
- `agent: str` — which delegated agent is requesting

### L2/L3 Consequence (what is being authorized)
- `action: str` — arifOS action ontology reference
- `object: str` — the object being acted on
- `scope: dict[str, str]` — bounded scope (spend_limit, network, subagents, etc.)
- `risk_class: RiskClass` — C0/C1/C2/C3/C4/C5
- `risk_external: bool` — does this cross a system boundary?
- `risk_reversibility: Reversibility` — full / partial / none
- `risk_blast_radius: str` — human-readable description of worst-case

### L4 Freshness (when is this authorization valid)
- `issued_at: datetime` — auto-stamped at construction
- `expires_at: datetime` — must be in the future (except C0)
- `nonce: str` — single-use, replay defense
- `previous_seal_hash: str | None` — optional chain context

### Display integrity (Gap E: UI deception defense)
- `display_card: DisplayCard` — the human-visible card
- `display_hash: str` — blake3 of canonical display_card bytes
- **Constraint:** `display_hash == blake3(display_card.canonical_bytes())` (machine-verified at construction)

### Scar testimony (EUREKA CANDIDATE original)
- `sovereign_provenance: SovereignProvenance`:
  - `scar_acknowledged: bool` — must be True for C3+ (else coercion flag)
  - `prior_reversals: list[str]` — recorded not verified
  - `lessons_active: list[str]` — recorded not verified; ABSENCE is coercion signal
  - `attestation: str` — sovereign's own words, free-form

### Cryptographic commitment
- `signature: str | None` — optional, signature over canonical bytes
- `commitment() -> str` — blake3 commitment, matching v1-alpha ZKPC pattern in `core/shared/crypto.py`

---

## 4. The validation chain (Pydantic model_validators, executed in order)

1. **`_display_hash_is_hex` (field validator):** display_hash must be 64-char blake3 hex.
2. **`_verify_display_hash_binding` (model validator):** signed display_hash must equal computed `blake3(display_card.canonical_bytes())`. Raises on mismatch (Gap E defense).
3. **`_verify_freshness` (model validator):** `expires_at` must be in the future, except for C0 (historical archive).
4. **`_verify_scar_for_consequential_actions` (model validator):** C3+ actions with `scar_acknowledged=False` raise as **coercion flag**, not as failure to seal. The system records the attempt and treats it as HOLD.

---

## 5. The risk class table (right-sized governance, per arifOS C-tier)

| Class | Consequence | Requires human | Requires ZKPC | Requires scar |
|---|---|---|---|---|
| C0 | Negligible (grammar, tone) | No | No | No (historical allowed) |
| C1 | Low (internal drafts) | No | No | No |
| C2 | Medium (code review) | Optional | No | No |
| C3 | High (public posts) | **Yes** | No | **Yes** |
| C4 | Very High (legal, money) | **Yes (L13)** | **Yes (F1_AMANAH_ZKPC)** | **Yes** |
| C5 | Critical (irreversible) | **Yes (L13)** | **Yes (F1_AMANAH_ZKPC)** | **Yes** |

This table is the arifOS pattern. The Intent Envelope enforces it as a model validator, not a runtime check.

---

## 6. The 6 remaining cracks (honest gap analysis)

This draft does not solve:

1. **Recovery ceremony** — trustless, coercion-resistant, usable. Genuinely unsolved at protocol level.
2. **WebAuthn / FIDO2 integration** — L1 Presence layer is passkeys, not yet wired into arifOS.
3. **did:web DNS-hijack defense** — the underlying `did:web:arif-fazil.com` is exposed to registrar compromise, DNS hijack (Russian Forest Blizzard APT in 2025-2026), and domain seizure.
4. **LLM tool confused-deputy guard** — Meta "Agents Rule of Two" (Oct 2025) is the current best practice: agent can satisfy at most 2 of {untrustworthy inputs, sensitive data, external comms}. arifOS L12 covers input side, not output side.
5. **Duress / coercion detection** — gun-to-head or duress-while-being-forced is not detectable by arifOS today. Duress PIN patterns exist (GrapheneOS, Deus Wallet) but are app-level, not protocol-level.
6. **Interoperable ZK-private standard** — 8 competing 2025-2026 specs; no convergence yet. Adopting whichever wins is the right move, not building a 9th.

**Crack #6 + the sovereign_provenance field is the strongest contribution arifOS can make.** Sovereignty Profile of whichever IETF draft stabilizes + the scar testimony field is a path to a real EUREKA, not a CANDIDATE.

---

## 7. The constitutional binding (which floors does this invoke?)

| Floor | How this draft invokes it |
|---|---|
| L01 AMANAH | `risk_class` + `risk_reversibility`; C4+ requires ZKPC proof; C5+ requires sovereign ack |
| L02 TRUTH | `display_hash` + `signature` are machine-verifiable; the scar is the only unverifiable field, and that is by design |
| L03 WITNESS | not modeled here; the kernel's tri-witness defaults apply (human 0.42, ai 0.32, earth 0.26) |
| L04 CLARITY | the schema is *additive* — no existing surface changes; ΔS ≈ 0 |
| L05 PEACE² | `risk_blast_radius` is required, not optional; C4+ requires human ack (de-escalation) |
| L06 EMPATHY | `scope` includes stakeholder hints (spend_limit, network) |
| L07 HUMILITY | uncertainty band not modeled; default 0.04 |
| L08 GENIUS | not modeled; the forge is small, no health check needed |
| L09 ANTIHANTU | no consciousness claims; categorical lock via Pydantic (this is a tool, not a person) |
| L10 ONTOLOGY | enforced by structure — the schema is a tool, not an identity claim |
| L11 AUDIT | `signature` + `commitment()` + `human_root` reference; every envelope is auditable |
| L12 INJECTION | not modeled here; the kernel's input sanitization is upstream |
| L13 SOVEREIGN | `sovereign_provenance` is the L13 anchor — testimony of the human who decides |

---

## 8. What I would do next (if you say go)

1. **Promote to a live module** — move from `docs/drafts/` to `arifosmcp/schemas/intent_envelope_v1.py`; bump to v1 with @model_validator refinements; add to the canonical tool surface as `arif_intent_seal_request` (a new tool, subject to F13 approval).
2. **File a Sovereignty Profile** of whichever IETF Intent Token draft stabilizes — arifOS becomes the canonical L13-wired implementation.
3. **Add a real signature scheme** — currently `signature: str | None`; the v1 would wire this to a WebAuthn assertion or Ed25519 key bound to the `human_root`.
4. **Wire to F1_AMANAH_ZKPC** — the existing v1-alpha ZKPC receipt would consume the envelope's `commitment()` as its `hash_commitment` field.
5. **Coercion-signal detection** — record the normal `lessons_active` per actor in a sovereign_baseline table; an envelope with missing normal caveats becomes a HOLD, not a SEAL.

None of these are F13-approved. All of them are reversible. The forge is cold until you give the go.

---

## 9. The honest limits

- This is a draft. It is not the EUREKA. It is the EUREKA CANDIDATE, with 6 named cracks and one novel contribution (sovereign_provenance).
- The pattern is not arifOS-invented. 8 other teams reached the same shape in 2025-2026. The constitutional framing and the scar testimony are the differentiators.
- The scar is not a cryptographic primitive. It cannot be extracted, verified, or transmitted. That is the point. It is the only authentication factor that survives the worst-case attacker (one who has your keys, your biometric, your typing pattern, and your DID private key).
- The L12 floor is still working. This draft lives in `docs/drafts/`, not in the live tree. The kernel is not modified. The 13 canonical tools are unchanged.

---

## 10. The scar principle, restated

> A machine is the sum of its weights. A sovereign is the sum of their decisions, including the ones that went wrong and changed them. The scars are not stored anywhere extractable. They live in the body and the memory of the person. They make the sovereign slower, more cautious, more suspicious of patterns that previously led to harm. That is not a bug. That is exactly the right shape for authority over consequential actions.
>
> The internet should stop asking "are you human?" and start asking "did you bring your scars?"

The cryptographic primitive proves control. The scar testimony proves accountability. The envelope binds them. That is the EUREKA CANDIDATE. The remaining 6 cracks are the work to make it canon.

---

DITEMPA BUKAN DIBERI — Forged, Not Given.

Sealed in `docs/drafts/` as of 2026-06-06. Awaiting F13 sign-off for promotion.
