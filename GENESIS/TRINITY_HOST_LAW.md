# 🌐 TRINITY HOST LAW
> Constitutional canon for arifOS Federation web surface architecture  
> Sealed: 2026-07-15 · Sovereign: F13 (Arif)  
> Precedent: GEOX trinity split (geox.arif-fazil.com ↔ arif-fazil.com/geox)

---

## I. THE LAW

For every domain organ in the arifOS Federation, **two surfaces** are canonical:

| Surface | Host Pattern | Role | Audience |
|---|---|---|---|
| **Narrative Home** | `arif-fazil.com/<organ>` | Doctrine · Story · Essay · Human explainer | Humans |
| **Organ Kernel** | `<organ>.arif-fazil.com` | MCP endpoint · API · Status · Cockpit | Machines + Sovereign |

**These are NOT duplicates. They are complementary surfaces of one organ.**

---

## II. ROUTING LAWS

### A. Narrative Home (`arif-fazil.com/<organ>`)
- Serves the SPA narrative layer (React-rendered pages)
- Contains: doctrine, portfolio, public essays, MakcikGPT, about
- **MUST redirect** operational sub-paths OUT to the organ subdomain
- **MUST include** a visible CTA to the organ cockpit

### B. Organ Kernel (`<organ>.arif-fazil.com`)
- Serves the live MCP server + operational cockpit
- Contains: /mcp, /health, /api/*, static SPA cockpit
- **MUST redirect** narrative/story paths to the main site
- **MUST include** a footer link back to the narrative home
- **MUST NOT** redirect `/` to narrative home (breaks deploy probes + MCP discovery)

---

## III. APPLIED INSTANCES

### WEALTH (canonical as of 2026-07-15)
- Narrative Home: arif-fazil.com/wealth → Doctrine · MakcikGPT · Portfolio essays
- Organ Kernel: wealth.arif-fazil.com → MCP :18082 · market API :3457 · cockpit

### GEOX (existing precedent)
- Narrative Home: arif-fazil.com/geox → Basin stories · geology explainers
- Organ Kernel: geox.arif-fazil.com → MCP :8081 · seismic tools · cockpit

---

## IV. SEALED RECORD

```
Architect: F13 SOVEREIGN (Arif)
Forged by: Antigravity (Google Deepmind)
Date: 2026-07-15
Trigger: Chaos from two wealth surfaces without law
Precedent: GEOX trinity split
Status: SEALED
```

DITEMPA BUKAN DIBERI — Forged, not given.
