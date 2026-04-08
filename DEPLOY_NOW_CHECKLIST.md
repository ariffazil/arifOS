# 🚀 DEPLOY NOW — Phase 1.5 Verification Checklist

**Status:** Files updated in repo ✅ | Container restart needed 🔄  
**Date:** 2026-04-09  
**Action Required:** Restart + verify

---

## Step 1: Restart Container

```bash
# SSH into VPS and restart
cd /path/to/arifOS
docker compose restart arifosmcp

# Or full rebuild if needed
docker compose down arifosmcp
docker compose up -d arifosmcp
```

---

## Step 2: Verify Backend Changes

### 2.1 Tool count = 11
```bash
curl -s https://arifosmcp.arif-fazil.com/health | jq '.tools_loaded'
# Expected: 11
```

### 2.2 Lane metadata present
```bash
curl -s https://arifosmcp.arif-fazil.com/tools | jq '.tools[] | {name, stage, lane}'
# Expected each tool has: name, stage (000_INIT, etc.), lane (Δ/Ω/Ψ)
```

### 2.3 Thermodynamic metrics
```bash
curl -s https://arifosmcp.arif-fazil.com/health | jq '.thermodynamic | {entropy_delta, peace2, verdict}'
# Expected: {"entropy_delta": -0.02, "peace2": 1.01, "verdict": "SEAL"}
```

---

## Step 3: Verify Static Files

### 3.1 llms.txt updated
```bash
curl -s https://arifosmcp.arif-fazil.com/llms.txt | head -25
# Should see:
# "arifOS MCP — Governed Intelligence Server"
# "Δ Discernment Lane (Reality + Reasoning)"
# "Never call arifos_forge without a prior arifos_judge SEAL"
```

### 3.2 humans.txt updated
```bash
curl -s https://arifosmcp.arif-fazil.com/humans.txt | head -10
# Should see:
# "Seri Kembangan / Kuala Lumpur, Malaysia"
# "lead forger"
```

---

## Step 4: Verify Landing Page (Visual Check)

Open https://arifosmcp.arif-fazil.com/ in browser and verify:

### Navigation Bar
- [ ] Shows: 🔥 arifOS MCP brand
- [ ] Links: Tools, Trinity, For Humans, For AI, Connect, humans.txt, llms.txt

### Hero Section
- [ ] Status badge: "AF-FORGE Online ✓" (green)
- [ ] Title: "arifOS MCP"
- [ ] Tagline: "Governed Intelligence Server — Reasoning. Safety. Memory. Judgment."
- [ ] Motto: "DITEMPA, BUKAN DIBERI"
- [ ] Stats: 11 Tools, 13 Floors, ΔΩΨ Trinity, MCP 2025-03-26

### "What is arifOS?" Section (NEW)
- [ ] Heading: "🧭 What is arifOS MCP?"
- [ ] Text explains: governed remote intelligence server
- [ ] Lists ΔΩΨ Trinity lanes with descriptions
- [ ] Mentions 13 Constitutional Floors
- [ ] Shows flow: sense → mind → heart → judge → forge
- [ ] Motto callout in gold
- [ ] Closing: "This is not just another MCP server..."

### Trinity Architecture Section
- [ ] Three color-coded cards:
  - [ ] Δ Delta (blue border) — 5 tools
  - [ ] Ω Omega (purple border) — 2 tools  
  - [ ] Ψ Psi (pink border) — 4 tools

### 11 Canonical Tools Section
- [ ] Shows 11 tool cards (not 10)
- [ ] Each card has: name, lane symbol (Δ/Ω/Ψ), stage code, description
- [ ] Color-coded left borders matching Trinity lanes

### For AI Agents Section
- [ ] Heading: "🤖 For AI Agents"
- [ ] Shows recommended sequence: init → sense → mind → route → heart → judge → vault
- [ ] **Warning box:** "⚠️ CRITICAL: Never call arifos_forge without prior arifos_judge SEAL"
- [ ] Key principles list

### Live System Status
- [ ] Governance card: status, version, floors, tools
- [ ] Thermodynamic Health card: entropy, Peace², confidence, verdict
- [ ] Witness Balance card: human 0.42, AI 0.32, earth 0.26

### Footer
- [ ] Large motto: "DITEMPA, BUKAN DIBERI"
- [ ] "Forged by Muhammad Arif bin Fazil in Seri Kembangan, Malaysia 🇲🇾"
- [ ] Links: GitHub, humans.txt, llms.txt, Audit Report

---

## Step 5: If Issues Persist

### Issue: Lane metadata still null
**Cause:** contracts.py changes not loaded  
**Fix:**
```bash
# Check if contracts.py is correct inside container
docker exec arifosmcp cat /usr/src/app/arifosmcp/runtime/contracts.py | grep -A5 "AAA_TOOL_STAGE_MAP ="

# If missing canonical names, rebuild:
docker compose down arifosmcp
docker compose build arifosmcp --no-cache
docker compose up -d arifosmcp
```

### Issue: Static files still old
**Cause:** Browser cache or volume not updated  
**Fix:**
```bash
# Force refresh static files
docker exec arifosmcp cp -r /usr/src/app/static/* /var/www/static/

# Or check container has new files:
docker exec arifosmcp head -5 /usr/src/app/static/llms.txt
```

### Issue: Landing page not showing new design
**Cause:** Old landing_page.html cached or not copied  
**Fix:**
```bash
# Verify file in container
docker exec arifosmcp grep -o "What is arifOS" /usr/src/app/arifosmcp/runtime/landing_page.html

# If not found, copy manually:
docker cp /root/arifOS/arifosmcp/runtime/landing_page.html arifosmcp:/usr/src/app/arifosmcp/runtime/landing_page.html
docker compose restart arifosmcp
```

---

## Success Criteria

✅ **All checks pass = Phase 1.5 Complete**

| Check | Status |
|-------|--------|
| /health returns tools_loaded: 11 | ⬜ |
| /tools returns lane metadata (Δ/Ω/Ψ) | ⬜ |
| llms.txt shows new model-optimized content | ⬜ |
| humans.txt shows Seri Kembangan | ⬜ |
| Landing page has "What is arifOS?" intro | ⬜ |
| Landing page has Trinity color cards | ⬜ |
| Landing page has 11 tools (not 10) | ⬜ |
| Landing page has AI warning box | ⬜ |
| Landing page has live thermodynamic display | ⬜ |

---

## Quick Debug Commands

```bash
# Full system check
echo "=== Health ===" && curl -s https://arifosmcp.arif-fazil.com/health | jq '{tools: .tools_loaded, floors: .floors_active, version: .version}'

echo "=== Tools Sample ===" && curl -s https://arifosmcp.arif-fazil.com/tools | jq '.tools[0,5,10] | {name, stage, lane}'

echo "=== llms.txt ===" && curl -s https://arifosmcp.arif-fazil.com/llms.txt | grep -E "(Discernment|forge without)" | head -3

echo "=== humans.txt ===" && curl -s https://arifosmcp.arif-fazil.com/humans.txt | grep -E "(Seri Kembangan|lead forger)"
```

---

**Execute restart now. Then run verification.**

ΔΩΨ | Ready to forge
