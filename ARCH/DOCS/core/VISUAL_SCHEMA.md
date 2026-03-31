# arifOS Visual Design Schema
## Constitutional Design Language v55.3

> **FORGE NOTICE**: This document defines the visual grammar of arifOS — a thermodynamically-grounded design system that embodies the Trinity architecture. All visual elements must honor the sacred geometry of governance.

---

## 1. CORE PHILOSOPHY

### Design Metaphor: The Forge
The arifOS visual system is built on the metaphor of **forging** — the transformation of raw material through heat, pressure, and time into something durable and purposeful.

- **Fire** → Energy, transformation, purification
- **Steel/Anvil** → Strength, resilience, structure  
- **Heat gradients** → Activity, life, attention
- **Dark void** → The substrate of potential, the unknown

### Visual Principles (F6 Clarity)
1. **Entropy Reduction**: Every element must reduce visual noise
2. **Thermodynamic Honesty**: Heat (activity) only where justified
3. **Sacred Geometry**: Triangles, circles, grids as foundational patterns
4. **Material Truth**: Textures suggest their real-world counterparts

---

## 2. THE TRINITY COLOR SYSTEM

### 2.1 HUMAN Layer — The Body (RED)
> Domain: arif-fazil.com | Symbol: Δ | Function: Epistemic

The HUMAN layer represents blood, life, danger, and the body. It is the **fire of the forge**.

| Token | Hex | HSL | Usage |
|-------|-----|-----|-------|
| `--human-primary` | `#8B0000` | 0° 100% 27% | Headers, primary actions |
| `--human-accent` | `#FF2D2D` | 0° 100% 59% | Hover states, links |
| `--human-glow` | `#FF4500` | 16° 100% 50% | Embers, pulses |
| `--human-bg` | `#0A0A0A` | 0° 0% 4% | Background |
| `--human-surface` | `#141414` | 0° 0% 8% | Cards, elevated surfaces |
| `--human-border` | `#333333` | 0° 0% 20% | Subtle borders |
| `--human-text` | `#E5E5E5` | 0° 0% 90% | Primary text |
| `--human-muted` | `#6B7280` | 220° 9% 46% | Secondary text |

**Psychological Profile**: Urgency, passion, warning, warmth, life-force

---

### 2.2 THEORY Layer — The Soul (GOLD/YELLOW WEAVE)
> Domain: apex.arif-fazil.com | Symbol: Ψ | Function: Authority

The THEORY layer represents wisdom, authority, and the blueprint — illuminated by gold light. It is the **architecture of the forge**, now gleaming with knowledge.

| Token | Hex | HSL | Usage |
|-------|-----|-----|-------|
| `--theory-primary` | `#D4AF37` | 45° 67% 43% | Headers, primary text |
| `--theory-accent` | `#FFD700` | 45° 100% 55% | Links, highlights |
| `--theory-light` | `#FFE66D` | 45° 100% 65% | Hover states |
| `--theory-bg` | `#1A1810` | 45° 30% 8% | Background |
| `--theory-surface` | `#3E3B28` | 45° 18% 18% | Cards |
| `--theory-border` | `#5A5840` | 45° 15% 28% | Borders |
| `--theory-text` | `#FFF8DC` | 45° 100% 98% | Primary text (Cornsilk) |
| `--theory-muted` | `#C0C0C0` | 45° 60% 75% | Secondary text (Silver) |

**Psychological Profile**: Golden knowledge, illuminated wisdom, scholarly warmth, precious insight

