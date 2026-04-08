---
type: Source
tags: [knowledge-management, llm, workflow]
sources: [karpathy-llm-wiki.md]
last_sync: 2026-04-08
confidence: 1.0
---

# Source: LLM Wiki (Karpathy Gist)

## Overview

A concise blueprint shared by Andrej Karpathy (April 2026) describing a pattern for building personal knowledge bases using LLMs. The core thesis is **Compilation over Retrieval**.

## Key Takeaways

- **The Problem**: Traditional RAG is ephemeral and forces the LLM to re-derive knowledge from scratch on every query.
- **The Solution**: An LLM-maintained wiki where knowledge is incrementally compiled into structured, interlinked markdown files.
- **The Architecture**:
    - **Raw Sources**: Immutable truth.
    - **The Wiki**: Persistent synthesis.
    - **The Schema**: Operational rules (e.g., `CLAUDE.md`).

- **Core Operations**: Ingest, Query, Lint.
- **Compounding Value**: The wiki gets richer over time; cross-references and contradictions are handled once and maintained.

## Related

- [[Concept_LLM_Wiki_Pattern]]
- [[Entity_Andrej_Karpathy]]
