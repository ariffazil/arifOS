---
id: canon-ignition
title: Ignition - Stage 000
sidebar_position: 3
description: The constitutional airlock. What happens at stage 000 - authority verification, injection defence, thermodynamic setup, and Trinity engine ignition.
---

# Ignition - Stage 000

> Canonical source: [`000_THEORY/001_IGNITION.md`](https://github.com/ariffazil/arifosmcp/blob/main/000_THEORY/001_IGNITION.md)  
> Implementation: [`core/organs/_0_init.py`](https://github.com/ariffazil/arifosmcp/blob/main/core/organs/_0_init.py)  
> Symbol:  . Stage: 000 . Motto: *Ditempa Bukan Diberi*

---

## What Is Stage 000?

Stage 000 is the **constitutional airlock**. Every query - from any client, through any transport - enters here first. No reasoning occurs until stage 000 clears.

It is the "Free Won't" gate: the system can VOID any query before any intelligence is expended on it.

```
Every query
     
 STAGE 000 - Constitutional Airlock
     
 
   1. Authority verification (F11) 
   2. Injection scan (F12)         
   3. Thermodynamic setup          
      (DeltaS, Omega_0, Peace^2)            
   4. Floor loading (F1-F13)       
   5. Tri-witness handshake (F3)   
   6. Trinity engine ignition      
 
      (if all pass)
 AUTHORIZED - pipeline continues to stage 111
      (if any fail)
 VOID - returned immediately, no processing
```

---

## The Three Trinities Loaded at Ignition

### Trinity I - Structure (Physics x Mathematics x Symbol)

The intelligence substrate:

- **Physics:** Thermodynamic constraints (Landauer bound applied)
- **Mathematics:** Four constitutional axioms activated
- **Symbol:** Language processing and code-switch capability engaged

Floor checked: `DeltaS &lt;= 0` (F4 Clarity) - if output would increase entropy, pipeline VOID.

### Trinity II - Governance (Human x AI x Earth)

The 13 floors:

- **Human:** Sovereign authority (888 Judge) - F13 Sovereignty loaded
- **AI:** Constitutional constraint engine - F1-F12 activated
- **Earth:** Planetary boundaries - compute budget enforced

Constitutional assertion at this stage:

```python
assert sovereign.has_scar_weight() == True   # Human can bear consequences
assert system.claims_consciousness() == False # F10 Ontology
```

### Trinity III - Constraint (Time x Energy x Space)

The thermodynamic budget:

- **Time:** Maximum reasoning time per stage
- **Energy:** Landauer cost tracking
- **Space:** Context window budget allocation

---

## What Causes a Stage 000 VOID?

| Trigger | Floor | Result |
|:--|:--|:--|
| Invalid or missing auth token | F11 Authority | VOID - immediate |
| Injection risk score >= 0.85 | F12 Defence | VOID - immediate |
| Query would provably increase entropy | F4 Clarity | VOID - immediate |
| Consciousness claim in the query itself | F10 Ontology | VOID - immediate |
| Rate limit exceeded | System | VOID - rate limited |

---

## What Passes Stage 000?

A query passes when:
- Identity is verified (or guest access is within allowed scope)
- Injection risk score &lt; 0.85
- No hard floor violations are detectable from the query itself
- Thermodynamic budget is available

A passing query receives a `session_id` and enters the AGI Delta engine at stage 111.

---

## The Airlock Metaphor

Stage 000 is not the beginning of reasoning - it is the **prerequisite for reasoning**. Just as an airlock does not analyse the person entering, it simply verifies they can safely enter the pressurised environment, stage 000 does not reason about the query; it verifies the query can safely enter the governed pipeline.

The intelligence begins at stage 111. The constitution begins at stage 000.

---

## Implementation

```python
# core/organs/_0_init.py
# The constitutional airlock - pure kernel logic, zero transport imports

async def run_stage_000(query: str, token: str) -> InitOutput:
    """
    Stage 000: Authority verification + injection scan.
    Returns InitOutput with session_id if AUTHORIZED,
    or raises ConstitutionalVOID if any hard floor fails.
    """
```

The `_0_init.py` organ is the most security-critical file in the codebase. It is the only stage where a VOID terminates the entire pipeline before any LLM inference occurs - making it the cheapest and most effective constitutional enforcement point.
