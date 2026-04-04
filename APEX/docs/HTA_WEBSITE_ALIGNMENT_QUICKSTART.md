# HTA Website Alignment Quickstart

**Task:** Align https://arif-fazil.com, https://apex.arif-fazil.com, and https://arifos.arif-fazil.com  
**Target Version:** v55.5-EIGEN  
**Time Required:** ~30 minutes  

---

## 📋 Summary of Changes Needed

### 1. arif-fazil.com (BODY / HUMAN Layer)

**File Location:** `arif-fazil-sites/body/` (React/Vite app)

**Changes:**
```diff
+ Add version badge: "v55.5-SEAL" in header
+ Add tagline: "Ditempa Bukan Diberi — Forged, Not Given" below name
+ Update footer to include:
    - Δ Ω Ψ symbols
    - "DITEMPA BUKAN DIBERI"
    - "Forged, Not Given"
    - "Muhammad Arif bin Fazil · Penang, Malaysia · 2026"
    - Navigation: HUMAN | THEORY | APPS
```

---

### 2. apex.arif-fazil.com (SOUL / THEORY Layer)

**File Location:** `arif-fazil-sites/apex.com/` (React/Vite app)

**Changes:**
```diff
- Change: "v55.5" → "v55.5-SEAL"
- Change navigation: "BODY | MIND | SOUL" → "HUMAN | THEORY | APPS"
  (or add subtitle mapping: BODY=HUMAN, MIND=APPS, SOUL=THEORY)
+ Add to footer: "Muhammad Arif bin Fazil · F13 Sovereign · Penang, Malaysia"
+ Ensure "Ditempa Bukan Diberi" is prominent in hero section
```

---

### 3. arifos.arif-fazil.com (MIND / APPS Layer)

**File Location:** `arif-fazil-sites/docs/` or `arif-fazil-sites/arifos/` (React/Vite app)

**Changes:**
```diff
- Change: "v55.1-SEAL" → "v55.5-SEAL"
+ Add footer with:
    - Δ Ω Ψ symbols
    - "DITEMPA BUKAN DIBERI — Forged, Not Given"
    - "Muhammad Arif bin Fazil · F13 Sovereign · Penang, Malaysia · 2026"
    - Navigation: HUMAN | THEORY | APPS
    - "arifOS Architecture: Human (Sovereign) | Idea (Constitutional) | Application (Runtime)"
```

---

## 🔧 Technical Implementation

### Common Elements for All Sites

#### 1. Version Badge Component
```tsx
// VersionBadge.tsx
export const VersionBadge = () => (
  <div className="version-badge">
    <span className="version">v55.5</span>
    <span className="separator">-</span>
    <span className="status">SEAL</span>
  </div>
);

// CSS
.version-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  background: linear-gradient(135deg, #1a1a2e 0%, #0a0a0f 100%);
  border: 1px solid #d4af37;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.875rem;
}

.version-badge .version {
  color: #d4af37;
  font-weight: 600;
}

.version-badge .separator {
  color: #666;
}

.version-badge .status {
  color: #00cc00;
  font-weight: 600;
}
```

#### 2. Trinity Footer Component
```tsx
// TrinityFooter.tsx
export const TrinityFooter = () => (
  <footer className="trinity-footer">
    <div className="trinity-symbols">Δ Ω Ψ</div>
    <p className="tagline-malay">DITEMPA BUKAN DIBERI</p>
    <p className="tagline-english">Forged, Not Given</p>
    <p className="sovereign">
      Muhammad Arif bin Fazil · F13 Sovereign · Penang, Malaysia · 2026
    </p>
    <nav className="trinity-nav">
      <a href="https://arif-fazil.com">HUMAN</a>
      <span className="separator">|</span>
      <a href="https://apex.arif-fazil.com">THEORY</a>
      <span className="separator">|</span>
      <a href="https://arifos.arif-fazil.com">APPS</a>
    </nav>
  </footer>
);

// CSS
.trinity-footer {
  text-align: center;
  padding: 2rem;
  background: #0a0a0f;
  color: #e0e0e0;
  border-top: 1px solid #d4af37;
}

.trinity-symbols {
  font-size: 1.5rem;
  letter-spacing: 0.5rem;
  color: #d4af37;
  margin-bottom: 1rem;
}

.tagline-malay {
  font-size: 1.25rem;
  font-weight: 600;
  color: #d4af37;
  margin: 0.5rem 0;
}

.tagline-english {
  font-size: 0.875rem;
  color: #888;
  margin: 0.25rem 0 1rem;
}

.sovereign {
  font-size: 0.875rem;
  color: #666;
  margin: 1rem 0;
}

.trinity-nav {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 1rem;
}

.trinity-nav a {
  color: #d4af37;
  text-decoration: none;
  font-weight: 500;
}

.trinity-nav a:hover {
  text-decoration: underline;
}

.trinity-nav .separator {
  color: #444;
}
```

