# L6_SEALION — SEA-LION Chat Integration

**Layer:** L6
**Purpose:** SEA-LION model integration with governed chat interface
**License:** AGPL-3.0

---

## What Lives Here

| Directory | Contents |
|-----------|----------|
| `arifos_sealion/` | Main SEA-LION package |
| `arifos_sealion/integrations/` | Model adapters and engines |
| `arifos_sealion/ui/` | UI components |
| `arifos_sealion/localization/` | Language files (EN, MS) |
| `tests/` | SEA-LION-specific tests |

---

## Features

- **Governed Chat:** All responses pass through APEX PRIME judiciary
- **Bilingual:** English and Bahasa Malaysia support
- **Web UI:** Streamlit-based chat interface
- **REST API:** FastAPI endpoints for integration

---

## Dependency Rules

```
L6_SEALION ← L7_DEMOS may showcase SEA-LION
           → Imports from L3_KERNEL (arifos_core)
           → May use L4_MCP tools
           → May use L5_CLI utilities
           → NEVER imports from L7_DEMOS
```

---

## Usage

```bash
# Install
pip install arifos

# Terminal chat
arifos-chat

# Web UI (Streamlit)
arifos-web

# Or run directly
python -m arifos_sealion.chat
python -m arifos_sealion.web_ui
```

---

## Localization

| File | Language |
|------|----------|
| `localization/en.yaml` | English |
| `localization/ms.yaml` | Bahasa Malaysia |

---

## SEA-LION Model

SEA-LION is a Southeast Asian language model optimized for:
- Bahasa Malaysia
- Bahasa Indonesia
- Thai
- Vietnamese
- Other SEA languages

arifOS wraps SEA-LION with constitutional governance to ensure safe, honest, and culturally appropriate responses.

---

## Test Archive

**Complete test suite consolidated:** All SEA-LION test and demo scripts are archived in:

- [tests_consolidated/](tests_consolidated/) - Complete test suite archive (15 files)

See [tests_consolidated/README.md](tests_consolidated/README.md) for complete index and run instructions.

**Active test suite** remains in:

- `tests/` - Current test suite (7 files)

**Organization:**

- `tests_consolidated/unit_tests/` - Unit & integration tests (8 files)
- `tests_consolidated/demos/` - Full demonstrations (3 files)
- `tests_consolidated/integration_examples/` - Integration patterns (4 files)

---

**DITEMPA BUKAN DIBERI** — Governed intelligence for Southeast Asia.
