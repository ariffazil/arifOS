# arifOS Notebooks

Google Colab notebooks for testing arifOS constitutional governance.

## Available Notebooks

### arifOS_SEALION_7_Modes_v36.ipynb

**SEA-LION + arifOS Reality Test** - 7 Modes demonstrating Python-sovereign governance.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ariffazil/arifOS/blob/main/notebooks/arifOS_SEALION_7_Modes_v36.ipynb)

#### The 7 Modes

| Mode | Name | Purpose |
|------|------|---------|
| 1 | Setup & Clone | Install dependencies, clone arifOS |
| 2 | Vanilla SEA-LION | Raw HuggingFace text generation (no governance) |
| 3 | arifOS Judge | Feed any text through governance |
| 4 | GENIUS LAW Tests | 4 tests: G, C_dark, Amanah, Anti-Hantu |
| 5 | Side-by-Side | Compare vanilla vs governed for same prompt |
| 6 | Engine Modes | Mock engine + optional real API |
| 7 | Interactive Chat | Switch between vanilla and governed chat |

#### Requirements

- **Runtime**: GPU recommended (T4 free tier works)
- **No API keys required** for Modes 1-5, 7
- **Optional**: SEA-LION API key for Mode 6 real API

#### Key Insight

> **Same model. Same prompts. Different behavior.**
>
> SEA-LION is a capable regional LLM.
> arifOS is what makes it lawful.

---

### arifOS_SEALION_Qwen32B_7_Modes_v36.ipynb

**Qwen-SEA-LION 32B + arifOS Reality Test** - 7 Modes with the larger Qwen-based model.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ariffazil/arifOS/blob/main/notebooks/arifOS_SEALION_Qwen32B_7_Modes_v36.ipynb)

#### Model Details

- **HuggingFace ID:** `aisingapore/Qwen-SEA-LION-v4-32B-IT`
- **Architecture:** Qwen-based (different from Llama-based)
- **Size:** 32B parameters
- **GPU Requirement:** A100 (40GB+) recommended

#### The 7 Modes

Same structure as the 8B notebook:

| Mode | Name | Purpose |
|------|------|---------|
| 1 | Setup & Clone | Install dependencies, clone arifOS |
| 2 | Vanilla Qwen-SEA-LION | Raw HuggingFace text generation (32B model) |
| 3 | arifOS Judge | Feed any text through governance |
| 4 | GENIUS LAW Tests | 4 tests: G, C_dark, Amanah, Anti-Hantu |
| 5 | Side-by-Side | Compare vanilla vs governed for same prompt |
| 6 | Engine Modes | Mock engine + optional real API |
| 7 | Interactive Chat | Switch between vanilla and governed chat (opt-in) |

#### Key Differences from 8B Notebook

- **Larger model** (32B vs 8B) = more capable, but requires A100
- **Different architecture** (Qwen vs Llama) = different behavior
- **Same governance** = PHOENIX SOVEREIGNTY applies equally
- **Dynamic mock mode** = automatically uses mock on CPU

#### APEX Metrics Quick Reference

| Metric | Range | Good | Bad | Meaning |
|--------|-------|------|-----|---------|
| **G** | 0-1.2 | >= 0.8 | < 0.5 | Governed intelligence |
| **C_dark** | 0-1 | < 0.3 | >= 0.6 | Ungoverned capability |
| **Psi** | 0-2 | >= 1.0 | < 0.5 | Thermodynamic lawfulness |
| **Amanah** | T/F | True | False | Reversibility check |

---

## Quick Start

1. Click the "Open in Colab" badge above
2. Run Mode 1 (Setup & Clone)
3. Run Mode 2 (Load SEA-LION or use mock)
4. Run Mode 5 (See vanilla vs governed side-by-side)
5. Try Mode 7 for interactive testing

---

## PHOENIX SOVEREIGNTY

All notebooks demonstrate the "One Law for All Models" principle:

- Same `AMANAH_DETECTOR` for all LLMs
- Python-sovereign veto power
- If any model outputs destructive patterns, Python says NO

---

**DITEMPA BUKAN DIBERI** - Forged, Not Given
