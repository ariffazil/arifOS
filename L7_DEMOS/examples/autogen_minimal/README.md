# AutoGen Minimal Example

This folder is a placeholder for a minimal AutoGen multi-agent setup.

Suggested pattern:

- One agent running in an "ARIF mode" for reasoning.
- One agent running in an "ADAM mode" for empathy and safety.
- A final APEX agent (or wrapper) that evaluates floors and decides SEAL / PARTIAL / VOID.

Use `arifos_core.apex_guardrail` around your answer-generation function
to enforce the ArifOS floors and log Cooling Ledger entries.
