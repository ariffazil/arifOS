# Repository Boundary Contract

## Critical Rule

**This bridge contains ONLY adapter/glue code.**

If you find yourself writing:
- Floor evaluation logic → Move to arifOS
- Constitutional definitions → Move to arifOS
- Thermodynamic calculations → Move to arifOS
- Vault/Merkle chain logic → Move to arifOS

## Allowed Contents

✅ **Adapter code**: OpenClaw msg → MCP tool call
✅ **Configuration**: Model selection, formatting rules
✅ **Prompts**: OpenClaw-specific agent alignment
✅ **Healthchecks**: Deployment validation scripts
✅ **Documentation**: Operator guides

## Forbidden Contents

❌ **Constitutional logic** (F1-F13 enforcement)
❌ **Verdict computation** (SEAL/VOID/PARTIAL)
❌ **Thermodynamic calculations** (ΔS, Ω₀, Peace²)
❌ **Vault operations** (Merkle chains, cryptographic sealing)
❌ **Canon definitions** (000_THEORY content)

## Test

If you can delete this repo and arifOS still enforces 13 Floors correctly,
this bridge is properly scoped.

## Violation Report

If boundary violations are found:
1. File issue with `BOUNDARY-VIOLATION` label
2. Move code to proper repo
3. Update this doc if rule was unclear

**DITEMPA BUKAN DIBERI** — Adapters are forged, not constitution.
