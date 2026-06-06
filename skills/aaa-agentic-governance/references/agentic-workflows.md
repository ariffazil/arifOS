# Agentic workflows

Use this file for repeatable AAA/arifOS task patterns.

## Workflow A: explain a federation concept

```text
1. Identify whether the user asks about AAA, arifOS, A-FORGE, GEOX, WEALTH, WELL, or profile context.
2. Abstract the owner layer and boundary.
3. Attest what is known from repo/tool/user evidence.
4. Explain in simple operator language.
5. State what is unverified and what would verify it.
```

Response:

```text
WHAT IT IS:
OWNER:
DOES:
DOES NOT:
HOW IT CONNECTS:
UNVERIFIED:
```

## Workflow B: route a request

```text
1. Extract domain nouns and verbs.
2. Classify the action: read, analyze, plan, mutate, deploy, decide, seal.
3. Map to the organ table.
4. Assign risk tier.
5. Produce route, evidence needed, and gates.
```

Example:

```text
Request: Evaluate a drilling prospect and decide whether to commit capital.
Route: GEOX evidence -> WEALTH economics -> arifOS judgment -> F13 final decision.
Risk: Tier 2 or Tier 3 if real allocation or irreversible commitment is implied.
```

## Workflow C: reduce entropy in a chaotic request

Use when the user asks for many overlapping agentic/governance concepts at once.

```text
1. List the overloaded concepts.
2. Collapse aliases into canonical names.
3. Separate abstraction, attestation, and abduction.
4. Split mixed-risk actions into separate tasks.
5. Return one clean operating model and one next step.
```

Template:

```text
CHAOS SOURCES:
CANONICAL TERMS:
ORTHOGONAL MODEL:
RISK SPLIT:
NEXT ACTION:
```

## Workflow D: multi-repo implementation plan

```text
1. Read source-of-truth docs for each affected repo when available.
2. Confirm owner boundaries.
3. Define interfaces between repos.
4. Split implementation into reversible patches.
5. Add tests at owner layer.
6. State deployment/secret/external gates.
```

Template:

```text
INTENT:
TARGET REPOS:
OWNER ORGAN:
ABSTRACTION:
ATTESTATION:
ABDUCTION:
RISK TIER:
PATCH PLAN:
TEST PLAN:
HOLD CONDITIONS:
ROLLBACK:
```

## Workflow E: repo/code review under AAA governance

Check for:

- Wrong-layer logic.
- Missing source-of-truth.
- Unattested claims.
- Self-authorization.
- Prompt/tool injection.
- Shell, secret, auth, deploy, or destructive command risk.
- Broad formatting churn.

Review output:

```text
BLOCKING:
CAUTION:
QUESTIONS:
TESTS TO RUN:
ATTESTATION GAPS:
```

## Workflow F: AREP/task declaration

Create the task object only after the intent is clear enough.

```json
{
  "intent": "clear human declaration",
  "target_organs": [],
  "abstraction": {
    "owner_organ": "",
    "interface": "",
    "boundary": ""
  },
  "attestation": {
    "reality_layer": "UNVERIFIED",
    "evidence_refs": [],
    "claim_limits": []
  },
  "abduction": {
    "best_route": [],
    "missing_evidence": [],
    "validation_step": ""
  },
  "risk_tier": 0,
  "hold_conditions": [],
  "expected_artifacts": []
}
```
