# Public Surface Canon

The canonical contract is the eight-capability Kernel ABI in `abi/capability_registry.json`; MCP tool names are provider bindings, not constitutional identity.

| Semantic capability | MCP binding |
|---|---|
| `session.bind` | `arif_init` |
| `reality.observe` | `arif_observe` |
| `cognition.think` | `arif_think` |
| `intent.route` | `arif_route` |
| `memory.govern` | `arif_memory` |
| `authority.judge` | `arif_judge` |
| `action.execute` | `arif_forge` |
| `history.seal` | `arif_seal` |

The generated `public_agent` profile lists the first six bindings. `executor` adds `arif_forge`; `sovereign` adds `arif_seal`; `operator` may add diagnostics only behind the explicit development gate.

Legacy tool names resolve server-side and never appear in discovery. Provider or platform aliases such as `chatgpt` are migration inputs that normalize to `public_agent`; they do not change policy.

Run `python scripts/sync_kernel_abi.py --check` to prove that the profile snapshot, server card, compatibility manifest, Smithery manifest, and generated ABI documentation agree.
