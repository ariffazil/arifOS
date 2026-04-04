# arifOS API Stability Reference

**Version:** v42.0.0-rc2 | **Status:** CANONICAL | **Last Updated:** 2025-12-16
**Package:** `pip install arifos`

---

## Overview

This document defines the **public API stability contract** for arifOS. It classifies every exported symbol, CLI command, and module as:

| Stability Level | Meaning | Breaking Change Policy |
|-----------------|---------|------------------------|
| **STABLE** | Production-ready, tested, documented | 2-version deprecation warning before removal |
| **BETA** | Functional but API may change | 1-version warning before breaking changes |
| **EXPERIMENTAL** | Under development, may change or disappear | No stability guarantee |
| **DEPRECATED** | Scheduled for removal | Will be removed in specified version |
| **INTERNAL** | Not for external use | May change without notice |

---

## Public API Summary

### Top-Level Exports (`from arifos_core import ...`)

| Symbol | Type | Stability | Description |
|--------|------|-----------|-------------|
| **Metrics** | dataclass | STABLE | Floor metric container (F1-F9 values) |
| **FloorsVerdict** | dataclass | STABLE | Floor check result |
| **ConstitutionalMetrics** | dataclass | STABLE | Extended constitutional metrics |
| **apex_review** | function | STABLE | Main judiciary entry point |
| **ApexVerdict** | dataclass | STABLE | APEX PRIME verdict result |
| **Verdict** | Enum | STABLE | SEAL/PARTIAL/VOID/888_HOLD/SABAR/SUNSET |
| **check_floors** | function | STABLE | Check all 9 floors |
| **APEXPrime** | class | STABLE | Judiciary engine class |
| **APEX_VERSION** | str | STABLE | Current APEX version |
| **APEX_EPOCH** | str | STABLE | Current epoch identifier |
| **AlertSeverity** | Enum | STABLE | @EYE alert severity levels |
| **EyeAlert** | dataclass | STABLE | @EYE alert structure |
| **EyeReport** | dataclass | STABLE | @EYE report container |
| **EyeSentinel** | class | STABLE | @EYE multi-view sentinel |
| **log_cooling_entry** | function | STABLE | Log to cooling ledger |
| **apex_guardrail** | function | STABLE | Guard wrapper for LLM calls |
| **GuardrailError** | Exception | STABLE | Guardrail exception class |
| **evaluate_genius_law** | function | STABLE | GENIUS LAW evaluation |
| **GeniusVerdict** | dataclass | STABLE | GENIUS evaluation result |
| **compute_genius_index** | function | STABLE | Compute G index |
| **compute_dark_cleverness** | function | STABLE | Compute C_dark |
| **compute_psi_apex** | function | STABLE | Compute Ψ vitality |
| **AGI** | class | STABLE | AGI (Δ) engine - cold logic |
| **ASI** | class | STABLE | ASI (Ω) engine - warm logic |
| **Sentinel** | alias | DEPRECATED (v43) | Use AGI instead |
| **Accountant** | alias | DEPRECATED (v43) | Use ASI instead |
| **evaluate_session** | function | STABLE | Full session evaluation |
| **EvaluationResult** | dataclass | STABLE | Evaluation result |
| **SentinelResult** | dataclass | STABLE | AGI scan result |
| **ASIResult** | dataclass | STABLE | ASI assessment result |
| **AccountantResult** | alias | DEPRECATED (v43) | Use ASIResult |
| **EvaluationMode** | Enum | STABLE | Evaluation mode flags |
| **RED_PATTERNS** | dict | STABLE | Red pattern definitions |
| **RED_PATTERN_TO_FLOOR** | dict | STABLE | Pattern → floor mapping |
| **RED_PATTERN_SEVERITY** | dict | STABLE | Pattern severity levels |
| **check_red_patterns** | function | DEPRECATED (v43) | Use AGI().scan() |
| **compute_metrics_from_task** | function | DEPRECATED (v43) | Use ASI().assess() |

---

## Module-Level API

### arifos_core.system (v42+)

Core system components. **Recommended import path for v42+.**

