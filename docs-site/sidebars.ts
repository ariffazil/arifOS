import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

/**
 * arifOS Documentation Sidebar Structure
 * Organized for zero-context readers, developers, and AI systems
 */
const sidebars: SidebarsConfig = {
  docsSidebar: [
    'introduction',
    {
      type: 'category',
      label: 'Getting Started',
      collapsed: false,
      items: [
        'getting-started/quick-start',
        'getting-started/installation',
        'getting-started/first-check',
      ],
    },
    {
      type: 'category',
      label: 'Core Concepts',
      items: [
        'concepts/problem',
        {
          type: 'category',
          label: 'TEACH Framework',
          items: [
            'concepts/teach/index',
            'concepts/teach/truth',
            'concepts/teach/empathy',
            'concepts/teach/amanah',
            'concepts/teach/clarity',
            'concepts/teach/humility',
          ],
        },
        'concepts/verdicts',
        'concepts/atlas-333',
        'concepts/trinity',
        'concepts/guarantees',
      ],
    },
    {
      type: 'category',
      label: 'Integration Guides',
      items: [
        'guides/system-prompt',
        'guides/claude-desktop',
        'guides/claude-code',
        'guides/cursor',
        'guides/kimi',
        'guides/gemini',
        'guides/chatgpt',
        'guides/python',
      ],
    },
    {
      type: 'category',
      label: 'MCP Reference',
      items: [
        'mcp/overview',
        'mcp/connection',
        {
          type: 'category',
          label: 'Tools',
          items: [
            'mcp/tools/init-000',
            'mcp/tools/agi-genius',
            'mcp/tools/asi-act',
            'mcp/tools/apex-judge',
            'mcp/tools/vault-999',
            'mcp/tools/trinity-loop',
          ],
        },
        'mcp/examples',
      ],
    },
    {
      type: 'category',
      label: 'Constitutional Floors',
      items: [
        'floors/overview',
        'floors/reference',
        'floors/thermodynamics',
      ],
    },
    {
      type: 'category',
      label: 'For AI Systems',
      items: [
        'ai/self-governance',
        'ai/checklist',
        'ai/identity',
        'ai/crisis',
        'ai/system-prompt',
      ],
    },
    'faq',
    'quick-reference',
  ],
};

export default sidebars;
