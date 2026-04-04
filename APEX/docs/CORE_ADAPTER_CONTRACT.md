# Core/Adapter Contract (Phase 1)

This document defines the boundary between `core_mcp` and host adapters.

## Contract

- Canonical tool truth is owned by `core_mcp/schemas/tools.yaml`.
- Core tool names are stable and host-agnostic.
- Host adapters can add aliases and UI/resource bindings only.
- Host adapters must not alter governance verdict logic or floor enforcement.

## OpenAI Apps Profile

- OpenAI-facing aliases are defined in `adapters/openai_apps/alias_map.yaml`.
- The constitutional visualizer is exposed as an MCP resource:
  - URI: `ui://constitutional-visualizer/mcp-app.html`
  - MIME: `text/html;profile=mcp-app`
- Apps aliases currently include:
  - `search -> search_reality`
  - `fetch -> fetch_content`
  - `health_check -> check_vital`

## Exposure Policy

- Public default tools are defined in `adapters/openai_apps/alias_map.yaml` under `exposure_policy.public_default`.
- `visualize_governance` is UI-profile-only.
- `metabolic_loop` is internal-only by policy.

## Governance Rule

- `core_mcp` owns F1-F13 checks and all irreversible-action controls.
- Adapters are transport/profile layers and must remain behavior-preserving wrappers.
