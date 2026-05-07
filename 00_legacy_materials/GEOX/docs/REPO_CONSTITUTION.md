# GEOX Repository Constitution 🔩

**Version:** 1.0.0
**Date:** 2026-04-12
**Status:** Canonical Law

---

## The Core Doctrine

This repository is unified under **One Contract, Multiple Planes**.
To prevent chaos, semantic drift, and uncontrolled branching, all code must adhere to strict folder boundaries. The repository is organized into distinct logical zones, and cross-contamination is strictly forbidden.

### 1. Contract Plane (`contracts/`)
**The Single Source of Truth.**
This folder defines the absolute public interface for GEOX. Nothing here depends on `fastmcp` or `vps` runtimes. It is the constitution.
- **Owns:** Canonical tool names, request schemas, artifact schemas, standard response envelopes, governance status enums, and the runtime parity matrix.
- **Rule:** If a feature or artifact is not defined here, it does not exist in GEOX.

### 2. Control Plane (`control_plane/`)
**The Showroom and Dashboard Router.**
This folder houses the FastMCP registry, app manifests, and dashboard APIs.
- **Owns:** Registry listings, MCP App manifests, UI metadata, capability discovery, and routing adapters.
- **Rule:** The control plane *must not* execute heavy geological or physical logic. It routes requests to the correct execution backend.

### 3. Execution Plane (`execution_plane/`)
**The Governed Engine Room.**
This folder houses the sovereign execution environment (e.g., VPS).
- **Owns:** Seismic volume processing, petrophysics compute, physical validation, and evidence-grounded operations.
- **Rule:** The execution plane *must not* define public API contracts. It merely implements the interfaces defined in the `contracts/` plane.

### 4. Domain Layer (`domain/`)
**The Science Logic.**
This folder holds the pure geological and physical logic.
- **Owns:** Prospect evaluation models, petrophysical equations, map projection math.
- **Rule:** Domain code is strictly scientific. It does not know about MCP, REST, or UI formatting.

### 5. Governance Layer (`governance/`)
**The Constitutional Logic.**
This folder enforces F1-F13 floors and the 888_HOLD logic.
- **Owns:** Verdict evaluation, bias checks, and operational halts.
- **Rule:** Governance code is decoupled from domain logic. It acts as an independent auditing wrapper.

### 6. Compatibility Zone (`compatibility/`)
**The Quarantine Area.**
This folder is the resting place for all legacy aliases, deprecated endpoints, and transitional mappings.
- **Owns:** Old `geox_` namespaces, deprecated flat return payloads.
- **Rule:** *No new features are born here.* This folder exists solely to prevent breaking existing integrations while they migrate to the canonical contracts.

---

## Unification Parity

- Both `GEOX-FastMCP` and `GEOX-VPS` runtimes **must** return the exact same `primary_artifact` shape for a given canonical tool.
- Both runtimes **must** wrap their responses in the canonical standard envelope defined in `contracts/enums/statuses.py` and `contracts/schemas/response/envelope.py`.
- Any discrepancy between the execution plane and control plane must be resolved in the adapter layers, ensuring the public contract remains immutable.

*DITEMPA BUKAN DIBERI — Forged, Not Given*
