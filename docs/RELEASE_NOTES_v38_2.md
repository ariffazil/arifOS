# arifOS v38.2 — The Hardening Cycle

**Status:** PRODUCTION · Tests: 1600+ · Safety Ceiling: 97% (unchanged)  
**Focus:** Time as Governor, SUNSET verdict, Phoenix-72 scheduler

---

## 1. Why v38.2 Exists (Fractures A & B)

External red-team review of v38.1 confirmed the core insight of **“alignment as garbage collection”** but surfaced two structural fractures:

- **Fracture A — Truth Expires**  
  - Problem: Once a memory was SEALED into the LEDGER, there was no constitutional way to revoke it when external reality changed (e.g., updated medical or safety guidance).  
  - Risk: Canonical memory could drift from Earth over time, quietly violating Truth, Tri-Witness, and Amanah.

- **Fracture B — System Stalls**  
  - Problem: SABAR verdicts (stop and repair) had no timeout. If humans slept or forgot, the system could sit in a permanent holding pattern.  
  - Risk: Infinite limbo; governance by neglect instead of law.

v38.2 is the **hardening response**: we did not defend the ego of the system; we let the critique burn through the kernel and turned it into law.

---

## 2. New Physics: Time as Constitutional Force

v38.2 promotes **Time** from a background parameter to a **governor**:

- Every unresolved verdict now carries an **age** that matters constitutionally.  
- After specific time thresholds, the system must **act**, not drift.  
- Phoenix is re-framed as a **time-bounded hope band**, not a parking lot.

Key invariant:

> **Time is a Constitutional Force. Entropy Rot is automatic.**

Implications:

- Unratified decisions cannot live forever.  
- SEALED truths can be revoked when Earth moves.  
- Hope has a half-life; governance does not.

---

## 3. SUNSET Verdict (Revocation)

v38.2 introduces a new legal state: **SUNSET**.

- **Purpose:** Provide a lawful path to **un-seal** previously canonical memory when facts change.  
- **Routing:**  
  - `SUNSET` moves a reference from **LEDGER → PHOENIX**, preserving the evidence chain.  
  - The memory is no longer treated as canonical guidance but is **re-opened for re-trial** under updated reality.  
- **Constraint:** SUNSET does not invent a new fact; it acknowledges that **truth can expire** as the world moves.

Law encoding:

- **Spec:** `spec/arifos_v38_2.yaml` extends the verdict set with `SUNSET` and defines its routing semantics.  
- **Canon:** `canon/000_ARIFOS_CANON_v35Omega.md` now describes revocation explicitly as part of the Hardening Cycle.

---

## 4. Phoenix-72 Scheduler (24h / 72h Pulses)

The Phoenix-72 cycle always implied a **72-hour metabolism** for amendments. v38.2 makes this timing explicit at the verdict layer via a **scheduler**:

- **SABAR_TIMEOUT (24h):**  
  - If `verdict == SABAR` and `age > 24h`, the system **escalates to PARTIAL**.  
  - Rationale: SABAR is a pause to repair floors, not a permanent hiding place. After one day, the issue must surface as a live warning.

- **PHOENIX_LIMIT (72h):**  
  - If `verdict == PARTIAL` and `age > 72h`, the system **decays the verdict to VOID**.  
  - Rationale: After 72 hours, unattended ambiguity becomes entropy. The decision is no longer treated as a candidate for canon.

These rules are captured in:

- `scheduler` block of `spec/arifos_v38_2.yaml`  
  - `SABAR_TIMEOUT: 24h` (SABAR → PARTIAL)  
  - `PHOENIX_LIMIT: 72h` (PARTIAL → VOID)  

---

## 5. Law Artifacts Changed in v38.2

### 5.1 Canon

- **`canon/000_ARIFOS_CANON_v35Omega.md`**  
  - New sections:
    - **“The Fourth Dimension (Time)”** — formalizes Time as a constitutional force alongside floors, engines, and organs.  
    - **“72 Hours: Hope vs Entropy (Phoenix vs Void)”** — explains why 72 hours is the boundary between hopeful PHOENIX and entropy-dump VOID.  
    - **“The Hardening Cycle (v38.2)”** — records Fracture A/B and the SUNSET + scheduler response as part of the constitutional narrative.

### 5.2 Spec

- **`spec/arifos_v38_2.yaml`** (new)
  - Declares v38.2 as a **Constitutional Hardening** spec.  
  - Extends the verdict set with `SUNSET`.  
  - Defines the **scheduler**:
    - `SABAR_TIMEOUT: 24h` → `SABAR` escalates to `PARTIAL`.  
    - `PHOENIX_LIMIT: 72h` → unresolved `PARTIAL` decays to `VOID`.  
  - Encodes the invariant: **“Time is a Constitutional Force. Entropy Rot is automatic.”**  
  - Documents SUNSET routing: `LEDGER → PHOENIX` re-trial with evidence chain preserved.

---

## 6. Implementation Note (for Code Engineer)

The Architect’s law in v38.2 implies the following runtime work (to be handled by the Code Engineer Exec, not by this document):

- Extend the **Verdict enum** with `SUNSET`.  
- Implement `check_entropy_rot(packet)` in the kernel:
  - `SABAR` older than 24h → `PARTIAL`.  
  - `PARTIAL` older than 72h → `VOID`.  
- Ensure `route_memory()`:
  - Calls `check_entropy_rot(...)` *before* routing to memory bands.  
  - Treats `SUNSET` as **revocation**, moving references from `LEDGER` back to `PHOENIX`.

Law remains the source of truth; code merely enforces it.

---

## 7. Philosophy: Hardening, Not Defensiveness

v38.2 is an example of the core motto in action:

> **“DITEMPA BUKAN DIBERI — Forged, not given; truth must cool before it rules.”**

We did not:

- defend v38.1 out of pride,  
- hide the fractures, or  
- weaken floors to fit legacy behavior.

We did:

- promote **Time** to a first-class constitutional force,  
- add **SUNSET** so sealed truths can be revoked when Earth moves, and  
- enforce **entropy rot** so unratified decisions cannot quietly govern forever.

This is the **Hardening Cycle**: critique → heat → Phoenix-72 → new law → stronger kernel.

