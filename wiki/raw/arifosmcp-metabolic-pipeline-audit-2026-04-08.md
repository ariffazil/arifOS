# arifosmcp Metabolic Pipeline Audit

Audit date: 2026-04-08
Scope: `arifOS/arifosmcp/` runtime shell and public runtime docs

## Source excerpts

- `arifosmcp/README.md`
  - Defines `arifosmcp` as the runtime implementation and packaging shell that enforces the 13 Floors at runtime, runs the `000-999` pipeline, and delivers the mega-tools.
  - Documents `arifOS_kernel` as the primary metabolic orchestration tool at stage `444`.
  - States that the runtime shell exposes a Horizon mode and a VPS mode, with different tool surfaces.

- `arifosmcp/server.py`
  - The top-level entrypoint auto-detects environment and switches between `server_horizon.py` and `runtime/server.py`.
  - Horizon mode is described as a gateway or proxy policy layer; VPS mode attempts to load the full sovereign kernel.

- `arifosmcp/server_horizon.py`
  - Maps legacy Horizon tool names onto canonical v2 names such as `arifOS_kernel -> arifos_route`, `agi_mind -> arifos_mind`, and `vault_ledger -> arifos_vault`.
  - Describes `arifOS_kernel` as the `444_ROUTER` and the primary metabolic conductor.

- `arifosmcp/constitutional_map.py`
  - Defines the constitutional tool lattice as `000_VOID`, `111_ANCHOR`, `222_EXPLORE`, `333_AGI`, `444_KERNEL`, `555_FORGE`, `666_RASA`, `777_MATH`, `888_APEX`, `999_SEAL`.
  - Marks `kernel_444` as the primary conductor that routes the query through the pipeline.

- `arifosmcp/runtime/tool_specs.py`
  - Declares canonical runtime tools as `arifos_init`, `arifos_sense`, `arifos_mind`, `arifos_route`, `arifos_heart`, `arifos_ops`, `arifos_judge`, and additional tools later in the tuple.
  - Labels `arifos_route` as stage `444` with purpose `Execution lane selection`.

- `arifosmcp/runtime/server.py`
  - Documents the full MCP package as canonical tools plus prompts, resources, and manifest.
  - Establishes the runtime server as the FastMCP-hosted sovereign surface.

- `arifosmcp/runtime/bridge.py`
  - Calls `arifOS_kernel` the primary metabolic loop for governed execution.
  - Requires auth continuity for protected execution paths and points operators to `verify_vault_ledger` for audit integrity.

## Audit findings

1. The metabolic pipeline is not a single function. It is a layered control path spanning environment detection (`server.py`), Horizon/VPS dispatch (`server_horizon.py` vs `runtime/server.py`), canonical routing (`arifos_route` / `arifOS_kernel`), and final audit verification (`verify_vault_ledger`).
2. The pipeline uses both legacy and canonical names. Public-facing and compatibility surfaces still reference `arifOS_kernel` and `metabolic_loop_router`, while newer maps and tool specs converge on `arifos_route` / `arifos_route`.
3. The pipeline is stage-oriented rather than strictly linear for every tool. Public docs state the full `000-999` loop is always traversed by `arifOS_kernel`, while simpler tools may bypass the full path.

## Contradictions to surface

- Tool count drifts across sources.
  - `arifosmcp/README.md` says `11 mega-tools` in one section and `12 Mega-Tools` in another.
  - `arifosmcp/constitutional_map.py` says `10-tool mega-surface`.
  - `arifosmcp/runtime/tool_specs.py` says `10 sovereign tools` but the tuple continues beyond the first seven shown in the initial excerpt.
- Naming drifts across layers.
  - Canonical v2 naming uses dotted or underscored `arifos_*` forms.
  - Legacy or compatibility layers still expose `arifOS_kernel`, `metabolic_loop`, and `metabolic_loop_router`.

## Working interpretation

Use `Metabolic Pipeline` to mean the governed execution path that starts with session and environment anchoring, routes through constitutional stages, and terminates in verdict and seal logic. Treat `arifOS_kernel` / `arifos_route` as the main conductor, not the entirety of the pipeline.
