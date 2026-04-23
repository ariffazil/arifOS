# @arifos/types

Shared types for arifOS ecosystem — constitutional governance OS.

## Structure

```
packages/arifos-types/
├── src/                    # TypeScript source (ES2022, NodeNext)
│   ├── index.ts
│   ├── epistemic.ts       # EpistemicTag enum
│   ├── verdict.ts         # Verdict enum
│   ├── telemetry.ts       # TelemetryPayload
│   ├── agent_message.ts  # AgentMessage A2A envelope
│   ├── floor_result.ts   # FloorResult F1-F13
│   └── resource_node.ts  # ResourceNode 4-layer kernel
├── py/                    # Python mirror (Pydantic v2)
│   ├── arifos_types/
│   └── pyproject.toml
├── package.json
└── tsconfig.json
```

## Usage

### TypeScript
```typescript
import { ResourceNode, EpistemicTag, Verdict } from "@arifos/types";
```

### Python
```python
from arifos_types import ResourceNode, EpistemicTag, Verdict
```

## DITEMPA BUKAN DIBERI