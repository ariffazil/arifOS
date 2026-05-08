# W@W Authority Envelope — Operational Spec

> **Version:** v1.0.0-canonical  
> **Status:** SEALED  
> **Epistemic:** CLAIM  
> **DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**

---

## 1. Definition

The **W@W Authority Envelope** is the canonical container for proposals flowing through the federated stack. It makes the "three authorities" abstraction machine-checkable and enforces the **monotone-narrowing invariant**: no downstream organ may widen the constraint set.

---

## 2. Authority Map

| Authority | Envelope Type | Question | Hard Stop |
|---|---|---|---|
| **arifOS** | `PERMITTED` | "Is this allowed?" | `VOID` or `888_HOLD` |
| **GEOX** | `FEASIBLE` | "Benda ni boleh jadi tak?" | `BLOCK` |
| **WEALTH** | `PRICED` | "At what cost?" | `VOID` / `HOLD` or `r_adj` spike |
| **F13 Sovereign** | `SEALED` | "Do I confirm?" | Veto / Approve |

---

## 3. Envelope State Machine

```
RAW proposal
    ↓
[arifOS]  →  PERMITTED  | VOID | HOLD
    ↓
[GEOX]    →  FEASIBLE   | BLOCK
    ↓
[WEALTH]  →  PRICED     | VOID | HOLD
    ↓
[F13]     →  SEALED     | VETO
    ↓
VAULT999
```

**Rule:** If any authority emits `VOID`, `BLOCK`, or `HOLD`, the envelope **terminates** and is logged to VAULT999 with the triggering authority recorded.

---

## 4. Monotone-Narrowing Invariant

For any valid transition from envelope `A` to envelope `B`:

```
constraints(A) ⊆ constraints(B)
```

That is:
- `floors` array must not shrink.
- `physics` array must not shrink.
- `capital` array must not shrink.

**Enforcement:** Any receiver (e.g. WEALTH MCP reading a GEOX envelope) must validate that the incoming constraints are a superset of the previous stage. If narrowing is violated, emit `F12` block (`No Override`) and log to VAULT999.

---

## 5. MCP Status Codes by Authority

### arifOS
| Code | Meaning | AKI Mapping |
|---|---|---|
| `200 CLEAR` | Proposal passes F1-F13, permitted to proceed | — |
| `-32001 HOLD` | Irreversible or high-risk; human veto required | `AKI_ERROR_HOLD` |
| `-32002 SABAR` | Vague input or low confidence; clarify and resubmit | `AKI_ERROR_SABAR` |
| `-32003 VOID` | Constitutional violation (harm, injection, override) | `AKI_ERROR_VOID` |

### GEOX
| Code | Meaning |
|---|---|
| `200 CLEAR` | Physics feasible, geo envelope valid |
| `400 BLOCK` | Violates physical law, resource limit, or geo constraint |
| `422 UNPRICEABLE` | Pass-through from WEALTH if it receives a BLOCKed envelope (should never happen; F12 guard) |

### WEALTH
| Code | Meaning |
|---|---|
| `200 PRICED` | `r_adj`, `Δbps`, and capital constraints computed |
| `-32001 HOLD` | Maruah RED (`M < 0.4`), irreversible capital op, or high shadow |
| `-32003 VOID` | `ΔS > 0` with no 888_HOLD, or `Peace² < 1.0` for sealed op |
| `402 UNPRICEABLE` | Received a BLOCKed envelope; reject immediately |

### F13 Sovereign
| Code | Meaning |
|---|---|
| `201 SEALED` | Human confirms; 999_SEAL issued |
| `403 VETOED` | Human rejects; envelope terminated |

---

## 6. Upstream Seals Chain

Every envelope carries `upstream_seals`: an append-only array of prior evaluations. Each entry contains:
- `authority`
- `envelope_type`
- `verdict`
- `integrity_hash` (SHA-256 prefix)
- `epoch`

This makes **audit replay** possible: any external validator can reconstruct the full narrowing history by reading VAULT999.

---

## 7. Failure Modes

| Failure | Symptom | Mitigation |
|---|---|---|
| **Envelope widening** | Downstream authority removes a constraint added upstream | F12 hard block; log to VAULT999; reject operation |
| **Phantom transition** | Envelope claims `FEASIBLE` without an `arifOS` upstream seal | Reject; no orphan envelopes permitted |
| **Stale envelope** | `epoch` older than threshold (e.g. 300s) when received | Reject; require fresh re-evaluation |
| **Hash mismatch** | `integrity_hash` of upstream seal does not recompute | Flag VAULT999 corruption; enter DEGRADED mode |
| **Authority impersonation** | Non-arifOS actor signs as arifOS | Cryptographic verification of seal signatures (future) |

---

## 8. Integration with Existing Types

This schema extends the AKI transport contract defined in `src/types/aki.ts`:
- `verdict` maps to `AkiVerdict`
- `verdict_code` maps to `AKI_ERROR_HOLD`, `AKI_ERROR_SABAR`, `AKI_ERROR_VOID`
- `witness` maps to AKI tri-witness `{ human, ai, earth }`
- `telemetry` fields (`dS`, `peace2`, `psi_le`) map to `AkiTelemetrySnapshot`

---

*Spec v1.0.0 | SEALED as arifOS canon | 999 SEAL ALIVE*
