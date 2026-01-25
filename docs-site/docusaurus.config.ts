import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'arifOS Documentation',
  tagline: 'AI That Can\'t Lie to You — Constitutional AI Governance',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  // Production URL - Cloudflare Pages
  url: 'https://docs.arif-fazil.com',
  baseUrl: '/',
  trailingSlash: false,

  // GitHub config
  organizationName: 'ariffazil',
  projectName: 'arifOS',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: '/', // Docs at root instead of /docs
          editUrl: 'https://github.com/ariffazil/arifOS/tree/main/docs-site/',
        },
        blog: false, // Disable blog
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/arifos-social-card.png',
    colorMode: {
      defaultMode: 'light',
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'arifOS',
      logo: {
        alt: 'arifOS Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docsSidebar',
          position: 'left',
          label: 'Documentation',
        },
        {
          href: 'https://arifos.arif-fazil.com/health',
          label: 'Live Server',
          position: 'left',
        },
        {
          href: 'https://arifos.arif-fazil.com/dashboard',
          label: 'Dashboard',
          position: 'left',
        },
        {
          href: 'https://pypi.org/project/arifos/',
          label: 'PyPI',
          position: 'right',
        },
        {
          href: 'https://github.com/ariffazil/arifOS',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Documentation',
          items: [
            { label: 'Getting Started', to: '/getting-started/quick-start' },
            { label: 'TEACH Framework', to: '/concepts/teach' },
            { label: 'MCP Reference', to: '/mcp/overview' },
            { label: 'For AI Systems', to: '/ai/self-governance' },
          ],
        },
        {
          title: 'Live Services',
          items: [
            { label: 'MCP Server', href: 'https://arifos.arif-fazil.com/sse' },
            { label: 'Health Check', href: 'https://arifos.arif-fazil.com/health' },
            { label: 'Dashboard', href: 'https://arifos.arif-fazil.com/dashboard' },
            { label: 'API Docs', href: 'https://arifos.arif-fazil.com/docs' },
          ],
        },
        {
          title: 'Resources',
          items: [
            { label: 'GitHub', href: 'https://github.com/ariffazil/arifOS' },
            { label: 'PyPI', href: 'https://pypi.org/project/arifos/' },
            { label: 'Issues', href: 'https://github.com/ariffazil/arifOS/issues' },
            { label: 'YouTube', href: 'https://www.youtube.com/watch?v=bGnzIwZAgm0' },
          ],
        },
        {
          title: 'Contact',
          items: [
            { label: 'Email', href: 'mailto:arifbfazil@gmail.com' },
            { label: '@ariffazil', href: 'https://github.com/ariffazil' },
          ],
        },
      ],
      copyright: `© ${new Date().getFullYear()} Muhammad Arif bin Fazil · Penang, Malaysia · <em>Ditempa Bukan Diberi</em>`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'python', 'json'],
    },
    // Algolia search (optional - can configure later)
    // algolia: {
    //   appId: 'YOUR_APP_ID',
    //   apiKey: 'YOUR_API_KEY',
    //   indexName: 'arifos',
    // },
  } satisfies Preset.ThemeConfig,
};

export default config;