---

## 🚀 Deployment Steps

### Step 1: Update arif-fazil.com (BODY)
```bash
cd arif-fazil-sites/body

# Edit src/components/Header.tsx or similar
# - Add VersionBadge component
# - Add "Ditempa Bukan Diberi" tagline

# Edit src/components/Footer.tsx or similar
# - Replace with TrinityFooter component

npm run build
npm run deploy  # or push to trigger CI/CD
```

### Step 2: Update apex.arif-fazil.com (SOUL)
```bash
cd arif-fazil-sites/apex.com

# Edit src/components/Header.tsx
# - Update version from "v55.1" to "v55.5-SEAL"
# - Update navigation labels

# Edit src/components/Footer.tsx
# - Add sovereign identity line
# - Ensure "Ditempa Bukan Diberi" is present

npm run build
npm run deploy
```

### Step 3: Update arifos.arif-fazil.com (MIND)
```bash
cd arif-fazil-sites/docs  # or arifos

# Edit src/components/Header.tsx
# - Update version from "v55.1-SEAL" to "v55.5-SEAL"

# Edit src/components/Footer.tsx
# - Replace with TrinityFooter component

npm run build
npm run deploy
```

---

## ✅ Post-Deployment Verification

Visit each site and verify:

### arif-fazil.com
- [ ] Version badge shows "v55.5-SEAL"
- [ ] "Ditempa Bukan Diberi — Forged, Not Given" is visible
- [ ] Footer has Δ Ω Ψ symbols
- [ ] Footer shows "Muhammad Arif bin Fazil · Penang, Malaysia · 2026"
- [ ] Navigation links work: THEORY → apex, APPS → arifos

### apex.arif-fazil.com
- [ ] Version badge shows "v55.5-SEAL"
- [ ] Navigation shows "HUMAN | THEORY | APPS" (or equivalent mapping)
- [ ] Footer shows "Muhammad Arif bin Fazil · F13 Sovereign · Penang, Malaysia"
- [ ] "Ditempa Bukan Diberi" is prominent
- [ ] Navigation links work: HUMAN → arif-fazil.com, APPS → arifos

### arifos.arif-fazil.com
- [ ] Version badge shows "v55.5-SEAL"
- [ ] Navigation shows "HUMAN | THEORY | APPS"
- [ ] Footer has Δ Ω Ψ symbols
- [ ] Footer shows "Ditempa Bukan Diberi — Forged, Not Given"
- [ ] Footer shows "Muhammad Arif bin Fazil · F13 Sovereign · Penang, Malaysia · 2026"
- [ ] Navigation links work: HUMAN → arif-fazil.com, THEORY → apex

---

## 🆘 Troubleshooting

### Build Errors
- Ensure all dependencies are installed: `npm install`
- Check for TypeScript errors: `npx tsc --noEmit`

### Deployment Failures
- Verify Cloudflare Pages / GitHub Pages settings
- Check that build output directory is correct (usually `dist/`)

### Styling Issues
- Ensure CSS variables match the Serena aesthetic:
  - `--color-bg: #0a0a0f`
  - `--color-gold: #d4af37`
  - `--color-text: #e0e0e0`

---

## 📚 References

- Full specification: `docs/WEBSITE_ALIGNMENT_v55.5.md`
- AGENTS.md protocol: `AGENTS.md` (in arif-fazil-sites root)
- Design system: Serena aesthetic (Dark/Gold/Premium)

---

**SEAL Status:** Pending deployment  
**Authority:** F13 Sovereign (Muhammad Arif bin Fazil)
