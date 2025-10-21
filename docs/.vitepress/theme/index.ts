import { h } from 'vue'
import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import './style.css'
import './custom.css'
import AnnouncementBanner from './components/AnnouncementBanner.vue'

export default {
  extends: DefaultTheme,
  Layout: () => {
    return h(DefaultTheme.Layout, null, {
      // https://vitepress.dev/guide/extending-default-theme#layout-slots
      'nav-bar-content-before': () => h(AnnouncementBanner, {
        title: '🎉 New Quick Start Tutorial Available!',
        details: 'Get started with VCF liftover in just 5 minutes',
        link: '/tutorials/quick-start'
      })
    })
  },
  enhanceApp({ app, router, siteData }) {
    // Register global components
    app.component('AnnouncementBanner', AnnouncementBanner)
  }
} satisfies Theme