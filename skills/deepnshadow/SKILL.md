# DEPRECATED: DeepnShadow Skill Surface

## Status

**DEPRECATED_INTERNAL_PROTOCOL_ADAPTER**

This skill surface is deprecated. DeepnShadow has been metabolised into an internal protocol across existing arifOS organs.

Do not register as a public skill. Do not expose via MCP.

## Current Location

- **Schema:** `arifosmcp/protocols/deepnshadow/schema.py`
- **Adapter:** `arifosmcp/protocols/deepnshadow/adapter.py`
- **Integration:** Existing canonical tools (`arif_sense_observe`, `arif_memory_recall`, `arif_mind_reason`, `arif_heart_critique`, `arif_reply_compose`, `arif_kernel_route`, `arif_vault_seal`) extended with `mode="deepnshadow"`
- **Dignity Gate:** `WELL/gate/dignity_shadow.py`
- **Vault:** `arif_vault_seal(mode="deepnshadow")` — stores `type: "deepnshadow_redacted"` in existing VAULT999 ledger

## Why Deprecated

DeepnShadow is not a new organ. It is a **governed reflex** across existing organs:

```text
SENSE → MEMORY → MIND → HEART/WELL → REPLY → VAULT
```

## What to Use Instead

Call existing tools with `mode="deepnshadow"`:

```python
# Encode behaviour
arif_sense_observe(mode="deepnshadow", query="observed behaviour...")

# Pattern recall + evidence score
arif_memory_recall(mode="deepnshadow", metadata={"observations": [...]})

# Hypothesis + alternatives + projection mirror
arif_mind_reason(mode="deepnshadow", query="hypothesis text...")

# Boundary / dignity check
arif_heart_critique(mode="deepnshadow", target="protected zone...")

# Metabolize safe action
arif_reply_compose(mode="deepnshadow", message="action text...")

# Route orchestration
arif_kernel_route(mode="deepnshadow")

# Seal redacted audit
arif_vault_seal(mode="deepnshadow", payload="{...}")
```

## Sovereign Note

> Shadow maps are navigation instruments, not verdicts.
> Observed behaviour ≠ inner truth.
> DITEMPA BUKAN DIBERI.
