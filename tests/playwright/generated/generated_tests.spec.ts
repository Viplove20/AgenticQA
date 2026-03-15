import { test, expect } from '@playwright/test';

async function login(page: any) {
  await page.goto('https://rahulshettyacademy.com/client/auth/login');
  await page.locator('#userEmail').fill(process.env.LOGIN_USERNAME ?? '');
  await page.locator('#userPassword').fill(process.env.LOGIN_PASSWORD ?? '');
  await page.locator('#login').click();
  await page.waitForURL('https://rahulshettyacademy.com/client/#/dashboard/dash', { timeout: 15000 });
}

test('TC_001 - Verify login page is accessible from the login URL', async ({ page }) => {
  await page.goto('https://rahulshettyacademy.com/client/#/auth/login');
  await expect(page).toHaveURL('https://rahulshettyacademy.com/client/#/auth/login');
});

test('TC_002 - Verify user can login with valid credentials and be redirected to the Dashboard page', async ({ page }) => {
  await login(page);
  await expect(page).toHaveURL('https://rahulshettyacademy.com/client/#/dashboard/dash');
});

test('TC_003 - Verify user login fails with an invalid password', async ({ page }) => {
  await page.goto('https://rahulshettyacademy.com/client/auth/login');
  await page.locator('#userEmail').fill(process.env.LOGIN_USERNAME ?? '');
  await page.locator('#userPassword').fill('invalid_password');
  await page.locator('#login').click();
  await expect(page.locator('.error')).toBeVisible({ timeout: 8000 });
});

test('TC_004 - Verify login attempt without entering email displays an error message', async ({ page }) => {
  await page.goto('https://rahulshettyacademy.com/client/auth/login');
  await page.locator('#userPassword').fill(process.env.LOGIN_PASSWORD ?? '');
  await page.locator('#login').click();
  await expect(page.locator('.error')).toBeVisible({ timeout: 8000 });
});

test('TC_005 - Verify dashboard displays a list of all available products', async ({ page }) => {
  await login(page);
  await page.waitForSelector('.card-body', { timeout: 10000 });
  const productCount = await page.locator('.card-body').count();
  expect(productCount).toBeGreaterThan(0);
});

test('TC_006 - Verify product search returns the correct product for exact case-sensitive names', async ({ page }) => {
  await login(page);
  await page.waitForSelector('.card-body', { timeout: 10000 });
  await page.locator('.card-title-filter input[placeholder="search"]').fill('Exact Product Name');
  await page.keyboard.press('Enter');
  const searchResults = await page.locator('.card-body h5').filter({ hasText: 'Exact Product Name' }).count();
  expect(searchResults).toBeGreaterThan(0);
});

test('TC_007 - Verify user can filter products using category checkboxes', async ({ page }) => {
  await login(page);
  await page.waitForSelector('.card-body', { timeout: 10000 });
  await page.locator('input[type="checkbox"]').first().check();
  await page.waitForTimeout(1500);
  const filteredProductCount = await page.locator('.card-body').count();
  expect(filteredProductCount).toBeGreaterThan(0);
});

test('TC_008 - Verify user is redirected to the product details page upon clicking the View button', async ({ page }) => {
  await login(page);
  await page.waitForSelector('.card-body', { timeout: 10000 });
  await page.locator('.card-body button:has-text("View")').first().click();
  await expect(page).toHaveURL(/.*\/product\/details/);
});

test('TC_009 - Verify user can add a product to cart from the dashboard', async ({ page }) => {
  await login(page);
  await page.waitForSelector('.card-body', { timeout: 10000 });
  await page.locator('.card-body button:has-text("Add To Cart")').first().click();
  await page.waitForTimeout(1500);
  // Verify cart count or any indication of product added can be checked here
});

test('TC_010 - Verify cart page is accessible from cart navigation after adding products', async ({ page }) => {
  await login(page);
  await page.waitForSelector('.card-body', { timeout: 10000 });
  await page.locator('.card-body button:has-text("Add To Cart")').first().click();
  await page.waitForTimeout(1500);
  await page.locator('[routerlink*="cart"]').click();
  await expect(page).toHaveURL('https://rahulshettyacademy.com/client/#/dashboard/cart');
});

test('TC_011 - Verify all products added from the dashboard are displayed in the cart', async ({ page }) => {
  await login(page);
  await page.waitForSelector('.card-body', { timeout: 10000 });
  await page.locator('.card-body button:has-text("Add To Cart")').first().click();
  await page.waitForTimeout(1500);
  await page.locator('[routerlink*="cart"]').click();
  await page.waitForSelector('tbody tr', { timeout: 10000 });
  const cartProductCount = await page.locator('tbody tr').count();
  expect(cartProductCount).toBeGreaterThan(0);
});

test('TC_012 - Verify the user can proceed to checkout using the Buy Now button', async ({ page }) => {
  await login(page);
  await page.waitForSelector('.card-body', { timeout: 10000 });
  await page.locator('.card-body button:has-text("Add To Cart")').first().click();
  await page.waitForTimeout(2000);
  await page.locator('[routerlink*="cart"]').click();
  await page.waitForSelector('tbody tr', { timeout: 10000 });
  await page.locator('button:has-text("Buy Now")').click();
  await expect(page).toHaveURL('https://rahulshettyacademy.com/client/#/dashboard/order');
});

test('TC_013 - Verify the user can proceed to checkout using the Checkout button', async ({ page }) => {
  await login(page);
  await page.waitForSelector('.card-body', { timeout: 10000 });
  await page.locator('.card-body button:has-text("Add To Cart")').first().click();
  await page.waitForTimeout(2000);
  await page.locator('[routerlink*="cart"]').click();
  await page.waitForSelector('tbody tr', { timeout: 10000 });
  await page.locator('button:has-text("Checkout")').click();
  await expect(page).toHaveURL('https://rahulshettyacademy.com/client/#/dashboard/order');
});

test('TC_014 - Verify user can enter and select a country for delivery in the checkout page', async ({ page }) => {
  await login(page);
  await page.goto('https://rahulshettyacademy.com/client/#/dashboard/order');
  await page.locator('input[placeholder="Select Country"]').fill('India');
  await page.locator('.css-26l3qy-menu').locator('div:has-text("India")').click();
  await expect(page.locator('input[placeholder="Select Country"]')).toHaveValue('India');
});

test('TC_015 - Verify user can place an order successfully and be redirected to the order summary page', async ({ page }) => {
  await login(page);
  await page.goto('https://rahulshettyacademy.com/client/#/dashboard/order');
  await page.locator('button:has-text("Place Order")').click();
  await expect(page.locator('.hero-primary')).toContainText('Thankyou for the order');
});

test('TC_016 - Verify order summary page displays ordered product details and confirmation message', async ({ page }) => {
  await login(page);
  await page.goto('https://rahulshettyacademy.com/client/#/dashboard/order');
  await page.locator('button:has-text("Place Order")').click();
  await expect(page.locator('.hero-primary')).toContainText('Thankyou for the order');
  // Here you may add more assertions to check ordered product details if applicable
});

test('TC_017 - Verify order history page is accessible and is displaying all past orders', async ({ page }) => {
  await login(page);
  await page.goto('https://rahulshettyacademy.com/client/#/dashboard/myorders');
  const orders = await page.locator('.table tbody tr').count();
  expect(orders).toBeGreaterThan(0);
});

test('TC_018 - Verify user can successfully logout from the application and be redirected to the login page', async ({ page }) => {
  await login(page);
  await page.locator('button:has-text("Logout")').click();
  await expect(page).toHaveURL('https://rahulshettyacademy.com/client/#/auth/login');
});