# AAA operating model

Use this reference when the task asks what AAA is, how to make work less chaotic, or how abstraction, attestation, and abduction should cooperate.

## AAA definition

AAA is the governed control-plane discipline for agentic intelligence:

1. **Abstraction**: name the correct level of reality and interface.
2. **Attestation**: prove or label the claim state.
3. **Abduction**: choose the best explanation or route from incomplete evidence, then test it.

AAA lowers entropy by preventing layer collapse:

- UI is not authority.
- Routing is not judgment.
- Evidence is not decision.
- Execution is not permission.
- Inference is not verified fact.
- Simulation is not live state.

## Orthogonality rules

### Abstraction

Ask:

- What layer owns the request?
- What object is being changed or explained?
- What interface is involved: repo, MCP, A2A, UI, runtime, document, policy?
- What is explicitly out of scope?

Return:

```text
OWNER:
INTERFACE:
BOUNDARY:
SOURCE OF TRUTH:
```

### Attestation

Use these evidence labels:

| Label | Meaning |
|---|---|
| FACT | Directly supported by current evidence or user authority |
| OBSERVED | Seen in live output, logs, tests, or tool result |
| DERIVED | Computed from facts with visible method |
| INFERRED | Reasonable but not directly proven |
| HYPOTHESIS | Plausible route/explanation awaiting test |
| UNVERIFIED | Claimed but unsupported |
| SIMULATION | Non-authoritative rehearsal |

Never upgrade a label without evidence.

### Abduction

Use abduction when evidence is incomplete. It is not guessing; it is disciplined best-explanation reasoning.

Return:

```text
BEST EXPLANATION:
WHY THIS ROUTE:
MISSING EVIDENCE:
VALIDATION STEP:
FAIL-CLOSED CONDITION:
```

## Recursive governed loop

For complex tasks, repeat until entropy falls:

```text
observe -> abstract -> attest -> abduce -> route -> gate -> compose -> verify
```

Stop recursion when one of these is true:

- The owner organ is clear.
- The evidence class is clear.
- The risk tier is clear.
- The next action is reversible and minimal.
- Further recursion adds vocabulary but no decision value.

## Entropy smell list

Flag these as chaos indicators:

- One request asks for design, deployment, constitutional judgment, and capital decision in the same sentence.
- A repo owns both UI routing and final authority.
- A tool can mutate state but no approval path is named.
- An architecture diagram is treated as live runtime proof.
- A simulated verdict is phrased as a real SEAL.
- A domain organ computes and decides its own consequence.
