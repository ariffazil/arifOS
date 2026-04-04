// @ts-check
// docusaurus.config.js - arifOS Docs Site
// Target: https://arifos.arif-fazil.com/
// Source: https://github.com/ariffazil/arifOS

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'arifOS — THE MIND',
  tagline: 'Constitutional Theory & Governance for AI Systems',
  titleDelimiter: '·',
  favicon: 'img/favicon.ico',

  url: 'https://arifos.arif-fazil.com',
  baseUrl: '/',

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
          editUrl: 'https://github.com/ariffazil/arifOS/edit/main/sites/docs/',
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
            type: 'docSidebar',
            sidebarId: 'docsSidebar',
            position: 'left',
            label: 'Docs',
          },
          {
            href: 'https://github.com/ariffazil/arifOS',
            label: 'GitHub (THE MIND)',
            position: 'right',
          },
          {
            href: 'https://github.com/ariffazil/arifosmcp',
            label: 'GitHub (THE BODY)',
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
              { 
                label: '🧠 THE MIND (Theory)', 
                href: 'https://github.com/ariffazil/arifOS',
              },
              { 
                label: '💪 THE BODY (Runtime)', 
                href: 'https://github.com/ariffazil/arifosmcp',
              },
              { 
                label: '👤 THE SURFACE (Portal)', 
                href: 'https://github.com/ariffazil/ariffazil',
              },
            ],
          },
          {
            title: 'Constitution',
            items: [
              { label: '13 Floors', to: '/constitution/floors' },
              { label: '7-Organ Canon', to: '/constitution/canon' },
              { label: 'Metabolic Loop', to: '/constitution/metabolic' },
              { label: 'Genius Equation', to: '/constitution/genius' },
            ],
          },
          {
            title: 'Runtime',
            items: [
              {
                label: 'Install (pip)',
                href: 'https://pypi.org/project/arifos/',
              },
              {
                label: 'Install (npm)',
                href: 'https://www.npmjs.com/package/@arifos/mcp',
              },
              {
                label: 'Live Status',
                href: 'https://arifosmcp.arif-fazil.com',
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
                label: 'KERNEL/FLOORS',
                href: 'https://github.com/ariffazil/arifOS/tree/main/KERNEL/FLOORS',
              },
              {
                label: 'License (AGPL-3.0)',
                href: 'https://github.com/ariffazil/arifOS/blob/main/LICENSE',
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

      // Announcement bar for theory/runtime separation
      announcementBar: {
        id: 'mind_body_split',
        content:
          '<span style="font-family: monospace; letter-spacing: 0.05em;">🧠 <strong>THE MIND</strong> (Theory) — 📖 Docs | 💪 <strong>THE BODY</strong> (Runtime) — <a href="https://github.com/ariffazil/arifosmcp">github.com/ariffazil/arifosmcp</a></span>',
        backgroundColor: '#060a14',
        textColor: '#10b981',
        isCloseable: true,
      },
    }),
};

module.exports = config;