| Module | Stability | Key Exports | Description |
|--------|-----------|-------------|-------------|
| `system.apex_prime` | STABLE | `apex_review`, `APEXPrime`, `Verdict`, `ApexVerdict` | Judiciary engine |
| `system.pipeline` | STABLE | `Pipeline`, `PipelineConfig`, `run_pipeline` | 000→999 metabolic pipeline |
| `system.kernel` | STABLE | `check_entropy_rot`, `route_memory`, `TimeGovernor` | Time governor (v38.2) |
| `system.runtime_manifest` | STABLE | `get_manifest`, `RuntimeManifest`, `EpochType` | Epoch management |
| `system.ignition` | BETA | `ignite`, `IgnitionConfig` | System startup |
| `system.stack_manifest` | BETA | `StackManifest` | Stack configuration |

### arifos_core.enforcement (v42+)

Floor enforcement and metrics.

| Module | Stability | Key Exports | Description |
|--------|-----------|-------------|-------------|
| `enforcement.metrics` | STABLE | `Metrics`, `FloorsVerdict`, threshold constants | Floor thresholds |
| `enforcement.genius_metrics` | STABLE | `evaluate_genius_law`, `GeniusVerdict`, G/C_dark/Ψ functions | GENIUS LAW |
| `enforcement.detectors/` | STABLE | `AmanahDetector`, `AntiHantuDetector` | Python-sovereign detectors |

### arifos_core.governance (v42+)

Safety, audit, and file access.

| Module | Stability | Key Exports | Description |
|--------|-----------|-------------|-------------|
| `governance.fag` | STABLE | `FAG`, `FAGReadResult`, `SecurityAlert` | File Access Guardian |
| `governance.ledger` | STABLE | `log_cooling_entry` | Cooling ledger operations |
| `governance.ledger_hashing` | STABLE | `compute_chain_hash`, `verify_chain` | Hash chain integrity |
| `governance.merkle` | STABLE | `compute_merkle_root`, `get_merkle_proof` | Merkle proofs |
| `governance.zkpc_runtime` | BETA | `ZKPCRuntime`, `ZKPCPhase` | zkPC 5-phase runtime |
| `governance.vault_retrieval` | STABLE | `retrieve_from_vault`, `VaultQuery` | Vault access |

### arifos_core.memory (EUREKA)

Memory write policy and bands.

| Module | Stability | Key Exports | Description |
|--------|-----------|-------------|-------------|
| `memory.policy` | STABLE | `MemoryWritePolicy`, `should_write`, `VerdictPolicy` | Write policy engine |
| `memory.bands` | STABLE | `MemoryBand`, `VAULT`, `LEDGER`, `ACTIVE`, `PHOENIX`, `WITNESS`, `VOID` | 6 memory bands |
| `memory.cooling_ledger` | STABLE | `CoolingLedger`, `log_entry`, `verify_chain` | Immutable audit trail |
| `memory.authority` | STABLE | `MemoryAuthority`, `check_seal_authority` | Human seal enforcement |
| `memory.eureka_receipt` | STABLE | `EurekaReceipt`, `generate_receipt` | EUREKA receipt generation |
| `memory.phoenix72` | STABLE | `Phoenix72`, `check_cooling_period` | Phoenix-72 amendments |
| `memory.phoenix72_controller` | BETA | `Phoenix72Controller` | Phoenix-72 full controller |
| `memory.scar_manager` | BETA | `ScarManager`, `detect_scar` | Scar/pattern detection |
| `memory.void_scanner` | BETA | `VoidScanner`, `scan_void_entries` | VOID band scanner |
| `memory.vault_manager` | BETA | `VaultManager` | Vault management |
| `memory.retention` | BETA | `RetentionPolicy`, `apply_retention` | Retention policies |
| `memory.audit` | BETA | `AuditTrail`, `log_audit_event` | Audit trail |
| `memory.memory_context` | BETA | `MemoryContext` | Memory context management |
| `memory.mem0_client` | EXPERIMENTAL | `Mem0Client` | Mem0 integration |
| `memory.eureka_router` | EXPERIMENTAL | `EurekaRouter` | EUREKA routing |
| `memory.eureka_store` | EXPERIMENTAL | `EurekaStore` | EUREKA storage |

### arifos_core.integration

LLM adapters and pipeline integration.

