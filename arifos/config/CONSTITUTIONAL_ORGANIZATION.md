# arifOS v49.1 - Constitutional Configuration Organization

**Authority:** 888 Judge | **Status:** SOVEREIGNLY_SEALED | **Motto:** *DITEMPA BUKAN DIBERI*

## Constitutional Hierarchy

This directory contains the **BBB (Machine Memory)** layer implementation of constitutional law from `000_THEORY/` (CCC layer).

### Constitutional Chain of Authority
```
888 Judge (Human Sovereign)
    ↓
000_THEORY/ (CCC - Constitutional Canon Core)
    ↓
config/ (BBB - Machine Memory Implementation)
    ↓
Runtime Systems (AAA - Human Agency Protection)
```

## Directory Structure

### `config/infrastructure/` - Constitutional Runtime Implementation
- **docker-compose.yml**: 4-Server constitutional runtime (AGI/ASI/APEX/VAULT)
- **docker-compose-vault999.yml**: VAULT-999 memory infrastructure (Postgres/Redis/Qdrant)
- **Authority**: Implements constitutional architecture from `000_THEORY/000_ARCHITECTURE.md`
- **Floors**: F2 (Truth), F4 (DeltaS), F7 (Omega0), F10 (Coherence)

### `config/governance/` - Constitutional Code Quality Enforcement
- **pre-commit-config.yaml**: F1-F13 floor enforcement through automated validation
- **Authority**: Implements governance from `000_THEORY/000_LAW.md`
- **Floors**: All F1-F13 constitutional floors enforced

### `config/deployment/` - Constitutional Deployment Configuration
- **render.yaml**: Production deployment configuration
- **Authority**: Implements deployment governance from constitutional specifications

## Root-Level Constitutional Anchors

The root directory contains **constitutional entry points** that delegate to canonical implementations:

- **docker-compose.yml**: Entry point referencing `config/infrastructure/`
- **.arifos_version_lock.yaml**: Entry point referencing `L1_THEORY/canon/`
- **.pre-commit-config.yaml**: Entry point referencing `config/governance/`

These anchors maintain constitutional separation while providing familiar interfaces.

## Cross-References

All configurations reference the constitutional canon:
- Infrastructure → `000_THEORY/000_ARCHITECTURE.md`
- Governance → `000_THEORY/000_LAW.md` (F1-F13)
- Version State → `L1_THEORY/canon/arifos_version_lock.yaml`

## Constitutional Compliance

This organization ensures:
1. **CCC/BBB/AAA Separation**: Clear layer boundaries
2. **Authority Chain**: 888 Judge → Canon → Implementation → Runtime
3. **Immutability**: Constitutional canon remains unchanged
4. **Auditability**: All changes tracked through governance layer
5. **Reversibility**: Can rollback through constitutional mechanisms

---

**DITEMPA BUKAN DIBERI** - Configuration is forged through constitutional law, not assumed through convenience.