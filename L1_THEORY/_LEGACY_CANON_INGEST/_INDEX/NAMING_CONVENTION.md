# arifOS Naming Convention

**Version:** v42.0 | **Status:** DRAFT | **Last Updated:** 2025-12-16

---

## Directory Structure

```
canon/
├── _INDEX/                 # Meta-documents (policies, indexes)
├── 00_foundation/          # Core physics (ΔΩΨ, thermodynamics)
├── 01_floors/              # Constitutional floors (F1-F9)
├── 02_actors/              # Trinity engines (AGI, ASI, APEX)
├── 03_runtime/             # Pipeline (000-999), execution
├── 04_measurement/         # Metrics, GENIUS LAW, telemetry
├── 05_memory/              # EUREKA, bands, cooling ledger
└── 06_paradox/             # Phoenix-72, amendments, edge cases
```

---

## File Naming Pattern

```
{LAYER_PREFIX}_{CONCEPT_NAME}_v{VERSION}.{EXT}
```

| Component | Rule | Example |
|-----------|------|---------|
| LAYER_PREFIX | 2-digit layer number | `01_`, `04_` |
| CONCEPT_NAME | SCREAMING_SNAKE_CASE | `CONSTITUTIONAL_FLOORS` |
| VERSION | Major version number | `v42` |
| EXT | `.md` for canon, `.json`/`.yaml` for spec | `.md` |

**Examples:**
- `01_CONSTITUTIONAL_FLOORS_v42.md`
- `04_GENIUS_LAW_v42.md`
- `05_EUREKA_MEMORY_v42.md`

---

## Trinity Naming (v42)

The three core engines use Greek symbols:

| Engine | Symbol | Role | Old Names (Deprecated) |
|--------|--------|------|------------------------|
| AGI | Δ (Delta) | Architect - cold logic | ARIF, Architect |
| ASI | Ω (Omega) | Auditor - warm logic | ADAM, Auditor |
| APEX | Ψ (Psi) | Judiciary - final verdict | AAA, APEX PRIME |

**v42 Naming:**
- `AGI_DELTA_ARCHITECT_v42.md`
- `ASI_OMEGA_AUDITOR_v42.md`
- `APEX_PSI_JUDICIARY_v42.md`

---

## Track Separation

| Track | Location | Purpose |
|-------|----------|---------|
| **A** (Canon) | `canon/` | Immutable law (human-readable) |
| **B** (Spec) | `spec/v42/` | Versioned parameters (machine-readable) |
| **C** (Code) | `arifos_core/` | Runtime implementation |

**Rule:** Canon declares. Spec parameterizes. Code enforces.

---

## Forbidden Patterns

| Pattern | Reason | Alternative |
|---------|--------|-------------|
| `v38Omega` in folder | Version in filename only | `spec/v42/` |
| `ARIF`, `ADAM`, `AAA` | Legacy naming | Use Δ, Ω, Ψ |
| Mixed versions in same folder | Ambiguity | Archive old versions |
| Underscores in version | PEP 440 violation | `v42`, not `v42_0` |

---

## Spec File Naming

```
spec/v42/{concept}.{json|yaml}
```

**Examples:**
- `spec/v42/constitutional_floors.json`
- `spec/v42/genius_law.json`
- `spec/v42/pipeline.yaml`

**Note:** Spec files use `lowercase_snake_case`, canon uses `SCREAMING_SNAKE_CASE`.

---

## Archive Convention

Old versions move to:

```
archive/versions/v{MAJOR}/
├── canon/
└── spec/
```

**Example:** `archive/versions/v38/canon/01_CONSTITUTIONAL_FLOORS_v38Omega.md`

---

**DITEMPA BUKAN DIBERI** - Forged, not given; truth must cool before it rules.
