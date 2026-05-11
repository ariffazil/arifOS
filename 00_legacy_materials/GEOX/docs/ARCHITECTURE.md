# GEOX Architecture — Earth Intelligence Core

**Version:** v2026.04.10-EIC
**For:** Operators, integrators, constitutional auditors

---

## 1. Design Philosophy

> "Perfection is achieved not when there is nothing more to add, but when there is nothing left to take away."
> — Antoine de Saint-Exupéry

**GEOX principles:**
1. **AC_Risk is the core** — Everything routes through ToAC
2. **7 tools, no more** — Essential functionality only
3. **Constitutional by default** — F1-F13 enforced everywhere
4. **MCP-native** — Built for AI agent integration
5. **Subtractive design** — Remove before adding

---

## 2. System Model

GEOX operates in **3 planes**:

```
┌─────────────────────────────────────────────────────────────────┐
│  PLANE 3: HUMAN / AI AGENT                                      │
│  (Claude Desktop, Copilot, Custom clients)                      │
└─────────────────────────────┬───────────────────────────────────┘
                              │ JSON-RPC (Streamable HTTP)
┌─────────────────────────────▼───────────────────────────────────┐
│  PLANE 2: MCP SERVER (Authority Layer)                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  • 7 essential tools                                    │   │
│  │  • AC_Risk calculation (ToAC)                           │   │
│  │  • Constitutional enforcement (F1-F13)                  │   │
│  │  • 888_HOLD gates                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              │ UI Resource URLs
┌─────────────────────────────▼───────────────────────────────────┐
│  PLANE 1: MCP APPS (Interactive UI Layer)                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ AC_Risk  │ │ Basin    │ │ Seismic  │ │ Well     │          │
│  │ Console  │ │ Explorer │ │ Viewer   │ │ Context  │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. The 7 Tools — Detailed

### 3.1 geox_compute_ac_risk (THE CORE)

**Purpose:** Calculate Theory of Anomalous Contrast risk score

**Input:**
```json
{
  "u_phys": 0.3,
  "transform_stack": ["linear_scaling", "agc_rms"],
  "bias_scenario": "ai_with_physics"
}
```

**Output:**
```json
{
  "ac_risk": 0.126,
  "verdict": "QUALIFY",
  "explanation": "AC_Risk=0.126: Moderate risk. Proceed with caveats.",
  "components": {
    "u_phys": 0.3,
    "d_transform": 1.15,
    "b_cog": 0.3
  }
}
```

**Floors:** F2 (Truth), F4 (Clarity), F7 (Humility)

---

### 3.2 geox_load_seismic_line

**Purpose:** Load seismic with F4 Clarity enforcement

**Key behavior:**
- Scale unknown → measurement tools disabled (888_HOLD)
- Units validated before any interpretation
- Provenance logged per F11

**Output:**
```json
{
  "line_id": "line_101",
  "scale": {
    "status": "UNKNOWN_PENDING_VALIDATION",
    "cdp_interval_m": null
  },
  "f4_clarity": {
    "units_validated": false,
    "warning": "Scale unknown — measurements disabled"
  }
}
```

---

### 3.3 geox_build_structural_candidates

**Purpose:** Generate multiple structural hypotheses

**Key behavior:**
- Never returns single model (F2 Truth)
- Confidence bounded at 12% (F7 Humility)
- Each candidate includes AC_Risk

**Output:**
```json
{
  "candidates": [
    {"rank": 1, "confidence": 0.12, "ac_risk": 0.25},
    {"rank": 2, "confidence": 0.10, "ac_risk": 0.30},
    {"rank": 3, "confidence": 0.09, "ac_risk": 0.35}
  ],
  "non_uniqueness_note": "Multiple interpretations exist per F2 Truth"
}
```

---

### 3.4 geox_verify_geospatial

**Purpose:** Coordinate grounding (F4 + F11)

**Key behavior:**
- Validates CRS (WGS84 default)
- Resolves geological province
- Logs to 999_VAULT

---

### 3.5 geox_feasibility_check

**Purpose:** Constitutional firewall

**Key behavior:**
- Checks plan against F1-F13
- Returns SEAL/QUALIFY/HOLD/VOID
- Grounding confidence score

---

### 3.6 geox_evaluate_prospect

**Purpose:** Prospect verdict with 888_HOLD

**Key behavior:**
- Blocks ungrounded claims (F9 Anti-Hantu)
- Triggers 888_HOLD if AC_Risk ≥ 0.60
- Requires human sign-off

---

### 3.7 geox_earth_signals

**Purpose:** Live temporal grounding

**Key behavior:**
- Fetches USGS earthquakes
- Open-Meteo climate data
- Validates temporal context (F2 Truth)

---

## 4. Constitutional Enforcement

### 4.1 Floor Implementation

| Floor | Enforcement Point | Failure Mode |
|-------|-------------------|--------------|
| F1 Amanah | Pre-execution logging | Operation blocked if logging fails |
| F2 Truth | All outputs include uncertainty | VOID verdict if uncertainty missing |
| F4 Clarity | Input validation layer | 400 error if units invalid |
| F7 Humility | Confidence caps in code | Hard limit at 15% |
| F9 Anti-Hantu | Physics validation layer | 888_HOLD if physically impossible |
| F11 Authority | Provenance chain required | Operation blocked if source unknown |
| F13 Sovereign | 888_HOLD gates | Human approval required for HOLD/VOID |

### 4.2 888_HOLD Mechanism

```python
if ac_risk >= 0.60:
    return {
        "verdict": "HOLD",
        "status": "888_HOLD",
        "requires_human_approval": True,
        "next_action": "Escalate to qualified interpreter"
    }
