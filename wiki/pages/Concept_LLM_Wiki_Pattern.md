---
type: Concept
tags: [architecture, knowledge-management, pattern]
sources: [karpathy-llm-wiki.md]
last_sync: 2026-04-08
confidence: 0.95
---

# Concept: LLM Wiki Pattern

# Concept: LLM Wiki Pattern

## Definition

The **LLM Wiki Pattern** is a methodology for utilizing LLMs to build and maintain a persistent, structured, and interlinked knowledge base (Wiki) from raw source materials.

## Contrast with Traditional RAG

| Feature | Traditional RAG | LLM Wiki Pattern |
| --- | --- | --- |
| **Persistence** | Ephemeral context | Durable Markdown files |
| **Logic** | Re-derives per query | Compiled synthesis |
| **Maintenance** | None (automatic) | LLM-maintained (structured) |
| **Scalability** | Prompt window limits | Interlinked pages (Graph) |
| **Synthesis** | On-the-fly | Incremental & Compounding |

## Implementation Layers

1. **Raw Layer**: Immutable PDFs, notes, transcripts.
2. **Wiki Layer**: The "Compiled Codebase" of knowledge.
3. **Schema Layer**: The prompt constraints that ensure the LLM acts as a "Disciplined Librarian."

## Core Workflows

- **Ingest**: The act of reading a source once and updating all relevant nodes in the graph.
- **Query**: Using the compiled index to find synthesized answers.
- **Lint**: Automated maintenance to ensure link integrity and cross-source consistency.

## Prototypical Implementation (Karpathy Style)

- **Frontend**: Obsidian (for visualization and human interaction).
- **Backend**: LLM Coding Agent (e.g., Antigravity, Claude Code).
- **Index**: `index.md` for fast navigation without vector search.

- **Backend**: LLM Coding Agent (e.g., Antigravity, Claude Code).
- **Index**: `index.md` for fast navigation without vector search.
