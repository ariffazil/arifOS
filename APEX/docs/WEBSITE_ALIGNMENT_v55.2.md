# 🏛️ HTA Website Alignment Specification v55.5

**Authority:** F13 Sovereign (Muhammad Arif bin Fazil)  
**Version:** v55.5-EIGEN  
**Date:** 2026-02-02  
**Status:** Alignment Mandate  

---

## 📋 Executive Summary

This document specifies the alignment requirements for the three Human Theory Apps (HTA) websites to ensure consistent branding, versioning, and identity across the arifOS ecosystem.

---

## 🌐 The Three Sites

| Layer | Site URL | Repo | Role | Current Version |
|-------|----------|------|------|-----------------|
| **HUMAN** (BODY) | https://arif-fazil.com | `body` | Front page, status, entry points | Unknown |
| **THEORY** (SOUL) | https://apex.arif-fazil.com | `soul` / `apex` | Axioms, constitutional canon | v55.5 |
| **APPS** (MIND) | https://arifos.arif-fazil.com | `docs` / `arifos` | API, MCP tools, quickstart | v55.1-SEAL |

**Target Version for All Sites:** `v55.5-SEAL`

---

## ✅ Alignment Checklist

### 1. Version Consistency

| Site | Current | Required | Action |
|------|---------|----------|--------|
| arif-fazil.com | Not visible | **v55.5-SEAL** | Add version badge in header |
| apex.arif-fazil.com | v55.1 | **v55.5-SEAL** | Update header version badge |
| arifos.arif-fazil.com | v55.1-SEAL | **v55.5-SEAL** | Update header version badge |

### 2. Navigation Consistency

**Standard Navigation Labels:**
- **HUMAN** → links to https://arif-fazil.com
- **THEORY** → links to https://apex.arif-fazil.com  
- **APPS** → links to https://arifos.arif-fazil.com

| Site | Current Nav | Required Nav | Action |
|------|-------------|--------------|--------|
| arif-fazil.com | HUMAN \| THEORY \| APPS | **HUMAN \| THEORY \| APPS** | ✅ No change |
| apex.arif-fazil.com | BODY \| MIND \| SOUL | **HUMAN \| THEORY \| APPS** | Change labels* |
| arifos.arif-fazil.com | HUMAN \| THEORY \| APPS | **HUMAN \| THEORY \| APPS** | ✅ No change |

*Alternative: Keep BODY/MIND/SOUL on apex but add subtitle clarifying: BODY=HUMAN, MIND=APPS, SOUL=THEORY

### 3. Sovereign Identity (F13)

**Required on ALL sites:**
- Full Name: **Muhammad Arif bin Fazil**
- Title: **F13 Sovereign** (on APEX) or **Sovereign Architect of arifOS** (on HUMAN)
- Location: **Penang, Malaysia**

| Site | Current | Required | Action |
|------|---------|----------|--------|
| arif-fazil.com | "Muhammad Arif bin Fazil \| Sovereign Architect of arifOS" | **Keep** | ✅ No change |
| apex.arif-fazil.com | Not prominently displayed | **Add footer**: "Muhammad Arif bin Fazil · F13 Sovereign · Penang, Malaysia" | Add identity line |
| arifos.arif-fazil.com | Not prominently displayed | **Add footer**: "Muhammad Arif bin Fazil · F13 Sovereign · Penang, Malaysia" | Add identity line |

### 4. "Ditempa Bukan Diberi" (Forged, Not Given)

**Required on ALL sites** - This is the core identity statement.

| Site | Current | Required | Action |
|------|---------|----------|--------|
| arif-fazil.com | Not visible | **Add prominently**: "Ditempa Bukan Diberi — Forged, Not Given" | Add tagline |
| apex.arif-fazil.com | Present in footer | **Keep + add to hero** | Enhance visibility |
| arifos.arif-fazil.com | Not visible | **Add to footer**: "Ditempa Bukan Diberi — Forged, Not Given" | Add tagline |

### 5. Visual Identity (Serena Aesthetic)

**Color Palette:**
- Primary Dark: `#0a0a0f` (Deep void)
- Primary Gold: `#d4af37` (Forged metal)
- Accent: `#1a1a2e` (Midnight)
- Text: `#e0e0e0` (Soft white)

**Typography:**
- Headings: Serif or premium sans-serif
- Body: Clean, readable sans-serif
- Monospace for code/technical content

| Site | Current | Required | Action |
|------|---------|----------|--------|
| arif-fazil.com | Light theme | **Dark/Gold premium** | Migrate to Serena aesthetic |
| apex.arif-fazil.com | Dark/Gold | **Keep** | ✅ No change |
| arifos.arif-fazil.com | Dark/Gold | **Keep** | ✅ No change |

### 6. Footer Alignment

**Standard Footer Elements:**
```
Δ Ω Ψ
DITEMPA BUKAN DIBERI
Forged, Not Given

Muhammad Arif bin Fazil · Penang, Malaysia · 2026

[HUMAN] [THEORY] [APPS] [GitHub] [LinkedIn]
```

