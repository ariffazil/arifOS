import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/',
    component: ComponentCreator('/', 'f57'),
    routes: [
      {
        path: '/',
        component: ComponentCreator('/', 'b5b'),
        routes: [
          {
            path: '/',
            component: ComponentCreator('/', '9f3'),
            routes: [
              {
                path: '/ai/checklist',
                component: ComponentCreator('/ai/checklist', '0a6'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/ai/crisis',
                component: ComponentCreator('/ai/crisis', '827'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/ai/identity',
                component: ComponentCreator('/ai/identity', '67a'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/ai/self-governance',
                component: ComponentCreator('/ai/self-governance', '018'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/ai/system-prompt',
                component: ComponentCreator('/ai/system-prompt', 'd64'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/concepts/atlas-333',
                component: ComponentCreator('/concepts/atlas-333', '459'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/concepts/problem',
                component: ComponentCreator('/concepts/problem', '177'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/concepts/teach/',
                component: ComponentCreator('/concepts/teach/', 'b2a'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/concepts/teach/amanah',
                component: ComponentCreator('/concepts/teach/amanah', '18f'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/concepts/teach/clarity',
                component: ComponentCreator('/concepts/teach/clarity', '5ba'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/concepts/teach/empathy',
                component: ComponentCreator('/concepts/teach/empathy', '0ff'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/concepts/teach/humility',
                component: ComponentCreator('/concepts/teach/humility', '7b0'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/concepts/teach/truth',
                component: ComponentCreator('/concepts/teach/truth', '763'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/concepts/trinity',
                component: ComponentCreator('/concepts/trinity', '8f1'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/concepts/verdicts',
                component: ComponentCreator('/concepts/verdicts', 'a08'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/faq',
                component: ComponentCreator('/faq', '7c5'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/floors/overview',
                component: ComponentCreator('/floors/overview', 'c8e'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/floors/reference',
                component: ComponentCreator('/floors/reference', '492'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/floors/thermodynamics',
                component: ComponentCreator('/floors/thermodynamics', 'da3'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/getting-started/first-check',
                component: ComponentCreator('/getting-started/first-check', '58d'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/getting-started/installation',
                component: ComponentCreator('/getting-started/installation', '91c'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/getting-started/quick-start',
                component: ComponentCreator('/getting-started/quick-start', 'a3a'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/guides/claude-code',
                component: ComponentCreator('/guides/claude-code', 'ffa'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/guides/claude-desktop',
                component: ComponentCreator('/guides/claude-desktop', '09d'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/guides/cursor',
                component: ComponentCreator('/guides/cursor', '017'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/guides/python',
                component: ComponentCreator('/guides/python', 'ae2'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/guides/system-prompt',
                component: ComponentCreator('/guides/system-prompt', '100'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/mcp/connection',
                component: ComponentCreator('/mcp/connection', '69c'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/mcp/examples',
                component: ComponentCreator('/mcp/examples', '605'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/mcp/overview',
                component: ComponentCreator('/mcp/overview', '4cb'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/mcp/tools/agi-genius',
                component: ComponentCreator('/mcp/tools/agi-genius', '7a0'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/mcp/tools/apex-judge',
                component: ComponentCreator('/mcp/tools/apex-judge', '32b'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/mcp/tools/asi-act',
                component: ComponentCreator('/mcp/tools/asi-act', 'f67'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/mcp/tools/init-000',
                component: ComponentCreator('/mcp/tools/init-000', 'e70'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/mcp/tools/vault-999',
                component: ComponentCreator('/mcp/tools/vault-999', '25b'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/quick-reference',
                component: ComponentCreator('/quick-reference', '0d9'),
                exact: true,
                sidebar: "docsSidebar"
              },
              {
                path: '/',
                component: ComponentCreator('/', '780'),
                exact: true,
                sidebar: "docsSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
