# The 9 Mottos — Stage Meta-Transformer System

**Version:** v60.0-FORGE  
**Philosophy:** Each stage outputs its own motto based on the transformation it performs.

---

## Concept

Instead of outputting "DITEMPA BUKAN DIBERI" everywhere, each 000-999 stage outputs **its own motto** as a **meta-transformer**. The motto reflects the specific transformation occurring at that stage.

---

## The 9 Mottos Mapped to Stages

| Stage | Motto | Meaning | Floor |
|-------|-------|---------|-------|
| **000_INIT** | **DITEMPA, BUKAN DIBERI** | Forged, not given | F1 Amanah |
| **111_SENSE** | **DIKAJI, BUKAN DISUAPI** | Examined, not assumed | F2 Truth |
| **222_THINK** | **DIJELAJAH, BUKAN DISEKATI** | Explored, not restricted | F4 Clarity |
| **333_REASON** | **DIJELASKAN, BUKAN DIKABURKAN** | Clarified, not obscured | F4 Clarity |
| **444_SYNC** | **DIHADAPI, BUKAN DITANGGUHI** | Faced, not postponed | F3 Tri-Witness |
| **555_EMPATHY** | **DIDAMAIKAN, BUKAN DIPANASKAN** | Calmed, not inflamed | F5 Peace² |
| **666_ALIGN** | **DIJAGA, BUKAN DIABAIKAN** | Guarded, not neglected | F6 Empathy |
| **777_FORGE** | **DIUSAHAKAN, BUKAN DIHARAPI** | Worked, not hoped | F8 Genius |
| **888_JUDGE** | **DISEDARKAN, BUKAN DIYAKINKAN** | Aware, not over-assured | F7 Humility |
| **999_SEAL** | **DITEMPA, BUKAN DIBERI** | Forged, not given | F1 Amanah |

---

## Rhythmic Structure

### Positive Declarations (All end in -I):
```
DITEMPA, DIKAJI, DIJELAJAH, DIJELASKAN, DIHADAPI, DIDAMAIKAN, DIJAGA, DIUSAHAKAN, DISEDARKAN
```

### Negative Negations (All end in -I):
```
BUKAN DIBERI, BUKAN DISUAPI, BUKAN DISEKATI, BUKAN DIKABURKAN, BUKAN DITANGGUHI, BUKAN DIPANASKAN, BUKAN DIABAIKAN, BUKAN DIHARAPI, BUKAN DIYAKINKAN
```

---

## Implementation

### Core Module
```python
from core.shared.mottos import get_motto_for_stage

# Get motto for any stage
motto = get_motto_for_stage("000_INIT")  # DITEMPA, BUKAN DIBERI
motto = get_motto_for_stage("888_JUDGE")  # DISEDARKAN, BUKAN DIYAKINKAN

# Access components
motto.positive   # "DITEMPA"
motto.negative   # "BUKAN DIBERI"
motto.meaning    # "Forged, Not Given"
motto.floor      # "F1 Amanah"
```

### MCP Tool Output
Each tool now outputs:
```json
{
  "stage": "000_INIT",
  "motto": "DITEMPA, BUKAN DIBERI",
  "motto_positive": "DITEMPA",
  "motto_negative": "BUKAN DIBERI",
  "meaning": "Forged, Not Given"
}
```

---

## Files Modified

1. **`core/shared/mottos.py`** (NEW) — Central motto registry
2. **`core/organs/_0_init.py`** — SessionToken includes motto
3. **`core/pipeline.py`** — Stage motto tracking
4. **`aaa_mcp/server.py`** — All 13 tools output stage-specific mottos

---

## Visual Pipeline

```
000_INIT      DITEMPA, BUKAN DIBERI          [Ignition]
    ↓
111_SENSE     DIKAJI, BUKAN DISUAPI          [Examination]
    ↓
222_THINK     DIJELAJAH, BUKAN DISEKATI      [Exploration]
    ↓
333_REASON    DIJELASKAN, BUKAN DIKABURKAN   [Clarification]
    ↓
444_SYNC      DIHADAPI, BUKAN DITANGGUHI     [Confrontation]
    ↓
555_EMPATHY   DIDAMAIKAN, BUKAN DIPANASKAN   [Calming]
    ↓
666_ALIGN     DIJAGA, BUKAN DIABAIKAN        [Protection]
    ↓
777_FORGE     DIUSAHAKAN, BUKAN DIHARAPI     [Work]
    ↓
888_JUDGE     DISEDARKAN, BUKAN DIYAKINKAN   [Awareness]
    ↓
999_SEAL      DITEMPA, BUKAN DIBERI          [Foundation]
```

---

## Usage in Error Messages

When a floor fails, the system can output the relevant motto:

```
⚠️ F2 Truth Floor Failed
Query increases uncertainty without clarification.
DIJELASKAN, BUKAN DIKABURKAN.
Please refine your query before proceeding.
```

---

## DITEMPA BUKAN DIBERI 💎🔥🧠

*Forged through 000-999 pipeline, not given.*
