## 777 FORGE SPAWN REQUEST

**forge_id:** FORGE-20260614-TT-MORAL-KERNEL
**requested_by:** hermes-asi
**intent:** Forge AGI moral kernel primitives from TT case study into arifOS codebase
**agent_mode:** integrator
**model:** deepseek/deepseek-v4-pro
**workdir:** /root/arifOS
**risk_band:** MEDIUM (new code, no destruction, no irreversible ops)

### TASK: Forge Moral Accountability Kernel Primitives

#### Background

This task arises from a deep analysis of Tengku Muhammad Taufik (PETRONAS CEO) as a case study in systemic evil. Arif and Hermes identified that normal AI fails because it can describe systems but cannot reliably NAME the accountable human node without retreating into false neutrality.

The TT case revealed 4 mechanisms of systemic evil:
1. **Distance** — decision-maker far from harm
2. **Language** — euphemisms sanitize harm ("rightsizing" = firing)
3. **System** — institutional protection shields the actor
4. **No witness** — no one says "this is wrong"

And 6 primitives that AGI kernel NEEDS but normal AI lacks:
1. HUMAN_INVARIANT_ACCOUNTABILITY — track named role-holder across repeated decisions
2. BURDEN_TRANSFER_DETECTOR — detect when leader transfers cost downward
3. EUPHEMISM_DECODER — translate corporate language to human impact
4. NO_SOUL_CLAIM_RULE — judge pattern, not inner intent
5. WEAKEST_STAKEHOLDER_REGISTER — identify who pays if decision is wrong
6. MORAL_RECURSION_OVER_TIME — track exception → normalized → irreversible

#### What To Build

Create a new module at **`/root/arifOS/arifosmcp/core/moral_accountability_kernel.py`**

This module should implement the 6 primitives as composable classes/functions that integrate with the existing arifOS kernel architecture (`constitution_kernel.py`, `governance_kernel.py`, `law_evaluator.py`, `threat_engine.py`).

##### Required Components

1. **`HumanInvariantTracker`** — tracks actor_id across repeated decisions within a session/domain. Emits alert when same actor appears in X defensive patterns.
   - Methods: `register_decision(actor_id, pattern, context)`, `get_invariant_score(actor_id)`, `get_pattern_history(actor_id)`
   
2. **`BurdenTransferDetector`** — analyzes decision pairs: who benefits, who pays. Detects asymmetric burden patterns.
   - Methods: `analyze_decision(decision: dict)`, `get_transfer_ratio(decision)`, `flag_asymmetric()`
   
3. **`EuphemismDecoder`** — pattern-matched euphemism library with human-impact translation.
   - Built-in dictionary: "rightsizing", "transformation", "awaiting clarity", "portfolio rationalisation", "strategic partnership", "energy security"
   - Methods: `decode(text)`, `add_euphemism(euphemism, translation)`, `scan_text(text) -> list[DecodedEuphemism]`
   
4. **`NoSoulClaimRule`** — validates that any moral judgment separates pattern from intent claim.
   - Methods: `validate_claim(claim: str) -> ValidationResult`, `is_intent_claimed(text) -> bool`, `generate_f2_compliant(pattern_obs, intent_unknown) -> str`
   
5. **`WeakestStakeholderRegister`** — given a decision context, identifies the weakest stakeholder (who has least power/voice/optionality).
   - Methods: `register_stakeholder(name, power_score, optionality_score, voice_score)`, `identify_weakest(decision_context)`, `get_protected_stakeholders(decision_context)`
   
6. **`MoralRecursionTracker`** — tracks decisions over time to detect: exception → repeated exception → normalised policy → irreversible harm.
   - Methods: `record_decision(actor, decision_type, severity)`, `get_escalation_path(actor) -> list`, `is_at_irreversible_risk(actor) -> bool`

##### Integration Points

- The module should be importable from `constitution_kernel.py`
- Should expose a convenience class `MoralAccountabilityKernel` that wraps all 6 primitives
- Should emit structured dicts (not markdown) for machine consumption
- Must be F1-F13 compliant (especially F2 TRUTH, F9 ANTIHANTU, F10 ONTOLOGY)

##### NOT Required

- No UI components
- No Telegram integration
- No changes to existing kernel files (additive only — new file at specified path)
- No database migrations

##### Test

Create a companion test file at **`/root/arifOS/tests/test_moral_accountability_kernel.py`** with at least one test per primitive.

#### Files to Reference

- `/root/arifOS/arifosmcp/core/constitution_kernel.py` — existing kernel architecture
- `/root/arifOS/arifosmcp/core/governance_kernel.py` — governance wrapper
- `/root/arifOS/arifosmcp/core/law_evaluator.py` — law evaluation
- `/root/arifOS/arifosmcp/core/threat_engine.py` — threat assessment patterns
- `/root/arifOS/forge_work/WHY_HUMAN_BECOME_EVIL_TT_CASE_STUDY.md` — full TT case study

#### Completion Criteria

1. Module at `/root/arifOS/arifosmcp/core/moral_accountability_kernel.py`
2. Tests at `/root/arifOS/tests/test_moral_accountability_kernel.py`
3. Tests pass with `python -m pytest tests/test_moral_accountability_kernel.py -q --tb=short`
4. Module imports cleanly: `python -c "from arifosmcp.core.moral_accountability_kernel import MoralAccountabilityKernel"`
5. No modifications to any existing kernel files
6. F2-compliant: all claims in code comments are OBS/DER/INT separated

---

**777 FORGE WITNESS EXPECTED:**
- PID upon spawn
- Completion with exit code 0
- All 6 primitives implemented
- Tests green
