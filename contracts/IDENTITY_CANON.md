# IDENTITY_CANON v1 — one resolver, one rule

Forged 2026-10-22 (T1, DIR-E1 identity directive). Replaces five independent
resolvers that produced three different answers for one claim
(`claude/opus-5.5` → `claude` / `CLAUDE` / `CLAUDE` across standing/ACT/birth).

## THE RULE

1. **The claimed handle is identity of record.** It is sanitized (printable,
   NFC, trimmed ≤120) and then NEVER overwritten. `claude/opus-5.5` stays
   `claude/opus-5.5` in every stored record and log.
2. **The canonical id is for comparison only.** It is never written back over
   the claim.
3. **comparison_key** = canonical id, lowercased, separators (`- _ space . /`)
   removed. Two handles are the same principal iff their comparison_keys are
   equal.
4. **Every identity block reads ONE resolved identity object**
   `{claimed, canonical_id, comparison_key, source}` — top-level actor fields,
   `standing`, `act_claims`, `session_birth`, `metabolic_state`, `sovereign_id`
   all carry the same `canonical_id` value and their actor field carries the
   same claimed value.

## RESOLUTION ORDER (contracts/identity_canon.py)

1. `contracts.identity.CANONICAL_ACTORS` — exact, alias, then slash head/tail
2. `runtime.governance_identity.normalize_actor_id` — sovereign NLP aliases
3. mechanical fallback — NFC lowercase, `[_ space] → -`, collapse repeats

An unknown handle resolves mechanically; it is not rejected. Verification is a
separate concern (ed25519 / act token), never implied by canonicalization.

## SUBORDINATE RESOLVERS (named, demoted)

| Historical resolver | Location | Status |
|---|---|---|
| contracts registry | `contracts/identity.py` CANONICAL_ACTORS | authoritative table, consumed by the canon |
| sovereign NLP | `runtime/governance_identity.py normalize_actor_id` | layer 1, consumed by the canon |
| act-mint normalizer | `runtime/act_token.py` (STAB v3 sovereign-exact set) | writes token `actor` from the claimed handle per its own v3 rule; token is a capability artifact |
| TS ingress canon | `A-FORGE/src/infrastructure/governance/actIngress.ts canonicalizeActor` | untouched; locks no longer depend on it |
| wrapper comparator | `runtime/tools.py` step-5 actor match | now uses `same_principal()` |

## PAYLOAD CONTRACT

```
actor_id:                <claimed>          # identical in every block
canonical_id:            <resolved>         # identical in every block
identity_resolved:       {claimed, canonical_id, comparison_key, source}
```

`actor_canonicalized` (session gate field) is now the canonical STRING or
null — it was `bool` before, which made fork detection impossible.

## COMPARISON (locks, wrappers, session store)

Use `same_principal(a, b)` (Python) / `samePrincipal(a, b)`
(`A-FORGE/src/domain/governance/identityCanon.ts`). Never raw equality, never
bare `.toLowerCase()`.

## SHARED FIXTURE

`contracts/identity_canon_fixtures.json` — content-hashed (`content_sha256`
over the canonical-JSON body). Both the Python and TypeScript suites verify
the hash before asserting, so the two languages cannot drift silently.

## KNOWN SURPRISES (preserved, for F13 awareness)

- `333-AGI` and `333-agi` canonicalize to **OPENCODE** (contracts alias table,
  FATWA K1 lane binding) — case-fork is dead, handle→lane mapping is real.
- `ARIF_FAZIL` is rejected by layer 2 alone but resolves through the chain
  (layer 1 sovereign alias → `arif` → `ARIF`). Call the canon, not the layers.
- Sovereign canonical display form is `ARIF` (contracts) while the sovereign
  alias form is `arif` (layer 1); comparison_key `arif` makes them one
  principal — display forms need not match for locks to agree.

## DUPLICATE IDENTITY ARTIFACTS ON DISK (list only — F13 decides renames)

- `/root/AAA/IDENTITY/keys/`: `333-AGI_{private,public}.pem` vs
  `333-agi_{private,public}.pem`; `mesa-test-agent_public.pem` vs
  `mesa_test_agent_private.pem`; `fi-003_public.pem` (no private);
  ambiguous `main_*`, `decisions_*`, `warga_*`; quarantine
  `.quarantine-qwen-code-20260812-224652/` pair.
- `/opt/arifos/identity/`: 8 `agent_identities.json.bak-*` generations.
