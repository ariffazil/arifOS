# Changelog — arifOS Kernel

All notable changes to the arifOS constitutional kernel.

## [Unreleased]

## [2026-10-22] External Footprint & Epistemic Demarcation

### Added
- External Footprint Register (`docs/EXTERNAL_FOOTPRINT.md`) and Canonical External Witness Ledger (`docs/EXTERNAL_WITNESS_LEDGER.md`).
- Verified External Footprint classification (Tier W1 Public Registries, Tier W2 Independent Catalogs).
- Candidate Independent References section (Tier W3: Agentrust, Tom Rochette, Hapax Systems).
- Public discovery status disclosures across `mcp.arif-fazil.com`, `llms.txt`, and `claims.json`.
- Disproof and Rejection Log tracking falsified/unverified claims as an anti-cult invariant.

### Changed
- Explicit distinction enforced across public surfaces:
  - Discoverability ≠ Validation
  - Indexing ≠ Endorsement
  - Mention ≠ Adoption
  - Claim ≠ Evidence
- Replaced self-referential positioning with observable public discovery metrics.

### Preserved
- No constitutional floor changes (F1–F13 unchanged).
- No MCP wire protocol changes.
- No authority model changes.
- No execution pathway changes.

### Open Gaps
- Independent verifier kit not yet bound into continuous CI (Open Gap 4).
- Academic peer review not yet established.
- Third-party reproduction pipeline incomplete.

### Added
- Theory of Operating System academic paper (LaTeX + PDF)
- Enhanced federation state reporting (`now` command)

### Changed
- Dropped dead `master` branch triggers — fleet unified to `main`
- Package version bumped `1!2026.9.6` → `1!2026.10.1` (first October epoch release; version surfaces synced: pyproject, well-known server card, README SOT-MANIFEST)

### Fixed
- APEX doctrine alignment (2026-10-04): HOLD floor restored to `G < 0.50` in A-FORGE runtime receipts; quote fingerprint dual-schema reads (nested v2 canonical, flat v3 fallback) — flat-only reads collapsed every nested quote to `G = 0.0`; Pillar VI `missing_prohibited` shadow restored per sealed federation contract; `APEXResult` terminal-metadata field order; wisdom namespace 9-URI federation contract restored (`quotes/disputed`, `quotes/arifos-doctrine`, `quotes/prohibited-uses`)

### Security
- All constitutional floors (F1–F13) active and passing
- VAULT999 immutable ledger: 67K+ sealed outcomes, 0 broken lines

## [2026.08.25] — Federation Release v2026.08.25

### Added
- ZEN first-fold integration
- Federation card documentation
- MCP dual-stack compatibility

### Changed
- README restructured with ZEN-first approach
- 48 total declared tools (8 public + 13 internal + 27 diagnostic)

## [2026.07.19] — Constitutional Hardening

### Added
- F13 sovereign ratification packet
- JWT enforcement migration
- Yubikey procurement process

### Changed
- Judge payload schema finalized (T0-T4)
- Kernel capability ABI defined

## [2026.06.02] — Federation v2.0

### Added
- Separation of powers thesis
- MCP endpoint registry
- A2A integration layer

### Changed
- Caddy F7 context normalization
- MCP auth design overhaul
