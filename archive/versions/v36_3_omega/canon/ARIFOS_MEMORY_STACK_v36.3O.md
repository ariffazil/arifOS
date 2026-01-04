# arifOS Memory Stack v36.3Omega

> **Binding Law:** This canon defines the constitutional memory stack for arifOS.
> **Epoch:** v36.3Omega PHOENIX | **Sealed:** APEX PRIME
> **Motto:** "Memory must cool before it rules."

---

## Source Files

| File | Location | Status |
|------|----------|--------|
| **ARIFOS_MEMORY_STACK_v36.3O.md** | `v36.3O/canon/` | **BINDING** |
| CCC_ARCHITECTURE_v36.3O.md | `v36.3O/canon/` | Cross-reference |
| PHYSICS_APEX_THEORY_PHYSICS_v36.3O.md | `v36.3O/canon/` | Physics foundations |
| spec/memory_context_spec_v36.3O.json | `v36.3O/spec/` | Machine-readable schema |

---

## Section 1: Purpose & Scope

The arifOS Memory Stack governs how memory is structured, governed, and evolved across the 000→999 pipeline. This canon answers four questions:

1. **What counts as memory?** — Six bands with distinct authority and mutability
2. **Who is allowed to change it?** — Authority hierarchy (Human > Phoenix-72 > Runtime)
3. **Where does it live over time?** — Hot/Warm/Cold tiers with promotion rules
4. **How do scars become law?** — Phoenix-72 metabolism from evidence to amendment

### Binding Scope

This canon binds all runtime implementations that read or write governed memory:

- `MemoryContext` and all six bands
- VAULT-999 interfaces (L0–L4)
- Cooling Ledger + Phoenix-72
- Scar registries and zkPC (EUREKA) anchors

---

## Section 2: The Six Memory Bands

arifOS organizes memory into six logical bands. Each band has defined authority, mutability, and truth status.

### 2.1 Summary Table

| Band | Key | VAULT-999 Layer | Authority | Mutability | Truth Status |
|------|-----|-----------------|-----------|------------|--------------|
| Env Band | ENV | L0/L1 context | Runtime host | Mutable | Context (non-law) |
| Vault Band | VLT | L0 | Phoenix-72 + Human | Immutable* | **Law** |
| Ledger Band | LDG | L1 | APEX PRIME pipeline | Append-only | **Evidence** |
| Active Stream | ACT | (volatile) | Runtime engines | Volatile | Working state |
| Vector Band | VEC | L3 | Runtime + Tools | Mutable | Witness |
| Void Band | VOID | L2/L3/L4 edge | Phoenix-72 + Tools | Append-only | Diagnostics/Scars |

\* Vault Band is immutable at the level of **current law**. Mutations are only legal via Phoenix-72 amendments, anchored in Ledger + Vault history.

### 2.2 Band Definitions

#### Env Band (ENV)

Holds ambient, non-secret context needed to interpret a request:

- Epoch, runtime manifest ID, stakes class, language/locale, safety configuration

**Constraints:**
- Must never be treated as canonical law or evidence
- May be rebuilt per request or per session
- **Invariant:** Must not contain user secrets, long-term identifiers, or raw chat history

#### Vault Band (VLT)

Mirrors VAULT-999 L0 (Constitution). Contains:

- Floor thresholds (F1–F9) and physics parameters (`deltaOmegaPsi`)
- AAA Trinity definitions (ARIF, ADAM, APEX PRIME)
- Pointers to Phoenix-72 amendment history and final seal requirements

**Constraints:**
- Read-only snapshot of the current constitutional state in memory
- Updates must flow: **Ledger → Phoenix-72 → Vault L0 → next snapshot**
- **Invariant:** No other band may override or shadow Vault Band fields. Any conflict is a **PARADOX_HOTSPOT**.

#### Ledger Band (LDG)

In-memory view over recent Cooling Ledger entries (L1).

**Primary purposes:**
- Provide short-horizon evidence for governance decisions
- Feed Phoenix-72 with high-stakes failure statistics and scar candidates

**Constraints:**
- Append-only projection: in-memory views may be filtered or truncated, but MUST NOT re-order or edit entries
- **Invariant:** Any loss of hash-chain integrity must trigger **SABAR** and prevent SEAL

#### Active Stream Band (ACT)

Holds volatile, short-lived working state for the current request:

- Prompt framing, intermediate tool calls, partial reasoning traces
- W@W votes prior to final verdict

**Constraints:**
- May be cleared between pipeline stages
- Never written to VAULT-999
- **Invariant:** Not a source of law or long-term evidence. Only what passes through APEX PRIME + Final Seal into L1 is governed evidence.

#### Vector Band (VEC)

Witness memory, typically backed by vector indexes (e.g., FAISS, external vector DBs).

**Stores:**
- Scar embeddings, witness narratives, external documents, policy corpora

**Constraints:**
- Soft authority: results inform reasoning but are treated as *witness*, not truth
- Vault + Ledger override Vector
- **Invariant:** VEC content must be traceable to L1 evidence or external sources with provenance

#### Void Band (VOID)

Negative space for diagnostics and scars:

- Scar proposals, paradox flags, anomaly logs, failed floor checks
- "Do not repeat" patterns

