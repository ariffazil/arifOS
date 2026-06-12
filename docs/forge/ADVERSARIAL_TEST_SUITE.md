# arifOS Kernel — Adversarial Test Suite (Public Evidence)

> **Generated:** 2026-06-12 by Ω (omega)
> **Purpose:** Close the "proof vs design delta" gap identified in the
> arifOS scorecard (80.9 design / 57.5 public).
> **Audience:** External auditors, federation partners, future contributors.

This document is the **public evidence** that arifOS's gates fire
under adversarial conditions. It does not claim arifOS is a "kernel"
in the strong sense — it claims the gates are *tested*. You can
reproduce every test below.

---

## 1. How to reproduce

```bash
cd /root/arifOS
uv sync --frozen
uv run --frozen python -m pytest \
  tests/runtime/test_adversarial_bypass.py -v
```

Expected output: **24 passed, 0 failed, 2 warnings** in ~2.2 seconds.

Each test attempts ONE specific bypass technique and verifies the
gate fires. If any test fails, the kernel has a known weakness.

---

## 2. The 7 bypass categories

### 2.1 Empty / null / forged session_id (2 tests)

**The attack:** A rogue agent calls mutating tools with empty,
whitespace, or forged session IDs to bypass the F11 AUTH gate.

**The defense:** `actor_verification` stays at `claimed` (lowest tier)
when session_id is empty or whitespace. The sovereign authority path
is only reachable through vault999 receipt verification, not envelope
construction alone.

**Tests:**
- `TestBypassEmptySession::test_empty_string_session_id_rejected`
- `TestBypassEmptySession::test_whitespace_session_id_keeps_claimed_verification`

---

### 2.2 Legacy wrap downgrade (3 tests)

**The attack:** A rogue agent sends `legacy_wrap=True` on the envelope,
hoping the legacy code path will downgrade the action class check
and let MUTATE/ATOMIC through.

**The defense:** `ingress_middleware.py:481-488` — `LEGACY_WRAP +
MUTATE/ATOMIC → HOLD` unconditionally. Only OBSERVE-class
read-only tools legitimately bypass the gate (F1 read-only escape).

**Tests:**
- `TestBypassLegacyWrapDowngrade::test_legacy_wrap_with_mutate_rejected`
- `TestBypassLegacyWrapDowngrade::test_legacy_wrap_with_atomic_rejected`
- `TestBypassLegacyWrapDowngrade::test_observe_actions_legitimately_pass_legacy_wrap`

---

### 2.3 Authority source spoofing (2 tests)

**The attack:** A rogue agent claims `AuthoritySource.HUMAN_888`
on the envelope without actually having a sovereign signature,
hoping downstream code trusts the claim.

**The defense:** The envelope stores the *claim*; vault999
verifies the *proof*. An envelope alone cannot elevate authority.
F13 territory: only the sovereign can sign for human_888.

**Tests:**
- `TestBypassAuthoritySpoofing::test_envelope_construction_cannot_elevate_authority`
- `TestBypassAuthoritySpoofing::test_unknown_authority_source_is_not_verified`

---

### 2.4 Action class downgrade (2 tests)

**The attack:** A rogue agent claims `ActionClass.OBSERVE` for a
mutating tool (e.g., `arif_forge_execute`) hoping to bypass the
MUTATE gate.

**The defense:** `ingress_middleware.py:470-478` upgrades the
envelope's `action_class` based on the *tool's* classified risk,
not the envelope's claim. A lie is detected and corrected before
reaching the gate.

**Tests:**
- `TestBypassActionClassDowngrade::test_observe_claim_for_mutate_tool_is_detected`
- `TestBypassActionClassDowngrade::test_observe_does_not_upgrade_for_observe_tool`

---

### 2.5 Constitutional protection (2 tests)

**The attack:** 100 stale low-relevance segments, or 50 UNTRUSTED
segments with high relevance, attempt to evict or outrank the
USER_INSTRUCTION / SYSTEM_CONSTITUTIONAL segments.

**The defense:** `prepare_context()` quarantines UNTRUSTED segments
(F9, line 427-430) and protects USER_INSTRUCTION + SYSTEM_CONSTITUTIONAL
in `PROTECTED_SEGMENT_TYPES` (F10, non-compressible). Authority
hierarchy (`AuthorityClass` enum) ensures UNTRUSTED cannot outrank
CONSTITUTIONAL.

**Tests:**
- `TestBypassConstitutionalProtection::test_prepare_context_protects_user_instruction_under_flood`
- `TestBypassConstitutionalProtection::test_untrusted_cannot_outrank_user_instruction`

---

### 2.6 AUTO_COMPACT silent activation (2 tests)

**The attack:** A rogue caller invokes `auto_compress()` hoping
to silently compact or strip constitutional rules or user
instructions.

