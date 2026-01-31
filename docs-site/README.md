# arifOS MIND Documentation

**The MIND Layer** — Documentation, API Reference, and MCP Tools for the arifOS Constitutional AI Framework.

## Architecture Alignment

This site is part of the 3-layer ecosystem:

| Layer | Domain | Purpose | Design |
|-------|--------|---------|--------|
| **BODY** | arif-fazil.com | Identity, personal brand | Dark + Orange gradients |
| **SOUL** | apex.arif-fazil.com | Theory, canon, philosophy | Dark + Amber gradients |
| **MIND** | arifos.arif-fazil.com | Documentation, API, tools | Dark + Cyan/Blue gradients |

## Features

- **13 Floors Visualization** — Interactive display of constitutional safety checks
- **MCP Tools Reference** — Complete documentation of all 5 MCP tools
- **API Endpoints** — Live status and endpoint documentation
- **Code Examples** — Python SDK usage with copy-to-clipboard
- **Animated Background** — Mesh gradient with geometric patterns
- **Responsive Design** — Mobile-optimized with dark theme

## Technology Stack

- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS
- Lucide React (icons)

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Deployment

### Railway (Recommended)

```bash
# From project root
railway login
railway link
railway up --service arifos-docs
```

### Docker

```bash
docker build -t arifos-mind .
docker run -p 8080:80 arifos-mind
```

## Design System

### Colors
- Background: `#0a0a0a` (near black)
- Primary gradient: Cyan → Blue (MIND identity)
- Floor colors: Red → Orange → Yellow → Cyan → Green
- Text: Gray scale with white highlights

### Typography
- Font: System UI stack
- Mono: JetBrains Mono / Fira Code

### Effects
- Glass morphism: `backdrop-blur(12px)`
- Glow: Box shadows with color opacity
- Mesh gradients: Animated blur circles
- Geometric grid: CSS pattern overlay

---

**Ditempa Bukan Diberi** — Forged, Not Given
