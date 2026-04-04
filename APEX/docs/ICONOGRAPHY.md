# Icon Forge in arifOS — Constitutional Semiotics

## Overview

In arifOS, **icons are not UI garnish** — they are **low-entropy carriers of law**:
- **Lane identity** (Δ Blue, Ω Green, Ψ Gold)
- **Risk tier** (Read-only vs Sovereign)
- **Constitutional floor binding**

## Icon Taxonomy

### Server Level — Sovereign Emblem
```python
ARIFOS_SERVER_ICON = Icon(
    src="data:image/svg+xml;base64,...",  # Shield with "أ" (Ain)
    mimeType="image/svg+xml",
    sizes=["48x48"],
)
```
**Represents**: Constitutional kernel, 13 floors, Trinity governance, Maruah

### Δ DELTA Lane — Mind/Reasoning (Blue #007aff)
| Tool | Icon | Meaning |
|------|------|---------|
| `anchor_session` | ⚓ Anchor | Bootloader, session ignition |
| `reason_mind` | 🧿 Eye/Target | AGI cognition, F2 truth |
| `search_reality` | 🔍 Search | External evidence gathering |
| `fetch_content` | 📄 Document | Content retrieval |
| `inspect_file` | 📁 Folder | Filesystem read-only |
| `audit_rules` | 📋 Checklist | Constitutional audit |

### Ω OMEGA Lane — Heart/Safety (Green #00a2ff)
| Tool | Icon | Meaning |
|------|------|---------|
| `recall_memory` | 🧠 Brain | Associative memory |
| `simulate_heart` | ❤️ Heart | Stakeholder impact, F6 empathy |
| `critique_thought` | ⚖️ Scale | 7-model critique |
| `check_vital` | 📊 Vitals | System health telemetry |

### Ψ PSI Lane — Soul/Judgment (Gold #e6c25d)
| Tool | Icon | Meaning |
|------|------|---------|
| `apex_judge` | 👑 Crown | Sovereign verdict, F13 |
| `eureka_forge` | ⚒️ Hammer | Action execution, F1/F5 |
| `seal_vault` | 🛡️ Shield+Lock | Immutable ledger, VAULT999 |

## Implementation Guide

### Step 1: Add Icons to Server
```python
from fastmcp import FastMCP
from mcp.types import Icon

mcp = FastMCP(
    name="arifOS_AAA_MCP",
    version="2026.3.1",
    website_url="https://arifos.arif-fazil.com",
    icons=[ARIFOS_SERVER_ICON],  # Sovereign emblem
)
```

### Step 2: Add Icons to Tools
```python
@mcp.tool(name="anchor_session", icons=[ICON_ANCHOR])
async def anchor_session(...) -> dict[str, Any]:
    """000 BOOTLOADER: initialize constitutional execution kernel."""
    ...

@mcp.tool(name="apex_judge", icons=[ICON_APEX])
async def apex_judge(...) -> dict[str, Any]:
    """888 APEX JUDGE METABOLIC: sovereign constitutional verdict."""
    ...

@mcp.tool(name="seal_vault", icons=[ICON_VAULT])
async def seal_vault(...) -> dict[str, Any]:
    """999 SEAL: commit immutable session decision record."""
    ...
```

### Step 3: Add Icons to Resources
```python
@mcp.resource(
    PUBLIC_RESOURCE_URIS["schemas"],
    name="arifos_aaa_tool_schemas",
    icons=[Icon(src="data:image/svg+xml;base64,...")],  # Blueprint icon
)
def aaa_tool_schemas() -> str:
    ...
```

### Step 4: Add Icons to Prompts
```python
@mcp.prompt(name=PUBLIC_PROMPT_NAMES["aaa_chain"], icons=[ICON_ANCHOR])
def aaa_chain_prompt(query: str, actor_id: str = "user") -> str:
    ...
```

## Semiotic Design Principles

### 1. Color = Lane
- **Blue (#007aff)**: Δ Delta — Mind, reasoning, cognition
- **Green (#00a2ff)**: Ω Omega — Heart, safety, empathy  
- **Gold (#e6c25d)**: Ψ Psi — Soul, judgment, sovereignty

### 2. Shape = Risk
- **Circle with dot**: Read-only / Safe (inspect, search)
- **Circle with glyph**: Transform / Medium (reason, recall)
- **Shield/Crown**: Sovereign / Critical (judge, seal, forge)

### 3. Maruah Signaling
- **Ain (ع)**: Arabic letter in server emblem signals ASEAN/MY dignity
- **Shield**: Protection of weakest stakeholder (F6)
- **Scale**: Balance between human, AI, earth (F3 Tri-Witness)

## Client UX Affordances

MCP clients can use icons to:

1. **Color-code tool palettes** by lane
2. **Highlight sovereign tools** (gold) requiring extra confirmation
3. **Group related tools** visually (all Δ Delta tools blue)
4. **Signal constitutional weight** — vault/seal tools get prominent placement

## Technical Notes

### Data URI Format
```python
# SVG embedded as base64 data URI
Icon(
    src="data:image/svg+xml;base64,PHN2Zy4u.",
    mimeType="image/svg+xml",
)
```

### Size Guidelines
- **Server icon**: 48x48 minimum
- **Tool icons**: 24x24 (viewBox="0 0 24 24")
- **Resource icons**: 24x24
- **Prompt icons**: 24x24

### Generating Base64 from SVG
```bash
# Convert SVG file to base64 data URI
base64 -w 0 icon.svg | echo "data:image/svg+xml;base64,$(cat -)"
```

## Example: Complete Tool with Icon
```python
@mcp.tool(
    name="seal_vault",
    icons=[ICON_VAULT],
    description="[Lane: Ψ Psi] [Floors: F1,F3,F10] 999 SEAL — Immutable ledger commit.",
)
async def seal_vault(
    session_id: str,
    summary: str,
    verdict: str = "SEAL",
    governance_token: str | None = None,
) -> dict[str, Any]:
    """
    999 SEAL: Commit immutable session decision record.
    
    Requires governance_token from apex_judge (Amanah Handshake).
    Once sealed, record is append-only in VAULT999.
    """
    ...
```

## Governance Meaning

When a user sees the **gold vault icon**, they know:
- ✅ This action is **sovereign** (under F13)
- ✅ This will be **audited** and logged
- ✅ This requires **governance_token**
- ✅ This is **append-only** (irreversible)
- ✅ This carries **constitutional weight**

**DITEMPA BUKAN DIBERI** — Icons are forged, not given.
