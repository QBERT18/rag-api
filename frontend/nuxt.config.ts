import tailwindcss from '@tailwindcss/vite'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  app: {
    head: {
      title: 'RAG Application',
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'alternate icon', href: '/favicon.ico' },
      ],
    },
  },
  runtimeConfig: {
    public: {
      apiBase: 'http://localhost:8000', // overridden by NUXT_PUBLIC_API_BASE
    },
  },
  modules: ['@nuxtjs/color-mode', '@nuxt/icon'],
  css: ['~/assets/css/main.css'],
  colorMode: {
    classSuffix: '',
    preference: 'system',
    fallback: 'light',
    storageKey: 'rag-color-mode',
  },
  icon: {
    mode: 'svg',
    serverBundle: {
      collections: ['lucide'],
    },
    localApiEndpoint: '/_nuxt_icon',
  },
  vite: {
    plugins: [tailwindcss()],
  },
})