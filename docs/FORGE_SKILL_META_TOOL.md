# `forge_skill` — Governed Dynamic Capability Creation

## Verdict

`forge_skill` is the missing meta-tool that makes A-FORGE a forge rather than a static toolbox.

It must be built as a constitutional capability generator, not as arbitrary self-modifying code.

```text
4 permanent tools. Unbounded generated tools. Constitutional gate on every forge act.
```

## Permanent A-FORGE MCP surface

```text
forge_execute   — run any approved registered capability
forge_skill     — forge a new capability under constitutional law
forge_probe     — federation health and readiness
forge_registry  — live registry of existing generated capabilities
```

Everything else is either:

```text
1. human-facing TUI/CLI/opencode capability
2. internal implementation detail
3. generated capability sealed through forge_skill
```

## Why this is different from a toolbox

Static toolbox:

```text
predict capability -> build tool -> deploy -> use
```

Dynamic forge:

```text
intent -> judge -> seal -> forge_skill -> scan -> register -> execute -> audit -> seal
```

The system grows its capabilities only after a lawful authorization chain exists.

## `forge_skill` invariants

```text
Generated tool cannot modify forge_skill itself.
Generated tool cannot modify ToolRegistry directly.
Generated tool cannot bypass Layer 1-4 gate.
Generated tool cannot write to VAULT999 directly.
Generated tool requires schema fingerprint before registration.
Generated tool requires code fingerprint before registration.
Generated tool requires HARAM scan before registration.
Generated irreversible capability requires F13 acknowledgement / 888_HOLD path.
Generated tool is sealed before first execution.
```

## First implementation layer

This PR introduces only the contract layer:

```text
arifosmcp/kernel/forge_skill_contract.py
```

It does not generate code, write files, register tools, execute tools, or seal to vault.

That is intentional. The contract must exist before the forge is allowed to create capabilities.

## Safe progression

```text
P0: contract + denial tests
P1: registry object + generated capability metadata
P2: sandboxed code generation
P3: HARAM scanner integration
P4: schema validator integration
P5: controlled registration
P6: execution through forge_execute only
P7: VAULT999 audit/seal integration
```

## Non-negotiable doctrine

```text
Agents cannot self-authorize improvement.
The forge can create tools, but the constitution governs the forge.
```

DITEMPA BUKAN DIBERI.
