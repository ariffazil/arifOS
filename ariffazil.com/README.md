# ariffazil.com — Trinity Static Sites

**Status:** Ready for extraction into separate repo (`arifOS-trinity`)

This directory contains all static website layers for the arif-fazil.com domain ecosystem.

## Structure

```
ariffazil.com/
├── body/       ← arif-fazil.com (Portfolio & Dashboard)
│   ├── src/    ← React 19 + Vite + TailwindCSS
│   ├── public/ ← Static assets
│   └── Dockerfile
├── soul/       ← apex.arif-fazil.com (Constitutional Canon)
│   ├── src/    ← React 19 + Vite + TailwindCSS
│   └── public/
├── docs/       ← arifos.arif-fazil.com (Documentation)
│   ├── src/    ← React 18 + Vite
│   └── Dockerfile
├── shared/     ← Deduplicated image assets
├── legacy/     ← Old dashboards, static HTML
└── README.md
```

## Domain Mapping

| Layer | Domain | Source | Deploy |
|-------|--------|--------|--------|
| BODY | arif-fazil.com | `body/` | Cloudflare Pages |
| SOUL | apex.arif-fazil.com | `soul/` | Cloudflare Pages |
| DOCS | arifos.arif-fazil.com | `docs/` | Cloudflare Pages |
| MIND | aaamcp.arif-fazil.com | `codebase/` (MCP server) | Railway |

## Migration to Separate Repo

To extract into `arifOS-trinity`:

```bash
# From arifOS root
cp -r ariffazil.com /tmp/arifOS-trinity
cd /tmp/arifOS-trinity
git init
git add .
git commit -m "init: Trinity static sites extracted from arifOS"
gh repo create ariffazil/arifOS-trinity --public --source=.
git push -u origin main
```

Then update Cloudflare Pages projects to point at `arifOS-trinity` repo.

## Dev

```bash
# BODY
cd body && npm ci && npm run dev

# SOUL
cd soul && npm ci && npm run dev

# DOCS
cd docs && npm ci && npm run dev
```

## Build

```bash
cd body && npm run build   # Output: body/dist/
cd soul && npm run build   # Output: soul/dist/
cd docs && npm run build   # Output: docs/dist/
```
