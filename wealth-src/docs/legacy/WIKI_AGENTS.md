# WIKI_AGENTS.md — WEALTH LLM Wiki Maintenance Schema

> For AI agents maintaining the `wiki/` and `raw/` layers of the WEALTH repository.
> Based on the llm-wiki pattern by Andrej Karpathy.
> DITEMPA BUKAN DIBERI — 999 SEAL ALIVE

---

## Purpose

This repository contains a **Karpathy-style LLM wiki** for the WEALTH/arifOS knowledge domain. The wiki is a persistent, compounding knowledge base that sits between raw sources and the user.

## Three Layers

```
raw/      → Immutable source documents (canonical repo docs, external articles, reports)
wiki/     → LLM-generated markdown files (synthesis, entity pages, concept pages)
WIKI_AGENTS.md → This schema — tells the LLM how to maintain the wiki
```

## Directory Conventions

- `raw/` — Copy canonical documents here before ingesting. Never edit files in `raw/`.
- `wiki/` — All wiki pages live here. Use lowercase filenames with hyphens.
- `wiki/index.md` — Content catalog. Update after every ingest.
- `wiki/log.md` — Append-only chronological log of ingests, queries, and lint passes.

## Page Types

| Prefix | Purpose | Example |
|--------|---------|---------|
| `concept-*.md` | Idea, principle, or framework | `concept-maruah.md` |
| `entity-*.md` | System, organization, or person | `entity-arifos.md` |
| `synthesis-*.md` | Cross-cutting analysis | `synthesis-foundations-of-wealth.md` |
| `source-*.md` | Summary of a specific raw document | `source-trinity.md` |

## Ingest Workflow

When a new source arrives in `raw/`:

1. Read the source.
2. Discuss key takeaways.
3. Write or update `source-<name>.md`.
4. Update relevant `concept-*.md` and `entity-*.md` pages.
5. Update `wiki/index.md`.
6. Append an entry to `wiki/log.md`.

## Query Workflow

When the user asks a question:

1. Read `wiki/index.md` to find relevant pages.
2. Read the relevant wiki pages.
3. Synthesize an answer with citations.
4. If the answer reveals a valuable new synthesis, file it as a new wiki page.

## Lint Workflow

Run periodically:

1. Check for contradictions between pages.
2. Find stale claims superseded by newer sources.
3. Identify orphan pages with no inbound links.
4. List missing concept pages for important terms.
5. Suggest new questions to investigate.
6. Log the lint pass in `wiki/log.md`.

## Format Rules

- All wiki pages must have YAML frontmatter: `title`, `date`, `tags`.
- Cross-reference other wiki pages using `[[page-name]]` style or direct relative links.
- Keep pages under 400 lines when possible; split if they grow too large.
- Use tables for comparisons.
- End every synthesis page with the 999 SEAL marker.

---
*Schema version: 1.0.0 | Last updated: 2026-04-13*