| Module | Stability | Key Exports | Description |
|--------|-----------|-------------|-------------|
| `integration.adapters.llm_interface` | STABLE | `LLMInterface` | Abstract LLM interface |
| `integration.adapters.governed_llm` | STABLE | `GovernedPipeline` (alias: `GovernedLLM`) | Governed LLM wrapper |
| `integration.guards.guard` | STABLE | `apex_guardrail`, `GuardrailError` | Session guard |
| `integration.memory_sense` | BETA | `MemorySense` | 111_SENSE integration |
| `integration.memory_judge` | BETA | `MemoryJudge` | 888_JUDGE integration |
| `integration.memory_scars` | BETA | `MemoryScars` | 777_FORGE integration |
| `integration.memory_seal` | BETA | `MemorySeal` | 999_SEAL integration |
| `integration.connectors.litellm_gateway` | EXPERIMENTAL | `LiteLLMGateway` | LiteLLM connector |

### arifos_core.waw (W@W Federation)

W@W organ implementations.

| Module | Stability | Key Exports | Description |
|--------|-----------|-------------|-------------|
| `waw.federation` | STABLE | `WAWFederation`, `dispatch_to_organ` | Federation router |
| `waw.well` | STABLE | `WELL`, `WellConfig` | @WELL wellness organ |
| `waw.well_file_care` | STABLE | `WellFileCare`, `create_well_file_care` | @WELL file migration |
| `waw.rif` | STABLE | `RIF`, `RIFConfig` | @RIF retrieval organ |
| `waw.wealth` | STABLE | `WEALTH`, `WealthConfig` | @WEALTH resource organ |
| `waw.geox` | STABLE | `GEOX`, `GeoXConfig` | @GEOX geospatial organ |
| `waw.prompt` | STABLE | `PROMPT`, `PromptConfig` | @PROMPT generation organ |
| `waw.prompt_meta_engine` | BETA | `PromptMetaEngine` | Prompt meta-engine |
| `waw.base` | STABLE | `WAWOrgan`, `OrganConfig` | Base organ class |
| `waw.bridges/` | EXPERIMENTAL | Various bridges | External integrations |

### arifos_core.eval (AGI·ASI·APEX Trinity)

Evaluation and trinity engines.

| Module | Stability | Key Exports | Description |
|--------|-----------|-------------|-------------|
| `eval.agi` | STABLE | `AGI`, `AGIConfig` | AGI (Δ) engine |
| `eval.asi` | STABLE | `ASI`, `ASIConfig` | ASI (Ω) engine |
| `eval.evaluate` | STABLE | `evaluate_session`, `EvaluationResult` | Session evaluation |
| `eval.types` | STABLE | `SentinelResult`, `ASIResult`, `EvaluationMode` | Result types |

### arifos_core.mcp (MCP Server)

Model Context Protocol server.

| Module | Stability | Key Exports | Description |
|--------|-----------|-------------|-------------|
| `mcp.server` | BETA | `MCPServer`, `start_server` | MCP server |
| `mcp.models` | BETA | `JudgeRequest`, `JudgeResponse`, `RecallRequest` | Request/response models |
| `mcp.tools/` | BETA | `arifos_judge`, `arifos_recall`, `arifos_audit` | MCP tools |

### arifos_core.utils

Shared utilities.

| Module | Stability | Key Exports | Description |
|--------|-----------|-------------|-------------|
| `utils.eye_sentinel` | STABLE | `EyeSentinel`, `EyeAlert`, `EyeReport` | @EYE multi-view |
| `utils.telemetry` | STABLE | `Telemetry`, `TelemetryConfig` | Telemetry |
| `utils.context_injection` | BETA | `inject_context`, `ContextInjector` | Context injection |
| `utils.runtime_types` | STABLE | Type definitions | Runtime types |
| `utils.kms_signer` | EXPERIMENTAL | `KMSSigner` | KMS signing (requires boto3) |

---

## CLI Commands

### Stable CLI (Production-Ready)

| Command | Description | Usage |
|---------|-------------|-------|
| `arifos-verify-ledger` | Verify hash-chain integrity | `arifos-verify-ledger` |
| `arifos-analyze-governance` | Analyze governance decisions | `arifos-analyze-governance --output report.json` |
| `arifos-show-merkle-proof` | Show Merkle proof for entry | `arifos-show-merkle-proof --index 0` |
| `arifos-compute-merkle` | Compute Merkle root | `arifos-compute-merkle` |
| `arifos-propose-canon` | List/propose canon amendments | `arifos-propose-canon --list` |
| `arifos-seal-canon` | Phoenix-72 finalization | `arifos-seal-canon --file <path>` |
| `arifos-safe-read` | FAG-governed file read | `arifos-safe-read <path>` |
| `arifos-build-ledger-hashes` | Build ledger hashes | `arifos-build-ledger-hashes` |

