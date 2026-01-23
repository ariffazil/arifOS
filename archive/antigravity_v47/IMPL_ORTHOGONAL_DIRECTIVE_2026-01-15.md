# IMPL PLAN: MCP AAA ORTHOGONAL (DUAL TRUTH)

**Authority:** Arif Fazil (Human Sovereign)
**Directive:** "Orthogonal is WAJIB (structure), Sequential is Emergent (flow). Only 000-999 exist."

## 1. The Dual Truth Architecture

We must code **Structure** and **Flow** separately.

### **Structure (The Kernels - WAJIB)**
Orthogonal logic units. PURE functions. No side effects.
- `arifos_core/agi/kernel.py` (Think: F2, F6)
- `arifos_core/asi/kernel.py` (Act: F3, F4, F5, F7)
- `arifos_core/apex/kernel.py` (Judge: F1, F8-F12)

### **Flow (The Emergence - RUNTIME)**
The sequence 000 → 999 is how we *orchestrate* the kernels.
- `000`: Reset
- `111-333`: AGI Kernel active (Sense, Reflect, Reason)
- `444-666`: ASI Kernel active (Evidence, Empathy, Align)
- `777`: Shared Forge
- `888-999`: APEX Kernel active (Judge, Seal)

---

## 2. Refined MCP Implementation Strategy

We will NOT create big `mcp_agi_think` blobs. That violates the "Emergent Flow" of 000-999.
Instead, we maintain the **000-999 Tool Interfaces**, but their **Internal Logic is Orthogonal**.

### **A. Code Structure**
```python
# arifos_core/mcp/tools/mcp_222_reflect.py (The Tool)

from arifos_core.agi.kernel import AGINeuralCore

async def mcp_222_reflect(ctx):
    # The Tool is just a wrapper for the Emergent Flow
    # The Logic comes from the Orthogonal Kernel
    return AGINeuralCore.reflect(ctx)
```

### **B. The Constitutional Particle Class**
We still implement `ConstitutionalParticle` as the base for the **Kernels**, not the tools.
- `AGINeuralCore` is a `ConstitutionalParticle`
- `ASIActionCore` is a `ConstitutionalParticle`
- `APEXJudicialCore` is a `ConstitutionalParticle`

### **C. 444 Web Search (Evidence)**
Lives in `mcp_444_evidence`.
- Powered by `ASIActionCore` (Safety check) AND `AGINeuralCore` (Relevance check).
- **Orthogonal Intersection:** 444 is where AGI & ASI meet.

---

## 3. Plan of Action (Revised)

1.  **Create Kernels:**
    -   `arifos_core/agi/kernel.py`
    -   `arifos_core/asi/kernel.py`
    -   `arifos_core/apex/kernel.py`
    -   *Move logic from old tools into these kernels.*

2.  **Refactor Tools (000-999):**
    -   Keep the 10 tools (000..999) as the **Interface**.
    -   Gut their internals. Replace with calls to Kernels.
    -   This satisfies "Sequential is Emergence" while keeping "Orthogonal is Logic".

3.  **Clean up Numbering:**
    -   Ensure NO file/tool uses non-canonical numbers (e.g., 301, 808).
    -   Strict validation in `server.py`.

**Status:** Ready to refactor.
