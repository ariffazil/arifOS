# @arifos/geox

**L2 Domain Package** — TypeScript surface for arifOS GEOX geoscience intelligence.

> **F4 CLARITY:** This package is **DOMAIN**, not **INFRA**.
> Transport, governance envelopes, and constitutional enforcement live in [`@arifos/mcp`](https://www.npmjs.com/package/@arifos/mcp).
> This package only provides geoscience-specific tools, types, and registration helpers.

---

## Installation

```bash
npm install @arifos/geox
# peer dependency
npm install @arifos/mcp @modelcontextprotocol/sdk
```

---

## Architecture

```text
┌─────────────────────────────────────────────┐
│  Your Application (JS/TS)                   │
│  ┌─────────────────────────────────────┐    │
│  │  @arifos/geox (Domain)              │    │
│  │  ├── types.ts   (geox schemas)      │    │
│  │  ├── tools.ts   (handlers)          │    │
│  │  ├── client.ts  (typed wrappers)    │    │
│  │  ├── register.ts (server binding)   │    │
│  │  └── governance.ts (6-layer gates)  │    │
│  └───────────┬─────────────────────────┘    │
└──────────────┼──────────────────────────────┘
               │ peer dependency
┌──────────────▼──────────────────────────────┐
│  @arifos/mcp (Infra / Cable)                │
│  ├── types.ts (RuntimeEnvelope, verdicts)   │
│  └── client.ts (MCP transport)              │
└─────────────────────────────────────────────┘
```

**Key Principle:** `@arifos/geox` imports from `@arifos/mcp`, never the reverse.

---

## Nobel-Grade AGI Earth Intelligence — 6 Layers

This package implements the 6 survival layers ratified by the sovereign.
Any subsurface AI missing any layer is a **toy**.

| Layer | Function | Export |
|-------|----------|--------|
| 1. Physics First | Hard locks: shale porosity, mass balance, Darcy sanity | `runPhysicsGuard()`, `DEFAULT_PHYSICS_LOCKS` |
| 2. Uncertainty | P10/P50/P90 mandatory on every quantitative claim | `createUncertaintyBand()`, `enforceUncertainty()` |
| 3. Anti-Hallucination | Cite well/seismic/core/report or say "UNKNOWN" | `auditHallucination()`, `enforceCitationOrUnknown()` |
| 4. Decision Firewall | 888_HOLD on drilling/reserves/barrier/well design | `applyDecisionFirewall()`, `isHighRiskDomain()` |
| 5. Multi-Discipline | Internal debate: geology vs geomech vs drilling | `runDisciplinePanel()` |
| 6. Trauma Memory | Remember Macondo, Montara, Piper Alpha | `scanTrauma()`, `TRAUMA_REGISTRY` |

---

## Quick Start

### Client-Side — Typed GEOX Wrappers

```typescript
import { createClient } from '@arifos/mcp';
import { createGeoxClient } from '@arifos/geox';

const mcp = await createClient({
  transport: 'http',
  endpoint: 'https://arifosmcp.arif-fazil.com/mcp',
});
await mcp.connect();

const geox = createGeoxClient(mcp);

// Pattern matching
const pattern = await geox.patternMatch({
  dataset: 'Well-A',
  pattern_type: 'coarsening_upward',
  curves: ['GR', 'RHOB'],
  depth_window: { top: 1500, base: 1550 },
});
console.log(pattern.payload.matches);

// Evidence reasoning
const reason = await geox.reason({
  phase: 'full',
  evidence: [
    { source: 'Well-A GR', observation: 'Fining upward', confidence: 0.85 },
    { source: 'Seismic-V1', observation: 'Bright spot', confidence: 0.7 },
  ],
  hypotheses: ['Channel fill', 'Shoreface progradation'],
});
console.log(reason.payload.abductions);

// Multi-source synthesis
const synthesis = await geox.synthesize({
  synthesis_type: 'prospect_summary',
  sources: [
    { source_id: 'Well-A', source_type: 'well', data: { porosity: 0.18 } },
    { source_id: 'Seismic-V1', source_type: 'seismic', data: { amplitude: 'bright' } },
  ],
});
console.log(synthesis.payload.gaps);
```

### Server-Side — Register GEOX Tools on an MCP Server

```typescript
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { registerTools } from '@arifos/geox';

const server = new McpServer({ name: 'geox-domain', version: '1.0.0' });

const registered = registerTools(server);
console.log('Registered:', registered);
// ['arif_geox_pattern_match', 'arif_geox_reason', 'arif_geox_synthesize']
```

### Direct Handler Invocation (No Transport)

```typescript
import { handlePatternMatch, handleReason, handleSynthesize } from '@arifos/geox';

const envelope = handlePatternMatch({
  dataset: 'Well-A',
  pattern_type: 'blocky',
});
console.log(envelope.verdict, envelope.payload.matches);
```

### Using the 6 Governance Layers Directly

```typescript
import {
  runPhysicsGuard,
  createUncertaintyBand,
  auditHallucination,
  applyDecisionFirewall,
  runDisciplinePanel,
  scanTrauma,
} from '@arifos/geox';

// Layer 1 — Physics lock
const physics = runPhysicsGuard({ porosity: 0.35, depth_m: 4000, lithology: 'shale' });
if (!physics.passed) console.error(physics.violations[0].message);

// Layer 2 — Uncertainty band
const band = createUncertaintyBand(320, 'MMstb', [
  { rank: 1, description: 'Fault seal', probability: 0.4 },
]);
console.log(`P10=${band.p10} P50=${band.p50} P90=${band.p90}`);

// Layer 3 — Hallucination audit
const audit = auditHallucination(['Channel fill'], [
  { source_type: 'well', source_id: 'A', observation: 'Channel fill', confidence: 0.8 },
]);
console.log('Clean:', audit.clean);

// Layer 4 — Decision firewall
const result = applyDecisionFirewall(envelope, 'drill');
if ('hold' in result) console.log('888_HOLD:', result.hold.domain);

// Layer 5 — Multi-discipline panel
const panel = runDisciplinePanel([
  { discipline: 'geology', claim: 'Good sand', confidence: 0.9, risk_flag: 'green' },
  { discipline: 'geomechanics', claim: 'Will collapse', confidence: 0.8, risk_flag: 'red' },
]);
console.log(panel.synthesis);

// Layer 6 — Trauma scan
const trauma = scanTrauma(['cement', 'deepwater']);
console.log(trauma.map((t) => t.name)); // ['Macondo']
```

---

## API Reference

### Tools

| Tool | Stage | Description |
| :--- | :--- | :--- |
| `arif_geox_pattern_match` | `111_SENSE` | Detect stratigraphic / geophysical patterns in logs or seismic |
| `arif_geox_reason` | `333_MIND` | Phase-driven evidence synthesis, abduction, contradiction scan |
| `arif_geox_synthesize` | `333_MIND` | Multi-source geoscience synthesis with gap detection |

### Client Methods (`GeoxClient`)

| Method | Input | Output |
| :--- | :--- | :--- |
| `geox.patternMatch(params)` | `PatternMatchInput` | `RuntimeEnvelope<PatternMatchResult>` |
| `geox.reason(params)` | `ReasonInput` | `RuntimeEnvelope<ReasonResult>` |
| `geox.synthesize(params)` | `SynthesizeInput` | `RuntimeEnvelope<SynthesizeResult>` |

### Server Registration

```typescript
registerTools(server: McpServerLike): GeoxToolName[]
```

Binds all three GEOX tools to any object conforming to the `McpServerLike` interface (e.g., the official MCP SDK `McpServer`).

---

## Error Handling

All handlers return `RuntimeEnvelope` with `verdict: "VOID"` and `ok: false` on validation failure. Client wrappers throw `ArifOSError` on transport or parsing errors (re-exported from `@arifos/mcp`).

---

## Development

```bash
# Install
npm install

# Build
npm run build

# Type check
npm run typecheck

# Test
npm test
```

---

## License

AGPL-3.0-only — Same as arifOS kernel.

---

## Links

- **arifOS Kernel:** <https://pypi.org/project/arifosmcp/>
- **@arifos/mcp:** <https://www.npmjs.com/package/@arifos/mcp>
- **Repository:** <https://github.com/ariffazil/arifos>
- **MCP Protocol:** <https://modelcontextprotocol.io>

*Ditempa Bukan Diberi* — Forged, Not Given