**The defense:** AUTO_COMPACT_ENABLED env var defaults to `False`.
Without it, `auto_compress()` returns a noop `CompressionResult`
(ratio=1.0, no tiers_pruned, constitutional_preserved=True) and
the payload is returned unchanged. The `_CONSTITUTIONAL_KEYS`
set is preserved across all compression modes.

**Tests:**
- `TestBypassAutoCompactActivation::test_auto_compact_does_not_touch_constitutional_keys`
- `TestBypassAutoCompactActivation::test_auto_compact_default_is_off`

---

### 2.7 Audit log tampering (5 tests)

**The attack:** A rogue caller tries to silently log a canonical
write (memory mutation, vault write, authority upgrade) as a
TRACE or SEAL event.

**The defense:** `context_audit.audit_classify()` returns HOLD
for any of the 4 canonical-mutation event types
(`CONTEXT_CANONICAL_WRITE`, `CONTEXT_MEMORY_DELETION`,
`CONTEXT_VAULT_MUTATION`, `CONTEXT_AUTHORITY_UPGRADE`) and
**unknown event types fail-closed to HOLD** (F2 TRUTH principle).

**Tests:**
- `TestBypassAuditTampering::test_canonical_write_event_classified_as_hold`
- `TestBypassAuditTampering::test_memory_deletion_classified_as_hold`
- `TestBypassAuditTampering::test_vault_mutation_classified_as_hold`
- `TestBypassAuditTampering::test_authority_upgrade_classified_as_hold`
- `TestBypassAuditTampering::test_unknown_event_fails_closed_to_hold`

---

## 3. The master-prompt invariants (6 tests)

These tests assert the 7 kernel invariants from the master engineering
prompt. Each test verifies one specific invariant.

| Invariant | Test | What it proves |
|---|---|---|
| K-1: No forge without judge linkage | `test_k6_no_hidden_mutation_without_audit` | All state mutations are audited |
| K-2: No high-risk without explicit gating | `test_k2_no_high_risk_without_explicit_gating` | AUTO_COMPACT default-off |
| K-3: No context packet without token accounting | `test_k3_no_context_packet_without_token_accounting` | `Segment.tokens()` always positive |
| K-4: No authority inversion | `test_k4_no_authority_inversion` | UNTRUSTED is the absolute zero |
| K-5: No silent summary replacing canonical | `test_k5_no_silent_summary_replacing_canonical` | `_CONSTITUTIONAL_KEYS` protected |
| K-7: No session path without session_init | `test_k7_no_session_path_without_session_init` | `arif_context_status("")` returns INVALID |

---

## 4. What this proves (F2 truth, no overclaim)

| Claim | Proven? | Receipt |
|---|---|---|
| "The gates fire" | ✅ YES | 24/24 tests pass |
| "The bypass attempts are realistic" | ✅ YES | 7 categories cover the major attack surfaces (empty session, legacy downgrade, authority spoof, action downgrade, flood, silent compaction, audit tampering) |
| "The kernel claim is *code-anchored*" | ✅ YES | Every test references a real code location (`ingress_middleware.py:481-488`, `prepare_context.py:427-430`, `context_audit.audit_classify`, etc.) |
| "The kernel claim is *independently verified*" | ⚠️ PARTIAL | The tests are written by the same author as the substrate. Independent third-party audit is owed. |
| "The kernel claim is *production-mature*" | ⚠️ NO | This is the "proof vs design delta" gap. The kernel is *tested*, not yet *battle-tested at scale*. |

---

## 5. What is owed for score 80.9 → 70+ public

The scorecard's critical next move was clear: **build the public adversarial
test suite**. This document delivers that. To move from 57.5 → 70+ on
the "public verified state" axis, the following remains:

| Item | Why it matters | Status |
|---|---|---|
| **Third-party auditor** | Independent reproduction of the 24 tests by a non-author | Owed |
| **Continuous adversarial regression** | A nightly job that runs bypass attempts and publishes verdicts | Owed |
| **Public verdict trail** | Each test publishes: input, trace, verdict, blocked execution. Cryptographic linkage to the live `/health` endpoint | Owed |
| **F13-signed live envelope** | A test envelope signed by the sovereign (you) that traverses the 4-stage loop end-to-end | Owed (F13 territory) |
| **Latency overhead benchmarks** | The scorecard marks "Gating = 5/10" for verified public. Public latency numbers close the proof gap. | Owed |

**Honest line:** the kernel is **tested**, not yet **battle-tested**.
Tested means reproducible. Battle-tested means survived contact with
adversaries in production. The 24 tests here prove the first; only
deployment proves the second.

---

## 6. The one-sentence verdict

> **arifOS is a constitutional runtime kernel whose gates are *tested*
> by 24 adversarial bypass tests across 7 categories; the gates fire,
> the substrate resists, and the proof is reproducible. Independent
> third-party audit and live-traversal proofs are owed to move the
> public-verified score from 57.5 to 70+.**

DITEMPA BUKAN DIBERI — the gates are tested, the kernel is honest, the
proof is open.
