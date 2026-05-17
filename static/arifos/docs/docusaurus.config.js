// @ts-check
// docusaurus.config.js - arifOS Docs Site
// Target: https://arifos.arif-fazil.com/
// Source: https://github.com/ariffazil/arifOS

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'arifOS',
  tagline: 'The System That Knows It Doesn\'t Know',
  titleDelimiter: '·',
  favicon: 'img/favicon.ico',

  url: 'https://arifos.arif-fazil.com',
  baseUrl: '/',
  scripts: [
    {
      src: '/scripts/sovereign-unify.js',
      async: true,
    },
  ],

  organizationName: 'ariffazil',
  projectName: 'arifOS',
  trailingSlash: false,

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  onBrokenAnchors: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          routeBasePath: '/',
          sidebarPath: './sidebars.js',
          editUrl: 'https://github.com/ariffazil/arifOS/edit/main/sites/library/',
          showLastUpdateTime: true,
          showLastUpdateAuthor: false,
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
        sitemap: {
          changefreq: 'weekly',
          priority: 0.5,
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Dark-first colour palette (matches arifOS identity)
      colorMode: {
        defaultMode: 'dark',
        disableSwitch: true,
        respectPrefersColorScheme: false,
      },

      image: 'img/arifos-og.png',

      navbar: {
        title: 'arifOS',
        logo: {
          alt: 'arifOS Logo',
          src: 'img/logo.svg',
          href: '/intro',
        },
        items: [
          {
            href: 'https://arif-fazil.com/',
            label: 'HUMAN',
            position: 'left',
          },
          {
            href: 'https://apex.arif-fazil.com/',
            label: 'THEORY',
            position: 'left',
          },
          {
            type: 'docSidebar',
            sidebarId: 'docsSidebar',
            position: 'left',
            label: 'Docs',
          },
          {
            href: 'https://github.com/ariffazil/arifOS',
            label: 'GitHub (Mind)',
            position: 'right',
          },
          {
            href: 'https://github.com/ariffazil/arifosmcp',
            label: 'GitHub (Body)',
            position: 'right',
          },
          {
            href: 'https://pypi.org/project/arifosmcp/',
            label: 'PyPI',
            position: 'right',
          },
          {
            href: 'https://arifosmcp.arif-fazil.com',
            label: 'Status',
            position: 'right',
          },

        ],
      },

      footer: {
        style: 'dark',
        links: [
          {
            title: 'Trinity',
            items: [
              { label: 'HUMAN', href: 'https://arif-fazil.com/' },
              { label: 'THEORY', href: 'https://apex.arif-fazil.com/' },
              { label: 'APPS', href: 'https://arifos.arif-fazil.com/' },
            ],
          },
          {
            title: 'Docs',
            items: [
              { label: 'Introduction', to: '/intro' },
              { label: 'MCP Server', to: '/mcp-server' },
              { label: 'Governance', to: '/governance' },
              { label: 'API Reference', to: '/api' },
            ],
          },
          {
            title: 'Source',
            items: [
              {
                label: 'GitHub (Mind)',
                href: 'https://github.com/ariffazil/arifOS',
              },
              {
                label: 'GitHub (Body)',
                href: 'https://github.com/ariffazil/arifosmcp',
              },
              {
                label: 'PyPI',
                href: 'https://pypi.org/project/arifosmcp/',
              },
            ],
          },
          {
            title: 'Governance',
            items: [
              {
                label: 'Live Health',
                href: 'https://arifosmcp.arif-fazil.com',
              },
              {
                label: '000_THEORY',
                href: 'https://github.com/ariffazil/arifosmcp/tree/main/000_THEORY',
              },
              {
                label: 'License (AGPL-3.0)',
                href: 'https://github.com/ariffazil/arifosmcp/blob/main/LICENSE',
              },
            ],
          },
        ],
        copyright: `arifOS - <em>Ditempa Bukan Diberi</em> (Forged, Not Given)<br/>Built ${new Date().getFullYear()} - ARIF FAZIL - AGPL-3.0`,
      },

      prism: {
        theme: require('prism-react-renderer').themes.dracula,
        darkTheme: require('prism-react-renderer').themes.dracula,
        additionalLanguages: ['bash', 'python', 'json', 'nginx', 'docker'],
      },

      // Announcement bar for live status
      announcementBar: {
        id: 'live_status',
        content:
          '<span class="health-pulse" style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#3b82f6;margin-right:8px;box-shadow:0 0 8px rgba(59,130,246,0.6);"></span> <span style="font-family: monospace; letter-spacing: 0.05em;">&gt; arifOS MCP :: <a href="https://arifosmcp.arif-fazil.com">STATUS LIVE</a> &mdash; <a href="/mcp-server">Connect in 30s</a></span>',
        backgroundColor: '#060a14',
        textColor: '#3b82f6',
        isCloseable: true,
      },
    }),
};

module.exports = config;
