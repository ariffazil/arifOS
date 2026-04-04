# Project Guidelines

## Code Style
- React + TypeScript with ESM; keep imports explicit and prefer functional components.
- Tailwind CSS is the primary styling tool; use existing utility patterns and design tokens.
- Theme tokens and CSS variables live in site/src/index.css; prefer extending them over ad-hoc colors.

## Architecture
- Static SPA built with Vite; entry in site/src/main.tsx and root UI in site/src/App.tsx.
- Shared UI primitives live in site/src/components/ui; feature components in site/src/components.
- Front-end only; no server runtime in this workspace.

## Build and Test
- Install: npm install
- Dev: npm run dev
- Build: npm run build
- Lint: npm run lint
- Preview: npm run preview

## Project Conventions
- Vite base is relative for static hosting (base: './'); do not switch to absolute without reason.
- Use the @ alias for src (configured in site/vite.config.ts).
- Typography and color system follow the gold-on-dark theme; see site/src/index.css and site/tailwind.config.js.

## Integration Points
- KaTeX for math rendering, Lucide React for icons, Radix + shadcn/ui for components (see site/package.json).
- Deployment target is static hosting; currently documented for Cloudflare Pages.

## Security
- Treat all content as public client-side assets; never embed secrets or credentials.
