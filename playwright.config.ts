import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/playwright/generated', // directory where your generated tests are saved
  //retries: 2,                               // retry failed tests automatically
  reporter: [
    ['list'],
    ['json', { outputFile: 'output/playwright-report/results.json' }]
  ],
  use: {
    headless: false,                         // run in headed mode
    screenshot: 'only-on-failure',          // take screenshots only on failure
  },
});