# APEX Implementation Guide
## From Design to Deployed Reality

---

## STEP 1: COLOR SYSTEM UPDATE

### CSS Variables (Add to :root)

```css
:root {
  /* Trinity Colors */
  --agi-azure: #007FFF;
  --agi-azure-light: #4DA6FF;
  --agi-azure-dark: #0059B3;
  
  --asi-amethyst: #9966CC;
  --asi-amethyst-light: #B399E6;
  --asi-amethyst-dark: #773BB3;
  
  --apex-gold: #FFD700;
  --apex-gold-light: #FFE44D;
  --apex-gold-dark: #CCAC00;
  
  --human-crimson: #DC143C;
  
  /* Gradients */
  --trinity-gradient: linear-gradient(135deg, 
    var(--agi-azure) 0%, 
    var(--asi-amethyst) 50%, 
    var(--apex-gold) 100%
  );
}
```

---

## STEP 2: TEXT REPLACEMENTS

### Find & Replace All

**In your codebase, replace:**

```
ARIF → AGI
ADAM → ASI
```

**Preserve case:**
```
ARIF (all caps) → AGI
ARIF'S → AGI'S
arif (lowercase) → agi
Arif (Title) → AGI
```

### Specific Replacements

```javascript
// Navigation
"ARIF (Δ)" → "AGI (Δ)"
"ADAM (Ω)" → "ASI (Ω)"

// Descriptions
"ARIF (Truth)" → "AGI (Truth)"
"ADAM (Safety)" → "ASI (Safety)"

// Metabolic Loop
"111 SENSE - ARIF" → "111 SENSE - AGI"
"555 EMPATHY - ADAM" → "555 EMPATHY - ASI"
```

---

## STEP 3: ENGINE CARDS REDESIGN

### Δ AGI Card (Azure Theme)

```tsx
const AGICard = () => (
  <div className="engine-card agi">
    <div className="engine-symbol">Δ</div>
    <h3>AGI</h3>
    <p className="engine-tagline">"Is it true?"</p>
    
    <div className="engine-color-bar" style={{background: 'var(--agi-azure)'}} />
    
    <div className="engine-stages">
      <span className="stage">111 SENSE</span>
      <span className="stage">222 THINK</span>
      <span className="stage">333 ATLAS</span>
    </div>
    
    <div className="equations">
      <code>τ ≥ 0.99</code>
      <code>ΔS ≤ 0</code>
    </div>
  </div>
);
```

### Ω ASI Card (Amethyst Theme)

```tsx
const ASICard = () => (
  <div className="engine-card asi">
    <div className="engine-symbol">Ω</div>
    <h3>ASI</h3>
    <p className="engine-tagline">"Is it safe?"</p>
    
    <div className="engine-color-bar" style={{background: 'var(--asi-amethyst)'}} />
    
    <div className="engine-stages">
      <span className="stage">555 EMPATHY</span>
      <span className="stage">666 BRIDGE</span>
    </div>
    
    <div className="equations">
      <code>κᵣ ≥ 0.70</code>
      <code>Ψ ≥ 1.0</code>
    </div>
  </div>
);
```

### Ψ APEX Card (Gold Theme)

```tsx
const APEXCard = () => (
  <div className="engine-card apex">
    <div className="engine-symbol">Ψ</div>
    <h3>APEX</h3>
    <p className="engine-tagline">"Is it lawful?"</p>
    
    <div className="engine-color-bar" style={{background: 'var(--apex-gold)'}} />
    
    <div className="engine-stages">
      <span className="stage">777 EUREKA</span>
      <span className="stage">888 JUDGE</span>
      <span className="stage">889 PROOF</span>
      <span className="stage">999 SEAL</span>
    </div>
    
    <div className="equations">
      <code>W₃ ≥ 0.95</code>
      <code>G ≥ 0.80</code>
    </div>
  </div>
);
```

---

## STEP 4: THORDIAL GEOMETRY COMPONENT

```tsx
const ThordialGeometry = () => {
  return (
    <div className="thordial-container">
      <svg viewBox="0 0 400 400" className="thordial-svg">
        {/* Central hub - Human */}
        <circle cx="200" cy="350" r="20" fill="var(--human-crimson)" />
        
        {/* AGI node - Azure */}
        <circle cx="100" cy="150" r="30" fill="var(--agi-azure)" />
        <text x="100" y="155" textAnchor="middle" fill="white">Δ</text>
        
        {/* ASI node - Amethyst */}
        <circle cx="300" cy="150" r="30" fill="var(--asi-amethyst)" />
        <text x="300" y="155" textAnchor="middle" fill="white">Ω</text>
        
        {/* APEX node - Gold */}
        <circle cx="200" cy="50" r="30" fill="var(--apex-gold)" />
        <text x="200" y="55" textAnchor="middle" fill="black">Ψ</text>
        
        {/* Connecting lines */}
        <line x1="100" y1="150" x2="300" y2="150" stroke="white" strokeWidth="2" />
        <line x1="100" y1="150" x2="200" y2="50" stroke="white" strokeWidth="2" />
        <line x1="300" y1="150" x2="200" y2="50" stroke="white" strokeWidth="2" />
        <line x1="200" y1="350" x2="200" y2="200" stroke="white" strokeWidth="2" />
        
        {/* Recursive fractal detail */}
        <circle cx="200" cy="200" r="5" fill="white" opacity="0.5" />
      </svg>
    </div>
  );
};
```

