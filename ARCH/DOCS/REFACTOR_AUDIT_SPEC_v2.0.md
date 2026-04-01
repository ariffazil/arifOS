# arifOS MCP Audit & Architecture Specification v2.0

> **DITEMPA BUKAN DIBERI** — *Forged, Not Given*

**Document Version**: 2026.04.01  
**Audit Scope**: arifOS MCP Repository (https://github.com/ariffazil/arifOS)  
**Auditor**: AGI Builder Agent  
**Classification**: ENGINEERING SPECIFICATION

---

## Executive Summary

This document provides a comprehensive audit of the arifOS MCP codebase, identifying architectural issues, orphaned code, schema conflicts, and proposes a clarified architecture with full engineering specifications for forging the next evolution of the kernel.

### Critical Findings Summary

| Category | Count | Severity |
|----------|-------|----------|
| Schema Conflicts | 7 | HIGH |
| Orphaned Code | 12 | MEDIUM |
| Duplicate Implementations | 5 | MEDIUM |
| FastMCP Version Conflicts | 3 | HIGH |
| Circular Dependencies | 4 | MEDIUM |
| Missing Error Handling | 8 | LOW |

---

## Part 1: Current Architecture Analysis

### 1.1 Directory Structure Overview

```
arifOS/
├── server.py                    # Root entry point (dual-mode detection)
├── config/environments.py       # Environment configuration (VPS/Horizon/Local)
│
├── arifos_mcp/                  # Main MCP implementation (symlink: arifosmcp)
│   ├── server.py               # Gateway with Horizon/VPS auto-detection
│   ├── server_horizon.py       # Horizon-specific implementation
│   ├── runtime/                # Core runtime
│   │   ├── server.py           # FastMCP server initialization
│   │   ├── tools.py            # Tool registration & dispatch
│   │   ├── tools_internal.py   # Internal tool implementations
│   │   ├── tools_hardened_dispatch.py  # Hardened dispatch map
│   │   ├── bridge.py           # Core communication bridge
│   │   ├── models.py           # Pydantic models (RuntimeEnvelope, etc.)
│   │   ├── schemas.py          # Input/output schemas
│   │   ├── tool_specs.py       # Tool specifications
│   │   ├── fastmcp_version.py  # FastMCP 2.x/3.x compatibility
│   │   ├── megaTools/          # 12 mega-tool implementations
│   │   └── ...
│   └── tools/                  # Additional tool modules
│
├── core/                        # Constitutional kernel
│   ├── floors.py               # F1-F13 floor implementations
│   ├── shared/types.py         # Canonical types (Verdict, AuthorityLevel, etc.)
│   ├── organs/                 # AGI, ASI, APEX, INIT, VAULT organs
│   └── ...
│
├── horizon/                     # Horizon deployment (LEGACY - CONFLICT!)
│   └── server.py               # DUPLICATE of arifos_mcp/server_horizon.py
│
└── archive/                     # Deprecated code
    └── ...
```

### 1.2 Current Request Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CURRENT REQUEST FLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CLIENT REQUEST                                                             │
│       │                                                                     │
│       ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  server.py (Root)                                                   │   │
│  │  ├── Detects environment (Horizon vs VPS)                          │   │
│  │  └── Routes to appropriate handler                                  │   │
│  └──────────────────────┬──────────────────────────────────────────────┘   │
│                         │                                                   │
│         ┌───────────────┴───────────────┐                                   │
│         │                               │                                   │
│         ▼                               ▼                                   │
│  ┌─────────────┐              ┌─────────────────┐                          │
│  │  Horizon    │              │  VPS Sovereign  │                          │
│  │  (2.x)      │              │  (3.x)          │                          │
│  └──────┬──────┘              └────────┬────────┘                          │
│         │                               │                                   │
│         ▼                               ▼                                   │
│  ┌─────────────┐              ┌─────────────────┐                          │
│  │  server_    │              │  runtime/       │                          │
│  │  horizon.py │              │  server.py      │                          │
│  └─────────────┘              └────────┬────────┘                          │
│                                        │                                    │
│                                        ▼                                    │
│                               ┌─────────────────┐                          │
│                               │  tools.py       │                          │
│                               │  (registers     │                          │
│                               │   mega-tools)   │                          │
│                               └────────┬────────┘                          │
│                                        │                                    │
│                                        ▼                                    │
│                               ┌─────────────────┐                          │
│                               │  megaTools/     │                          │
│                               │  (12 tools)     │                          │
│                               └────────┬────────┘                          │
│                                        │                                    │
│                                        ▼                                    │
│                               ┌─────────────────┐                          │
│                               │  tools_internal │                          │
│                               │  OR             │                          │
│                               │  hardened_      │                          │
│                               │  dispatch.py    │                          │
│                               └────────┬────────┘                          │
│                                        │                                    │
│                                        ▼                                    │
│                               ┌─────────────────┐                          │
│                               │  bridge.py      │                          │
│                               │  (call_kernel)  │                          │
│                               └────────┬────────┘                          │
│                                        │                                    │
│                                        ▼                                    │
│                               ┌─────────────────┐                          │
│                               │  core/organs/   │                          │
│                               │  (AGI, ASI,     │                          │
│                               │   APEX, etc.)   │                          │
│                               └─────────────────┘                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 2: Critical Issues Identified

### 2.1 SCHEMA CONFLICTS (HIGH SEVERITY)

#### Issue 2.1.1: Dual Verdict Enum Definitions

**Location**: `core/floors.py` vs `core/shared/types.py`

**Problem**: Two different `Verdict` enums exist with different values:

```python
# core/floors.py (lines 26-31)
class Verdict(Enum):
    SEAL = "SEAL"      # Approved - proceed
    VOID = "VOID"      # Rejected - no action
    HOLD = "HOLD"      # Pending - need clarification
    SABAR = "SABAR"    # Wait - rate limited

# core/shared/types.py (lines 205-232)
class Verdict(str, Enum):
    SEAL = "SEAL"
    PROVISIONAL = "PROVISIONAL"
    PARTIAL = "PARTIAL"
    SABAR = "SABAR"
    HOLD = "HOLD"
    HOLD_888 = "HOLD_888"
    VOID = "VOID"
    PAUSED = "PAUSED"
    ALIVE = "ALIVE"
    DEGRADED = "DEGRADED"
```

**Impact**: 
- Runtime type confusion when comparing verdicts
- Serialization/deserialization errors
- Inconsistent verdict handling across modules

**Fix**: Consolidate to single source of truth in `core/shared/types.py`

---

#### Issue 2.1.2: Inconsistent Input Schema for `init_anchor`

**Location**: Multiple files define different signatures

| File | Signature |
|------|-----------|
| `horizon/server.py` | `init_anchor(actor_id: str, declared_name: str = None)` |
| `arifos_mcp/server_horizon.py` | `init_anchor(actor_id: str, declared_name: str = None)` |
| `arifos_mcp/runtime/megaTools/tool_01_init_anchor.py` | 15+ parameters including `mode`, `payload`, `query`, `session_id`, `actor_id`, `declared_name`, `intent`, `human_approval`, etc. |
| `arifos_mcp/runtime/schemas.py` | `InitAnchorInput` with `actor_id`, `declared_name`, `intent`, `session_id`, `human_approval`, `reason` |

**Impact**:
- Clients can't reliably call `init_anchor` with consistent parameters
- Horizon proxy fails when VPS expects additional parameters
- Schema validation errors

**Fix**: Define canonical ABI v1.0 schema and implement adapters

---

#### Issue 2.1.3: RuntimeEnvelope vs Dict Return Type Conflict

**Location**: `arifos_mcp/runtime/megaTools/` vs `arifos_mcp/runtime/tools_internal.py`

**Problem**: Tools return different types:

```python
# megaTools return RuntimeEnvelope
return RuntimeEnvelope(
    tool=res.get("tool", "init_anchor"),
    stage=res.get("organ_stage") or res.get("stage") or "000_INIT",
    status=RuntimeStatus.SUCCESS if ok else RuntimeStatus.ERROR,
    verdict=effective_verdict,
    ...
)

# But horizon/server.py returns dict
return {
    "status": "initialized",
    "actor_id": actor_id,
    ...
}
```

**Impact**: Type errors, inconsistent client handling

**Fix**: Standardize on RuntimeEnvelope with `.dict()` conversion at boundary

---

#### Issue 2.1.4: Floor Name Inconsistencies

**Location**: Multiple files

| Location | F7 Name | F9 Name | F11 Name |
|----------|---------|---------|----------|
| `core/floors.py` | `F7_HUMIDITY` | `F9_ANTI_HANTU` | `F11_COMMAND_AUTH` |
| `core/shared/types.py` | `f7_humility` | `f9_anti_hantu` | `f11_command_auth` |
| `README.md` | `F7: HUMILITY` | `F9: ETHICS` | `F11: AUDITABILITY` |
| `ARCH/CONSTITUTION/FLOORS/` | `F07_HUMILITY.md` | `F09_ANTIHANTU.md` | `F11_AUTH.md` |

**Impact**: Confusion about floor semantics, search/replace errors

**Fix**: Canonical naming convention document and refactoring

---

#### Issue 2.1.5: AuthorityLevel Enum Inconsistency

**Location**: `core/shared/types.py` vs `arifos_mcp/runtime/models.py`

**Problem**: `AuthorityLevel` defined in types.py but some code expects different values:

```python
# core/shared/types.py
class AuthorityLevel(str, Enum):
    HUMAN = "human"
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
    ANONYMOUS = "anonymous"
    OPERATOR = "operator"
    SOVEREIGN = "sovereign"
    DECLARED = "declared"
    CLAIMED = "claimed"
    VERIFIED = "verified"
    APEX = "apex"
    NONE = "none"

# But bridge.py uses:
"observe", "advise", "execute", "execute_limited", "verified_execute"
```

**Impact**: Identity resolution failures

**Fix**: Single AuthorityLevel enum with all valid values

---

#### Issue 2.1.6: W³ vs Tri-Witness Formula Inconsistency

**Location**: `core/floors.py` vs `core/shared/types.py`

**Problem**: Different formulas for the same concept:

```python
# core/floors.py (line 153)
tri_witness = self._calculate_tri_witness(
    human_intent, tool_name, environment_safety
)

# core/shared/types.py (lines 334-337)
def tri_witness_consensus(self) -> float:
    # Geometric mean of H, A, E witnesses (v60 definition)
    # H = Sovereign, A = Truth, E = Earth
    return (self.f13_sovereign * self.f2_truth * self.f3_earth_witness) ** (1 / 3)
```

**Impact**: Different W³ scores in different parts of system

**Fix**: Single W³ calculation in constitutional kernel

---

#### Issue 2.1.7: Session ID Resolution Inconsistency

**Location**: Multiple files

**Problem**: Session ID normalization happens in multiple places with different logic:

```python
# arifos_mcp/runtime/sessions.py
def _normalize_session_id(session_id: str | None) -> str:
    if not session_id:
        return "global"
    normalized = str(session_id).strip().lower()
    normalized = normalized.replace(" ", "-").replace("_", "-")
    return normalized

# But tool_01_init_anchor.py has different logic
# And bridge.py has yet another variant
```

**Impact**: Session continuity breaks

**Fix**: Single normalization function in sessions module

---

### 2.2 ORPHANED CODE (MEDIUM SEVERITY)

#### Issue 2.2.1: `init_000` References in tools.py

**Location**: `arifos_mcp/runtime/tools.py` (lines 107-118)

```python
try:
    # init_000 was purged in sovereign unification
    init_000_get_deployment = None
    init_000_get_provider_soul = None
    ...
except (ImportError, ModuleNotFoundError):
    # init_000 not available in this environment
    init_000_get_deployment = None
    ...
```

**Fix**: Remove dead code

---

#### Issue 2.2.2: Legacy Tool Map in bridge.py

**Location**: `arifos_mcp/runtime/bridge.py` (lines 72-98)

```python
TOOL_MAP = {
    "init_anchor": "anchor_session",
    "arifOS_kernel": "metabolic_loop",
    "arifOS.kernel": "metabolic_loop",
    "metabolic_loop_router": "metabolic_loop",
    "agi_reason": "reason_mind",
    ...  # Many mappings to non-existent functions
}
```

Most of these mapped functions don't exist in the codebase.

**Fix**: Remove or update TOOL_MAP

---

#### Issue 2.2.3: Duplicate Horizon Server Implementations

**Location**: 
- `horizon/server.py` (238 lines)
- `arifos_mcp/server_horizon.py` (233 lines)
- `infrastructure/horizon/server.py` (likely another copy)

**Problem**: Three different Horizon server implementations with different tool sets!

**Fix**: Consolidate to single Horizon implementation

---

#### Issue 2.2.4: Unused FastMCP Compat Code

**Location**: `arifos_mcp/runtime/fastmcp_compat.py`

This file appears to be largely superseded by `fastmcp_version.py`.

**Fix**: Audit and merge or remove

---

#### Issue 2.2.5: Orphaned Archive Code

**Location**: `archive/deprecated/geox_local_diverged/`

Entire GEOX implementation that's been superseded.

**Fix**: Move to separate repository or remove

---

#### Issue 2.2.6: Unused Tool Implementations

**Location**: `arifos_mcp/runtime/tools_hardened_v2.py` (42K!)

This file is massive but may not be actively used.

**Fix**: Audit usage and potentially remove

---

#### Issue 2.2.7: Dead Code in tools_internal.py

**Location**: `arifos_mcp/runtime/tools_internal.py`

Lines 185+ contain `_wrap_call` and other functions that may not be used.

**Fix**: Audit and remove dead code

---

#### Issue 2.2.8: Unused Imports

**Location**: Multiple files

Many files import modules that are never used:
- `arifos_mcp/runtime/tools.py`: `CurrentContext` imported but not used
- `arifos_mcp/runtime/tools_internal.py`: Multiple unused imports

**Fix**: Clean up imports

---

#### Issue 2.2.9: Orphaned Test Files

**Location**: `tests/` directory

Many test files reference non-existent modules or outdated APIs.

**Fix**: Update tests or remove

---

#### Issue 2.2.10: Unused Schema Definitions

**Location**: `arifos_mcp/runtime/schemas.py`

Several schemas defined but never used:
- `IntentSpec` (partially used)
- `MegaToolInput` (may be unused)
- `ErrorResponse` (may be unused)

**Fix**: Audit and remove or implement

---

#### Issue 2.2.11: Orphaned Config Files

**Location**: Root directory

Files like `fastmcp.json`, `mcp.json`, `arifos.yml` may be outdated.

**Fix**: Audit and update or remove

---

#### Issue 2.2.12: Duplicate Symlinks

**Location**: Root directory

`arifosmcp -> arifos_mcp` symlink exists but may cause import issues.

**Fix**: Standardize imports to use `arifos_mcp`

---

### 2.3 DUPLICATE IMPLEMENTATIONS (MEDIUM SEVERITY)

#### Issue 2.3.1: Three Horizon Server Implementations

As noted above, three different Horizon servers exist.

---

#### Issue 2.3.2: Multiple Tool Dispatch Mechanisms

**Location**: 
- `arifos_mcp/runtime/tools.py` (register_tools)
- `arifos_mcp/runtime/tools_hardened_dispatch.py` (HARDENED_DISPATCH_MAP)
- `arifos_mcp/runtime/tools_internal.py` (internal dispatch)

**Problem**: Three different ways tools are dispatched:

```python
# tools.py: Direct mega-tool import
from arifos_mcp.runtime.megaTools import init_anchor

# tools_hardened_dispatch.py: Dispatch map
HARDENED_DISPATCH_MAP = {
    "init_anchor": init_anchor_hardened_dispatch,
    ...
}

# tools_internal.py: Internal implementations
async def init_anchor_impl(...)
```

**Fix**: Consolidate to single dispatch mechanism

---

#### Issue 2.3.3: Multiple Session Management Systems

**Location**:
- `arifos_mcp/runtime/sessions.py`
- `core/state/session_manager.py`

**Problem**: Two session management systems with overlapping functionality.

**Fix**: Consolidate to core session manager

---

#### Issue 2.3.4: Multiple Vault Implementations

**Location**:
- `arifos_mcp/runtime/vault_redis.py`
- `core/organs/_4_vault/`
- `arifos_mcp/runtime/bridge.py` (file-based fallback)

**Problem**: Three vault backends with different APIs.

**Fix**: Single vault interface with pluggable backends

---

#### Issue 2.3.5: Duplicate Floor Evaluation

**Location**:
- `core/floors.py` (ConstitutionalFloors class)
- `core/judgment.py` (Apex judgment)
- Individual organ implementations

**Problem**: Floor evaluation happens in multiple places.

**Fix**: Single floor evaluation in constitutional kernel

---

### 2.4 FASTMCP VERSION CONFLICTS (HIGH SEVERITY)

#### Issue 2.4.1: Incompatible Import Patterns

**Location**: Multiple files

```python
# FastMCP 3.x only (FAILS on 2.x)
from fastmcp.dependencies import CurrentContext
from fastmcp.server.context import Context

# FastMCP 2.x compatible
from fastmcp import FastMCP
```

**Problem**: Files import `CurrentContext` unconditionally, causing ImportError on Horizon.

**Fix**: Use compatibility layer in `fastmcp_version.py`

---

#### Issue 2.4.2: Context Parameter Handling

**Location**: Tool implementations

**Problem**: Tools use `ctx: Context` parameter which doesn't exist in FastMCP 2.x

**Fix**: Make context parameter optional with fallback

---

#### Issue 2.4.3: HTTP App Creation

**Location**: `arifos_mcp/runtime/server.py`

**Problem**: Different HTTP app creation for 2.x vs 3.x

**Fix**: Already partially handled but needs consolidation

---

### 2.5 CIRCULAR DEPENDENCIES (MEDIUM SEVERITY)

#### Issue 2.5.1: tools.py → megaTools → tools_internal → bridge → tools

**Location**: Multiple files

**Problem**: Circular import chain exists.

**Fix**: Refactor to break cycles

---

#### Issue 2.5.2: models.py → core.shared.types → models

**Location**: `arifos_mcp/runtime/models.py`

**Problem**: Models import from core, but core may import from models.

**Fix**: Ensure unidirectional dependency

---

#### Issue 2.5.3: sessions.py → models.py → sessions.py

**Location**: `arifos_mcp/runtime/sessions.py`

**Problem**: Sessions imports models, models may need sessions.

**Fix**: Refactor

---

#### Issue 2.5.4: bridge.py → core.organs → bridge.py

**Location**: `arifos_mcp/runtime/bridge.py`

**Problem**: Bridge calls organs, organs may call bridge.

**Fix**: Define clear interface boundaries

---

### 2.6 MISSING ERROR HANDLING (LOW SEVERITY)

#### Issue 2.6.1: Bare Except Clauses

**Location**: Multiple files

```python
try:
    something()
except:  # Bare except - catches KeyboardInterrupt, SystemExit
    pass
```

**Fix**: Use specific exception types

---

#### Issue 2.6.2: Missing Validation in Tool Inputs

**Location**: Tool implementations

**Problem**: Many tools don't validate inputs before processing.

**Fix**: Add Pydantic validation

---

#### Issue 2.6.3: No Timeout Handling

**Location**: HTTP calls

**Problem**: HTTP calls to external services may hang.

**Fix**: Add timeout parameters

---

#### Issue 2.6.4: Missing Fallback for Redis

**Location**: `arifos_mcp/runtime/vault_redis.py`

**Problem**: If Redis fails, no graceful fallback.

**Fix**: Implement circuit breaker pattern

---

#### Issue 2.6.5: No Retry Logic

**Location**: External API calls

**Problem**: Transient failures not retried.

**Fix**: Add exponential backoff retry

---

#### Issue 2.6.6: Missing Logging Context

**Location**: Multiple files

**Problem**: Logs don't include session_id, tool_name for correlation.

**Fix**: Use structured logging with context

---

#### Issue 2.6.7: No Rate Limiting

**Location**: Tool implementations

**Problem**: No protection against abuse.

**Fix**: Implement rate limiting

---

#### Issue 2.6.8: Missing Health Checks

**Location**: External dependencies

**Problem**: No health checks for Redis, PostgreSQL, etc.

**Fix**: Add health check endpoints

---

## Part 3: Proposed Architecture v2.0

### 3.1 Architectural Principles

1. **Single Source of Truth**: Each concept has exactly one canonical definition
2. **Unidirectional Dependencies**: Lower layers never depend on upper layers
3. **Explicit Interfaces**: All cross-module communication through defined interfaces
4. **Version Compatibility**: FastMCP 2.x and 3.x support through adapter pattern
5. **Fail Fast, Fail Safe**: Errors detected early, system degrades gracefully

### 3.2 Proposed Directory Structure

```
arifOS/
├── server.py                           # Entry point (unchanged)
├── config/
│   ├── environments.py                 # Environment config (consolidated)
│   └── settings.py                     # Pydantic settings (NEW)
│
├── arifos_mcp/                         # MCP implementation
│   ├── __init__.py
│   ├── server.py                       # Gateway (simplified)
│   ├── server_horizon.py               # Horizon adapter (consolidated)
│   │
│   ├── abi/                            # Application Binary Interface (NEW)
│   │   ├── __init__.py
│   │   ├── v1_0.py                     # Canonical ABI v1.0 definitions
│   │   └── schemas.py                  # All input/output schemas
│   │
│   ├── runtime/                        # Runtime layer
│   │   ├── __init__.py
│   │   ├── server.py                   # FastMCP server init
│   │   ├── dispatcher.py               # SINGLE dispatch mechanism (NEW)
│   │   ├── middleware.py               # Request/response middleware
│   │   └── compat.py                   # FastMCP 2.x/3.x compatibility
│   │
│   ├── tools/                          # Tool implementations
│   │   ├── __init__.py
│   │   ├── registry.py                 # Tool registry (NEW)
│   │   ├── base.py                     # Base tool class (NEW)
│   │   ├── governance/                 # Governance tools
│   │   │   ├── init_anchor.py          # Canonical init_anchor
│   │   │   ├── kernel.py               # arifOS_kernel
│   │   │   ├── apex.py                 # apex_judge
│   │   │   └── vault.py                # vault_ledger
│   │   ├── intelligence/               # Intelligence tools
│   │   │   ├── agi.py                  # agi_mind
│   │   │   ├── asi.py                  # asi_heart
│   │   │   └── memory.py               # engineering_memory
│   │   ├── reality/                    # Reality tools
│   │   │   ├── physics.py              # physics_reality
│   │   │   └── math.py                 # math_estimator
│   │   └── execution/                  # Execution tools
│   │       └── code.py                 # code_engine
│   │
│   └── models/                         # Data models (consolidated)
│       ├── __init__.py
│       ├── envelope.py                 # RuntimeEnvelope
│       ├── verdict.py                  # Canonical Verdict enum
│       ├── identity.py                 # Identity models
│       └── telemetry.py                # Telemetry models
│
├── core/                               # Constitutional kernel (unchanged structure)
│   ├── shared/
│   │   ├── types.py                    # SINGLE type definitions
│   │   └── floors.py                   # Floor definitions (moved from core/floors.py)
│   ├── organs/                         # Organ implementations
│   ├── floors.py                       # REMOVED (merged to shared/floors.py)
│   └── ...
│
├── infrastructure/                     # Infrastructure layer (NEW)
│   ├── vault/
│   │   ├── __init__.py
│   │   ├── interface.py                # Vault interface (NEW)
│   │   ├── redis.py                    # Redis backend
│   │   ├── postgres.py                 # PostgreSQL backend
│   │   └── file.py                     # File backend
│   ├── session/
│   │   ├── __init__.py
│   │   ├── manager.py                  # SINGLE session manager
│   │   └── store.py                    # Session storage
│   └── memory/
│       ├── __init__.py
│       └── vector.py                   # Vector memory interface
│
└── tests/                              # Tests (consolidated)
    ├── unit/
    ├── integration/
    └── e2e/
```

### 3.3 Proposed Request Flow v2.0

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PROPOSED REQUEST FLOW v2.0                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CLIENT REQUEST                                                             │
│       │                                                                     │
│       ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  server.py (Entry Point)                                            │   │
│  │  └── Detect environment → route to appropriate server               │   │
│  └──────────────────────┬──────────────────────────────────────────────┘   │
│                         │                                                   │
│         ┌───────────────┴───────────────┐                                   │
│         │                               │                                   │
│         ▼                               ▼                                   │
│  ┌─────────────┐              ┌─────────────────┐                          │
│  │  Horizon    │              │  VPS Sovereign  │                          │
│  │  Adapter    │              │  Runtime        │                          │
│  │  (2.x)      │              │  (3.x)          │                          │
│  └──────┬──────┘              └────────┬────────┘                          │
│         │                               │                                   │
│         │    ┌──────────────────────────┘                                   │
│         │    │                                                               │
│         │    ▼                                                               │
│         │  ┌─────────────────────────────────────────┐                      │
│         │  │  ABI Layer (Canonical Schemas)          │                      │
│         │  │  ├── Validates input against schema     │                      │
│         │  │  └── Transforms to canonical format     │                      │
│         │  └─────────────────────┬───────────────────┘                      │
│         │                        │                                          │
│         └────────────────────────┤                                          │
│                                  ▼                                          │
│                    ┌─────────────────────────┐                             │
│                    │  Tool Dispatcher        │                             │
│                    │  (SINGLE dispatch point)│                             │
│                    └────────────┬────────────┘                             │
│                                 │                                          │
│                    ┌────────────┴────────────┐                            │
│                    │                           │                            │
│                    ▼                           ▼                            │
│         ┌─────────────────┐        ┌─────────────────┐                     │
│         │  Tool Registry  │        │  Floor Engine   │                     │
│         │  (lookup tool)  │        │  (F1-F13 check) │                     │
│         └────────┬────────┘        └────────┬────────┘                     │
│                  │                          │                               │
│                  └────────────┬─────────────┘                               │
│                               ▼                                             │
│                    ┌─────────────────┐                                     │
│                    │  Tool Execution │                                     │
│                    │  (implementation)│                                    │
│                    └────────┬────────┘                                     │
│                             │                                               │
│                             ▼                                               │
│                    ┌─────────────────┐                                     │
│                    │  Core Bridge    │                                     │
│                    │  (call_kernel)  │                                     │
│                    └────────┬────────┘                                     │
│                             │                                               │
│                             ▼                                               │
│                    ┌─────────────────┐                                     │
│                    │  Constitutional │                                     │
│                    │  Kernel (core/) │                                     │
│                    └─────────────────┘                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.4 Key Architectural Changes

#### 3.4.1: Single Verdict Enum

```python
# core/shared/types.py - CANONICAL
class Verdict(str, Enum):
    """Canonical constitutional verdict outcomes."""
    
    # Non-terminal (proceed with caution)
    SEAL = "SEAL"              # All floors passed
    PROVISIONAL = "PROVISIONAL"  # Proceed with warnings
    PARTIAL = "PARTIAL"        # Incomplete but usable
    SABAR = "SABAR"            # Pause, needs more context
    HOLD = "HOLD"              # Wait for human
    HOLD_888 = "HOLD_888"      # High-stakes human gating
    
    # Terminal (stop processing)
    VOID = "VOID"              # Hard rejection
    
    # System states
    PAUSED = "PAUSED"
    ALIVE = "ALIVE"
    DEGRADED = "DEGRADED"
```

#### 3.4.2: Single Tool Dispatcher

```python
# arifos_mcp/runtime/dispatcher.py
from typing import Callable, Dict, Any
from abc import ABC, abstractmethod

class Tool(ABC):
    """Base class for all arifOS tools."""
    
    name: str
    stage: str
    floors: list[str]
    
    @abstractmethod
    async def execute(self, payload: dict) -> dict:
        """Execute the tool with validated payload."""
        pass
    
    async def check_floors(self, payload: dict) -> FloorResult:
        """Check constitutional floors before execution."""
        return await floor_engine.check(self.floors, payload)

class ToolRegistry:
    """Central registry for all tools."""
    
    _tools: Dict[str, Tool] = {}
    
    @classmethod
    def register(cls, tool: Tool) -> None:
        cls._tools[tool.name] = tool
    
    @classmethod
    def get(cls, name: str) -> Tool:
        return cls._tools.get(name)
    
    @classmethod
    def list_tools(cls) -> list[str]:
        return list(cls._tools.keys())

class ToolDispatcher:
    """Single dispatch point for all tool calls."""
    
    async def dispatch(
        self,
        tool_name: str,
        payload: dict,
        auth_context: dict | None = None
    ) -> RuntimeEnvelope:
        # 1. Lookup tool
        tool = ToolRegistry.get(tool_name)
        if not tool:
            return self._error_envelope(f"Unknown tool: {tool_name}")
        
        # 2. Check floors
        floor_result = await tool.check_floors(payload)
        if floor_result.verdict == Verdict.VOID:
            return self._void_envelope(floor_result)
        
        # 3. Execute
        result = await tool.execute(payload)
        
        # 4. Wrap in envelope
        return RuntimeEnvelope(
            tool=tool_name,
            stage=tool.stage,
            status=RuntimeStatus.SUCCESS,
            verdict=floor_result.verdict,
            payload=result
        )
```

#### 3.4.3: ABI Layer for Schema Validation

```python
# arifos_mcp/abi/v1_0.py
from pydantic import BaseModel, Field
from typing import Literal, Any

class InitAnchorRequest(BaseModel):
    """Canonical init_anchor request (ABI v1.0)."""
    
    actor_id: str = Field(default="anonymous", min_length=2, max_length=64)
    declared_name: str | None = Field(default=None, max_length=64)
    intent: str | dict | None = None
    session_id: str | None = Field(default=None, min_length=8, max_length=128)
    human_approval: bool = False
    risk_tier: Literal["low", "medium", "high", "critical"] = "low"
    dry_run: bool = True
    allow_execution: bool = False

class InitAnchorResponse(BaseModel):
    """Canonical init_anchor response (ABI v1.0)."""
    
    ok: bool
    session_id: str
    auth_state: Literal["unverified", "anchored", "verified", "rejected"]
    identity: dict
    allowed_next_tools: list[str]
    verdict: str

# Schema registry
ABI_SCHEMAS = {
    "init_anchor": {
        "request": InitAnchorRequest,
        "response": InitAnchorResponse
    },
    # ... other tools
}

def validate_request(tool_name: str, payload: dict) -> BaseModel:
    """Validate request against ABI schema."""
    schema = ABI_SCHEMAS.get(tool_name, {}).get("request")
    if not schema:
        raise ValueError(f"No schema for tool: {tool_name}")
    return schema(**payload)
```

#### 3.4.4: Pluggable Vault Interface

```python
# infrastructure/vault/interface.py
from abc import ABC, abstractmethod
from typing import Any

class VaultBackend(ABC):
    """Abstract vault backend interface."""
    
    @abstractmethod
    async def write(self, entry: dict) -> str:
        """Write entry to vault, return entry ID."""
        pass
    
    @abstractmethod
    async def read(self, entry_id: str) -> dict | None:
        """Read entry from vault."""
        pass
    
    @abstractmethod
    async def query(self, filters: dict) -> list[dict]:
        """Query vault with filters."""
        pass
    
    @abstractmethod
    async def health(self) -> dict:
        """Return vault health status."""
        pass

class Vault:
    """Unified vault with pluggable backend."""
    
    def __init__(self, backend: VaultBackend):
        self._backend = backend
    
    async def seal(self, record: dict) -> SealRecord:
        """Seal a record to the vault."""
        entry_id = await self._backend.write(record)
        return SealRecord(
            status="sealed",
            ledger_id=entry_id,
            timestamp=datetime.utcnow()
        )
```

#### 3.4.5: FastMCP Compatibility Layer

```python
# arifos_mcp/runtime/compat.py
import fastmcp
from typing import Any, Callable

VERSION_MAJOR = int(fastmcp.__version__.split('.')[0])
IS_FASTMCP_3 = VERSION_MAJOR >= 3
IS_FASTMCP_2 = VERSION_MAJOR == 2

# Exception compatibility
from fastmcp.exceptions import FastMCPError

try:
    from fastmcp.exceptions import ToolError, AuthorizationError
    HAS_TOOL_ERROR = True
    HAS_AUTH_ERROR = True
except ImportError:
    HAS_TOOL_ERROR = False
    HAS_AUTH_ERROR = False
    
    class ToolError(FastMCPError):
        pass
    
    class AuthorizationError(FastMCPError):
        pass

# Context compatibility
try:
    from fastmcp.server.context import Context
    from fastmcp.dependencies import CurrentContext
    HAS_CONTEXT = True
except ImportError:
    HAS_CONTEXT = False
    Context = Any
    CurrentContext = Any

def get_context_param() -> Any:
    """Get context parameter for tool decorators."""
    if HAS_CONTEXT:
        return CurrentContext
    return None

def create_http_app(mcp: Any, stateless: bool = True) -> Any:
    """Create HTTP app compatible with FastMCP 2.x and 3.x."""
    if IS_FASTMCP_3:
        return mcp.http_app(stateless_http=stateless)
    elif hasattr(mcp, 'streamable_http_app'):
        return mcp.streamable_http_app()
    else:
        return mcp.http_app()
```

---

## Part 4: Implementation Roadmap

### Phase 1: Schema Consolidation (Week 1)

1. **Consolidate Verdict enum**
   - Move to `core/shared/types.py`
   - Update all imports
   - Remove duplicate from `core/floors.py`

2. **Define canonical ABI v1.0**
   - Create `arifos_mcp/abi/v1_0.py`
   - Document all tool schemas
   - Implement validation layer

3. **Standardize AuthorityLevel**
   - Single enum with all values
   - Document mapping from session classes

### Phase 2: Architecture Refactoring (Week 2-3)

1. **Create Tool Registry**
   - Implement `arifos_mcp/runtime/dispatcher.py`
   - Migrate tools to new base class

2. **Implement Pluggable Vault**
   - Create `infrastructure/vault/` package
   - Migrate existing vault code

3. **Consolidate Session Management**
   - Single session manager in `infrastructure/session/`
   - Remove duplicate implementations

### Phase 3: Code Cleanup (Week 4)

1. **Remove Orphaned Code**
   - Delete `init_000` references
   - Clean up TOOL_MAP
   - Remove unused imports

2. **Consolidate Horizon Servers**
   - Single implementation in `arifos_mcp/server_horizon.py`
   - Remove duplicates

3. **Fix Circular Dependencies**
   - Refactor import patterns
   - Add interface boundaries

### Phase 4: Testing & Validation (Week 5)

1. **Update Tests**
   - Fix broken tests
   - Add schema validation tests
   - Add integration tests

2. **Performance Testing**
   - Benchmark tool dispatch
   - Verify no regression

3. **Documentation**
   - Update API documentation
   - Document ABI v1.0

---

## Part 5: Migration Guide

### For Tool Developers

```python
# OLD WAY (scattered, inconsistent)
async def my_tool(
    query: str,
    session_id: str = None,
    ctx: Context = None  # BREAKS on Horizon!
) -> dict:
    return {"result": "..."}

# NEW WAY (canonical, compatible)
from arifos_mcp.tools.base import Tool
from arifos_mcp.abi.v1_0 import MyToolRequest, MyToolResponse

class MyTool(Tool):
    name = "my_tool"
    stage = "444_ROUTER"
    floors = ["F1", "F2", "F4"]
    request_schema = MyToolRequest
    response_schema = MyToolResponse
    
    async def execute(self, payload: dict) -> dict:
        # Validated payload
        request = self.request_schema(**payload)
        
        # Implementation
        result = await do_work(request.query)
        
        return self.response_schema(result=result).dict()

# Register
from arifos_mcp.runtime.dispatcher import ToolRegistry
ToolRegistry.register(MyTool())
```

### For Client Developers

```python
# ABI v1.0 guarantees consistent interface
request = {
    "actor_id": "my_agent",
    "declared_name": "My Agent",
    "intent": "test query",
    "risk_tier": "low"
}

# Works on both Horizon and VPS
response = await client.call("init_anchor", request)

# Response structure guaranteed
assert "session_id" in response
assert "auth_state" in response
assert "verdict" in response
```

---

## Appendix A: File Inventory

### Files to Keep (Canonical)

| File | Purpose |
|------|---------|
| `server.py` | Entry point |
| `config/environments.py` | Environment config |
| `arifos_mcp/runtime/server.py` | FastMCP server |
| `core/shared/types.py` | Canonical types |
| `core/floors.py` | Floor evaluation |
| `core/organs/` | Organ implementations |

### Files to Consolidate

| Current | Consolidate To |
|---------|----------------|
| `horizon/server.py` | `arifos_mcp/server_horizon.py` |
| `arifos_mcp/runtime/tools_hardened_*.py` | `arifos_mcp/runtime/dispatcher.py` |
| `arifos_mcp/runtime/tools_internal.py` | Individual tool files |
| `arifos_mcp/runtime/vault_redis.py` | `infrastructure/vault/redis.py` |

### Files to Remove

| File | Reason |
|------|--------|
| `init_000` references | Purged, not needed |
| `archive/deprecated/` | Move to separate repo |
| Duplicate Horizon servers | Consolidated |
| `fastmcp_compat.py` | Merged into `compat.py` |

---

## Appendix B: Schema Reference

### ABI v1.0 Tool Signatures

```python
# All tools follow this pattern:
{
    "name": str,           # Tool name
    "stage": str,          # Metabolic stage (000, 111, ..., 999)
    "floors": list[str],   # F1-F13 floors to check
    "input": {
        "mode": str,       # Operation mode
        "payload": dict,   # Mode-specific data
        "auth_context": dict | None,  # Optional auth
        "risk_tier": "low" | "medium" | "high" | "critical",
        "dry_run": bool,
        "allow_execution": bool
    },
    "output": {
        "ok": bool,
        "verdict": str,    # SEAL, PROVISIONAL, PARTIAL, SABAR, HOLD, VOID
        "payload": dict,   # Tool-specific result
        "session_id": str,
        "stage": str,
        "errors": list[dict] | None
    }
}
```

---

## Appendix C: Glossary

| Term | Definition |
|------|------------|
| **ABI** | Application Binary Interface - canonical schema definitions |
| **Floor** | Constitutional constraint (F1-F13) |
| **Organ** | Core processing module (AGI, ASI, APEX, INIT, VAULT) |
| **Stage** | Metabolic pipeline stage (000-999) |
| **Trinity** | ΔΩΨ - Delta (human), Omega (constitution), Psi (machine) |
| **Verdict** | Constitutional decision outcome |
| **W³** | Tri-witness consensus score |

---

**DITEMPA BUKAN DIBERI** — *Forged, Not Given*

```
ΔΩΨ | ARIF | 888_JUDGE
```

---

*Document Version: 2026.04.01*  
*Kernel Hash: ΔΩΨ-ARIF-888*  
*Status: ARCHITECTURE SPECIFICATION*
