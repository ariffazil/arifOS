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
│  │  └── register.ts (server binding)   │    │
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

## Tool Schemas

### `PatternMatchInput`

```typescript
interface PatternMatchInput {
  dataset: string;
  pattern_type: 'coarsening_upward' | 'fining_upward' | 'blocky' | ...;
  curves?: string[];
  depth_window?: { top: number; base: number };
  custom_pattern?: Record<string, unknown>;
  min_thickness?: number;
  session_id?: string;
}
```

### `ReasonInput`

```typescript
interface ReasonInput {
  phase: 'synthesize' | 'abduct' | 'contradict' | 'full';
  evidence: Array<{ source: string; observation: string; confidence: number; data_type?: ... }>;
  hypotheses?: string[];
  context?: Record<string, unknown>;
  session_id?: string;
}
```

### `SynthesizeInput`

```typescript
interface SynthesizeInput {
  synthesis_type: 'prospect_summary' | 'reservoir_characterization' | ...;
  sources: Array<{ source_id: string; source_type: ...; data: Record<string, unknown>; weight?: number }>;
  objective?: string;
  constraints?: { max_sources?: number; required_confidence?: number; exclude_uncertain?: boolean };
  session_id?: string;
}
```

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
