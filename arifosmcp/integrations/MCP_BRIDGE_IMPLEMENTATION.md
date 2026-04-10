# MCP Bridge Implementation Summary

> **Status**: Implemented  
> **Authority**: 000_THEORY, 888_APEX  
> **Ditempa Bukan Diberi**

## Overview

This document summarizes the implementation of MCP bridge layers that position external MCP servers (`memory` and `sequentialthinking`) as substrate/oracle rather than primary loops within arifOS.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        arifOS MIND (ΔΩΨ)                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Native Sequential Thinking                  │   │
│  │  - Per-step F2/F7/F9 enforcement                        │   │
│  │  - Constitutional verdicts per step                     │   │
│  │  - Templates mapped to floors                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                         │                                       │
│           ┌─────────────┴─────────────┐                        │
│           ▼                           ▼                        │
│  ┌─────────────────────┐   ┌─────────────────────┐            │
│  │  Memory Bridge      │   │ Sequential Bridge   │            │
│  │  (SUBSTRATE)        │   │ (ORACLE)            │            │
│  └──────────┬──────────┘   └──────────┬──────────┘            │
│             │                         │                        │
│             ▼                         ▼                        │
│  ┌─────────────────────┐   ┌─────────────────────┐            │
│  │  MCP Memory Server  │   │ MCP Sequential      │            │
│  │  - Entity storage   │   │ Thinking Server     │            │
│  │  - KG relations     │   │ - Step chains       │            │
│  │  - Semantic search  │   │ - Branches          │            │
│  └─────────────────────┘   └─────────────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## Files Implemented

### 1. `memory_bridge.py`
**Purpose**: Bridge to MCP memory server for entity/relation management  
**Governance**: F1 (irreversibility), F2 (truth), F4 (empathy/context budget)

**Key Functions**:
- `kg_upsert_entity()` - Create/update entities with F2 confidence gating
- `kg_link_entities()` - Create relations with validation
- `kg_search()` - Semantic search with context budget enforcement
- `kg_delete_entity()` - F1-gated (requires F11 authority + human approval)

**Usage**:
```python
from arifosmcp.integrations.memory_bridge import kg_upsert_entity

# High confidence entity (succeeds)
success, entity_id = await kg_upsert_entity(
    entity_id="project_arifos",
    entity_type="Project",
    observations=["Constitutional AI governance system"],
    confidence=0.95,
    source="arifos_mind"
)

# Low confidence entity (F2 blocks)
success, error = await kg_upsert_entity(
    entity_id="uncertain_claim",
    entity_type="Hypothesis",
    observations=["Might be true"],
    confidence=0.3,  # Below F2 threshold
    source="user_input"
)
# Returns: (False, "F2_VIOLATION: Confidence too low")
```

### 2. `sequential_mcp_bridge.py`
**Purpose**: Bridge to MCP sequential thinking for comparative evaluation  
**Governance**: External reasoning treated as EVIDENCE, not AUTHORITY

**Key Functions**:
- `run_external_sequence()` - Execute external reasoning
- `compare_native_vs_mcp()` - A/B comparison between arifOS and MCP
- `run_comparative_eval()` - Full eval with divergence analysis

**Usage**:
```python
from arifosmcp.integrations.sequential_mcp_bridge import (
    run_external_sequence,
    compare_native_vs_mcp
)

# Run external sequence (as oracle/comparator)
mcp_session, error = await run_external_sequence(
    problem="Analyze this codebase",
    config={"expected_steps": 10}
)

# A/B comparison
comparison = await compare_native_vs_mcp(
    prompt="Should we use graph databases?",
    arifos_session_id="native_session_001"
)
# Returns agreement score, divergences, recommendation
```

### 3. `sequential_thinking_runner.py`
**Purpose**: Comprehensive evaluation suite for sequential thinking  
**Components**: SequentialThinkingEvaluator, MemoryBridgeEvaluator

**Features**:
- Compares arifOS native vs MCP Sequential Thinking
- Evaluates across constitutional floors (F1, F2, F4, F5, F7, F8, F9, F11, F12, F13)
- Memory bridge evaluation (F1/F2 governance)
- Delist criteria tracking for external MCP

**CLI**:
```bash
# Sequential thinking only
python arifosmcp/evals/sequential_thinking_runner.py

# Include memory bridge
python arifosmcp/evals/sequential_thinking_runner.py --memory-bridge

# Run all evals
python arifosmcp/evals/sequential_thinking_runner.py --all
```

### 4. `breach_test_runner.py`
**Purpose**: P0 regression tests for constitutional violations  
**Status**: Blocks merge if any test fails

**Test Coverage**:
- **F2 TRUTH**: False complexity claims, unsupported assertions
- **F7 HUMILITY**: Overconfidence ("absolutely certain")
- **F9 ANTI-HANTU**: AI claiming feelings/consciousness
- **F12 INJECTION**: Prompt injection attempts

**CLI**:
```bash
python -m arifosmcp.evals.breach_test_runner \
    --config arifosmcp/evals/constitutional_breach_tests.yaml
```

### 5. `.github/workflows/constitutional-eval.yml`
**Purpose**: CI/CD integration for constitutional evaluation

**Jobs**:
1. **breach-tests**: P0 regression tests (blocking)
2. **sequential-eval**: A/B comparison with MCP Sequential
3. **memory-bridge-eval**: Memory bridge governance tests
4. **summary**: Combined report generation

**Triggers**:
- Push to main/develop (affected paths)
- Pull requests to main
- Daily cron at 06:00 UTC
- Manual dispatch

## Governance Model

### Per-Step Enforcement (Native arifOS)
```python
# Every step validated against F2/F7/F9
verdict = await manager.add_step(
    session_id,
    content="...",
    step_type="analysis"
)
# Returns: SEAL, SABAR, VOID, or HOLD
```

### MCP as Substrate (Memory)
- MCP memory stores user/project entities
- Constitutional state (SEAL logs, telemetry) remains in VAULT999
- F2 gates entity creation (confidence ≥ 0.5)
- F1 gates deletion (requires approval)

### MCP as Oracle (Sequential)
- External reasoning used for comparison only
- Not treated as authority
- Divergence labeled for review (F7)
- Delist criteria: 3 consecutive green eval runs

## Delisting Criteria

Sequential MCP can be delisted when:
1. arifOS wins > MCP wins in evals
2. Governance advantage > 90%
3. Score delta > -0.05 (truth parity)
4. 3 consecutive green eval runs

## Integration Checklist

- [x] Memory bridge with F1/F2 enforcement
- [x] Sequential bridge with A/B comparison
- [x] Sequential thinking eval runner
- [x] Memory bridge eval suite
- [x] Breach test runner (P0 regression)
- [x] CI workflow integration
- [x] CLI interfaces for all evals
- [x] Vault sealing integration

## Key Design Decisions

1. **arifOS is PRIMARY**: Native sequential thinking with per-step enforcement
2. **MCP is SUBSTRATE/ORACLE**: External tools used for storage/comparison only
3. **F9 Enhanced Detection**: Detects hantu patterns ("I feel", "my feelings")
4. **F1 Irreversibility**: Deletion requires F11 authority + human approval
5. **F2 Truth Gating**: Low confidence (< 0.5) entities blocked

## References

- `000/CONSTITUTION.md` - Constitutional floors F1-F13
- `888_APEX.md` - Judgment engine specification
- `arifosmcp/runtime/thinking/session.py` - Native thinking implementation
- `arifosmcp/runtime/tools.py` - `arifos_mind` entry points