| Site | Current Footer | Required | Action |
|------|----------------|----------|--------|
| arif-fazil.com | Basic contact info | **Add ΔΩΨ + Ditempa Bukan Diberi** | Enhance footer |
| apex.arif-fazil.com | Has ΔΩΨ + Ditempa | **Standardize format** | Minor tweaks |
| arifos.arif-fazil.com | Basic copyright | **Add full standard footer** | Major update |

### 7. Cross-Linking Verification

Ensure all inter-site links work:

| From → To | URL | Status |
|-----------|-----|--------|
| arif-fazil.com → apex | https://apex.arif-fazil.com | ✅ Verify |
| arif-fazil.com → arifos | https://arifos.arif-fazil.com | ✅ Verify |
| apex → arif-fazil.com | https://arif-fazil.com | ✅ Verify |
| apex → arifos | https://arifos.arif-fazil.com | ✅ Verify |
| arifos → arif-fazil.com | https://arif-fazil.com | ✅ Verify |
| arifos → apex | https://apex.arif-fazil.com | ✅ Verify |

### 8. HTA Mapping Statement

**Add to footer of all sites:**
```
HTA: BODY (HUMAN) · SOUL (THEORY) · MIND (APPS)
```

---

## 🔧 Implementation Priority

### P0 (Critical) - Must Complete
1. ✅ Update version to v55.5-SEAL on all sites
2. ✅ Add "Ditempa Bukan Diberi" to arif-fazil.com and arifos.arif-fazil.com
3. ✅ Add F13 Sovereign identity to apex and arifos footers

### P1 (High) - Should Complete
4. Align navigation labels (HUMAN/THEORY/APPS)
5. Standardize footers across all sites
6. Verify all cross-links work

### P2 (Medium) - Nice to Have
7. Migrate arif-fazil.com to Serena aesthetic (Dark/Gold)
8. Add HTA mapping statement to all footers

---

## 📝 Specific File Changes Required

### arif-fazil.com (BODY)

**File:** `index.html` or main page component
```html
<!-- Add to header -->
<div class="version-badge">v55.5-SEAL</div>

<!-- Add below name -->
<p class="tagline">Ditempa Bukan Diberi — Forged, Not Given</p>

<!-- Update footer -->
<footer>
  <div class="trinity-symbols">Δ Ω Ψ</div>
  <p>DITEMPA BUKAN DIBERI</p>
  <p>Forged, Not Given</p>
  <p>Muhammad Arif bin Fazil · Penang, Malaysia · 2026</p>
  <nav>
    <a href="https://arif-fazil.com">HUMAN</a>
    <a href="https://apex.arif-fazil.com">THEORY</a>
    <a href="https://arifos.arif-fazil.com">APPS</a>
  </nav>
</footer>
```

### apex.arif-fazil.com (SOUL)

**File:** Header component
```html
<!-- Update version -->
<div class="version">v55.5-SEAL</div>

<!-- Update navigation -->
<nav>
  <a href="https://arif-fazil.com">HUMAN</a>
  <a href="https://arifos.arif-fazil.com">APPS</a>
  <a href="https://apex.arif-fazil.com">THEORY</a>
</nav>
```

**File:** Footer component
```html
<footer>
  <div class="trinity-symbols">Δ Ω Ψ</div>
  <p>DITEMPA BUKAN DIBERI · Forged, Not Given</p>
  <p>Muhammad Arif bin Fazil · F13 Sovereign · Penang, Malaysia · February 2026</p>
  <!-- Keep existing links -->
</footer>
```

### arifos.arif-fazil.com (MIND)

**File:** Header component
```html
<!-- Update version -->
<div class="version-badge">v55.5-SEAL</div>
```

**File:** Footer component  
```html
<footer>
  <div class="trinity-symbols">Δ Ω Ψ</div>
  <p>DITEMPA BUKAN DIBERI — Forged, Not Given</p>
  <p>Muhammad Arif bin Fazil · F13 Sovereign · Penang, Malaysia · 2026</p>
  <nav>
    <a href="https://arif-fazil.com">HUMAN</a>
    <a href="https://apex.arif-fazil.com">THEORY</a>
    <a href="https://arifos.arif-fazil.com">APPS</a>
  </nav>
  <p>arifOS Architecture: Human (Sovereign) | Idea (Constitutional) | Application (Runtime)</p>
</footer>
```

---

## 🚀 Deployment Sequence

1. **Phase 1:** Update apex.arif-fazil.com (SOUL/Theoretical foundation)
2. **Phase 2:** Update arifos.arif-fazil.com (MIND/Documentation)
3. **Phase 3:** Update arif-fazil.com (BODY/Human interface)
4. **Phase 4:** Verify cross-links and test
5. **Phase 5:** Seal and document completion

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] All three sites show version v55.5-SEAL
- [ ] All three sites display "Ditempa Bukan Diberi"
- [ ] All three sites reference Muhammad Arif bin Fazil as F13 Sovereign
- [ ] Navigation is consistent (HUMAN/THEORY/APPS)
- [ ] All cross-links work correctly
- [ ] Footers have standardized format
- [ ] Visual identity is consistent (Dark/Gold)

---

**Signed,**  
*Antigravity (The Architect)*  
*On behalf of F13 Sovereign*

---

*This document is sealed under VAULT-999 protocol.*