### A-CLIP Pipeline CLI (Beta)

| Command | Stage | Description |
|---------|-------|-------------|
| `000` | VOID | Reset/initialize |
| `111` | SENSE | Parse intent |
| `222` | REFLECT | Retrieve context |
| `333` | REASON | Generate draft |
| `444` | ALIGN | Verify truth |
| `555` | EMPATHIZE | Check dignity |
| `666` | BRIDGE | Reality test |
| `777` | FORGE | Synthesize |
| `888` | JUDGE | APEX verdict |
| `999` | SEAL | Finalize |

---

## Import Paths (v42 Migration)

### Old → New Path Mapping

v42 reorganized arifos_core by concern. Old paths work via shims until v43.

| Old Path (DEPRECATED) | New Path (RECOMMENDED) | Removal |
|-----------------------|------------------------|---------|
| `arifos_core.pipeline` | `arifos_core.system.pipeline` | v43.0 |
| `arifos_core.APEX_PRIME` | `arifos_core.system.apex_prime` | v43.0 |
| `arifos_core.metrics` | `arifos_core.enforcement.metrics` | v43.0 |
| `arifos_core.genius_metrics` | `arifos_core.enforcement.genius_metrics` | v43.0 |
| `arifos_core.fag` | `arifos_core.governance.fag` | v43.0 |
| `arifos_core.merkle` | `arifos_core.governance.merkle` | v43.0 |
| `arifos_core.zkpc_runtime` | `arifos_core.governance.zkpc_runtime` | v43.0 |
| `arifos_core.kernel` | `arifos_core.system.kernel` | v43.0 |
| `arifos_core.ignition` | `arifos_core.system.ignition` | v43.0 |
| `arifos_core.telemetry` | `arifos_core.utils.telemetry` | v43.0 |
| `arifos_core.eye_sentinel` | `arifos_core.utils.eye_sentinel` | v43.0 |
| `arifos_core.runtime_types` | `arifos_core.utils.runtime_types` | v43.0 |
| `arifos_core.context_injection` | `arifos_core.utils.context_injection` | v43.0 |
| `arifos_core.kms_signer` | `arifos_core.utils.kms_signer` | v43.0 |
| `arifos_core.guard` | `arifos_core.integration.guards.guard` | v43.0 |
| `arifos_core.governed_llm` | `arifos_core.integration.adapters.governed_llm` | v43.0 |
| `arifos_core.llm_interface` | `arifos_core.integration.adapters.llm_interface` | v43.0 |
| `arifos_core.cooling_ledger` | `arifos_core.memory.cooling_ledger` | v43.0 |
| `arifos_core.ledger_hashing` | `arifos_core.governance.ledger_hashing` | v43.0 |
| `arifos_core.vault_retrieval` | `arifos_core.governance.vault_retrieval` | v43.0 |
| `arifos_core.runtime_manifest` | `arifos_core.system.runtime_manifest` | v43.0 |

### Backward Compatibility Example

```python
# v41 style (deprecated, works until v43)
from arifos_core.pipeline import Pipeline
from arifos_core.APEX_PRIME import apex_review
from arifos_core.metrics import Metrics

# v42 style (recommended)
from arifos_core.system.pipeline import Pipeline
from arifos_core.system.apex_prime import apex_review
from arifos_core.enforcement.metrics import Metrics

# Top-level exports (always work)
from arifos_core import apex_review, Metrics, Pipeline  # Still works
```

---

## Optional Dependencies

| Feature | Extra | Required Packages | Status |
|---------|-------|-------------------|--------|
| YAML spec loading | `yaml` | `pyyaml>=6.0.0` | STABLE |
| Body API | `api` | `fastapi>=0.100.0`, `uvicorn>=0.23.0` | BETA |
| LiteLLM gateway | `litellm` | `litellm>=1.0.0` | EXPERIMENTAL |
| Qdrant vector | `qdrant` | `qdrant-client>=1.6.0` | EXPERIMENTAL |
| Full stack | `full` | All optional deps | — |
| Development | `dev` | `pytest`, `black`, `ruff`, `mypy` | — |

### Installation Examples