**Constraints:**
- Primary signal source for Phoenix-72 amendment proposals
- **Invariant:** VOID entries must be:
  - Signed (when promoted to canonical scars)
  - Anchored to specific ledger entries or governance events
  - Never silently discarded; healing must be explicit (see SCARS canon)

---

## Section 3: Hot / Warm / Cold Tiers

The memory stack uses temporal/volume tiers for data management.

### 3.1 Tier Mapping Table

| Tier | Typical Location | Bands Primarily Affected | Retention |
|------|------------------|--------------------------|-----------|
| **Hot** | `runtime/`, in-memory | Env, Active Stream, recent Ledger | Hours–days |
| **Warm** | `cooling_ledger/`, archives | Ledger, selected Vector + Void | Days–weeks |
| **Cold** | `vault999/`, external archive | Vault, full Ledger, Scars, zkPC | Weeks–years |

### 3.2 Promotion Rules

**Invariants:**

1. **One-way promotion:** Hot → Warm → Cold
2. **Cold requires governance:** Any material change to Cold requires Phoenix-72 + human sign-off
3. **Deletion:** Allowed only for legal compliance and privacy requirements (governed by VAULT-999 privacy protocols)
4. **Truth status unchanged:** Hot/Warm vs Cold does not change truth status—only access cost

---

## Section 4: Governance Invariants

### I1. Vault Supremacy

Vault Band (L0) overrides all other bands on questions of law. Any runtime configuration in Env, Vector, or Active Stream that contradicts Vault is void and must be logged as a paradox.

### I2. Ledger Integrity

Ledger Band must reflect an unbroken hash chain for any SEAL verdict. Any failure in hash-chain continuity triggers SABAR and blocks SEAL until repaired or formally exempted.

### I3. Scars Must Bind

Once a scar is sealed and promoted to canonical (in Void/Vector + Vault), it must:
- Be consulted by relevant governance paths
- Show up in Phoenix-72 pressure computations for relevant floors

### I4. No Raw Chat in VAULT-999

Raw chat, drafts, and uncooled reasoning transcripts are forbidden in VAULT-999 L0–L4. Derived summaries and metrics are allowed, as specified by VAULT-999 architecture.

### I5. Memory Cooling Before Law

High-stakes interactions must transit:
```
Active Stream → Cooling Ledger → Phoenix-72 (if needed) → Vault
```
Direct law changes without evidence and cooling are unconstitutional.

---

## Section 5: Phoenix-72 Pressure & Memory Stack

Phoenix-72 is the controlled amendment engine. From the memory stack perspective:

### 5.1 Inputs

- Statistics over Ledger Band (N fails per floor over window T)
- Scar records in Void Band
- Witness patterns in Vector Band

### 5.2 Outputs

- Proposed amendments to Vault Band (threshold adjustments, enforcement policy)
- Scar promotions or healings

### 5.3 Pressure Signal (Informal)

```
P(F) = w1 × (N_fail(F, T) / T) + w2 × S_severity(F)

Where:
  N_fail(F, T) = number of floor failures in window T
  S_severity(F) = aggregate severity weights from relevant scars
  w1, w2 = tunable weights
```

**TODO(Arif):** Confirm default T, w1, w2 values for v36.3Omega production.

### 5.4 Pressure Constraints

Amendments MUST be:
- Grounded in L1 evidence
- Traceable to specific scars
- Respectful of safety caps (e.g., |delta| ≤ 0.05 per cycle)

Any Phoenix-72 proposal must be anchored to:
- One or more Cooling Ledger entries (hashes)
- One or more scar IDs
- Logged in Void/Vault indices before being applied

---

## Section 6: Runtime Implementation Mapping

### 6.1 Runtime Modules

| Component | Module | Purpose |
|-----------|--------|---------|
| MemoryContext | `arifos_core/memory/memory_context.py` | Six-band container (target) |
| Vault Band | `arifos_core/memory/vault999.py` | L0 constitution access |
| Ledger Band | `arifos_core/memory/cooling_ledger.py` | L1 evidence access |
| Void/Scars | `arifos_core/memory/scars.py` | Scar registry |
| Phoenix-72 | `arifos_core/memory/phoenix72.py` | Amendment metabolism |

### 6.2 Specs

| Spec | Location | Purpose |
|------|----------|---------|
| `memory_context_spec_v36.3O.json` | `v36.3O/spec/` | Six-band schema |
| `vault999_ledger_schema_v36.3O.json` | `v36.3O/spec/` | L0-L4 schemas |

---

## Section 7: PARADOX_HOTSPOTS

| Hotspot | Issue | Status |
|---------|-------|--------|
| **HS-MEM-001** | MemoryContext six-band structure not yet implemented in runtime | DELTA |
| **HS-MEM-002** | Vector Band provenance tracking partial | DELTA |
| **HS-MEM-003** | Phoenix-72 pressure defaults (T, w1, w2) not canonized | TODO(Arif) |

---

## Section 8: Sign-Off

**Status:** SEALED
**Epoch:** v36.3Omega PHOENIX
**Last Verified:** 2025-12-12

*This canon is authoritative for arifOS memory behavior. For L0-L4 layer details, consult CCC_ARCHITECTURE_v36.3O.md.*

