import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './tests/web',
  use: { baseURL: 'http://127.0.0.1:4173/happy-mi/', headless: true },
  webServer: {
    command: 'npm run docs:preview -- --port 4173',
    url: 'http://127.0.0.1:4173/happy-mi/',
    reuseExistingServer: !process.env.CI
  },
  projects: [
    { name: 'desktop', use: { viewport: { width: 1440, height: 1000 } } },
    { name: 'mobile', use: { viewport: { width: 390, height: 844 }, isMobile: true } }
  ]
})
