import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/playwright/generated', // directory where your generated tests are saved
  //retries: 2,                               // retry failed tests automatically
  reporter: [
    ['list'],                               // console output
    ['json', { outputFile: 'playwright-report/results.json' }] // JSON report
  ],
  use: {
    headless: true,                         // run in headless mode
    screenshot: 'only-on-failure',          // take screenshots only on failure
  },
});