# THREE-LAYER ONTOLOGY — arifOS Federation | Canonical Doctrine

> **Δ** = **SUBSTRATE** (Machine Layer) — What physically/systemically changed?
> **Ω** = **CONSTITUTION** (Governance Layer) — Was it allowed, bounded, reversible?
> **Ψ** = **COGNITION** (Intelligence Layer) — Did reasoning stay alive, useful, truthful?

---

## 1. Ontology Separation

```
                  ┌─────────────────────────┐
                  │       COGNITION (Ψ)     │  Is the reasoning good?
                  │    "Never let Ψ execute"│
                  └────────────┬────────────┘
                               ▼
                  ┌─────────────────────────┐
                  │     CONSTITUTION (Ω)    │  Is the action allowed?
                  │  "Never let Ω hallucinate"│
                  └────────────┬────────────┘
                               ▼
                  ┌─────────────────────────┐
                  │       SUBSTRATE (Δ)     │  Is the machine real and stable?
                  │    "Never let Δ judge"  │
                  └─────────────────────────┘
```

Never mix these layers.

* A bug in schema is a **substrate failure** (Δ).
* A bad SEAL or skipped lease is a **constitution failure** (Ω).
* A hallucinated interpretation or poetry pretending to be code is a **cognition failure** (Ψ).

---

## 2. Layer Verbs & Rules

### Layer 1: SUBSTRATE (Δ)
* **Function**: Carry state.
* **Question**: What changed?
* **Failure Modes**: Drift, crash, schema mismatch, stale dependency, hidden side effect.
* **Evidence**: Health check, schema echo, version, latency, logs, dependency state.
* **Verbs**: `probe`, `echo`, `validate`, `route`, `execute`, `record`, `recover`.
* **Engineering Rule**: *No substrate claim without live or cached evidence level.*

### Layer 2: CONSTITUTION (Ω)
* **Function**: Bound action.
* **Question**: Is this allowed?
* **Failure Modes**: Overreach, faked authority, skipped 888, unclear reversibility, unleased action.
* **Evidence**: Floor result, verdict, authority level, lease, blast radius, human veto.
* **Verbs**: `classify`, `bound`, `hold`, `judge`, `lease`, `veto`, `seal`.
* **Engineering Rule**: *No mutation without authority, reversibility class, blast radius, and receipt path.*

### Layer 3: COGNITION (Ψ)
* **Function**: Reduce uncertainty.
* **Question**: What is the best interpretation?
* **Failure Modes**: Hallucination, overconfidence, false synthesis, stale memory.
* **Evidence**: Reasoning trace, counterargument, confidence band, missing tests, source provenance.
* **Verbs**: `observe`, `infer`, `compare`, `challenge`, `synthesize`, `metabolize`, `recommend`.
* **Engineering Rule**: *No inference upgrades itself into truth.*

---

## 3. The Reality Engineering Loop

```
SENSE → DECODE → GROUND → CLASSIFY → DELIBERATE → JUDGE → ENCODE → EXECUTE → VERIFY → SEAL → METABOLIZE → RETURN
```

1. **SENSE (Δ + Ψ)**: Pull live state from machine, repo, tool, human, domain.
2. **DECODE (Ψ)**: Convert messy input into structured intent and evidence.
3. **GROUND (Δ)**: Assign evidence level: `LIVE`, `FAST`, `CACHED`, or `INFERRED`.
4. **CLASSIFY (Ω)**: Determine domain, action class, reversibility, and blast radius.
5. **DELIBERATE (Ψ)**: Reason, challenge, detect contradictions, expose unknowns.
6. **JUDGE (Ω)**: Apply floors and authority: `SEAL`, `SABAR`, `HOLD`, or `VOID`.
7. **ENCODE (Δ)**: Convert approved judgment into exact tool/action envelope.
8. **EXECUTE (Δ)**: Act only through a leased executor, usually `A-FORGE`.
9. **VERIFY (Δ + Ψ)**: Compare expected state against observed state.
10. **SEAL (Ω)**: Write receipt, consequence, trace, and cooling ledger.
11. **METABOLIZE (Ψ)**: Convert result into learning: update route, doctrine, tests, and scars.
12. **RETURN (Δ)**: Feed new reality back into the next loop.

---

## 4. Canonical Triplet Invariant

Every loop step must output this triplet structure:

```json
{
  "substrate": {
    "state": "...",
    "evidence_level": "LIVE | FAST | CACHED | INFERRED",
    "dependencies": "..."
  },
  "constitution": {
    "authority": "...",
    "reversibility": "...",
    "blast_radius": "...",
    "verdict": "..."
  },
  "cognition": {
    "claim": "...",
    "confidence": "...",
    "unknowns": "...",
    "counterargument": "..."
  }
}
```
