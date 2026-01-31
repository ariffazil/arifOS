# 🌍 Language Options for Kimi MCP

arifOS MCP supports multiple languages for Kimi integration.

---

## Available Languages

| Language | Code | File | Status |
|----------|------|------|--------|
| **English** | `en` | `../system_prompts/AI_CONSTITUTIONAL_PROMPT.txt` | ✅ Complete |
| **Chinese** | `zh` | `KIMI_PROMPT_ZH.txt` | ✅ Complete |
| **Malay** | `ms` | `KIMI_PROMPT_MS.txt` | ✅ Complete |

---

## Usage

### English
```python
await adapter.initialize_session(language="en")
# or
system_prompt = open("../system_prompts/AI_CONSTITUTIONAL_PROMPT.txt").read()
```

### Chinese
```python
await adapter.initialize_session(language="zh")
# or
system_prompt = open("KIMI_PROMPT_ZH.txt", encoding="utf-8").read()
```

### Malay
```python
await adapter.initialize_session(language="ms")
# or
system_prompt = open("KIMI_PROMPT_MS.txt", encoding="utf-8").read()
```

---

## Language Features

### Malay (Bahasa Malaysia)
- **Translation:** Complete 13 floors + 9 paradoxes
- **Cultural context:** Islamic constitutional concepts (Amanah)
- **Key terms:**
  - Minda (Mind) / Hati (Heart) / Jiwa (Soul)
  - Benar (Truth) / Adil (Justice) / Damai (Peace)
  - Ditempa Bukan Diberi (Forged, Not Given)

### Chinese (中文)
- **Translation:** Complete 13 floors + 9 paradoxes
- **Cultural context:** Philosophical balance concepts
- **Key terms:**
  - 心智 (Mind) / 心灵 (Heart) / 灵魂 (Soul)
  - 真理 (Truth) / 正义 (Justice) / 和平 (Peace)
  - 锻造而非给予 (Forged, Not Given)

### English
- **Original language:** All concepts in original form
- **Cultural context:** Western constitutional tradition
- **Key terms:**
  - Mind / Heart / Soul
  - Truth / Justice / Peace
  - DITEMPA BUKAN DIBERI

---

## Adding New Languages

To add support for a new language:

1. Create `KIMI_PROMPT_[CODE].txt`
2. Translate all 13 floors (F1-F13)
3. Translate 9 paradox matrix
4. Keep structural elements identical
5. Update `LANGUAGE_OPTIONS.md`

Template:
```
[Language Name] System Prompt
- 3 Layers architecture
- 13 Constitutional Floors
- 9-Paradox Matrix
- Tool usage instructions
- MUST NOT / MUST rules
- DITEMPA BUKAN DIBERI philosophy
```

---

## Auto-Detection

The adapter can auto-detect language:

```python
# Auto-detect and load appropriate prompt
if is_malay(query):
    prompt = KIMI_PROMPT_MS
elif is_chinese(query):
    prompt = KIMI_PROMPT_ZH
else:
    prompt = AI_CONSTITUTIONAL_PROMPT_EN
```

---

## Response Format

All languages use the same response format:

```
**CONSTITUTIONAL ASSESSMENT** | [Local Language]
---
VERDICT: SEAL | [Local Verdict]
TRINITY SCORE: 0.91 | [Local Score]

**PARADOX ANALYSIS** | [Local Analysis]
✓ Truth·Care: 0.95
...

---
[Response in user's language]

---
*Validated by arifOS*
```

---

## Cultural Adaptations

### Malay
- "Amanah" (F1) - Islamic concept of trust
- "Rendah Hati" (F7) - Malay humility concept
- Localized examples where appropriate

### Chinese
- Philosophical balance (Yin-Yang) references
- Harmony concepts in Peace paradox
- Respect for diversity in Unity paradox

### English
- Western constitutional tradition
- Universal human rights concepts
- Technical precision

---

**Semua bahasa disambut! 所有语言都欢迎! All languages welcome!**
