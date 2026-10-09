# Release Integrity — SBOM & Signing Requirements

> Tracks the supply-chain side of `threat-model.md`. Current claim:
> CLAIM-003 in `claims.yaml` (CycloneDX SBOM = verified, with limitations).

## Current State (2026-09-16)
- **SBOM generation**: `arifosmcp/arifos_sbom.py` — CycloneDX format — ACTIVE
- **CI attachment**: `.github/workflows/07-publish-pypi.yml` `sbom` job — ACTIVE
- **CVE scanning**: none (Phase 2)
- **Signed releases**: none yet

## SBOM Requirements
1. Every PyPI publish must emit a CycloneDX SBOM (JSON) as a build artifact.
2. SBOM must list all runtime dependencies with resolved versions and hashes.
3. SBOM generation failure must fail the publish job — never degrade silently.

## Signing Requirements (to close the "No signed releases yet" gap)
1. Artifacts (wheel + sdist + SBOM) signed at publish time.
2. Signature + provenance attestation published alongside the release.
3. Public verification instructions added to `docs/QUICKSTART.md`.
4. Signing key material never enters the repo or VAULT999 (5-R protocol).

## Phase 2 (CVE Scanning)
1. SBOM scanned against a vulnerability feed on every publish.
2. Known-exploitable findings block the release or require a recorded waiver.

## Evidence Thresholds
| Claim | Minimum Proof |
|---|---|
| "Releases are SBOM-covered" | SBOM artifact present on every release run (met) |
| "Releases are verifiable" | Third party verifies a signature without maintainer help |
| "Releases are CVE-screened" | Scan report attached to release, zero unwaived exploitables |
