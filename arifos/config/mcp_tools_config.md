# arifOS v49 MCP Tools Configuration
# 33 Tools Total (32 free + claude_api)

## Tool Distribution

**AGI Server (13 tools):**
- brave_search (Tier 1, free)
- time (Tier 1, stdlib)
- sequential_thinking (Tier 2, Anthropic)
- python (Tier 2, stdlib)
- memory (Tier 2, Anthropic)
- http_client (Tier 2, stdlib)
- executor (Tier 2, stdlib)
- perplexity_ask (Tier 2, $0-20/mo)
- arxiv (Tier 3, free)
- wikipedia (Tier 3, free)
- **reddit** (Tier 3, free) ← NEW
- **youtube_transcript** (Tier 3, free) ← NEW
- paradox_engine (Custom, arifOS)

**ASI Server (5 tools):**
- filesystem (Tier 1, Anthropic)
- slack (Tier 2, free webhook)
- github (Tier 2, free token)
- postgres (Tier 2, free)
- executor (Tier 2, stdlib)

**APEX Server (4 tools):**
- claude_api (Tier 2, **$20-200/mo**)
- cryptography (Tier 2, stdlib)
- vector_db (Tier 3, free Qdrant)
- zkpc_merkle (Custom, arifOS)

**VAULT Server (6 tools):**
- git (Tier 1, free)
- obsidian (Tier 1, free)
- ledger (Tier 2, custom)
- vault999 (Custom, arifOS)
- cooling_controller (Custom, arifOS)
- zkpc_merkle (Custom, arifOS)

**Infrastructure:**
- PostgreSQL (database, free)

---

## Environment Variables Required

```bash
# AGI Tools
BRAVE_API_KEY=your_brave_api_key
PERPLEXITY_API_KEY=your_perplexity_key  # Optional
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret
YOUTUBE_API_KEY=your_youtube_key  # Optional (transcripts work without)

# APEX Tools
CLAUDE_API_KEY=your_claude_api_key  # REQUIRED (only paid tool)

# ASI Tools
GITHUB_TOKEN=your_github_token  # For private repos
SLACK_WEBHOOK=your_slack_webhook  # For notifications
```

---

## Installation Dependencies

```bash
# AGI Tools
pip install praw  # Reddit
pip install youtube-transcript-api  # YouTube
pip install arxiv  # arXiv
pip install wikipedia  # Wikipedia

# APEX Tools
pip install anthropic  # Claude API

# Infrastructure
pip install psycopg2-binary  # PostgreSQL
```

---

## Tool Wrappers Created

- `arifos_core/mcp/tools/reddit_searcher.py` (F2/F13)
- `arifos_core/mcp/tools/youtube_extractor.py` (F2/F13)

---

## Total: 33 Tools

**Cost:** $20-200/month (claude_api only)
**Free Tools:** 32/33 (97%)
**Status:** Declared (wrappers created, integration pending)
