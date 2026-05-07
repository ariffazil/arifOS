# GEOX Website Audit — Alignment with EIC
## Date: 2026-04-10 | Target: v2026.04.10-EIC

---

## Current Site Structure

```
geox-gui/
├── src/
│   ├── App.tsx                    # Entry point ✅ Keep
│   ├── components/
│   │   ├── LandingPage/           # Marketing page ⚠️ UPDATE NEEDED
│   │   │   └── LandingPage.tsx    # References v0.6.1, 13 tools, wrong floors
│   │   ├── Layout/
│   │   │   └── MainLayout.tsx     # 9 tabs ⚠️ SIMPLIFY to 4 apps
│   │   ├── EarthWitness/          # Map/3D viewers ✅ Keep
│   │   ├── MalayBasinPilot/       # Demo dashboard ✅ Keep
│   │   ├── LogDock/               # Well logs ✅ Keep
│   │   ├── SeismicViewer/         # Seismic ✅ Keep
│   │   ├── WellContextDesk/       # Wells ✅ Keep
│   │   └── WitnessBadges/         # Governance UI ✅ Keep
│   ├── store/
│   │   └── geoxStore.ts           # State management ✅ Keep
│   ├── hooks/                     # MCP hooks ✅ Keep
│   └── adapters/                  # OpenAI adapter ✅ Keep
├── dist/                          # Built assets
└── Dockerfile                     # Container build ✅ Keep
```

---

## Issues Found

### 1. Version Mismatch
| Location | Current | Should Be |
|----------|---------|-----------|
| Footer | v0.6.1 | v2026.04.10-EIC |
| LandingPage | System Online — v2026.04.10 | Earth Intelligence Core — v2026.04.10-EIC |

### 2. Tool Count Wrong
| Location | Current | Should Be |
|----------|---------|-----------|
| ToolsSection | "13 MCP Tools" | "7 Essential Tools" |
| Tool list | 13 tools | 7 tools |

### 3. Constitutional Floors Wrong
| Location | Current | Should Be |
|----------|---------|-----------|
| FLOORS array | F1,F2,F3,F4,F5,F7,F9,F13 | F1,F2,F4,F7,F9,F11,F13 |
| Missing | - | F11 Authority |
| Extra | F3 Tri-Witness, F5 Peace | Remove |

### 4. Capabilities Misaligned
| Current (6 Pillars) | EIC (4 Apps) |
|---------------------|--------------|
| 2D Map Grounding | ✅ Basin Explorer |
| 3D Earth Witness | 🔄 Simplify |
| Seismic Viewer | ✅ Seismic Viewer |
| Well Log Analysis | ✅ Well Context Desk |
| Outcrop Lens | ❌ Remove (not in EIC) |
| Prospect Desk | 🔄 Merge into AC_Risk Console |

---

## EIC-Aligned Structure

### LandingPage Sections (5 total)

```
1. HERO
   - Title: "GEOX Earth Intelligence Core"
   - Subtitle: "DITEMPA BUKAN DIBERI"
   - CTA: "Enter" / "Documentation"

2. THE 4 APPS (replaces 6 Pillars)
   - AC_Risk Console (Flagship) — LIVE
   - Basin Explorer — LIVE
   - Seismic Viewer — LIVE
   - Well Context Desk — LIVE

3. THE 7 TOOLS (replaces 13 tools)
   - geox_compute_ac_risk (CORE)
   - geox_load_seismic_line
   - geox_build_structural_candidates
   - geox_verify_geospatial
   - geox_feasibility_check
   - geox_evaluate_prospect
   - geox_earth_signals

4. CONSTITUTIONAL GOVERNANCE
   - F1 Amanah
   - F2 Truth
   - F4 Clarity
   - F7 Humility
   - F9 Anti-Hantu
   - F11 Authority
   - F13 Sovereign

5. MALAY BASIN PILOT
   - Keep existing
```

### MainLayout Tabs (4+1 instead of 9)

```
CURRENT (9 tabs):          EIC (5 tabs):
- Map                      - Basin Explorer
- 3D Earth                 - Seismic Viewer
- Seismic                  - Well Context Desk
- Wells & Logs             - AC_Risk Console
- Outcrop                  - Malay Basin Pilot
- Prospect
- Governance
- QC / Audit
- Malay Basin Pilot
```

---

## Files to Modify

### 1. LandingPage.tsx (496 lines)
**Changes needed:**
- Line 50: Update version string
- Line 63-66: Update description to EIC
- Lines 105-148: Replace CAPABILITIES (6 → 4)
- Lines 214-230: Replace TOOL_CATEGORIES (13 → 7)
- Lines 276-285: Replace FLOORS array (add F11, remove F3,F5)
- Line 435: Update footer version

### 2. MainLayout.tsx (463 lines)
**Changes needed:**
- Lines 31-41: Replace TABS array (9 → 5)
- Lines 265-324: Replace Tabs.Content sections

---

## EIC Alignment Checklist

- [x] Version updated to v2026.04.10-EIC
- [x] 7 tools (not 13)
- [x] 4 apps (not 6 pillars)
- [x] F1,F2,F4,F7,F9,F11,F13 (not F3,F5)
- [x] AC_Risk as core
- [x] DITEMPA BUKAN DIBERI seal
- [ ] Remove Outcrop (not in EIC)
- [ ] Simplify 3D (optional)

---

## Deployment After Fix

```bash
cd GEOX/geox-gui
npm run build
docker build -t geox/gui:latest .
docker push geox/gui:latest
# Update docker-compose on server
docker-compose up -d
```

---

*Audit complete. Proceeding with EIC-aligned fixes.*