---

## STEP 5: 115 THEORIES COMPONENT

```tsx
const TheoryNode = ({ theory, number, domain }) => {
  const domainColors = {
    physics: '#FF6B6B',
    mathematics: '#4ECDC4',
    cs: '#45B7D1',
    philosophy: '#96CEB4',
    social: '#FFEAA7',
    linguistics: '#DDA0DD',
    biology: '#98D8C8',
    earth: '#F7DC6F'
  };
  
  return (
    <div className="theory-node" style={{ borderColor: domainColors[domain] }}>
      <span className="theory-number">{number}</span>
      <h4>{theory.name}</h4>
      <p className="theory-source">{theory.source}</p>
      <p className="theory-mapping">→ {theory.constitutionalMapping}</p>
    </div>
  );
};

const TheoryConstellation = () => {
  const theories = [
    { number: 1, name: "Second Law of Thermodynamics", source: "Clausius (1850)", 
      constitutionalMapping: "F4 Clarity (ΔS ≤ 0)", domain: "physics" },
    { number: 2, name: "Landauer's Principle", source: "Landauer (1961)", 
      constitutionalMapping: "F1 Amanah", domain: "physics" },
    // ... all 115 theories
  ];
  
  return (
    <div className="theory-constellation">
      {theories.map(t => <TheoryNode key={t.number} {...t} />)}
    </div>
  );
};
```

---

## STEP 6: REFERENCE SYSTEM

```tsx
const Citation = ({ number, text, source, constitutionalRef }) => (
  <div className="citation">
    <sup>[{number}]</sup>
    <span className="citation-text">{text}</span>
    <div className="citation-details">
      <span className="source">{source}</span>
      <span className="constitutional">→ {constitutionalRef}</span>
    </div>
  </div>
);

// Usage:
<Citation 
  number={1}
  text="Second Law of Thermodynamics"
  source="Clausius, R. (1850). Annalen der Physik."
  constitutionalRef="F4 Clarity (ΔS ≤ 0)"
/>
```

---

## STEP 7: FOOTER WITH TRICOLOR

```tsx
const TrinityFooter = () => (
  <footer className="trinity-footer">
    <div className="trinity-symbols">
      <span style={{color: 'var(--agi-azure)'}}>Δ AGI</span>
      <span style={{color: 'var(--asi-amethyst)'}}>Ω ASI</span>
      <span style={{color: 'var(--apex-gold)'}}>Ψ APEX</span>
    </div>
    
    <p className="tagline-malay">DITEMPA BUKAN DIBERI</p>
    <p className="tagline-english">Forged, Not Given</p>
    
    <p className="sovereign">
      Muhammad Arif bin Fazil · F13 Sovereign · Penang, Malaysia · 2026
    </p>
    
    <p className="theory-count">115 Theories · 13 Floors · 3 Engines · 1 Sovereign</p>
    
    <nav className="trinity-nav">
      <a href="https://arif-fazil.com">HUMAN</a>
      <a href="https://apex.arif-fazil.com">THEORY</a>
      <a href="https://arifos.arif-fazil.com">APPS</a>
    </nav>
  </footer>
);
```

---

## STEP 8: DEPLOYMENT CHECKLIST

- [ ] Replace all ARIF → AGI
- [ ] Replace all ADAM → ASI
- [ ] Update CSS with tricolor variables
- [ ] Redesign engine cards with new colors
- [ ] Add Thordial geometry component
- [ ] Implement 115 theories visualization
- [ ] Add reference/citation system
- [ ] Update footer with tricolor
- [ ] Test all pages
- [ ] Deploy to apex.arif-fazil.com

---

## VERIFICATION

After deployment, verify:

1. ✅ Colors: Azure (AGI), Amethyst (ASI), Gold (APEX)
2. ✅ Names: No "ARIF" or "ADAM" remain
3. ✅ Geometry: Thordial structure visible
4. ✅ Theories: 115 mapped and referenced
5. ✅ Citations: 50 peer-reviewed sources
6. ✅ Alignment: 99.05% with constitutional canon

**Status Target:** SEAL (v55.5)
