import tailwindcss from '@tailwindcss/vite'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
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
  },
  vite: {
    plugins: [tailwindcss()],
  },
})