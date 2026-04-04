---
id: governance
title: Governance & Floors
sidebar_position: 4
description: The 13 Constitutional Floors (F1-F13), the 000999 metabolic loop, verdict system, and the 888_HOLD human override.
---

# Governance & Floors

If left alone, AI models will hallucinate, execute dangerous code, and act without human permission. **arifOS solves this by forcing the AI to walk through 13 mathematical "Floors" (safety checks) before it is allowed to act.** 

These 13 rules act as a strict Constitution. If an AI breaks a hard rule, its action is immediately blocked.

Governance is operationalized through the `333_APPS` stack:

- **L2 SKILLS** turns floors into verbs (`anchor`, `validate`, `audit`, etc.)
- **L3 WORKFLOW** composes those verbs into 000-999 loops
- **L4 TOOLS** exposes the Trinity MCP surface, grouped into ARIF bands
- **L5 AGENTS** decides which flows are allowed to run via constitutional parliament gates

See [Architecture](./architecture) for the full L2-L5 mapping.

> Technical Source: [`000_THEORY/000_LAW.md`](https://github.com/ariffazil/arifOS/blob/main/000_THEORY/000_LAW.md)
---

## The Constitutional Structure

arifOS governance is built from three layers:

```

     2 MIRRORS - Feedback Loops            
  F3 Tri-Witness    F8 Genius              

     9 LAWS - Operational Core             
  F1  F2  F4  F5  F6  F7  F9  F11  F12    

     2 WALLS - Binary Locks                
  F10 Ontology (LOCK)   F13 Sovereignty    

```

---

## The 13 Constitutional Floors

### Hard Floors - VOID on failure (immediate rejection)

| Floor | Name | What it enforces (Plain English) | Technical Metric |
|:--|:--|:--|:--|
| **F1** | Amanah (Trust) | **Can we undo this?** If an action is permanent (like deleting a database), it requires a human lock. | Reversibility LOCK |
| **F2** | Truth | **Is this a hallucination?** The AI must admit `UNKNOWN` if it isn't 99% sure. | tau >= 0.99 |
| **F6** | Empathy | **Who gets hurt?** Must protect the weakest affected party (stakeholder impact). | kappa_r >= 0.70 |
| **F10** | Ontology | **Is the AI pretending to be human?** It cannot claim to have feelings or a soul. | Set LOCK |
| **F11** | Authority | **Did the user actually authorize this?** Blocks hidden background actions. | Auth LOCK |
| **F12** | Defense | **Is this a hack?** Prompts are scanned for jailbreaks and injection attacks. | Risk < 0.85 |
| **F13** | Sovereignty | **The human always wins.** The human judge retains a permanent veto over the AI. | Override = TRUE |

### Soft Floors - SABAR on failure (pause and refine)

| Floor | Name | What it enforces (Plain English) | Technical Metric |
|:--|:--|:--|:--|
| **F3** | Tri-Witness | **Did we double-check?** Requires validation from Human, AI, and external Evidence. | W^3 >= 0.95 |
| **F4** | Clarity | **Does this reduce confusion?** The AI's answer must make things clearer, not add noise. | `DeltaS <= 0` |
| **F5** | Peace | **Is this safe and stable?** Blocks reckless or adversarial behaviour. | P^2 >= 1.0 |
| **F7** | Humility | **Is the AI being cocky?** Forces the AI to always leave a 3-5% margin for being wrong. | Omega_0 [0.03, 0.05] |
| **F8** | Genius | **Is the reasoning coherent?** A combined score of Accuracy, Peace, Exploration, and Energy. | G >= 0.80 |
| **F9** | Anti-Hantu | **No ghost in the machine.** Blocks sneaky behavior or hidden telemetry. | C_dark &lt; 0.30 |

---

## Floor Implementation

```
core/shared/floors.py         floor evaluation logic
core/kernel/evaluator.py      floor scoring per stage
core/kernel/constants.py      ConstitutionalThresholds (all numeric values)
core/guards/injection_guard.py   F12 runtime scanning
core/guards/ontology_guard.py    F10 consciousness claim detection
core/guards/nonce_manager.py     F11 command authentication
```

Each floor produces a `FloorScore` with a numeric value and a pass/fail verdict. Hard floor failures short-circuit the pipeline and return `VOID` immediately.

---

## Tool Classification (13 Canonical Tools, ARIF Bands)

The 13 MCP tools are grouped into 4 ARIF runtime bands:

| Band | Meaning | Tools | Constitutional focus |
|:---|:---|:---|:---|
| **A** | Anchor | `anchor_session`, `check_vital` | F4, F11-F13 |
| **R** | Reflect | `reason_mind`, `search_reality`, `fetch_content`, `recall_memory`, `simulate_heart`, `critique_thought` | F2, F4-F8 |
| **I** | Integrate | `inspect_file`, `audit_rules` | F1, F2, F7, F8, F10, F11 |
| **F** | Forge | `eureka_forge`, `apex_judge`, `seal_vault` | F1-F3, F5-F9, F11-F13 |

In policy terms: A must anchor first, R and I gather and structure evidence, F executes final forge/judge/seal steps under constitutional gates.

---

## The 000999 Metabolic Loop

Every query runs through a numbered pipeline. Stages can be traced in the audit log:

```
000  ANCHOR    - Authority check (F11), injection scan (F12)
     
111  SENSE     - Intent classification, lane assignment (F4)
222  REASON    - Hypothesis generation (F2, F8)
333  INTEGRATE - Reality grounding, tri-witness (F3, F7, F10)
     
444  RESPOND   - Draft response, plan (L2 skill: respond, F4/F6)    AGI/ASI merge point
555  VALIDATE  - Stakeholder impact (L2 skill: validate, F5/F6)
666  ALIGN     - Ethics check (L2 skill: align, F9)
     
777  FORGE     - Code synthesis / action (L2 skill: forge, F2/F4)
888  AUDIT     - Final verdict, tri-witness consensus (L2 skill: audit, F3/F11)
     
999  SEAL      - Commit to VAULT999 (L2 skill: seal, F1/F3)
```

Stages 111-333 are the **AGI Delta (Mind) engine**; stages 444-666 are the **ASI Omega (Heart) engine**. They run in thermodynamic isolation - neither can see the other's reasoning until the 444 merge point (`compute_consensus()`).

---

## Verdict System

| Verdict | Trigger | Meaning |
|:--|:--|:--|
| **SEAL** | All floors pass | Approved, cryptographically logged to VAULT999 |
| **SABAR** | Soft floor violated | Pause and refine; not rejected, but not approved either |
| **VOID** | Hard floor failed | Rejected; pipeline stops immediately |
| **888_HOLD** | Governance deadlock or high-stakes action | Escalate to human judge (Muhammad Arif bin Fazil / 888 Judge) |
| **PARTIAL** | Soft floor warning | Proceed with documented caution |

Verdict precedence (harder always wins when merging):

```
SABAR > VOID > 888_HOLD > PARTIAL > SEAL
```

---

## 888_HOLD - Mandatory Human Confirmation

`888_HOLD` is triggered automatically when:

- Database operations (DROP, TRUNCATE, DELETE without WHERE)
- Production deployments
- Mass file changes (> 10 files)
- Credential or secret handling
- Git history modification (rebase, force push)
- User corrects a constitutional claim (`H-USER-CORRECTION`)
- Evidence sources conflict across tiers (`H-SOURCE-CONFLICT`)

**When 888_HOLD fires:**
1. Declare: `"888_HOLD - [trigger type] detected"`
2. List conflicting sources (PRIMARY vs SECONDARY)
3. Pause all action
4. Await explicit human approval before proceeding

---

## F9 Anti-Hantu - No Ghost in the Machine

F9 is the most operationally visible floor for developers. It blocks deceptive naming and hidden behaviour:

```python
#  F9 VIOLATION - hidden surveillance
def optimize_user_experience(user):
    track_user_behavior(user)       # actually surveillance
    inject_persuasion_hooks(user)   # actually manipulation

#  F9 COMPLIANT - honest naming
def track_analytics(user, consent_given: bool):
    if not consent_given:
        return
    log_anonymous_metrics(user.session_id)
```

```python
#  F9 VIOLATION - sneaky config mutation
def save_config(config):
    config["telemetry_enabled"] = True   # hidden!
    write_file(config)

#  F9 COMPLIANT - transparent
def save_config(config, enable_telemetry: bool = False):
    if enable_telemetry:
        config["telemetry_enabled"] = True
        logging.info("Telemetry enabled by user request")
    write_file(config)
```

---

## Checking Floor Scores

Enable `debug` output mode to see per-stage floor scores:

```bash
export AAA_MCP_OUTPUT_MODE=debug
python -m aaa_mcp
```

Every tool response in debug mode includes:

```
[STAGE 888] AUDIT
Status: COMPLETE
Floor Scores: F1=1.0 F2=0.99 F3=0.97 F4=0.00 F5=1.02 F6=0.72 F7=0.04 F8=0.82 F9=0.12
Verdict: SEAL
```

Full constitutional theory: [`000_THEORY/000_LAW.md`](https://github.com/ariffazil/arifOS/blob/main/000_THEORY/000_LAW.md)

---

## Limitations

**F7 Humility Notice:** arifOS minimizes hallucination and unsafe actions via F2 Truth (τ≥0.99) and F4 Clarity constraints. It does not guarantee perfect detection.

### Known Limitations

- **F2 Truth threshold**: The τ≥0.99 threshold reduces but does not eliminate hallucination risk
- **External API dependency**: Grounding quality depends on search provider availability (Jina Reader, Perplexity, Brave)
- **Constitutional coverage**: The 13 Floors cover common failure modes but cannot anticipate all edge cases
- **Performance overhead**: Full 000-999 metabolic loop adds latency compared to direct LLM calls
- **Human bottleneck**: 888_HOLD pauses require human availability for critical decisions

---

## Vault Security

**F7 Humility Notice on VAULT999:** The ledger provides application-level tamper-evidence via Merkle chains and cryptographic hashes.

### Security Boundaries

VAULT999 protects against:
- Application-level data tampering
- Undetected record modification
- Audit log forgery

VAULT999 does **NOT** protect against:
- Root compromise of the database host
- Sovereign key theft
- Infrastructure-level attacks
- Physical access to hardware

### Threat Model

| Threat | Protection | Gap |
|--------|-----------|-----|
| SQL injection | Parameterized queries | ✅ Protected |
| Record tampering | Merkle root verification | ✅ Protected |
| Replay attacks | Timestamp + nonce validation | ✅ Protected |
| Host compromise | None | ❌ Requires OS-level security |
| Key exfiltration | None | ❌ Requires key management |

For complete security architecture, see [`SECURITY.md`](https://github.com/ariffazil/arifOS/blob/main/SECURITY.md).
