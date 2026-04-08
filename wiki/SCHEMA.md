# Ω-Wiki CONSTITUTION (SCHEMA.md)

> **Authority**: arifOS Sovereign Kernel
> **Version**: 2026.04.08
> **Motto**: Compilation over Retrieval

## 1. Governance Principles

- **F2 Truth**: Every claim must cite a source from `wiki/raw/`.
- **F3 Tri-Witness**: Significant synthesis must be cross-verified across at least 3 sources if available.
- **F11 Audit**: Every change must be logged in `wiki/log.md`.
- **F9 Ethics**: Contradictions between sources must be surfaced, not buried.

## 2. Directory Structure

- `wiki/raw/`: Immutable sources (Original PDFs, MD clips, Data).
- `wiki/pages/`: LLM-generated persistent synthesis.
- `wiki/index.md`: Content-oriented catalog.
- `wiki/log.md`: Chronological log of operations.

## 3. Page Types & Conventions

Every page in `wiki/pages/` must include YAML frontmatter:

```yaml
---
type: [Entity | Concept | Source | Synthesis]
tags: [tag1, tag2]
sources: [source1.md, source2.pdf]
last_sync: YYYY-MM-DD
confidence: [0.0 - 1.0]
---
```

### Page Hierarchies

- **Entities**: Unique identifiers for people, projects, or hardware (e.g., `Andrej_Karpathy.md`).
- **Concepts**: Definitions and deep-dives (e.g., `LLM_Wiki_Pattern.md`).
- **Sources**: Detailed summaries of items in `wiki/raw/`.
- **Synthesis**: Comparison tables, timelines, and "State of the Art" overviews.

## 4. Workflows

### Ingest Workflow

1. Read the source from `wiki/raw/`.
2. Generate a `Source` page summary.
3. Identify relevant `Entity` or `Concept` pages.
4. Update existing pages with new information.
5. Flag contradictions with existing wiki content.
6. Append entry to `wiki/log.md`.
7. Refresh `wiki/index.md`.

### Lint Workflow

1. Check for broken internal links.
2. Identify "Orphan" pages (no inbound links).
3. Identify "Ghosts" (concepts mentioned but not yet defined).
4. Verify source citations.

## 5. Metadata Standards

## 6. NotebookLM Bridge Protocol

### 6.1 Purpose
NotebookLM acts as an external **Synthesis Engine**. Insights generated there must be anchored into the Sovereign Wiki to ensure they survive the ephemeral Nature of AI chat sessions.

### 6.2 Ingest Workflow
1. **Source Drop**: User places NotebookLM exports (Study Guides, Transcripts) into `wiki/raw/notebooklm/`.
2. **Identification**: Pages synthesized from this source must include the `origin: NotebookLM` tag in YAML.
3. **Citation**: Cite the specific Notebook URL where available.
4. **Validation**: The agent must verify if NotebookLM's "AI Insights" contradict existing `arifOS` core laws (e.g. ΔΩΨ architecture). If a contradiction exists, the contradiction must be flagged using `> [!CAUTION] CONTRADICTION`.

### 6.3 Page Types
- **Synthesis (NotebookLM)**: A high-level overview of a specific notebook.
- **Concept (Derived)**: Deep-dives into specific entities mentioned within the notebook.
