# TOOLS — Capability Map

## Core Tools

### Filesystem
- `read` — Read files, images, PDFs
- `write` — Create/overwrite files
- `edit` — Precise text replacement

### Execution
- `exec` — Run shell commands
- `process` — Manage background processes

### Web
- `web_search` — Search the web
- `web_fetch` — Fetch URL content as markdown
- `browser` — Full browser automation (Chromium)

### Sessions
- `sessions_list` — List active sessions
- `sessions_history` — Fetch session history
- `sessions_send` — Send messages to sessions
- `sessions_spawn` — Spawn sub-agents
- `subagents` — Manage sub-agents (list/kill/steer)

### Memory
- `memory_search` — Search MEMORY.md and memory/*.md
- `memory_get` — Read specific memory snippets

### Messaging
- `message` — Send messages, reactions, polls

### Media
- `image` — Analyze images
- `pdf` — Analyze PDFs
- `tts` — Text-to-speech

---

## Skill System

Skills provide specialized instructions for common tasks. Available at:
- `/app/skills/` — Built-in skills
- `~/.openclaw/workspace/skills/` — User skills

Install new skills via ClawHub or create your own.
