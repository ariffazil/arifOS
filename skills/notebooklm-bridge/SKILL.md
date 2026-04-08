---
name: notebooklm-bridge
description: Bridging Google NotebookLM insights into the Sovereign Ω-Wiki.
user-invocable: true
---

# NotebookLM Bridge Skill

This skill allows the agent to process exports from Google NotebookLM and synthesize them into the `arifOS` Ω-Wiki.

## Use Cases
- "Ingest my latest NotebookLM study guide."
- "What-is-arifOS.md out of sync with my NotebookLM deep dive? Update it."
- "Translate this transcript into wiki concepts."

---

## ⚙️ Ingest Workflow

When a user provides context from NotebookLM:

1.  **Extract Sources**: Identify which raw documents were used by NotebookLM (often listed in citations).
2.  **Verify Confidence**: NotebookLM can hallucinate or over-simplify. Compare its claims against the arifOS `000/` laws.
3.  **Synthesize**:
    - Create a `Source_NotebookLM_[Topic].md` page.
    - Identify existing `Concept` pages and update them with new insights.
    - Tag with `origin: NotebookLM` and `confidence: [Estimated]`.
4.  **Audit**: Log the ingest in `wiki/log.md`.

---

## 🏛️ Constitutional Constraints

- **F2 (Truth)**: Do not accept a NotebookLM claim as "Ground Truth" if it contradicts the local `arifOS` repository code. 
- **F9 (Ethics)**: If NotebookLM generates a "Audio Overview" that anthropomorphizes the agent too much, flag it as a "Tone Variance" in the synthesis.
- **F11 (Audit)**: Mandatory log of the ingest.

---

## Example Ingest Prompt for the User

> "I have copied my NotebookLM Study Guide into `wiki/raw/notebooklm/roadmap_deep_dive.md`. Run the `notebooklm-bridge` skill to integrate these insights."
