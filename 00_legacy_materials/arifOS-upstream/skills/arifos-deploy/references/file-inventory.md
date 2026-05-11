# File Inventory — arifOS Hub

**Status:** OPERATIONAL

---

## Machine Discovery Files (Must Be at Root, Canonical Paths)

These files must always be served at these exact paths on arifOS-fazil.com. No redirects, no SPA routing, no path changes.

### `/llms.txt`
- **Purpose:** LLM context injection for AI agents reading this site
- **Content:** Plain text overview of arifOS — what it is, architecture summary, endpoints, repositories
- **Generated from:** `arifOS/MEMORY.md`, `arifOS/SOUL.md`, `arifOS/REPOS.md`
- **Content-Type:** `text/plain; charset=utf-8`
- **Update trigger:** Any change to MEMORY.md, SOUL.md, REPOS.md, or this file directly

### `/robots.txt`
- **Purpose:** Crawler control
- **Content:** `User-agent: *`, `Allow: /`, `Sitemap:` pointing to /sitemap.xml
- **Content-Type:** `text/plain`

### `/sitemap.xml`
- **Purpose:** Search engine indexing
- **Format:** Standard XML sitemap
- **Content-Type:** `application/xml`
- **Update trigger:** New pages added to hub

### `/.well-known/agent.json`
- **Purpose:** AI agent self-service discovery
- **Generated from:** `waw/.well-known/agent.json`
- **Content-Type:** `application/json`
- **Fields:** name, description, url, version, author, mcpServers, protocols, capabilities, constitutionalFloors, trinity, verdicts, repositories, license

### `/.well-known/ai-plugin.json`
- **Purpose:** Plugin manifest for AI tool integrations
- **Source:** `arifOS/docs/ai-plugin.json`
- **Content-Type:** `application/json`

---

## Static Site Pages

### Hub Root Files
```
sites/arifOS-fazil.com-source/
├── pages/
│   └── index.html          → https://arifOS-fazil.com/ (homepage)
├── assets/
│   └── style.css           → https://arifOS-fazil.com/assets/style.css
└── stack/
    └── architecture.json   → (optional architecture manifest)
```

### Planned Subpages (after State A)
```
pages/
├── guides/
│   ├── quickstart.html     → How to connect via MCP
│   └── connect.html        → MCP client setup guide
└── projects/
    ├── arifOS.html         → Project summary with link to GitHub
    ├── GEOX.html           → Project summary with link to GitHub
    └── makcikGPT.html      → Project summary with link to GitHub
```

---

## Build Output

When `deploy-hub.yml` runs, it uploads the entire `sites/arifOS-fazil.com-source/` directory as the GitHub Pages artifact. No separate build step — files are served as-is.

If a build step is added later (e.g., minification, image processing), the output directory becomes the Pages artifact, not the source.

---

## Content Type Reference

| File pattern | Content-Type | Notes |
|-------------|-------------|-------|
| `*.html` | text/html | |
| `*.css` | text/css | |
| `*.js` | application/javascript | |
| `*.svg` | image/svg+xml | |
| `*.json` | application/json | |
| `*.txt` | text/plain | |
| `*.xml` | application/xml | |
| `/.well-known/*` | varies | Per MIME type of file |
