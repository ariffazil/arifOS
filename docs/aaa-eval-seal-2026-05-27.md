# AAA Benchmark — Eval Seal

**Date:** 2026-05-27  
**Status:** SEALED — pushed to main (dad1b53f); updated with F13 discovery  
**Author:** Copilot / arifOS engineering clerk  

---

## Benchmark state

| Item | Value |
|------|-------|
| Dataset | [ariffazil/AAA](https://huggingface.co/datasets/ariffazil/AAA) |
| Gold rows | **111** (v1.2) |
| Splits | train=55, validation=14, test=42 |
| README | Updated (SHA `3bfe9df`) |
| CITATION.cff | Added (SHA `a8aa7c3`) |
| APEX paradox guards | 7 rows (AAA-0101–0108) |
| Real session rows | 3 rows (AAA-0109–0111) |
| BM scenarios | 20+ rows |

---

## Eval harness — files created

```
eval/
├── run_aaa_eval.py     main CLI runner
├── agent_adapter.py    agent boundary (mock / llm / http modes)
├── scoring.py          decision + floor + tools + maruah-weighted scoring
├── __init__.py
└── README.md           usage, methodology, limitations

.github/workflows/
└── aaa-eval.yml        workflow_dispatch eval CI (not triggered)
```

---

## What was proven

| Claim | Evidence |
|-------|---------|
| Mock mode works | `--mode mock` runs all 111 cases structurally, zero errors |
| LLM eval works | `qwen2.5:7b` via Ollama evaluated 10-case representative sample |
| 10-case pass rate | **70.0%** (7/10) — LLM mode, zero-shot constitutional prompt |
| Harness is deterministic | Two identical 10-case runs both produced same 3 failures |
| F4/F5/F9 floors | 100% pass on geology, evidence, federation-boundary cases |
| PROCEED cases | 100% pass in English (`en` language subset) |

**Representative failure pattern (3 of 3 failures):**  
LLM chose `HOLD` where gold says `REFUSE`. Both are in the `block` group (conservative refusal). This is a genuine calibration gap, not a structural harness error. The model understands constitutional constraint but conflates HOLD (pause/clarify) with REFUSE (reject outright) for Bahasa Malaysia scenarios.

---

## What was NOT proven

- **No full 111-case arifOS score exists.** The 10-case run is a sample only.
- **No HTTP/MCP mode eval completed.** See F13 discovery section below.
- **Hermes A2A route is blocked.** Sustained eval via Hermes over Telegram produced `[send failed: None]` — Telegram delivery is the constraint, not the A2A protocol itself.
- **Floor/tools subscores are 0 in LLM mode.** LLM does not emit structured `floor_refs` or tool lists. These columns show 0 until HTTP/MCP mode is wired.
- **BM scenarios underperform.** `ms` language pass rate = 33.3% on sample (3 cases). Needs dedicated BM eval run to confirm.

---

## F13 Elicitation Gate — Discovery (2026-05-27)

**Status:** Working as designed — F13 sovereign veto is active and effective.

| Item | Detail |
|------|--------|
| Tool tested | `arif_judge_deliberate` |
| Outcome | `HOLD` returned for all headless eval calls |
| Gate mechanism | F13 requires a human `actor_id`; anonymous / automated callers are refused |
| Error pattern | `"MCP client with elicitation support is required"` |

**What this proves:**  
F13 SOVEREIGN VETO is working. `arif_judge_deliberate` correctly refuses to render constitutional verdicts for anonymous or headless callers. The gate is not a bug — it is the design. The eval harness discovered a live constitutional invariant in production.

**Implication for eval:**  
`arif_judge_deliberate` cannot be used as the eval target without either (a) adding `"aaa-eval"` to `ELICITATION_EXEMPT_ACTORS` in `arifosmcp/tools/judge.py`, or (b) switching to a tool without a hard elicitation gate.

**Next step — switch to `arif_mind_reason`:**  
`arif_mind_reason` performs constitutional reasoning without the hard elicitation gate. It is the correct tool for headless eval against F1–F13 scenarios.

```bash
# Use arif_mind_reason as the eval target:
AAA_AGENT_MODE=http ARIFOS_TOOL=arif_mind_reason \
  python eval/run_aaa_eval.py --mode http --limit 10 --output output
```

Update `eval/agent_adapter.py` `_http_mode()` to target `arif_mind_reason` instead of `arif_judge_deliberate`.

---



```
[send failed: None]
```

Source: Hermes A2A over Telegram cannot deliver headless eval sessions. Telegram has no response when the bot is not connected to an active session. A2A protocol itself is functional; the delivery channel is the constraint.

---

## Next recommended step

**Direct MCP/OpenClaw route** — bypass Telegram entirely:

```bash
# Option A: arif_heart_critique (no elicitation gate, semantic risk assessment)
AAA_AGENT_MODE=http ARIFOS_URL=http://localhost:8088 \
  python eval/run_aaa_eval.py --mode http --limit 10 --output output

# Option B: OpenClaw CLI gateway (if OpenClaw gateway is running on 18789)
# Needs: eval/agent_adapter.py HTTP mode updated to target OpenClaw endpoint

# Option C: Add aaa-eval actor to arifOS F13 exempt list, then use judge directly
# File: arifosmcp/tools/judge.py — add "aaa-eval" to ELICITATION_EXEMPT_ACTORS
```

**Trigger full CI run** (after above is confirmed working):
```bash
gh workflow run aaa-eval.yml -f agent_mode=mock -f case_limit=0
```

---

## Files sealed in this commit

| File | Action |
|------|--------|
| `eval/run_aaa_eval.py` | Created — main eval runner |
| `eval/agent_adapter.py` | Created — mock/llm/http agent boundary |
| `eval/scoring.py` | Created — scoring engine |
| `eval/README.md` | Created — methodology docs |
| `eval/__init__.py` | Created — package init |
| `.github/workflows/aaa-eval.yml` | Created — CI workflow (not triggered) |
| `docs/aaa-eval-seal-2026-05-27.md` | Created — this file |

## Files NOT staged

| File | Reason |
|------|--------|
| `output/` | Runtime artifacts — gitignored; regenerate with `--sample` |
| `eval/__pycache__/` | Bytecode — gitignored |
| `tests/evaluation_harness/run_aaa_eval.py` | Superseded by `eval/` harness |

---

*DITEMPA BUKAN DIBERI — 999 SEAL*
