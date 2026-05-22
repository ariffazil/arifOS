---
type: Tool
tier: 20_RUNTIME
strand:
- tools
- research
- web
audience:
- engineers
- researchers
- operators
difficulty: beginner
prerequisites:
- MCP_Tools
- Skill_MCP_Mcporter
tags:
- searxng
- search
- meta-search
- web-search
- privacy
- self-hosted
- free
- no-api-key
sources:
- Hermes official skill: official/research/searxng-search
- SearXNG docs: https://docs.searxng.org
- GitHub: https://github.com/searxng/searxng
last_sync: '2026-05-18'
confidence: 0.95
---

# Skill: SearXNG — Meta-Search

**SearXNG** is the privacy-respecting, self-hosted meta-search engine that aggregates results from 70+ search engines simultaneously. No API key required. The canonical free search fallback for the arifOS Federation.

## Purpose

To give federation agents a search capability that:
- Requires **no API key** — free forever
- Aggregates 70+ engines (Google, Brave, DuckDuckGo, Bing, Wikipedia, and more)
- Respects privacy — no tracking, no profiling
- Can be self-hosted for full control
- Automatically falls back when paid search APIs are unavailable or rate-limited

## Specifications

- **Stage**: 111 (Sensing) + 222 (Fetch)
- **Layer**: WEB
- **Trinity**: Δ (Mind — grounding against web reality)
- **Floors touched most directly**: F2 (Truth — multi-engine cross-verification), F4 (Guardrails — safe search levels), F9 (Anti-Hantu — no single-source dependency)

## Instance

**Self-hosted on this VPS:**
- **URL**: `http://127.0.0.1:8888`
- **Container**: `searxng` (Docker, `unless-stopped` restart)
- **Config**: `/root/compose/searxng-config/settings.yml`
- **Port**: 8888 (localhost only — not exposed externally)
- **Env**: `SEARXNG_URL=http://127.0.0.1:8888`

**Hermes config updated:** `terminal.env_passthrough` includes `SEARXNG_URL`

## Installation (Self-Host)

```bash
# Docker (already deployed on this host)
docker run -d --name searxng \
  --restart unless-stopped \
  -p 127.0.0.1:8888:8080 \
  -v /root/compose/searxng-config:/etc/searxng \
  -e SEARXNG_SECRET="your-secret-key" \
  searxng/searxng:latest
```

**Required settings** (`/etc/searxng/settings.yml`):
```yaml
server:
  limiter: false        # Disable for internal use
  bind_address: "0.0.0.0"

search:
  formats:
    - html
    - json
    - csv
    - rss
```

## Usage

### CLI via curl (preferred)
```bash
# Basic search
SEARXNG_URL="http://127.0.0.1:8888"
curl -s --max-time 10 \
  "${SEARXNG_URL}/search?q=python+async+programming&format=json&limit=10"

# Specific engines
curl -s --max-time 10 \
  "${SEARXNG_URL}/search?q=AI+news&format=json&engines=google,bing&limit=5"

# Category filter
curl -s --max-time 10 \
  "${SEARXNG_URL}/search?q=quantum+computing&format=json&categories=science&limit=5"

# Recency filter
curl -s --max-time 10 \
  "${SEARXNG_URL}/search?q=llama+4&format=json&time_range=week&limit=10"
```

### Python via requests
```python
import os, requests

base_url = os.environ.get("SEARXNG_URL", "http://127.0.0.1:8888")

params = {
    "q": "fastapi deployment guide",
    "format": "json",
    "limit": 5,
    "engines": "google,bing,brave",
}

resp = requests.get(f"{base_url}/search", params=params, timeout=10)
data = resp.json()

for r in data.get("results", []):
    print(r["title"])
    print(r["url"])
    print(r.get("content", "")[:200])
    print()
```

## CLI Flags

| Flag | Description | Example |
| :--- | :--- | :--- |
| `q` | Query string (URL-encoded) | `q=python+async` |
| `format` | Output format | `format=json` |
| `engines` | Comma-separated engine names | `engines=google,bing,ddg` |
| `limit` | Max results per engine | `limit=5` |
| `categories` | Filter by category | `categories=news,science` |
| `safesearch` | 0=none, 1=moderate, 2=strict | `safesearch=0` |
| `time_range` | day, week, month, year | `time_range=week` |

## Result Schema

```json
{
  "query": "arifOS",
  "number_of_results": 0,
  "results": [
    {
      "title": "...",
      "url": "...",
      "content": "...",
      "engine": "google",
      "engines": ["google", "brave"],
      "score": 9.0,
      "category": "general",
      "publishedDate": null
    }
  ],
  "suggestions": ["..."],
  "unresponsive_engines": [["startpage", "CAPTCHA"]]
}
```

## Workflow: Search then Extract

SearXNG returns titles, URLs, and snippets — not full page content. To get full content:

```bash
# 1. Search for relevant pages
results=$(curl -s "${SEARXNG_URL}/search?q=fastapi+deployment&format=json&limit=3")

# 2. Extract the best URL with parallel-cli, web_extract, or curl
curl -s "$(echo $results | jq -r '.results[0].url')" | html2text
```

## Federation Context

- **Hermes**: Skill installed at `~/.hermes/skills/research/searxng-search/`
- **A-FORGE / arifOS**: Can query via ShellTool or HTTP client
- **No API key**: Completely free, self-hosted
- **Fallback**: Automatically used when Brave Search / Firecrawl APIs are rate-limited or unavailable
- **Contrast with Parallel CLI**: SearXNG = quick meta-search (free); Parallel = deep research + enrichment (paid)

## Search Stack Priority

| Need | Tool | Cost |
| :--- | :--- | :--- |
| Quick fact lookup | SearXNG | Free |
| Deep research | Parallel CLI | Paid |
| AI-powered synthesis | Inference.sh | Per-use |
| Structured web data | mcporter + MCP | Free / API key |

## Pitfalls

| Problem | Fix |
| :--- | :--- |
| `SEARXNG_URL` not set | `export SEARXNG_URL=http://127.0.0.1:8888` |
| 403 Forbidden | Check `server.limiter: false` in settings.yml |
| Empty results | Try different engines or check instance health |
| Slow responses | Some engines may be slow; use `engines=` to narrow |
| JSON not supported | Ensure `search.formats` includes `json` |
| Public instances rate-limit | Self-host (already done on this VPS) |

## Related

- [[Skill_Parallel_CLI]] (Deep research — complementary paid tier)
- [[Skill_Inference_CLI]] (AI app gateway)
- [[Skill_MCP_Mcporter]] (MCP mesh CLI)
- [[MCP_Tools]] (Tool surface architecture)
