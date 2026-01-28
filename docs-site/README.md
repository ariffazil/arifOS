# arifOS Pages Redirect

This folder contains the Cloudflare Pages redirect setup for `arifos.pages.dev`.

## Purpose

Redirect all traffic from `arifos.pages.dev` → `https://arif-fazil.com/arifos`

This consolidates all arifOS web presence to the single Railway deployment.

## Files

| File | Purpose |
|------|---------|
| `_redirects` | Cloudflare Pages redirect rules (301 permanent) |
| `index.html` | Fallback HTML with meta refresh for browsers |

## Deployment Instructions

### Option A: Deploy via Wrangler CLI (Recommended)

```bash
# Install Wrangler if not already installed
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Deploy the redirect
wrangler pages deploy . --project-name=arifos
```

### Option B: Deploy via Git Integration

1. Push this `docs-site/` folder to a GitHub repo
2. Go to [Cloudflare Dashboard](https://dash.cloudflare.com) → Pages
3. Create new project → Connect to GitHub
4. Select the repo with this folder
5. Build settings:
   - Build command: (leave empty)
   - Build output: `/`
6. Deploy

### Option C: Direct Upload

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com) → Pages
2. Select `arifos` project
3. Create deployment → Upload assets
4. Select both `_redirects` and `index.html`
5. Deploy

## Redirect Behavior

```
arifos.pages.dev/           → 301 → https://arif-fazil.com/arifos
arifos.pages.dev/docs       → 301 → https://arif-fazil.com/arifos
arifos.pages.dev/anything   → 301 → https://arif-fazil.com/arifos
```

All paths redirect to the main arifOS framework page.

## Verification

After deployment, test:

```bash
curl -I https://arifos.pages.dev/
# Should show: HTTP/2 301 + Location: https://arif-fazil.com/arifos
```

## Notes

- 301 redirect is SEO-friendly (search engines will update their index)
- The `index.html` provides a fallback for browsers that don't follow redirects
- No need to maintain content here anymore - everything is on Railway!