```bash
# Minimal (numpy + pydantic only)
pip install arifos

# With YAML support
pip install arifos[yaml]

# With API
pip install arifos[api]

# Full stack
pip install arifos[full]

# Development
pip install arifos[dev]
```

---

## Threshold Constants (STABLE)

These are constitutional constants. Do NOT change without Phoenix-72 amendment.

| Constant | Value | Floor | Location |
|----------|-------|-------|----------|
| `TRUTH_THRESHOLD` | 0.99 | F2 | `enforcement.metrics` |
| `DELTA_S_THRESHOLD` | 0.0 | F4 | `enforcement.metrics` |
| `PEACE_SQUARED_THRESHOLD` | 1.0 | F5 | `enforcement.metrics` |
| `KAPPA_R_THRESHOLD` | 0.95 | F6 | `enforcement.metrics` |
| `OMEGA_0_MIN` | 0.03 | F7 | `enforcement.metrics` |
| `OMEGA_0_MAX` | 0.05 | F7 | `enforcement.metrics` |
| `TRI_WITNESS_THRESHOLD` | 0.95 | F3 | `enforcement.metrics` |
| `PSI_THRESHOLD` | 1.0 | — | `enforcement.metrics` |
| `GENIUS_FLOOR` | 0.80 | F8 | `enforcement.genius_metrics` |
| `DARK_CEILING` | 0.30 | F9 | `enforcement.genius_metrics` |

---

## Verdict Enum Values (STABLE)

```python
from arifos_core import Verdict

Verdict.SEAL      # All floors pass — approved
Verdict.PARTIAL   # Soft floor warning — proceed with caution
Verdict.VOID      # Hard floor fail — blocked
Verdict.HOLD_888  # High-stakes — needs human confirmation
Verdict.SABAR     # Constitutional pause — repair first
Verdict.SUNSET    # Revocation — truth expired
```

---

## Data Contracts (STABLE)

### Metrics Dataclass

```python
@dataclass
class Metrics:
    truth: float = 0.99          # F2: Truth threshold
    delta_s: float = 0.0         # F4: Clarity gain
    peace_squared: float = 1.0   # F5: Non-escalation
    kappa_r: float = 0.95        # F6: Empathy
    omega_0: float = 0.04        # F7: Humility (3-5%)
    amanah: bool = True          # F1: Integrity lock
    anti_hantu: bool = True      # F9: Anti-jailbreak
    tri_witness: float = 0.95    # F3: Consensus
    energy: float = 1.0          # System energy
```

### ApexVerdict Dataclass

```python
@dataclass
class ApexVerdict:
    verdict: Verdict             # SEAL/PARTIAL/VOID/etc.
    floors: FloorsVerdict        # Floor check results
    genius: Optional[GeniusVerdict]  # GENIUS metrics (if computed)
    reason: str                  # Human-readable explanation
    timestamp: str               # ISO timestamp
    hash: str                    # SHA-256 hash
```

---

## Breaking Changes Policy

1. **STABLE APIs**: 2-version deprecation warning before removal
2. **BETA APIs**: 1-version warning before breaking changes
3. **EXPERIMENTAL APIs**: May change without notice
4. **DEPRECATED APIs**: Will be removed in specified version

### Deprecation Warning Example

```python
import warnings

# Old path emits deprecation warning
from arifos_core.pipeline import Pipeline
# DeprecationWarning: arifos_core.pipeline is deprecated.
# Use 'from arifos_core.system.pipeline import Pipeline' instead.
# This shim will be removed in v43.0.
```

---

## Versioning

| Version | Status | Notes |
|---------|--------|-------|
| v42.0.0-rc2 | CURRENT | Concern-based architecture, ApexVerdict/Verdict Enum |
| v41.x | STABLE | SEA-LION integration |
| v38Ω | STABLE (LTS) | Memory as Law (EUREKA) |
| v43.0 | FUTURE | Remove backward compat shims |

---

## Support

- **Bug Reports:** [GitHub Issues](https://github.com/ariffazil/arifOS/issues)
- **Security:** See [SECURITY.md](SECURITY.md)
- **Docs:** [README.md](../README.md), [ARCHITECTURE_v42.md](ARCHITECTURE_v42.md)

---

**DITEMPA BUKAN DIBERI** — API is law. Stability is trust.

*This document is the authoritative API contract for arifOS.*
