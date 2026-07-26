# FEDERATION_MAP.md — arifOS

```yaml
layer: L0
role: CONSTITUTION
function: Law
status: ACTIVE
canon: arif-fazil.com/arifos/

identity:
  repository: ariffazil/arifos
  organ: arifOS Constitutional Kernel
  floor_range: F1–F13
  sovereign: Muhammad Arif bin Fazil (F13)

function: |
  arifos is the constitutional kernel of the arifOS Federation.
  It owns: identity, sessions, authority, floor enforcement (F1–F13),
  judgment routing (000→999 pipeline), VAULT999 immutable ledger,
  and all SEAL/HOLD/SABAR/VOID verdicts.

  arifos judges. It does NOT execute.
  Execution is A-FORGE's domain (L1).
  Domain organs (GEOX, WEALTH, WELL) compute evidence — they never adjudicate.

downstream:
  - ariffazil/AAA          # L1 — control plane
  - ariffazil/APEX         # L1 — judgment engine
  - ariffazil/arifFlow     # L1 — coordination
  - ariffazil/A-FORGE      # L1 — execution shell

domain_bridges:
  - ariffazil/geox         # L2 — earth evidence
  - ariffazil/wealth       # L2 — capital evidence
  - ariffazil/well         # L2 — human readiness
  - ariffazil/HERMES       # L2 — multi-modal bridge

federation_surface: https://arif-fazil.com/arifos/
```

**DITEMPA BUKAN DIBERI — Forged, Not Given.**
