import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'VCF Liftover',
  titleTemplate: ':title | AfriGen-D',
  description: 'A robust Nextflow pipeline for converting VCF files between genome builds using CrossMap - developed by AfriGen-D',
  base: '/vcf-liftover/',
  ignoreDeadLinks: true,
  lang: 'en-US',

  head: [
    ['link', { rel: 'icon', href: '/vcf-liftover/logo.png' }],
    ['meta', { name: 'theme-color', content: '#3c82f6' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'en' }],
    ['meta', { property: 'og:title', content: 'VCF Liftover | AfriGen-D' }],
    ['meta', { property: 'og:site_name', content: 'VCF Liftover' }],
    ['meta', { property: 'og:image', content: 'https://afrigen-d.github.io/vcf-liftover/logo.png' }],
    ['meta', { property: 'og:url', content: 'https://afrigen-d.github.io/vcf-liftover/' }],
    ['meta', { property: 'og:description', content: 'A robust Nextflow pipeline for converting VCF files between genome builds using CrossMap - developed by AfriGen-D' }]
  ],

  themeConfig: {
    logo: '/logo.png',

    nav: [
      { text: 'Home', link: '/' },
      { text: 'Guide', link: '/guide/getting-started' },
      { text: 'Parameters', link: '/reference/parameters' },
      { text: 'Examples', link: '/examples/' },
      { text: 'Workflow', link: '/workflow/' }
    ],

    sidebar: {
      '/guide/': [
        {
          text: 'Getting Started',
          collapsed: false,
          items: [
            { text: 'Introduction', link: '/guide/getting-started' },
            { text: 'Installation', link: '/guide/installation' },
            { text: 'Quick Start', link: '/guide/quick-start' },
            { text: 'Configuration', link: '/guide/configuration' }
          ]
        },
        {
          text: 'Pipeline Usage',
          collapsed: false,
          items: [
            { text: 'Input Files', link: '/guide/input-files' },
            { text: 'Running the Pipeline', link: '/guide/running' },
            { text: 'Output Files', link: '/guide/output-files' },
            { text: 'Troubleshooting', link: '/guide/troubleshooting' }
          ]
        }
      ],
      '/reference/': [
        {
          text: 'Reference',
          collapsed: false,
          items: [
            { text: 'Parameters', link: '/reference/parameters' },
            { text: 'Profiles', link: '/reference/profiles' },
            { text: 'Configuration', link: '/reference/configuration' }
          ]
        }
      ],
      '/workflow/': [
        {
          text: 'Workflow Details',
          collapsed: false,
          items: [
            { text: 'Overview', link: '/workflow/' },
            { text: 'Process Flow', link: '/workflow/process-flow' },
            { text: 'Subworkflows', link: '/workflow/subworkflows' },
            { text: 'Resource Usage', link: '/workflow/resources' }
          ]
        }
      ]
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/AfriGen-D/vcf-liftover' },
      {
        icon: {
          svg: '<svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><title>Docker</title><path d="M13.983 11.078h2.119a.186.186 0 00.186-.185V9.006a.186.186 0 00-.186-.186h-2.119a.185.185 0 00-.185.185v1.888c0 .102.083.185.185.185m-2.954-5.43h2.118a.186.186 0 00.186-.186V3.574a.186.186 0 00-.186-.185h-2.118a.185.185 0 00-.185.185v1.888c0 .102.082.185.185.186m0 2.716h2.118a.187.187 0 00.186-.186V6.29a.186.186 0 00-.186-.185h-2.118a.185.185 0 00-.185.185v1.887c0 .102.082.185.185.186m-2.93 0h2.12a.186.186 0 00.184-.186V6.29a.185.185 0 00-.185-.185H8.1a.185.185 0 00-.185.185v1.887c0 .102.083.185.185.186m-2.964 0h2.119a.186.186 0 00.185-.186V6.29a.185.185 0 00-.185-.185H5.136a.186.186 0 00-.186.185v1.887c0 .102.084.185.186.186m5.893 2.715h2.118a.186.186 0 00.186-.185V9.006a.186.186 0 00-.186-.186h-2.118a.185.185 0 00-.185.185v1.888c0 .102.082.185.185.185m-2.93 0h2.12a.185.185 0 00.184-.185V9.006a.185.185 0 00-.184-.186h-2.12a.185.185 0 00-.184.185v1.888c0 .102.083.185.185.185m-2.964 0h2.119a.185.185 0 00.185-.185V9.006a.185.185 0 00-.184-.186h-2.12a.186.186 0 00-.186.186v1.887c0 .102.084.185.186.185m0 2.715h2.119a.185.185 0 00.185-.185v-1.888a.185.185 0 00-.184-.185h-2.12a.185.185 0 00-.185.185v1.888c0 .102.084.185.186.185m16.646-7.22c-.46-.02-.94.02-1.26.14-.55-.02-1.26.04-2.02.27a.142.142 0 00-.1.17c.06.14.14.24.22.34 1.06-.83 2.572-.84 4.24-.34l.28.14c.26-.48.32-1.01.24-1.55a.186.186 0 00-.37-.11c-.22.45-.44.84-.73 1.07-.14-.01-.28-.02-.42-.02-.51 0-.98.03-1.42.08z"/></svg>'
        },
        link: 'https://hub.docker.com/u/afrigend'
      }
    ],

    footer: {
      message: 'Released under the MIT License.',
      copyright: 'Copyright © 2025 AfriGen-D Project'
    },

    search: {
      provider: 'local',
      options: {
        placeholder: 'Search documentation...',
        translations: {
          button: {
            buttonText: 'Search',
            buttonAriaLabel: 'Search documentation'
          },
          modal: {
            displayDetails: 'Display detailed list',
            resetButtonTitle: 'Reset search',
            backButtonTitle: 'Close search',
            noResultsText: 'No results for',
            footer: {
              selectText: 'to select',
              selectKeyAriaLabel: 'enter',
              navigateText: 'to navigate',
              navigateUpKeyAriaLabel: 'up arrow',
              navigateDownKeyAriaLabel: 'down arrow',
              closeText: 'to close',
              closeKeyAriaLabel: 'escape'
            }
          }
        }
      }
    },

    editLink: {
      pattern: 'https://github.com/AfriGen-D/vcf-liftover/edit/main/docs/:path',
      text: 'Edit this page on GitHub'
    },

    lastUpdated: {
      text: 'Last updated',
      formatOptions: {
        dateStyle: 'short',
        timeStyle: 'medium'
      }
    }
  },

  markdown: {
    lineNumbers: true,
    math: true
  }
})