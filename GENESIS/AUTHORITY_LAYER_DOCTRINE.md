# AUTHORITY_LAYER_DOCTRINE

> **Canonical:** `/root/arifOS/GENESIS/AUTHORITY_LAYER_DOCTRINE.md`
> **Forged by F13 SOVEREIGN** (Arif bin Fazil)
> **Date:** 2026-08-09T06:00:00Z
> **Parent:** LAYER_SEPARATION_DOCTRINE.md (060)

## The Core Distinction

ACT and did:web are NOT communication protocols like MCP or A2A.

They are **authority layers**.

| Layer | Answer | Domain |
|-------|--------|--------|
| MCP | How do I call? | Plumbing |
| A2A | Who talks to who? | Coordination |
| **did:web** | Who are you? | **Identity** |
| **ACT** | What may you do? | **Authority** |
| **F1-F13** | Should that office be allowed? | **Constitution** |
| **VAULT999** | Can we prove it later? | **Evidence** |

---

## did:web = Identity

did:web provides cryptographically verifiable identity.

```
did:web:arif-fazil.com:hermes
did:web:arif-fazil.com:aaa
did:web:arif-fazil.com:a-forge
```

When AAA receives:

```json
{
  "sender": "did:web:arif-fazil.com:hermes"
}
```

AAA can verify:
- Is this identity real?
- Is it a known entity?
- Without did:web: "trust me bro"
- With did:web: cryptographically identifiable actor

---

## ACT = Authority

After identity is established:

```
WHO ARE YOU?
    ↓
WHAT MAY YOU DO?
```

Example:

```json
{
  "actor": "did:web:arif-fazil.com:hermes",
  "capability": "research"
}
// → ALLOWED

{
  "actor": "did:web:arif-fazil.com:hermes",
  "capability": "seal"
}
// → DENIED
```

Because in arifOS: Research ≠ Judge ≠ Seal.

---

## Separation of Powers

ACT enforces the constitutional separation of powers.

| Actor | Office | Allowed |
|-------|--------|---------|
| 333-AGI | Proposer | Propose |
| 555-ASI | Verifier | Verify |
| 888-APEX | Judge | Judge |
| A-FORGE | Executor | Execute |
| VAULT999 | Witness | Record |

Therefore:

```
333 trying to SEAL
    ↓
ACT DENY
```

Even though:
- A2A valid ✓
- MCP valid ✓
- JSON-RPC valid ✓

Authority still fails.

---

## The Four-Step Flow

```
did:web
  ↓
  "Who sent this?"
  → did:web:arif-fazil.com:hermes

ACT
  ↓
  "What rights does Hermes have?"
  → READ, RESEARCH, OBSERVE

Request arrives
  ↓
  "SEAL this action"

ACT Check
  ↓
  "Does Hermes possess SEAL authority?"
  → NO
```

**Result: 403 AUTHORITY DENIED**

Without ACT: Identity → Action (dangerous)
With ACT: Identity → Capability Check → Authority Check → Action (safe)

---

## arifOS Constitutional Language

```
did:web    = "Who are you?"
ACT        = "What office do you hold?"
F1-F13     = "Should that office be allowed to do this?"
VAULT999   = "Can we prove it later?"
```

Authority enforcement is layered:

```
did:web
    ↓
ACT
    ↓
F1-F13
    ↓
Execution
    ↓
VAULT999 receipt
```

> did:web establishes identity, ACT binds identity to permitted capabilities,
> arifOS F1-F13 judges whether the requested action is constitutionally
> allowed, and VAULT999 records evidence that the decision occurred.

---

## The Anti-Pattern Without Authority Layers

Most systems do:

```
Identity → Action
```

This means ANY identified entity can perform ANY action. Identity alone is not authority.

In arifOS:

```
Identity → Office → Constitution → Action → Receipt
```

Every action passes through four gates. The system can deny at any gate, even after identity is confirmed.

---

## Verification

If ACT disappears tomorrow, can any identified entity perform any action? Yes → institution compromised. Therefore ACT is constitutional.

If did:web disappears, is identity verifiable? No → impersonation possible. Therefore did:web is constitutional.

---

*Forged 2026-08-09 from sovereign reasoning.*
*DITEMPA BUKAN DIBERI — Separation of powers is forged, not assumed.*
*F13 SOVEREIGN: Muhammad Arif bin Fazil holds final veto.*
