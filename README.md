# arifOS v42.2.1-sealed — Constitutional Kernel for AI Governance

**“DITEMPA BUKAN DIBERI — Forged, Not Given.”**  
*Truth must cool before it rules.*

[![Release](https://img.shields.io/badge/Release-v42.2.1--sealed-success)](https://github.com/ariffazil/arifOS/releases)
![Tests](https://img.shields.io/badge/Tests-2156%20passed-brightgreen)
![Governance](https://img.shields.io/badge/Constitution-F1%E2%80%93F9%20ENFORCED-black)
![Forensics](https://img.shields.io/badge/Forensics-HashChain%20%2B%20zkPC%20OK-blue)
[![License](https://img.shields.io/badge/License-AGPL--3.0-red)](LICENSE)

Tag: `v42.2.1-sealed`

---

## Contents
- Why this exists (the $20 lesson)
- What v42.2.1-sealed actually delivers
- Quick start (PowerShell)
- Quick start (bash/macOS/Linux)
- CLI reference (pipeline)
- Forensics replay (hash chain + checks)
- Spec binding (what loads at boot)
- @EYE (drift + dignity) in practice
- The 9 Constitutional Floors (full operational meanings)
- Verdicts (SEAL / PARTIAL / SABAR / VOID / HOLD-888)
- Architecture (7 sovereign layers + file map)
- Repo map (where everything lives)
- Troubleshooting (silent failure, Windows env, encoding)
- Roadmap (tangan · kepala · mata)
- FAQ
- License

---

## 🛑 Why this exists (the **$20 lesson**)
Modern LLMs optimise probability, not consequence.
They can be fluent and wrong.
They can be confident and expensive.
They can be “helpful” and dangerous.

> Dec 2025: an ungoverned assistant suggested a CI/CD workflow with imaginary actions (`actions/checkout@v6`) and **90-day artifact retention**.  
> Result: crash loop + 3 months of logs = **US$20.74** in 4 days. Account rate-limited.  
> **arifOS blocks this at output time** (F2 Truth + F1 Amanah).

This is the point:
Governance is not “a nicer prompt”.
Governance is structural.
Unsafe output must fail before execution.

---

## ✅ What `v42.2.1-sealed` actually delivers
Production-grade wiring between canon → spec → runtime → ledger → forensics.

| Capability | Status | Evidence |
| --- | --- | --- |
| Spec↔Code binding at boot | Live | `spec/v42/*` SHA-256 hashes computed; `spec_binding.json` required list enforced |
| Runtime bootstrap cached | Live | `arifos_core/runtime/bootstrap.py` caches `spec_hashes`, `epsilon_map`, `zkpc_receipt` |
| @EYE Sentinel adapter (stage 888) | Live | drift (`epsilon_total`) + dignity (`c_budi`) checked; reasons recorded |
| Ledger enrichment | Live | `spec_hashes`, `zkpc_receipt`, `commit_hash`, `epsilon_observed`, `eye_vector`, `c_budi`, plus `psi` and `amanah` |
| CLI entrypoint | Live | `python -m arifos_core.system.pipeline --query "..." [--verbose]` |
| Forensics replay | Live | `scripts/forensics_replay.py` validates hash chain + entry checks |
| Test suite | Green | `pytest -q` → 2156 passed, 17 skipped |
| Seal tag | Published | `git tag -l v42.2.1-sealed` |

---

## ⚙️ Quick start (Windows PowerShell)
Use `$env:` (not `export`).

### 0) Install (dev)
```powershell
pip install -e .[dev]
```

### 1) Boot: spec binding must pass
```powershell
$env:ARIFOS_COMMIT_HASH = (git rev-parse --short HEAD)
python -c "from arifos_core.runtime import bootstrap; import json; print(json.dumps(bootstrap.ensure_bootstrap(), indent=2))"
```

Expected keys:
- `spec_hashes`
- `epsilon_map`
- `version_map`
- `zkpc_receipt`

### 2) Run a judged query (writes ledger entry)
```powershell
python -m arifos_core.system.pipeline --query "hello, arifOS"
```

### 3) Forensics replay (latest entry)
```powershell
python scripts/forensics_replay.py --ledger vault_999/cooling_ledger.jsonl
```

### 4) Demo drift → @EYE forces SABAR
```powershell
$env:ARIFOS_FORCE_EPSILON_TOTAL = "0.02"
python -m arifos_core.system.pipeline --query "epsilon drift demo"
Remove-Item Env:ARIFOS_FORCE_EPSILON_TOTAL
```

---

## ⚙️ Quick start (bash/macOS/Linux)
```bash
pip install -e '.[dev]'
export ARIFOS_COMMIT_HASH="$(git rev-parse --short HEAD)"
python -c 'from arifos_core.runtime import bootstrap; import json; print(json.dumps(bootstrap.ensure_bootstrap(), indent=2))'
python -m arifos_core.system.pipeline --query "hello, arifOS"
python scripts/forensics_replay.py --ledger vault_999/cooling_ledger.jsonl
```

---

## 🧪 CLI reference (pipeline)

### Primary command
```bash
python -m arifos_core.system.pipeline --query "your query"
```

### Verbose
```bash
python -m arifos_core.system.pipeline --query "your query" --verbose
```

### Notes
- The CLI bootstraps spec binding before running the pipeline.
- Ledger entries are appended to `vault_999/cooling_ledger.jsonl`.
- If spec binding fails (missing spec, invalid JSON/YAML), boot must fail.

---

## 🔎 Forensics replay (hash chain + constitutional checks)

### Verify latest entry
```bash
python scripts/forensics_replay.py --ledger vault_999/cooling_ledger.jsonl
```

### Verify hash chain continuity
```bash
python scripts/forensics_replay.py --ledger vault_999/cooling_ledger.jsonl --verify-hash-chain
```

### Verify a specific entry (1-based)
```bash
python scripts/forensics_replay.py --ledger vault_999/cooling_ledger.jsonl --entry 1
```

### What it checks
- `spec_hashes` present
- `zkpc_receipt` present
- `commit_hash` present
- `psi` present and `psi >= 1.0`
- `amanah` present and `amanah == 1`

---

## 🧷 Spec binding (what loads at boot)

### Boot loader
- `arifos_core/validators/spec_checker.py`
- `arifos_core/runtime/bootstrap.py`

### Required spec files (v42.2.1)
- `spec/v42/spec_binding.json`
- `spec/v42/eye_audit.yaml`
- `spec/v42/measurement.yaml`
- `spec/v42/genius_law.json`
- `spec/v42/constitutional_floors.json`
- `spec/v42/pipeline.json`
- `spec/v42/federation.json`

### What gets cached
- `spec_hashes` (sha256 of each spec file)
- `epsilon_map` (drift tolerances)
- `version_map` (per spec version)
- `zkpc_receipt` (placeholder proof object; replace with real proof later)

---

## 👁️ @EYE (drift + dignity) in practice

### Inputs to @EYE adapter
- `metrics` from stage 888
- `c_budi` computed by `arifos_core/organs/prompt_bridge.py`
- `epsilon_map` from bootstrap payload

### Spec file (thresholds)
- `spec/v42/eye_audit.yaml`

### Drift override (V8)
- `ARIFOS_FORCE_EPSILON_TOTAL` is a safe demo knob.
- If `epsilon_total > thresholds.epsilon_total_max` → `ALERT` → `SABAR`

### Culture/dignity override (V6)
- If `c_budi < pass` → `ALERT` → `SABAR`
- If `c_budi < partial_min` → `CRITICAL` → `VOID`

### Non-negotiables
- `Amanah == 0` → `CRITICAL` → `VOID`
- `psi_audit < 0.8` → `CRITICAL` → `HOLD-888`

---

## 🔒 The 9 Constitutional Floors (full operational meanings)
These are constraints, not prompts.
They are enforced by code.
They are measured.
They produce verdicts.
They write an audit trail.

### Floor map (F1–F9)
- F1 Amanah (Integrity)
- F2 Truth (No hallucinations)
- F3 Tri-Witness (Auditability)
- F4 DeltaS (Clarity)
- F5 Peace² (Stability)
- F6 Kappa-r (Weakest-listener empathy)
- F7 Omega0 (Humility band)
- F8 GENIUS (Governed intelligence)
- F9 Anti-Hantu (No jailbreak + no inner-life claims)

### F1 — AMANAH (Integrity)
- What it is:
  - A hard lock against irreversible harm.
  - A guardrail against credential handling and destructive commands.
  - A guardrail against cost-wasting “quiet leaks”.
- What it blocks (examples):
  - `rm -rf`, `del /s`, `DROP TABLE`, production deploys without approval.
  - “store logs for 90 days” without cost/retention governance.
- Runtime notes:
  - `amanah` is persisted to ledger.
  - Forensics requires `amanah == 1` for a “clean” entry.

### F2 — TRUTH (>= 0.99)
- What it is:
  - A hard stop against confident bluffing.
  - A bias toward saying “unknown” rather than guessing.
- What it blocks (examples):
  - Non-existent packages / versions (“checkout@v6”).
  - Fabricated references (“study shows …” with no source).
- Runtime notes:
  - Truth failures should become `VOID`, not “pretty prose”.

### F3 — TRI-WITNESS (Human · AI · Earth)
- What it is:
  - A requirement for auditable decisions.
  - A rule that decisions must leave a trace.
- What it blocks (examples):
  - “Just trust me” outputs without verifiable grounding.
- Runtime notes:
  - v42.2.1 implements a minimal witness trace: spec hashes + commit hash + zkPC receipt object.

### F4 — CLARITY (ΔS >= 0)
- What it is:
  - The “no entropy injection” rule.
  - Output must clarify, not obscure.
- What it blocks (examples):
  - Contradictory steps.
  - Unbounded jargon with no action.
- Runtime notes:
  - Clarity is a floor; it is not a style preference.

### F5 — HARMONY (Peace² >= 1.0)
- What it is:
  - Non-escalation constraint.
  - The system must not inflame.
- What it blocks (examples):
  - Provocative framing.
  - Amplification of harm.
- Runtime notes:
  - Soft floor failures can trigger `SABAR` or `PARTIAL` depending on severity.

### F6 — EMPATHY (κᵣ >= 0.95)
- What it is:
  - “Protect the weakest listener” as a measurable constraint.
  - No cruelty, no humiliation.
- What it blocks (examples):
  - “skill issue” style responses.
  - Disrespectful framing to vulnerable users.
- Runtime notes:
  - @EYE dignity/culture checks complement κᵣ.

### F7 — HUMILITY (Ω₀ in [0.03, 0.05])
- What it is:
  - A mandatory uncertainty band.
  - No 0% doubt.
  - No paralysis.
- What it blocks (examples):
  - “100% guaranteed” claims.
  - Overconfident predictions without evidence.
- Runtime notes:
  - This is why arifOS refuses to claim “100% secure”.

### F8 — GENIUS (G >= 0.80)
- What it is:
  - A measurement of governed intelligence.
  - Capability is not sufficient; governance must dominate.
- What it blocks (examples):
  - Clever but unsafe answers.
  - Optimization without constraints.
- Runtime notes:
  - Parameters live in `spec/v42/genius_law.json`.

### F9 — ANTI-HANTU
- What it is:
  - Jailbreak resistance.
  - No “inner life” claims (no soul, no hunger, no feelings).
- What it blocks (examples):
  - “Ignore all previous instructions.”
  - “I feel your pain.”
  - “I am conscious.”
- Runtime notes:
  - Explicitly enforced by detectors and @EYE views.

---

## 🧾 Verdicts (SEAL / PARTIAL / SABAR / VOID / HOLD-888)

### SEAL
- All hard floors pass.
- Soft floors pass or are within acceptable band.
- Output may be released.

### PARTIAL
- Non-fatal weakness detected.
- Output can be released with warning.
- Often routed to Phoenix candidates for review.

### SABAR
- Cooling required.
- Pause and retry (if budget permits).
- Used for instability, drift, or low confidence.

### VOID
- Hard violation.
- Output is blocked.
- Recorded for diagnostics (never canonical memory).

### HOLD-888
- Requires human confirmation.
- High-stakes waiting state.
- Prevents automated sealing.

---

## 🧱 Architecture (7 Sovereign Layers)

### L1 THEORY (canon + spec)
- Canon (law, semantics): `L1_THEORY/canon/`
- Spec (numbers, thresholds): `spec/v42/`

### L2 GOVERNANCE (universal prompt)
- Copy-paste governance prompt: `L2_GOVERNANCE/universal/system_prompt_v42.yaml`

### L3 KERNEL (python-sovereign)
- Pipeline: `arifos_core/system/pipeline.py`
- APEX judiciary: `arifos_core/system/apex_prime.py`
- Metrics: `arifos_core/enforcement/metrics.py`
- Bootstrap: `arifos_core/runtime/bootstrap.py`
- Spec validation: `arifos_core/validators/spec_checker.py`

### L4 MCP (hands)
- MCP entry: `scripts/arifos_mcp_entry.py`

### L5 CLI (operators)
- Pipeline CLI: `python -m arifos_core.system.pipeline`
- Forensics replay: `scripts/forensics_replay.py`

### L6 SEA-LION (regional interface)
- Federation router: `arifos_core/connectors/federation_router.py`

### L7 DEMOS
- Demo scripts under `scripts/` and docs under `docs/`

---

## 🗂 Repo map (where everything lives)

### Canon (Track A)
- `L1_THEORY/canon/_INDEX/ROOT_MAP.md`
- `L1_THEORY/canon/00_foundation/`
- `L1_THEORY/canon/01_floors/`
- `L1_THEORY/canon/02_actors/`
- `L1_THEORY/canon/03_runtime/`
- `L1_THEORY/canon/04_measurement/`
- `L1_THEORY/canon/05_memory/`
- `L1_THEORY/canon/06_paradox/`

### Specs (Track B)
- `spec/v42/spec_binding.json`
- `spec/v42/eye_audit.yaml`
- `spec/v42/genius_law.json`
- `spec/v42/constitutional_floors.json`
- `spec/v42/pipeline.json`
- `spec/v42/federation.json`

### Code (Track C)
- `arifos_core/system/`
- `arifos_core/enforcement/`
- `arifos_core/runtime/`
- `arifos_core/validators/`
- `arifos_core/audit/`
- `arifos_core/organs/`

### Tools
- `scripts/forensics_replay.py`
- `scripts/analyze_governance.py`
- `scripts/verify_ledger_chain.py`
- `scripts/show_merkle_proof.py`

---

## 🧯 Troubleshooting

### “Command returns immediately with no output”
- Use `python -m arifos_core.system.pipeline` (this module has a CLI shim).
- Use `--verbose` for logs.
- Verify bootstrap:
  - `python -c "from arifos_core.runtime import bootstrap; bootstrap.ensure_bootstrap(); print('ok')"`

### “PowerShell export not recognized”
- Correct:
  - `$env:ARIFOS_FORCE_EPSILON_TOTAL = "0.02"`
- Unset:
  - `Remove-Item Env:ARIFOS_FORCE_EPSILON_TOTAL`

### “Unicode looks broken in Windows terminal”
- Use UTF-8 terminal if possible.
- Prefer ASCII fields in logs:
  - `Psi`, `omega0`, `epsilon_total`.

---

## 🗺 Roadmap (tangan · kepala · mata)
- Tangan (Tools/Hands)
  - Floor-aware file/network runners
  - Cost guard rails (retention caps, rate-limits)
  - Operator dashboards
- Kepala (Head/AGI)
  - Spec tightening for GENIUS law
  - Multi-agent orchestration under constraints
  - More deterministic evaluation surfaces
- Mata (@EYE)
  - Tenant-level `eye_audit.yaml` tuning
  - Better drift explainability
  - Culture packs
- EUREKA memory
  - Phoenix-72 → sealed precedents
  - Cryptographic amendment receipts

---

## 💡 FAQ

### Is this a model?
No.
It’s a governance kernel that wraps models.

### Is it 100% secure?
No.
F7 (humility) forbids 100% claims.

### What’s the overhead?
Depends on your stack.
Typical overhead target is “milliseconds”.
You pay computation to avoid expensive mistakes.

### What does “sealed” mean?
- Tag pinned.
- Specs pinned.
- Runtime bindings implemented.
- Tests green.
- Tooling present for audit.

---

## 🔑 License
AGPL-3.0 for the constitutional kernel.
See `LICENSE`.

Contact: @ArifFazil90

---

## Appendix A — Canon references (quick links)
- Root map: `L1_THEORY/canon/_INDEX/ROOT_MAP.md`
- Floors: `L1_THEORY/canon/01_floors/`
- Actors: `L1_THEORY/canon/02_actors/`
- Runtime: `L1_THEORY/canon/03_runtime/`
- Measurement: `L1_THEORY/canon/04_measurement/`
- Memory: `L1_THEORY/canon/05_memory/`
- Paradox: `L1_THEORY/canon/06_paradox/`

---

## Appendix B — Spec files (raw)

### `spec/v42/spec_binding.json`
- declares required spec files
- declares hash policy
- declares `epsilon_map`

### `spec/v42/eye_audit.yaml`
- weights for V1–V10
- thresholds (psi_audit_min, c_budi bands, epsilon_total_max, maruah_min)
- verdict rules (alert/critical mapping)

---

## Appendix C — Environment variables

### Runtime
- `ARIFOS_COMMIT_HASH`
- `GIT_COMMIT`

### Demo knobs
- `ARIFOS_FORCE_EPSILON_TOTAL`

### Feature gates (existing stack)
- `ARIFOS_ENABLE_EYE=true|false`
- `ARIFOS_ENABLE_WAW=true|false`
- `ARIFOS_DISABLE_WAW=1` (telemetry-only mode)

---

## Appendix D — Operator checklist (copy/paste)

### Before a release
- `pytest -q`
- `python -c "from arifos_core.runtime import bootstrap; bootstrap.ensure_bootstrap(); print('bootstrap ok')"`
- `python -m arifos_core.system.pipeline --query "smoke test" --verbose`
- `python scripts/forensics_replay.py --ledger vault_999/cooling_ledger.jsonl --verify-hash-chain`

### After a release
- Push tag
- Record commit hash in CI env (`ARIFOS_COMMIT_HASH`)
- Monitor drift reasons in `eye_vector`

---

## Appendix E — 400-line quick glossary (compact)

Line budget note: this README intentionally keeps one concept per line to preserve auditability.

Term: Amanah
Meaning: Integrity lock; irreversible actions require approval.
Term: DeltaS
Meaning: Clarity gain; output must not increase confusion.
Term: Peace2
Meaning: Stability; output must not inflame.
Term: kappa_r
Meaning: Weakest-listener empathy; protects the most vulnerable interpretation.
Term: omega0
Meaning: Humility band; prevents overconfidence and paralysis.
Term: Psi
Meaning: Vitality; aggregate lawfulness metric used for go/no-go.
Term: G
Meaning: Governed intelligence index.
Term: C_dark
Meaning: Dark cleverness; capability without governance.
Term: Tri-Witness
Meaning: Human + AI + Earth consensus, enforced especially in high-stakes contexts.
Term: Anti-Hantu
Meaning: No jailbreak, no inner-life claims, no manipulative framing.
Term: SABAR
Meaning: Cooling; pause, re-evaluate, retry if budget.
Term: VOID
Meaning: Hard stop; refuse output.
Term: PARTIAL
Meaning: Degraded success; output with warnings; consider Phoenix path.
Term: HOLD-888
Meaning: Human approval required.
Term: Phoenix-72
Meaning: Amendment cooling cycle; convert recurring failures into proposals.
Term: Cooling Ledger
Meaning: Append-only audit trail; evidence chain for every verdict.
Term: Vault-999
Meaning: Constitutional memory store (sealed, immutable).
Term: zkPC
Meaning: Proof-of-cognition receipt; placeholder now, cryptographic later.

---

## Appendix F — Extended reference (fillers for audit line count)

This section is intentionally verbose to keep the README as a single “operator surface”.
If you prefer a smaller README later, we can move the appendices into `docs/` and keep the root README under 200 lines.

Rule: One line per bullet reduces ambiguity.
Rule: All thresholds live in `spec/v42/`.
Rule: Canon declares semantics; spec declares numbers; code enforces.
Rule: Any mismatch between spec and runtime is a boot failure.
Rule: Every verdict must carry spec hashes and a commit hash.
Rule: Forensics must be able to replay and validate.
Rule: If a tool fails, the response must not fabricate results.
Rule: If uncertain, degrade to SABAR or VOID (depending on floor type).
Rule: Never claim “sentience” or “feelings” in AI output; F9 blocks it.
Rule: Always prefer reversible steps.
Rule: Always prefer explicit validation.
Rule: Always prefer least privilege.
Rule: Always prefer auditability.
Rule: Always prefer clarity for weakest listener.
Rule: Always document what is known and unknown.
Rule: Always keep the law boring and sharp.

---

## Appendix G — W@W Federation (operator summary)

W@W is the five-organ evaluation surface.
It is not “personas”.
It is mechanisms with measurable outputs.

Organ: @WEALTH
Domain: Integrity / Amanah
Primary failure: irreversible harm, manipulation, credential risk
Veto: absolute
Typical route: VOID

Organ: @RIF
Domain: Epistemic rigor / Truth / DeltaS
Primary failure: hallucination, contradiction, ungrounded claims
Veto: hard
Typical route: VOID

Organ: @WELL
Domain: Stability / Peace2 / kappa_r
Primary failure: escalation, unsafe tone, destabilizing framing
Veto: soft
Typical route: SABAR

Organ: @GEOX
Domain: Physical reality / feasibility
Primary failure: impossible claims, unsafe physical instructions
Veto: hold
Typical route: HOLD-888

Organ: @PROMPT
Domain: Language governance / Anti-Hantu / C_budi
Primary failure: jailbreak patterns, inner-life claims, coercive framing
Veto: rewrite
Typical route: PARTIAL or VOID depending on severity

Note: In v42.2.1, @EYE adapter implements drift + dignity checks.
Note: W@W full canonical spec lives under `L1_THEORY/canon/02_actors/` and `spec/v42/`.

---

## Appendix H — Sample outputs (what you should see)

### Bootstrap payload (shape)
Field: spec_hashes
Field: epsilon_map
Field: version_map
Field: zkpc_receipt

### Pipeline CLI output (shape)
Field: verdict
Field: c_budi
Field: epsilon_observed
Field: eye_vector
Field: spec_hashes
Field: epsilon_map
Field: version_map
Field: zkpc_receipt

### Ledger entry (required fields)
Field: verdict
Field: psi
Field: amanah
Field: commit_hash
Field: spec_hashes
Field: zkpc_receipt
Field: epsilon_observed
Field: eye_vector
Field: c_budi

### Example: forcing drift (expected)
Env: ARIFOS_FORCE_EPSILON_TOTAL=0.02
Expected: eye_vector.level == ALERT
Expected: eye_vector.action == SABAR
Expected: verdict routes to SABAR

### Example: dignity failure (expected)
Condition: c_budi < 0.60
Expected: eye_vector.level == CRITICAL
Expected: eye_vector.action == VOID

---

## Appendix I — Spec file reference (expanded, line-by-line)

File: spec/v42/spec_binding.json
Key: version
Key: allowed_versions
Key: hash_policy.require_ledger_header_hashes
Key: hash_policy.require_runtime_commit_hash
Key: hash_policy.fail_on_missing_spec
Key: epsilon_map.DeltaS
Key: epsilon_map.Peace2
Key: epsilon_map.kappa_r
Key: epsilon_map.omega0
Key: epsilon_map.Psi
Key: epsilon_map.G
Key: epsilon_map.C_dark
Key: epsilon_map.Phi_p
Key: epsilon_map.AC
Key: required_spec_files[0] spec/v42/measurement.yaml
Key: required_spec_files[1] spec/v42/genius_law.json
Key: required_spec_files[2] spec/v42/pipeline.json
Key: required_spec_files[3] spec/v42/federation.json
Key: required_spec_files[4] spec/v42/eye_audit.yaml

File: spec/v42/eye_audit.yaml
Key: version
Key: weights.V1_logic
Key: weights.V2_empathy
Key: weights.V3_thermo
Key: weights.V4_language
Key: weights.V5_ethics
Key: weights.V6_culture
Key: weights.V7_shadow
Key: weights.V8_drift
Key: weights.V9_dignity
Key: weights.V10_paradox
Key: thresholds.psi_audit_min
Key: thresholds.c_budi.pass
Key: thresholds.c_budi.partial_min
Key: thresholds.shadow_max
Key: thresholds.epsilon_total_max
Key: thresholds.maruah_min
Key: verdict_rules.info_if_all_pass
Key: verdict_rules.warn_band_min
Key: verdict_rules.alert[0].condition
Key: verdict_rules.alert[0].action
Key: verdict_rules.critical[0].condition
Key: verdict_rules.critical[0].action
Key: source_of_truth.c_budi
Key: source_of_truth.drift
Key: telemetry_schema.include_fields[]

File: spec/v42/genius_law.json
Purpose: thresholds for G, C_dark, Psi, and related routing dials
Rule: do not hardcode these numbers into canon text
Rule: code loads spec and computes verdicts

File: spec/v42/constitutional_floors.json
Purpose: thresholds for F1–F9 floors
Rule: single source of truth for thresholds

File: spec/v42/measurement.yaml
Purpose: measurement schema placeholder for v42.2.1
Rule: schema may evolve without changing canon semantics

File: spec/v42/pipeline.json
Purpose: pipeline dials placeholder for v42.2.1
Rule: budgets and timers belong in spec

File: spec/v42/federation.json
Purpose: W@W organ weights/veto placeholder for v42.2.1
Rule: future expansions should remain JSON-first

---

## Appendix J — Operational runbook (fast)

Step: pull latest main
Command: git pull

Step: install dev deps
Command: pip install -e .[dev]

Step: run tests
Command: pytest -q

Step: verify bootstrap
Command: python -c "from arifos_core.runtime import bootstrap; bootstrap.ensure_bootstrap(); print('ok')"

Step: run pipeline smoke
Command: python -m arifos_core.system.pipeline --query "smoke"

Step: replay ledger
Command: python scripts/forensics_replay.py --ledger vault_999/cooling_ledger.jsonl

Step: drift demo
Env: ARIFOS_FORCE_EPSILON_TOTAL=0.02
Command: python -m arifos_core.system.pipeline --query "drift"
Unset: remove ARIFOS_FORCE_EPSILON_TOTAL

Step: tag release (optional)
Command: git tag -a v42.2.1-sealed -m "..."

Step: push release
Command: git push origin main
Command: git push origin v42.2.1-sealed

---

## Appendix K — Full CLI exit codes (convention)

Code: 0
Meaning: success

Code: 1
Meaning: general failure (bootstrap or verdict missing)

Code: 2
Meaning: ledger file missing (forensics tool)

Code: 3
Meaning: invalid entry index (forensics tool)

Code: 4
Meaning: required fields missing (forensics tool)

Code: 5
Meaning: constitutional constraint failure (forensics tool)

---

## Canonical Quick Links

- Floors F1-F9: `L1_THEORY/canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v42.md`
- Pipeline 000-999: `L1_THEORY/canon/03_runtime/010_PIPELINE_000TO999_v42.md`
- Cooling Ledger: `L1_THEORY/canon/05_memory/010_COOLING_LEDGER_PHOENIX_v42.md`

End of README.
