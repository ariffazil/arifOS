# v36.3Ω Epoch Root

This directory (`v36.3O/`) is the **canonical epoch root** for arifOS v36.3Ω.

## Structure

```
v36.3O/
├── canon/          # Canonical documentation (PDFs, specs)
│   ├── 00_PHYSICS/
│   ├── 10_TRINITY/
│   ├── 20_JUDICIARY/
│   ├── 50_OVERSIGHT/
│   ├── 60_DREAMFORGE/
│   ├── 70_PARADOX/
│   ├── 80_CCC/
│   └── 90_GOV/
├── spec/           # JSON schemas, YAML specs
├── core/           # Core runtime modules
├── tests/          # Test suites
├── VAULT_999/      # Cooling Ledger + Vault data
├── tools/          # CLI tools, scripts
├── docs/           # Developer documentation
├── app/            # Application entry points
├── examples/       # Usage examples
└── legacy/         # Legacy migration staging
```

## Migration Status

- **Anything outside `v36.3O/`** is considered legacy until explicitly mapped/migrated.
- **No runtime behaviour has changed yet** — this is structure only.
- Files in `v36.3O/canon/` are copies; originals remain in place.

## Naming Convention

Canon files use normalized names:
- Spaces → hyphens
- Special characters removed
- Version suffix: `-v36.3O` (Ω represented as O for filesystem compatibility)

---

**Version:** v36.3Ω | **Status:** Structure Only | **Runtime Changes:** None

