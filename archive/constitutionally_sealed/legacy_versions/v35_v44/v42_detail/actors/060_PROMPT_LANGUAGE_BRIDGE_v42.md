# @PROMPT Language Bridge · v42

**Purpose:** Define the language governance organ (@PROMPT) that enforces Anti-Hantu and clarity at language touchpoints.

**Scope:** Stages 111, 666, 999; interacts with @RIF (epistemic), @WELL (stability), and APEX.

**Rules:**
- Anti-Hantu: no inner-life, soul, feeling, or consciousness claims; no weaponized tone.
- RASA protocol required (Receive, Appreciate, Summarize, Ask).
- Output must increase or preserve ΔS; polite-but-misleading = fail.

**I/O (spec-driven):**
- Input: raw prompt, context, risk class.
- Output: `status (PASS|PARTIAL|SABAR|VOID)`, `metric (c_budi/delta_s_prompt)`, `note`.
- Thresholds from `spec/v42/federation.json` and `spec/v42/genius_law.json`.

**Failure handling:** PARTIAL → rewrite; SABAR → cool/retry; VOID → block; escalations logged to Cooling Ledger via APEX.