```

---

## 5. MCP App Architecture

### 5.1 App Manifest Structure

```json
{
  "app_id": "geox.ac_risk.console",
  "version": "1.0.0-EIC",
  "ui_entry": {
    "resource_uri": "https://geox.arif-fazil.com/apps/ac_risk_console/",
    "mode": "inline-or-external"
  },
  "arifos": {
    "required_floors": ["F1", "F2", "F4", "F7", "F9", "F11", "F13"],
    "vault_route": "999_VAULT"
  }
}
```

### 5.2 Event System

Apps communicate with MCP host via postMessage:

```javascript
// App → Host
window.parent.postMessage({
  type: 'ac_risk.calculated',
  data: { ac_risk: 0.25, verdict: 'QUALIFY' }
}, '*');

// Host → App
window.addEventListener('message', (e) => {
  if (e.data.type === 'set_parameters') {
    // Update UI with new parameters
  }
});
```

---

## 6. Data Flow

### 6.1 AC_Risk Calculation Flow

```
User Input
    ↓
[Schema Validation] → F4 Clarity check
    ↓
[AC_Risk Engine]
    ├─ U_phys validation
    ├─ D_transform calculation
    └─ B_cog selection
    ↓
[Verdict Determination]
    ├─ SEAL (< 0.15)
    ├─ QUALIFY (< 0.35)
    ├─ HOLD (< 0.60) → 888_HOLD gate
    └─ VOID (≥ 0.60)
    ↓
[Audit Logging] → 999_VAULT
    ↓
Response with AC_Risk + Verdict
```

### 6.2 Seismic Interpretation Flow

```
Load Seismic Line
    ↓
[F4 Clarity Check]
    ├─ Scale known? → Enable measurements
    └─ Scale unknown? → 888_HOLD (measurements disabled)
    ↓
Build Structural Candidates
    ├─ Generate 3+ models
    ├─ Apply F7 Humility (confidence ≤ 12%)
    └─ Calculate AC_Risk per candidate
    ↓
Evaluate Prospect
    ├─ Check physical grounding (F9)
    ├─ Apply 888_HOLD if needed
    └─ Log to 999_VAULT (F11)
    ↓
Governed Verdict
```

---

## 7. Deployment Patterns

### 7.1 Research Profile
- Single container
- Local data volume
- Human-in-the-loop enforced
- Docker Compose

### 7.2 Enterprise Profile
- 2+ MCP server replicas
- Redis caching layer
- Nginx reverse proxy + SSL
- CDN for MCP Apps
- Kubernetes-ready

---

## 8. Extension Points

**Adding a new tool:**
1. Add to `geox/core/tool_registry.py`
2. Implement in `geox/server.py`
3. Define error codes
4. Add constitutional floor mapping
5. Update tests

**Adding a new MCP App:**
1. Create `geox/apps/{app_name}/`
2. Build HTML/JS app
3. Create `manifest.json`
4. Add to nginx config
5. Update tool registry

---

## 9. Testing Strategy

### 9.1 Constitutional Tests

```python
def test_f7_humility_ceiling():
    """Confidence must never exceed 15%"""
    result = geox_build_structural_candidates(line_id="test")
    for c in result["candidates"]:
        assert c["confidence"] <= 0.15, "F7 Humility violated"

def test_f2_truth_uncertainty():
    """All outputs must include uncertainty"""
    result = geox_compute_ac_risk(u_phys=0.5, transform_stack=["linear"])
    assert "ac_risk" in result, "F2 Truth: uncertainty missing"

def test_888_hold_trigger():
    """AC_Risk >= 0.60 triggers HOLD"""
    result = geox_compute_ac_risk(u_phys=0.9, transform_stack=["vlm"])
    assert result["verdict"] == "VOID", "888_HOLD not triggered"
```

---

## 10. Glossary

| Term | Definition |
|------|------------|
| **AC_Risk** | Anomalous Contrast Risk — uncertainty metric |
| **ToAC** | Theory of Anomalous Contrast |
| **888_HOLD** | Human approval gate (F13 Sovereign) |
| **999_VAULT** | Immutable audit log |
| **MCP** | Model Context Protocol |
| **EIC** | Earth Intelligence Core |

---

*DITEMPA BUKAN DIBERI — Forged, Not Given*
