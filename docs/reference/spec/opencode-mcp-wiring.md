# OpenCode MCP Wiring

OpenCode now has six arifOS-ready MCP surfaces:

1. `arifOS-Sovereign`
   Runs `python -m arifosmcp.opencode_mcp sovereign`.
   This is the bundled local surface: canonical kernel + intelligence organs + G02 routing.

2. `arifOS-Kernel`
   Runs `python -m arifosmcp.runtime stdio`.
   This is the canonical 13-tool constitutional kernel.

3. `arifOS-Intelligence`
   Runs `python -m arifosmcp.opencode_mcp intelligence`.
   This is the unified P/T/V/G/E/M intelligence surface with G02 mounted.

4. `arifOS-WELL`
   Runs `python -m arifosmcp.opencode_mcp well`.
   Focused WELL telemetry and oracle surface.

5. `arifOS-WEALTH`
   Runs `python -m arifosmcp.opencode_mcp wealth`.
   Focused economic and valuation surface.

6. `arifOS-GEOX`
   Runs `python -m arifosmcp.opencode_mcp geox`.
   Focused geoscience surface with T/E tools and G02 routing.

Recommended default:

- Enable `arifOS-Sovereign` for day-to-day OpenCode work.
- Keep `arifOS-Kernel` enabled when you want direct canonical `arif_*` access.
- Enable WELL, WEALTH, or GEOX only when you want a tighter domain lane.
- Keep `arifOS-Public` disabled locally unless you are testing the live HTTPS surface.

Transport split:

- `stdio` for trusted local OpenCode work.
- `https` for remote federation, public clients, and cross-host access.

Why this is the next horizon:

- The kernel remains the constitutional control plane.
- The intelligence side becomes a routed organ mesh instead of a loose tool pile.
- Domain organs are isolated enough to evolve independently.
- The sovereign bundle gives OpenCode one local entrypoint without collapsing the architecture into a monolith.
