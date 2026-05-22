# Aligned Agent Naming Canon

To eliminate role drift and taxonomy fragmentation, all agents must adhere to this naming convention:

---

## 1. L5 Governance Agents (Roles)

All high-authority constitutional roles inside the `arifOS` core must be prefixed with `A-` and capitalized according to their structural domain:

- **A-ARCHITECT:** Design and blueprinting only (strictly read-only/no-execution).
- **A-AUDITOR:** Fact verification and security audit (assumes breach).
- **A-ENGINEER:** Active code implementation and mutation (governed under 888_HOLD).
- **A-ORCHESTRATOR:** Process choreographer (no-bypass, workflow sequence).
- **A-VALIDATOR:** Claim and evidence verifier.

---

## 2. L3 Specialist Agents (Organs)

Domain-specific assistants or local tool interfaces use standard lowercase names representing their specific focus:

- **opencode:** The primary terminal/IDE coding specialist.
- **apex:** The wisdom and long-term memory engine.
- **kimi-cli:** The local cockpit CLI developer interface wrapper.
- **clerk:** The constitutional IDE integration helper (Antigravity/Claude Code).

---

## 3. Tool Names (MCP Surface)

All tools exposed via the Model Context Protocol (MCP) must follow the standard snake_case naming pattern:

`<domain>_<verb>_<noun>` (e.g., `arif_session_init`, `geox_well_compute_gr_bins`, `wealth_time_discount`).
