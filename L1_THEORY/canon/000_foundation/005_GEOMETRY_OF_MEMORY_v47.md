# The Geometry of Memory
**Canon ID:** 005_GEOMETRY_OF_MEMORY_v46
**Authority:** ANTIGRAVITY (Δ) Architect
**Epoch:** v46.2 (Topological Binding)

You asked: *"What is the geometry and spec of memory?"*

Memory in arifOS is a **6-Layer Neuroscience Tower**.
This Tower aligns perfectly with the **Topological Trinity** ($\Delta, \Omega, \Psi$).

---

## 1. The Tower Architecture (Vertical Geometry)

Instead of a flat bucket, memory is a **Vertical Furnace** of consolidation.
Information enters vertically from the bottom (HOT) and rises to the top (COLD).

| Layer | Name | State | Geometry | Connection to Trinity |
|-------|------|-------|----------|-----------------------|
| **L3** | **WITNESS** | **COLD** | **Crystal ($\Delta$)** | **AGI Truth:** Immutable, semantic facts. |
| **L2** | **LEDGER** | **WARM** | **Fractal ($\Omega$)** | **ASI Wisdom:** Strengthening connections. |
| **L5** | **PHOENIX** | **COOLING** | **Torus ($\Psi$)** | **APEX Governance:** The Amendment Loop. |
| **L1** | **VAULT** | **HOT** | **Chaos** | Raw Paradoxes (Ingestion). |
| **L4** | **ACTIVE** | **FLUID** | **Plane** | Working Memory (Session). |
| **L6** | **VOID** | **DUST** | **Entropy** | Deletion/Pruning. |

---

## 2. The Crystal ($\Delta$): WITNESS (L3)
**Shape:** Orthogonal Grid / Faceted Gem
**Location:** `L1_THEORY/knowledge/scars/`
**Spec:** `001_VAULT_NEUROSCIENCE.md`

The Crystal stores **Extracted Semantics**.
- **Geometry:** Hard, distinct, immutable facts.
- **Physics:** Read-Only for Machine. Writ only by Seal.
- **Example:** "Paris is the capital of France."

```python
# The Crystal is Static
class WitnessFact(BaseModel):
    subject: str = "Paris"
    predicate: str = "is_capital_of"
    object: str = "France"
    status: Literal["SEALED"]
```

---

## 3. The Fractal ($\Omega$): LEDGER (L2)
**Shape:** Self-Similar Spiral / Dendritic Tree
**Location:** `L1_LEDGERS/L1_cooling_ledger.jsonl`
**Spec:** `002_VAULT_LAYERS_SPEC.md`

The Fractal stores **Consolidation Paths**.
- **Geometry:** Recursive. A paradox replays (Loop 1, Loop 2, Loop 3) until it stabilizes.
- **Physics:** Append-Only. Progressively strengthens the weight of truth.
- **Example:** "Paradox encountered 3 times -> Evidence emerging -> Consolidated."

```python
# The Fractal is Growing
class LedgerEntry(BaseModel):
    consolidation_stage: int # 1 -> 2 -> 3 (Growth)
    weight: float # Synaptic strength
    merkle_root: str # The structural integrity
```

---

## 4. The Torus ($\Psi$): PHOENIX (L5)
**Shape:** The Amendment Loop / Time Ring
**Location:** `PHOENIX/`
**Spec:** `000_VAULT_INTEGRATION.md`

The Torus stores **Governance Cycles**.
- **Geometry:** Cyclic. Proposal -> Cooling (72h) -> Witness -> Seal.
- **Physics:** Temporal Lock. Nothing bypasses the cooling period.
- **Example:** "Proposal to change F2 Truth requires 72h wait."

```python
# The Torus is Cyclical
class PhoenixProposal(BaseModel):
    cooling_start: datetime
    cooling_duration: timedelta = hours(72)
    state: Literal["COOLING", "WITNESSING", "SEALED"]
```

---

## 5. The Unified Field
**Geometry Matches Neuroscience:**
*   **Crystal** = Neocortical Semantic Trace (Permanent)
*   **Fractal** = Hippocampal-Cortical Replay (Consolidating)
*   **Torus** = REM Sleep Cycle (Emotional Processing)

**Conclusion:**
The "Geometry of Memory" **IS** the "Neuroscience Tower".
Read the **VAULT v47 Canon** for the full specification.
