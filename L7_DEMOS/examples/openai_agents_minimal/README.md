# OpenAI Agents Minimal Example

This folder is a placeholder for a minimal OpenAI Agents / Assistants setup.

Suggested pattern:

- Your assistant/tool logic does its normal reasoning.
- Wrap final answer emission with `arifos_core.apex_guardrail`
  to evaluate floors (truth, ΔS, Peace², κᵣ, Ω₀, Amanah, Tri-Witness, Ψ)
  and log Cooling Ledger entries for sealed answers.

This keeps your existing agent logic,
but subjects all answers to ArifOS constitutional governance.
