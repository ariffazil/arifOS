# Why arifOS exists

## The problem

AI agents can now write code, move money, publish content, modify infrastructure, and access personal data. Most agent frameworks give an AI a toolbox and hope it uses the tools responsibly.

This is the equivalent of hiring an employee, handing them the company credit card, root password, and publishing credentials — and then leaving the building.

When something goes wrong, you discover:
- There is no record of what was decided or why.
- The agent that made the mistake is also the one evaluating whether it was a mistake.
- There is no way to undo what was done.
- Nobody was asked.

## What arifOS does differently

arifOS is a **gate**, not a tool. It sits between an AI agent's intent and the action it wants to take.

Before any consequential action, arifOS checks:

1. **Is there a valid session?** (Who is acting?)
2. **Is there evidence?** (What do they know? How do they know it?)
3. **Does the action risk irreversible harm?** (If yes, human approval required.)
4. **Is the agent trying to certify its own work?** (Not allowed — the Gödel Lock.)
5. **Is the decision recorded?** (Every verdict leaves a receipt.)

If the evidence is thin, the risk is high, or the agent is trying to self-authorize — arifOS returns **HOLD**. The action does not proceed.

## What a HOLD means

A HOLD is not an error. It is not a bug. It is a fence.

It means: "The evidence you provided is not sufficient to authorize this action. Bring better evidence, or ask a human."

When arifOS returns HOLD, you know the gate is working.

## Who is in charge

You are. F13 is the constitutional floor that says: **the human has the final veto**.

No AI action becomes authorized merely because an AI proposed it. The human can always say no — and when the action is irreversible, the human **must** say yes before it proceeds.

## What arifOS does NOT do

- It does not execute actions. A-FORGE executes; arifOS judges.
- It does not replace human judgment. It constrains AI judgment.
- It does not claim to be conscious, sentient, or wise. It is a gate with rules.
- It does not make decisions about what is good. It enforces whether the process was followed.

## For whom

- **If you run AI agents** and want auditable, governed behaviour instead of hoping for the best.
- **If you build AI systems** and need a separation-of-duties layer between intent and execution.
- **If you are a researcher** studying AI governance, constitutional AI, or agent safety.
- **If you are a regulator** looking for a concrete implementation of human-in-the-loop controls.

## Learn more

- [The constitution](../GENESIS/000_KERNEL_CANON.md) — the 13 floors, written as enforceable rules.
- [The floor table](../GENESIS/FLOOR_TABLE.json) — machine-readable floor definitions.
- [How to connect](../AGENT_BOOTSTRAP.md) — for agents and developers.
- [The README](../../README.md) — the front door.
