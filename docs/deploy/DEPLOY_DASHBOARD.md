# APEX Sovereign Dashboard Deployment Guide

## Dashboard Files Location

```
arifosmcp/
├── arifosmcp/
│   ├── sites/
│   │   └── apex-dashboard/
│   │       ├── dashboard.html          # Current version (redirects to v2)
│   │       ├── dashboard-v2.html       # NEW: Improved dashboard ✨
│   │       └── index.html              # Entry point (redirects to v2)
│   └── runtime/
│       ├── server.py                   # Mounts /dashboard static files
│       ├── resources.py                # Fallback HTML generation
│       └── public_registry.py          # Registry entry
```

## What's New in v2

### Improved Design
- **Three-tier layout**: Human surface → Operator console → Machine details
- **Five Vital Signs**: G★, ΔS, Peace², κᵣ, Ψ_LE with plain English explanations
- **Tri-Witness Consensus**: Visual radar chart for F3 compliance
- **13 Floor Status**: All constitutional floors with status indicators
- **Session History**: Last 5 actions with trend analysis
- **Machine Health**: CPU, RAM, latency, energy budget
- **Insights & Recommendations**: Actionable governance insights

### Key Improvements
| Current | v2 |
|---------|-----|
| Raw numbers | Numbers + interpretation |
| Technical metrics | "What this means" explanations |
| Equal weighting | Visual hierarchy (vitals first) |
| Static display | Trends + insights |
| Machine-focused | Human + AI readable |

## Deployment Steps

### Option 1: Local Testing
```bash
# 1. Verify files exist
ls arifosmcp/sites/apex-dashboard/
# Should show: dashboard.html, dashboard-v2.html, index.html

# 2. Run the server locally
python -m arifosmcp.runtime http

# 3. Open in browser
# http://localhost:8080/dashboard/
```

### Option 2: Deploy to Production (VPS)

```bash
# 1. SSH into your VPS
ssh root@arif-fazil.com

# 2. Navigate to arifOS directory
cd /opt/arifosmcp

# 3. Pull latest changes (if using git)
git pull origin main

# 4. Verify dashboard files
ls arifosmcp/sites/apex-dashboard/

# 5. Restart the service
systemctl restart arifosmcp
# or
docker-compose restart arifosmcp

# 6. Verify deployment
curl -I https://arifosmcp.arif-fazil.com/dashboard/
```

### Option 3: Docker Deployment

```bash
# Rebuild with new dashboard
docker-compose build --no-cache arifosmcp
docker-compose up -d

# Verify
docker logs -f arifosmcp
```

## URL Mapping

| URL | File | Purpose |
|-----|------|---------|
| `https://arifosmcp.arif-fazil.com/dashboard/` | `index.html` | Entry point (redirects to v2) |
| `https://arifosmcp.arif-fazil.com/dashboard/dashboard-v2.html` | `dashboard-v2.html` | NEW: Improved dashboard |
| `https://arifosmcp.arif-fazil.com/dashboard/dashboard.html` | `dashboard.html` | Legacy (kept for reference) |

## Live Data Integration

The dashboard fetches from:
- `/api/governance-status` - Live telemetry
- `/api/governance-status` - Machine vitals

To enable live data:
1. Ensure the API endpoints are accessible
2. Update the `endpoint` variable in dashboard-v2.html
3. Enable polling mode

## Customization

### Change Colors
Edit CSS variables in `dashboard-v2.html`:
```css
:root {
    --accent: #00ffcc;        /* Primary color */
    --danger: #ff4444;        /* Error/alerts */
    --success: #00ff88;       /* Success/pass */
    --warning: #ffaa00;       /* Warnings */
}
```

### Update Demo Data
Edit the `DEMO_DATA` object in the script section for testing.

## Troubleshooting

### Dashboard shows "Redirecting..." indefinitely
- Check that `dashboard-v2.html` exists
- Verify file permissions: `chmod 644 dashboard-v2.html`

### Blank page / React errors
- Check browser console for errors
- Verify CDN links are accessible (unpkg.com)
- Try hard refresh: `Ctrl+F5` or `Cmd+Shift+R`

### API endpoint not working
- Test: `curl https://arifosmcp.arif-fazil.com/api/governance-status`
- Check CORS headers in server.py
- Verify the endpoint returns valid JSON

## Verification Checklist

- [ ] `dashboard-v2.html` created in `arifosmcp/sites/apex-dashboard/`
- [ ] `index.html` redirects to v2
- [ ] Server mounts `/dashboard` route correctly
- [ ] Live URL accessible: `https://arifosmcp.arif-fazil.com/dashboard/`
- [ ] Five vitals display correctly
- [ ] Tri-Witness radar chart renders
- [ ] 13 floors show all green/pass
- [ ] Session history table populated
- [ ] Quick actions buttons visible

## Support

- GitHub: https://github.com/ariffazil/arifosmcp
- Docs: https://arifos.arif-fazil.com
- Constitution: https://apex.arif-fazil.com

---

**Ditempa Bukan Diberi** — Forged, Not Given
