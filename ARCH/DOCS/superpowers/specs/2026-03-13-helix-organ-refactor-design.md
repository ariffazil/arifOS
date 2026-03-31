# Double Helix Organ Refactor — Design Spec

**Date:** 2026-03-13
**Status:** APPROVED — Implementation in progress
**Motto:** DITEMPA BUKAN DIBERI — Forged, Not Given

---

## Goal

Refactor the arifOS MCP codebase from a monolithic `runtime/tools.py` into the AGI-level Double Helix architecture: 8 sovereign organ modules with constitutional floor enforcement, a shared metabolism layer, and a clean compatibility shim.

---

## Section 1 — Folder Structure

```
arifosmcp/
  helix/
    organs/
      inner/
        __init__.py          ← importlib bridge (re-exports all metabolism functions)
        000_anchor/          ← existing package (digit-prefix, importlib-loaded)
          __init__.py
          metabolism.py
        333_reason/          ← existing
          __init__.py
          metabolism.py
        555_reflect/         ← existing
          __init__.py
          metabolism.py
        666a_simulate/       ← existing
          __init__.py
          metabolism.py
        critique/            ← new (valid Python name, no digit prefix)
          __init__.py
          metabolism.py
        forge/               ← new
          __init__.py
          metabolism.py
        judge/               ← new
          __init__.py
          metabolism.py
        vault/               ← new
          __init__.py
          metabolism.py
  runtime/
    tools.py                 ← shim layer (imports from helix, exposes lowercase aliases)
    exceptions.py            ← ConstitutionalViolation, InfrastructureFault, EpistemicGap
    fault_codes.py           ← FaultClass, ConstitutionalFaultCode, MechanicalFaultCode
```

**Wall of Silence:** organs must not import each other. Each organ calls the kernel directly via `call_kernel(tool_name, session_id, payload)`.

---

## Section 2 — Per-Organ Anatomy

Each organ package exports one public function: `<stage>_metabolism(...)`.

```python
# organ/metabolism.py contract
async def <stage>_metabolism(<params>, ctx: CurrentContext, session_id: str) -> RuntimeEnvelope:
    # 1. Resolve session
    # 2. Assert floors (raise ConstitutionalViolation on hard breach)
    # 3. Build payload and call kernel via call_kernel(tool_name, session_id, payload)
    # 4. Emit helix_tracer span + constitutional event
    # 5. Return RuntimeEnvelope
```

```python
# organ/__init__.py contract
from .metabolism import <stage>_metabolism
__all__ = ["<stage>_metabolism"]
```

---

## Section 3 — Metabolism Layer

Shared helpers remain in `runtime/tools.py` until a dedicated `helix/metabolism/` layer is warranted. The organs use:

- `call_kernel(tool_name, session_id, payload)` — bridge to governance kernel
- `helix_tracer.start_organ_span(name, session_id)` — OTel span emission
- `ConstitutionalViolation(message, floor_code, extra)` — hard floor breach → VOID
- `InfrastructureFault(message, fault_code, extra)` — mechanical fault → 888_HOLD

---

## Section 4 — Migration Contract

### 4.1 Python module naming

Digit-prefix packages (`000_anchor`, `333_reason`, `555_reflect`, `666a_simulate`) cannot be imported via standard `from ... import` syntax. The `inner/__init__.py` uses `importlib.import_module()` to bridge them:

```python
import importlib as _il
def _from(pkg, name):
    return getattr(_il.import_module(f"arifosmcp.helix.organs.inner.{pkg}"), name)

init_anchor_metabolism = _from("000_anchor", "init_anchor_metabolism")
agi_reason_metabolism  = _from("333_reason", "agi_reason_metabolism")
# ...
```

New organs (critique, forge, judge, vault) use valid Python names and are imported directly.

### 4.2 `runtime/tools.py` shim

After organ extraction, `tools.py` UPPERCASE handlers delegate to organ metabolism functions:

```python
async def INIT_ANCHOR(...) -> RuntimeEnvelope:
    from arifosmcp.helix.organs.inner import init_anchor_metabolism
    return await init_anchor_metabolism(...)
```

`server.py` and `orchestrator.py` require **zero changes** — they continue importing lowercase aliases from `tools.py`.

### 4.3 Migration order

```
anchor → reason → reflect → simulate → critique → forge → judge → vault
```

Each organ is extracted and verified independently before the next begins.

---

## Constitutional Invariants

| Floor | Enforcement point | Verdict on breach |
|-------|-------------------|-------------------|
| F12 Injection | INIT·ANCHOR (PNS shield check) | VOID |
| F11 Auth | INIT·ANCHOR (session nonce) | VOID |
| F4 Clarity (ΔS) | AGI·REASON, ASI·SIMULATE | VOID |
| F5 Peace² | ASI·SIMULATE | VOID |
| F7 Humility | APEX·JUDGE | VOID |
| F1 Amanah | VAULT·SEAL (irreversibility gate) | VOID |
