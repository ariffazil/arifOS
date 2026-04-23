---
type: Concept
tier: 10_FOUNDATIONS
strand:
- constitutional
- architecture
audience:
- all
difficulty: beginner
prerequisites:
- What-is-arifOS
tags:
- naming
- canon
- governance
- federation
- architecture
sources:
- Concept_Architecture.md
- Audit_MCP_Tools_vs_Wiki.md
- Federation_Three_Wikis.md
last_sync: '2026-04-10'
confidence: 0.95
---

# Naming Canon

Naming is not decoration.
Naming is control surface.

When naming drifts, architecture drifts.
When architecture drifts, truth, governance, and operations all get slower and more fragile.

## Core rule

Every important thing gets:
- **one canonical name**
- optional aliases for compatibility
- one declared source of truth
- one scope

Aliases may exist.
Authority does not split.

## Why this matters

Bad naming creates avoidable chaos:
- duplicate concepts that look different but mean the same thing
- one label used for multiple realities
- slow operator reasoning
- broken links between runtime, docs, and machine state
- migration pain when legacy names are treated as peers instead of aliases

## Naming law

### 1. Canon first
A concept, tool, page, service, or component must have exactly one canonical label.

### 2. Alias second
Legacy, transport, shorthand, and operator-friendly names are allowed only as aliases.
They must point back to the canonical name.

### 3. Scope must be explicit
The same token should not silently mean different things across different layers.
At minimum, name scope should be clear across:
- **arifOS**: governance, runtime, tools, floors
- **GEOX**: Earth-domain theory, physics, materials, tools
- **A-FORGE**: infrastructure, services, deployment, recovery

### 4. Truth source must be declared
For every canonical name, there should be a declared truth source:
- runtime spec
- wiki page
- schema
- compose/service definition
- registry page

### 5. Rename slowly, alias immediately
If a rename is needed:
1. define the new canonical name
2. keep the old label as alias during transition
3. update references
4. remove alias only after the ecosystem is clean

## Three-wiki naming split

| Wiki | Naming responsibility |
|------|-----------------------|
| **arifOS** | canonical governance terms, runtime tools, floors, verdict language |
| **GEOX** | canonical Earth-domain concepts, theory, material and physics naming |
| **A-FORGE** | canonical machine, service, component, and operator naming |

## Practical examples

### Good
- canonical runtime tool name in arifOS, transport aliases mapped explicitly
- canonical container/service name in A-FORGE, current running drift logged as alias/drift
- canonical Earth-state term in GEOX, derived variables not mislabeled as base canon

### Bad
- same service called three different names in compose, docs, and dashboards
- a deprecated tool name treated as equal to the canonical tool id
- a descriptive nickname replacing the actual source-of-truth identifier

## Operational test

A naming system is healthy when an operator can answer these quickly:
1. what is the canonical name?
2. what aliases exist?
3. where is truth defined?
4. what scope does this name belong to?
5. is this name active, legacy, or deprecated?

If those answers are not immediate, naming drift is already happening.

## Federation rule

Across arifOS, GEOX, and A-FORGE:
- **one thing -> one canonical name**
- **many surfaces -> many aliases if needed**
- **one truth source -> always declared**

That is how the three wikis stay federated without collapsing into ambiguity.

## Related
- [[Federation_Three_Wikis]]
- [[Concept_Architecture]]
- [[Audit_MCP_Tools_vs_Wiki]]
