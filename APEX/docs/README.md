# docs/ README

> **Documentation Layer for arifOS**

---

## 🧭 Repository Identity: The Trinity

| Repository | Role | Purpose |
|:-----------|:-----|:--------|
| [**arifOS**](https://github.com/ariffazil/arifOS) | **THE MIND** | Theory, Constitution, Canonical Law |
| [**arifosmcp**](https://github.com/ariffazil/arifosmcp) | **THE BODY** | Runtime MCP server, Execution |
| [**ariffazil**](https://github.com/ariffazil/ariffazil) | **THE SURFACE** | Human professional portal, Interface |

---

`docs/` is the operational documentation layer for arifOS. Use it to understand runtime behavior, endpoint usage, deployment, and maintenance workflows without digging through source code first.

## Where to start

- Start at the root `README.md` for project orientation and install commands.
- Use `docs/60_REFERENCE/ARCHITECTURE.md` for system boundaries and layer ownership.
- Use `docs/60_REFERENCE/TOOLS_CANONICAL_13.md` for canonical tool behavior and contracts.
- Use `docs/60_REFERENCE/DEPLOYMENT.md` for VPS and runtime deployment steps.

## Endpoint surfaces

Use one endpoint surface per session.

| Surface | Purpose | Use when |
| --- | --- | --- |
| `/` | Canonical 13-tool surface | Default for governed sessions and standard clients |
| `/mcp` | Runtime MCP protocol surface | Your client expects MCP runtime protocol routing |
| `/tools` | Full capabilities with compatibility shims | You need extended tools or legacy/client compatibility |

Recommended session order:

1. `anchor_session`
2. `reason_mind` and/or `simulate_heart` and/or `critique_thought`
3. `apex_judge`
4. `seal_vault`

## Authoring rules

- Use date-based labels for active architecture and seal references: `YYYY.MM.DD[-SUFFIX]`.
- Do not reintroduce semantic version labels in active docs.
- Treat `core/shared/floors.py` as the single canonical source for floor thresholds and definitions.
- If docs disagree with code, update docs to match runtime behavior and source constants.

## Quick docs maintenance checklist

- Confirm endpoint descriptions match current server routes and behavior.
- Verify tool names and call order against canonical MCP surface.
- Check floor names/thresholds against `core/shared/floors.py`.
- Ensure examples use current commands and valid paths.
- Run docs site build before merging: `npm run build` in `sites/docs`.