**Contrast Analysis**: 
- Gold (#FFD700) on Dark Brown (#1A1810): 12.8:1 ✓ WCAG AAA
- Cornsilk (#FFF8DC) on Dark Brown: 15.6:1 ✓ WCAG AAA
- Primary Gold (#D4AF37) on Dark: 10.2:1 ✓ WCAG AA

---

### 2.3 APPS Layer — The Mind (CYAN)
> Domain: arifos.arif-fazil.com | Symbol: Ω | Function: Safety

The APPS layer represents logic, flow, and the technical runtime. It is the **cooling water and precision tools**.

| Token | Hex | HSL | Usage |
|-------|-----|-----|-------|
| `--apps-primary` | `#0EA5E9` | 199° 89% 48% | Primary actions |
| `--apps-accent` | `#06B6D4` | 187° 94% 43% | Links, highlights |
| `--apps-glow` | `#22D3EE` | 190° 80% 53% | Glow effects |
| `--apps-bg` | `#0A0A0A` | 0° 0% 4% | Background |
| `--apps-surface` | `#171717` | 0° 0% 9% | Cards |
| `--apps-border` | `#262626` | 0° 0% 15% | Borders |
| `--apps-text` | `#FAFAFA` | 0° 0% 98% | Primary text |
| `--apps-muted` | `#A3A3A3` | 0° 0% 64% | Secondary text |

**Psychological Profile**: Clarity, technology, flow, precision, coolness

---

### 2.4 The Trinity Unified

When all three layers appear together:

```
TRINITY GRADIENT: #00D4FF (Cyan) → #FFB800 (Amber) → #FF2D2D (Red)
                 MIND           SOUL           BODY
```

**Usage**: Logo animations, hero backgrounds, transition effects

---

## 3. TYPOGRAPHY SYSTEM

### 3.1 Font Families

| Layer | Primary | Monospace | Display |
|-------|---------|-----------|---------|
| HUMAN | Inter | JetBrains Mono | — |
| THEORY | Space Mono | JetBrains Mono | Syncopate |
| APPS | Inter | JetBrains Mono | — |

### 3.2 Type Scale

```css
/* Base */
--text-xs: 0.75rem;    /* 12px - Captions, metadata */
--text-sm: 0.875rem;   /* 14px - Body small, nav */
--text-base: 1rem;     /* 16px - Body */
--text-lg: 1.125rem;   /* 18px - Lead paragraph */
--text-xl: 1.25rem;    /* 20px - H3 */
--text-2xl: 1.5rem;    /* 24px - H2 */
--text-3xl: 1.875rem;  /* 30px - H1 small */
--text-4xl: 2.25rem;   /* 36px - H1 medium */
--text-5xl: 3rem;      /* 48px - Hero */
```

### 3.3 Typography Rules

1. **Headings**: Use layer's primary color, font-weight 600-700
2. **Body**: Gray-300 to Gray-400, font-weight 400, line-height 1.6-1.7
3. **Monospace**: Used for code, version numbers, floor labels, mathematical notation
4. **Uppercase tracking**: Used for section labels, badges, tracking-wide (0.05em to 0.15em)

---

## 4. SPATIAL SYSTEM

### 4.1 Border Radius Scale

```css
--radius-none: 0;        /* THEORY: sharp, academic */
--radius-sm: 0.375rem;   /* 6px */
--radius-md: 0.5rem;     /* 8px - HUMAN: slightly softer */
--radius-lg: 0.75rem;    /* 12px - APPS: technical but friendly */
--radius-xl: 1rem;       /* 16px */
--radius-full: 9999px;   /* Pills, avatars */
```

### 4.2 Spacing Scale (Tailwind)

```
1  = 0.25rem  (4px)
2  = 0.5rem   (8px)
3  = 0.75rem  (12px)
4  = 1rem     (16px)
5  = 1.25rem  (20px)
6  = 1.5rem   (24px)
8  = 2rem     (32px)
10 = 2.5rem   (40px)
12 = 3rem     (48px)
16 = 4rem     (64px)
20 = 5rem     (80px)
```

### 4.3 Layout Principles

1. **Max-width containers**: 
   - Tight: `max-w-2xl` (42rem) — Reading content
   - Standard: `max-w-3xl` (48rem) — General content
   - Wide: `max-w-4xl` (56rem) — Visual showcases

2. **Section padding**: `py-20` (5rem) standard section spacing

3. **Container padding**: `px-6` (1.5rem) mobile, consistent horizontal rhythm

---

## 5. VISUAL ELEMENTS

### 5.1 Background Patterns

#### Triangle Pattern (HUMAN)
```css
.triangle-bg {
  background-color: #050505;
  background-image: 
    linear-gradient(30deg, rgba(139, 0, 0, 0.1) 12%, ...),
    linear-gradient(150deg, rgba(139, 0, 0, 0.1) 12%, ...);
  background-size: 80px 140px;
}
```
**Meaning**: Sierpinski fractal, infinite depth, sacred geometry

#### Sacred Grid (THEORY)
```css
.sacred-grid {
  background-image:
    linear-gradient(rgba(107, 140, 206, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(107, 140, 206, 0.04) 1px, transparent 1px);
  background-size: 40px 40px;
}
```
**Meaning**: Blueprint, scientific precision, architectural planning

#### Geometric Grid (APPS)
```css
.geometric-bg {
  background-image:
    linear-gradient(rgba(14, 165, 233, 0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(14, 165, 233, 0.025) 1px, transparent 1px);
  background-size: 200px 200px, 200px 200px, 50px 50px, 50px 50px, 12.5px 12.5px, 12.5px 12.5px;
}
```
**Meaning**: Multi-scale system, fractal organization, technical precision

---

### 5.2 The Trinity Symbol

The **Sierpinski Triangle** is the sacred geometric symbol of arifOS:

```svg
<svg viewBox="0 0 200 173">
  <!-- Main triangle outline -->
  <path d="M100 10 L190 163 L10 163 Z" 
        fill="none" 
        stroke="url(#trinityGradient)" 
        stroke-width="2"/>
  
  <!-- Inner triangle -->
  <path d="M100 50 L145 130 L55 130 Z" 
        fill="none" 
        stroke="url(#amberGradient)" 
        stroke-width="1.5"/>
  
  <!-- Center point (the witness) -->
  <circle cx="100" cy="100" r="5" fill="url(#trinityGradient)">
    <animate attributeName="opacity" values="0.9;0.4;0.9" dur="3s" repeatCount="indefinite"/>
  </circle>
</svg>
```

**Symbolism**:
- Outer triangle: The three layers (HUMAN, THEORY, APPS)
- Inner triangle: The recursive, self-similar nature of governance
- Center point: The witness — the sovereign human at the center

---

### 5.3 Glow & Shadow Effects

#### HUMAN (Forge Glow)
```css
.forge-glow {
  box-shadow: 
    0 0 20px rgba(139, 0, 0, 0.4),
    0 0 40px rgba(139, 0, 0, 0.2),
    0 0 60px rgba(139, 0, 0, 0.1);
}
```

#### THEORY (Scholarly Glow)
```css
.glass-apex {
  background: rgba(9, 11, 16, 0.9);
  border: 1px solid rgba(107, 140, 206, 0.15);
}
```

#### APPS (Tech Glow)
```css
.glow-cyan {
  box-shadow: 0 0 30px rgba(6, 182, 212, 0.3);
}
```

---

### 5.4 Animation Principles

| Animation | Duration | Easing | Usage |
|-----------|----------|--------|-------|
| Hover transitions | 200-300ms | ease | Interactive elements |
| Page transitions | 300-500ms | ease-out | Route changes |
| Ambient loops | 8-20s | ease-in-out infinite | Background elements |
| Pulse effects | 2-3s | ease-in-out infinite | Active states |
| Ember float | 10-15s | ease-out infinite | Atmospheric |

**Animation Values**:
- Subtle: opacity 0.9 ↔ 0.5, scale 1 ↔ 1.02
- Moderate: translateY(0) ↔ translateY(-10px)
- Dramatic: rotate(0deg) ↔ rotate(360deg)

---

## 6. COMPONENT PATTERNS

### 6.1 Buttons

#### Primary Button (HUMAN)
```
BG: #DC2626 (red-600)
Hover: #EF4444 (red-500)
Text: white
Padding: px-5 py-2.5
Radius: rounded-xl
Shadow: shadow-lg shadow-red-900/20
```

#### Secondary Button
```
BG: #262626 (neutral-800)
Border: 2px solid #404040 (neutral-700)
Hover: border-neutral-600, bg-neutral-700
Text: #E5E5E5
```

#### Ghost Button
```
BG: transparent
Border: 1px solid #333
Hover: bg-gray-900/50, border-gray-600
Text: gray-400
```

### 6.2 Cards

#### Standard Card
```
BG: bg-gray-900/20 or bg-[#141414]
Border: 1px solid #262626 (neutral-800)
Hover: border-gray-700, bg-gray-900/30
Radius: rounded-xl (12px)
Padding: p-6
```

#### Featured Card
```
BG: gradient from layer-primary/10 to transparent
Border: 2px solid layer-primary/30
Hover: border-layer-primary/50, shadow-lg shadow-layer-primary/10
```

### 6.3 Badges

```
BG: layer-primary/10
Border: 1px solid layer-primary/20
Text: layer-primary
Padding: px-2.5 py-1
Radius: rounded-md
Font: text-xs font-mono uppercase
```

---

## 7. VISUAL METAPHORS BY DISCIPLINE

### 7.1 Geology (Earth Element)
**Colors**: Browns, ochres, deep reds
**Patterns**: Strata lines, sedimentary layers, seismic waves
**Shapes**: Irregular, organic, eroded
**Textures**: Rough, weathered, compressed

```css
.strata-card {
  background: linear-gradient(135deg, #140A05, #28140A, #140A05);
  border: 1px solid rgba(139, 69, 19, 0.3);
}
```

### 7.2 Economics (Market Element)
**Colors**: Gold, crimson, green accents
**Patterns**: Grid lines, candlesticks, trend lines
**Shapes**: Precise, angular, chart-based
**Textures**: Clean, data-driven, numerical

```css
.market-card {
  background: rgba(10, 5, 5, 0.95);
  border: 1px solid rgba(220, 20, 60, 0.3);
  border-bottom: 3px solid linear-gradient(90deg, #8B0000, #DC143C);
}
```

### 7.3 AI/Neural (Mind Element)
**Colors**: Electric blue, cyan, purple accents
**Patterns**: Neural meshes, circuit traces, node networks
**Shapes**: Geometric, hexagonal, interconnected
**Textures**: Digital, glowing, transparent

```css
.neural-card {
  background: rgba(5, 5, 10, 0.95);
  border: 1px solid rgba(178, 34, 34, 0.3);
}
```

---

## 8. ACCESSIBILITY & CONTRAST

### 8.1 Contrast Ratios (WCAG 2.1)

| Combination | Ratio | Grade |
|-------------|-------|-------|
| `#E5E5E5` on `#0A0A0A` | 16.8:1 | AAA |
| `#FF2D2D` on `#0A0A0A` | 7.2:1 | AAA |
| `#8B0000` on `#0A0A0A` | 3.1:1 | AA (large text only) |
| `#6B7280` on `#0A0A0A` | 5.4:1 | AA |

### 8.2 Focus States

```css
:focus-visible {
  outline: 2px solid var(--layer-primary);
  outline-offset: 2px;
}
```

### 8.3 Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 9. IMPLEMENTATION CHECKLIST

### For New Components

- [ ] Color uses appropriate layer tokens
- [ ] Typography follows hierarchy (Inter/Space Mono/JetBrains)
- [ ] Border radius matches layer personality
- [ ] Spacing follows 4px grid
- [ ] Hover states defined with transitions
- [ ] Focus states accessible
- [ ] Dark mode only (no light mode in arifOS)
- [ ] Animation respects `prefers-reduced-motion`

### For Images/Illustrations

- [ ] Dark background (#0A0A0A or darker)
- [ ] Layer-appropriate accent colors
- [ ] Geometric elements where possible
- [ ] No pure white (#FFFFFF) — use #E5E5E5 or #FAFAFA
- [ ] Thermodynamic or constitutional symbolism

---

## 10. EXAMPLES

### Hero Section (HUMAN)
```
Background: #0A0A0A with subtle grid
Triangle: Tricolor gradient (Cyan→Amber→Red)
Name: White, text-5xl, font-semibold
Subtitle: Gray-400, font-mono, text-sm
Social buttons: Bordered pills with hover bg
```

### Constitutional Table (THEORY)
```
Table bg: transparent
Header: Steel blue border-bottom, uppercase mono
Rows: Hover bg-theory-primary/5
Borders: 1px solid theory-border
Text: theory-text, theory-muted
```

### Code Block (APPS)
```
Bg: #0D0D0D
Border: 1px solid #222
Radius: rounded-lg
Font: JetBrains Mono
Syntax: Cyan for keywords, Red for errors
```

---

## 11. SEAL

```
Version: v55.3
Schema Type: VISUAL_DESIGN_SYSTEM
Authority: 888_JUDGE
Status: FORGED_IN_RED
Last Updated: 2026-02-03
```

---

*"The design must cool before it rules."*

**Ditempa Bukan Diberi — Forged, Not Given.**
