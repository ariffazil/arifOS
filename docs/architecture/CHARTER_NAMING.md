# Charter Naming Canon

Canonical rule: use `charter` as the singular term for authored declarative system truth in arifOS.

Use `charter` for:
- federation truth
- deployment truth
- kernel capability truth
- spec-level authored declarations

Do not rename these into `charter` because they are semantically different:
- `server.json` — protocol discovery document
- `registry.json` / `tool_registry.json` — registry surface
- `server-card.json` / `agent.json` — card/discovery surface
- `contract` — executable or policy contract

Active canonical files after unification:
- `federation.charter.json`
- `deploy/stack.charter.json`
- `config/charter/kernel.charter.yaml`
- `docs/reference/spec/mcp.charter.json`
- `docs/reference/spec/arif.charter.yaml`
- `arifosmcp/sites/apex-dashboard/federation.charter.json`
