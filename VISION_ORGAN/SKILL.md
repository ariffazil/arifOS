# Vision Organ v0.1 — Scene Contract & Quality Gate Pipeline

## Overview
Shadow-mode vision intelligence pipeline for the arifOS federation.
Generates image candidates via MiniMax, analyzes via Qwen Token Plan, scores via atomic quality gates.

## Architecture
```
User intent → Scene Contract Compiler → MiniMax image-01 → Candidate artifact → Qwen qwen3.8-max vision → Atomic quality report → Human decision
```

## Provider Map
- **Generator:** MiniMax `image-01` ($0.0035/image, confirmed working)
- **Analyzer:** Qwen Token Plan `qwen3.8-max` (vision analysis, confirmed working)
- **Text orchestration:** FED proxy (text only, no vision routing)

## Default Policy (SHADOW MODE)
- Maximum candidates per request: 1
- Maximum analysis calls: 1
- Automatic retries: 0
- Automatic approval: disabled
- External publishing: disabled
- Identity-bearing images: blocked
- Personal photo uploads: blocked
- Asset retention: ephemeral (delete after review unless approved)
- Paid routing: requires explicit per-job budget

## Adapters
- `adapters/minimax_image01.py` — Text-to-image generation
- `adapters/qwen_vision.py` — Image analysis / quality gate

## Quality Gate
Evaluates atomic checks (PASS/FAIL/UNCERTAIN) against scene contract requirements.
Never returns aesthetic score — only structural compliance.

## Failure Taxonomy
- `OBJECT_SUBSTITUTION` — wrong object instead of required
- `ACTION_MISSING` — required action not depicted
- `CONTACT_RELATION_FAIL` — required spatial relation absent
- `LOCALE_GENERIC` — setting not matching contract
- `COMPOSITION_CROP_FAIL` — required elements cropped out
- `ANATOMY_FAIL` — malformed hands, limbs, or faces
- `TEXT_WATERMARK` — unwanted text or branding

## Usage
```python
from adapters.minimax_image01 import generate_image
from adapters.qwen_vision import analyze_image
from compiler.compile_contract import compile_prompt
from evaluator.quality_gate import evaluate_candidate

# 1. Compile scene contract to prompt
prompt = compile_prompt(contract)

# 2. Generate candidate
result = generate_image(prompt, budget_usd=0.005)

# 3. Analyze against contract
report = analyze_image(result.image_url, contract)

# 4. Human decides: approve, reject, or retry
```

## Ledger
All jobs logged to `ledger/vision-jobs.jsonl` (append-only, local only).
No VAULT999 writes. No external publishing.

DITEMPA BUKAN DIBERI — SHADOW MODE ACTIVE
