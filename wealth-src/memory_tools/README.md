# Memory Pipeline v1.1

This is the offline-first memory system for OpenClaw workspace memory.

Canonical source:
- `memory/YYYY-MM-DD.md`
- optional `## Retain` section with typed bullets

Derived index:
- `.memory/index.sqlite` (SQLite + FTS5)

Generated summaries:
- `bank/world.md`
- `bank/experience.md`
- `bank/opinions.md`
- `bank/entities/*.md`

## Retain Format

Inside each daily file, add:

```md
## Retain
- W @Peter: Currently in Marrakech (Nov 27-Dec 1, 2025) for Andy's birthday.
- B @warelay: Fixed Baileys WS crash by wrapping connection.update handlers in try/catch.
- O(c=0.95) @Peter: Prefers concise replies (<1500 chars) on WhatsApp.
```

Type keys:
- `W` = world fact
- `B` = experience/biographical
- `O(c=...)` = opinion with confidence
- `S` = summary

## Commands

From workspace root:

```bash
python3 memory_tools/memory_pipeline.py --workspace /root/openclaw_data/workspace index --rebuild
python3 memory_tools/memory_pipeline.py --workspace /root/openclaw_data/workspace recall "kimi cost" --k 10
python3 memory_tools/memory_pipeline.py --workspace /root/openclaw_data/workspace reflect
python3 memory_tools/memory_pipeline.py --workspace /root/openclaw_data/workspace doctor
python3 memory_tools/memory_pipeline.py --workspace /root/openclaw_data/workspace env-lint --env-file /root/XXX/.env.master

# semantic v1.1
# MEMORY_EMBED_MODEL is optional; pipeline auto-resolves installed Ollama model
python3 memory_tools/memory_pipeline.py --workspace /root/openclaw_data/workspace semantic-upsert
python3 memory_tools/memory_pipeline.py --workspace /root/openclaw_data/workspace semantic-search "kimi preference" --k 5
python3 memory_tools/memory_pipeline.py --workspace /root/openclaw_data/workspace recall "kimi" --hybrid --k 10

# quick retain write helper
python3 memory_tools/memory_pipeline.py --workspace /root/openclaw_data/workspace retain-add "W @Arif: Example durable fact"

# daily retain consistency helper
python3 memory_tools/memory_pipeline.py --workspace /root/openclaw_data/workspace retain-daily --min-count 3
```

## Environment Variables

- `QDRANT_URL` (default: `http://127.0.0.1:6333`)
- `QDRANT_API_KEY` (required if Qdrant auth enabled)
- `MEMORY_QDRANT_COLLECTION` (default: `openclaw_workspace_memory`)
- `OLLAMA_BASE_URL` (default: `http://127.0.0.1:11434`)
- `MEMORY_EMBED_MODEL` (optional; auto-resolved if unset)
- `OPENCLAW_ENV_FILE` (optional, for `run_cycle.sh`; default: `/root/XXX/.env.master`)

## Why this architecture

- Markdown remains human-auditable source of truth.
- SQLite index is rebuildable and fast for retrieval.
- `bank/` files are durable summaries for low-token agent context.
- Works fully offline.
