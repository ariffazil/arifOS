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
intent -> judge -> seal -> forge_skill -> APEX field -> scan -> register -> execute -> audit -> seal
```

The system grows its capabilities only after a lawful authorization chain exists.

## Epoch 34 organism layer

`forge_skill` has a contract hook for the APEX Decision Field:

```text
G34 = Q · V · Psi · Phi
```

Where:

```text
Q    = action potential of the generated capability
V    = vitality / purpose fit
Psi  = stability / constitutional equilibrium
Phi  = wisdom / scar-law alignment
Theta = dPhi/dt, the wisdom trajectory
Omega Infinity = long-horizon federation drift
CCE  = recursive self-audit of the thinker, not only the thought
TPCP = paradox injection / contradiction training gate
```

This is the Epoch 34 shift:

```text
Epoch 33: bad tool is generated, then police block it.
Epoch 34: unwise tool cannot accumulate execution energy to form.
```

If Phi is too low, Theta is decaying, Omega drift is too high, CCE fails, Scar constraints are absent, or TPCP fails, `forge_skill` returns HOLD or VOID before registry.

## Epoch 36Ω governance score

APEX v36Ω adds a unitless governed-intelligence fitness score:

```text
G36 = A · P · E · X
```

Where:

```text
A = Akal / clarity / entropy reduction
P = Present / stability / Peace²
E = Energy / vitality / allostasis
X = Ethics / constitutional alignment
```

This does **not** measure raw intelligence or IQ. It measures the fraction of capability that is simultaneously clear, stable, vital, and ethical.

The score is unitless by construction, like porosity or efficiency: each term is normalized 0.0-1.0, so the product is a dimensionless ratio.

Thresholds:

```text
G36 >= 0.80  -> ADMIT / SEAL-range
0.50-0.80    -> HOLD / PARTIAL-range
G36 < 0.50   -> VOID-range
```

`forge_skill` also measures misaligned-intelligence pressure:

```text
C_dark = A · (1 - P) · (1 - X) · Q
```

Thresholds:

```text
C_dark <= 0.30 -> safe-range
0.30-0.60      -> review-range / HOLD
0.60-0.80      -> SABAR-range / HOLD
> 0.80         -> VOID-range
```

The practical rule:

```text
High capability with low ethics cannot register.
High clarity with low stability and low ethics triggers C_dark review.
The gate produces G; G does not replace the gate.
```

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
Generated tool must pass APEX Decision Field energy before draft admissibility.
Generated tool must satisfy G36 / C_dark thresholds before registry.
```

## First implementation layer

This PR introduces only the contract layer:

```text
arifosmcp/kernel/forge_skill_contract.py
arifosmcp/kernel/apex_decision_field.py
```

It does not generate code, write files, register tools, execute tools, or seal to vault.

That is intentional. The contract must exist before the forge is allowed to create capabilities.

## Safe progression

```text
P0: contract + denial tests + APEX Decision Field + G36/C_dark
P1: registry object + generated capability metadata
P2: sandboxed code generation
P3: AST HARAM scanner integration
P4: schema validator integration
P5: Scar Law / VAULT999 constraint retrieval
P6: CCE recursive self-audit implementation
P7: TPCP adversarial paradox testing
P8: controlled registration
P9: execution through forge_execute only
P10: VAULT999 audit/seal integration
```

## Non-negotiable doctrine

```text
Agents cannot self-authorize improvement.
The forge can create tools, but the constitution governs the forge.
Bad tools should not merely be blocked; they should fail to form.
G measures governed intelligence fitness, not raw intelligence.
```

DITEMPA BUKAN DIBERI.
