# Caddy Patch F7-0a — proposed (NOT applied)

> **Forged 2026-06-02 19:35 UTC under F13 SOVEREIGN ratification.**
> Per CLAUDE.md: "Caddy is a sovereign-locked file. /etc/caddy/Caddyfile has stale port mappings (see FEDERATION_INVENTORY.md §4). **Do NOT edit it without explicit Arif approval** — document the drift and surface it."
>
> This is the **proposed diff**, not an apply. Caddyfile snapshot saved at `Caddyfile.pre-f7-2026-06-02-19-35.snapshot` (20,020 bytes).

## Why this patch

The arifOS audit at `bb5e83b6` captured live operator mission strings on the public AAA Cockpit (`aaa.arif-fazil.com/`), including inappropriate text. F1 AMANAH dignity breach.

The **real fix** is the server-side redaction in AAA, committed at `66e14da3` (this session). That patch redacts operator text at the `/operator/events` endpoint.

This Caddy patch is the **interim shield** until the AAA `66e14da3` deploys to production. It:
- Tells search engines and crawlers not to index the surface
- Prevents caching of the live mission stream
- Is reversible (just remove the `header` block)

## How to apply

The sovereign runs:

```bash
cd /etc/caddy
patch Caddyfile /root/arifOS/docs/Caddyfile.F7-0a-proposed.patch
caddy validate --config /etc/caddy/Caddyfile
systemctl reload caddy
```

If `patch` is unavailable, the user can edit manually: open `/etc/caddy/Caddyfile`, find `aaa.arif-fazil.com {` block (line 490), paste the header block right after `root * /var/www/html/aaa`.

## How to revert

```bash
cp /root/arifOS/docs/Caddyfile.pre-f7-2026-06-02-19-35.snapshot /etc/caddy/Caddyfile
systemctl reload caddy
```

## Scope (this patch only)

- `aaa.arif-fazil.com` block (lines 490–529)
- Adds a `header` directive with three lines: X-Robots-Tag, Cache-Control, Pragma
- Touches nothing else

## Out of scope (separate PRs)

The audit also flagged:
- F1 (MakCikGPT misroute) — needs routing decision
- F2 (well.arif-fazil.com 404) — needs organ restoration
- F3 (dashboard-v2 404) — needs nav edit in arif-sites
- F4 (mcp.arif-fazil.com redirect) — needs gateway architecture
- F5 (apex→AAA) — needs APEX surface rebuild
- F6 (canon 404s) — needs SPA route or remove links
- F10 (wiki port 8080) — one-line wiki fix
- F11 (wiki overclaim) — needs live state sync
- F13 (forge stub) — needs A-FORGE decision

These are all PR 2/3/4 territory. F7-0a is the P0 dignity shield only.
