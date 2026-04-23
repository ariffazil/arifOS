# CI/CD Patterns

**Status:** TO BE WRITTEN — populate after State A is proven live

---

## Workflow Patterns

### Hub Deploy Workflow

See: `.github/workflows/deploy-hub.yml` in `ariffazil/arifOS` repo.

Key patterns:
- Trigger: path filter on `sites/arifOS-fazil.com-source/**`
- Pages upload: `actions/upload-pages-artifact@v3`
- Deploy: `actions/deploy-pages@v4`
- Validation step: verify index.html, style.css, llms.txt exist before upload

### Preview Deploys (PR)

On pull_request, GitHub Actions creates a preview URL. The exact mechanism depends on hosting platform:
- GitHub Pages: Pages doesn't natively support per-PR previews — work around with `deploy-pages@v4` and a comment on PR with the URL
- Cloudflare Pages: Native preview URLs via `cloudflare/pages-action@v1`

### Health Check in CI

After runtime deploy, add a step:
```bash
curl -sf https://arifosmcp.arif-fazil.com/health || exit 1
```

If this fails, the workflow should exit with failure and not mark deploy complete.

### Rollback Pattern

GitHub Pages rollback: re-run the previous successful `deploy-pages` action, or use GitHub Pages API to set deployment to a specific commit SHA.

Cloudflare Pages rollback: via `wrangler pages deployment list` and `wrangler pages rollback <deployment-id>`.

---

## TO BE COMPLETED AFTER STATE A PROVEN
