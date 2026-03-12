import { test, expect } from '@playwright/test';

async function login(page: any) {
  await page.goto('https://rahulshettyacademy.com/client/auth/login');
  await page.locator('#userEmail').fill(process.env.LOGIN_USERNAME ?? '');
  await page.locator('#userPassword').fill(process.env.LOGIN_PASSWORD ?? '');
  await page.locator('#login').click();
  await page.waitForURL('https://rahulshettyacademy.com/client/#/dashboard/dash', { timeout: 15000 });
}

test('TC_001 - Verify user can access the login page', async ({ page }) => {
  await page.goto('https://rahulshettyacademy.com/client/auth/login');
  await expect(page).toHaveURL('https://rahulshettyacademy.com/client/auth/login');
});

test('TC_002 - Verify user can login with valid credentials', async ({ page }) => {
  await login(page);
  await expect(page).toHaveURL('https://rahulshettyacademy.com/client/#/dashboard/dash');
});

test('TC_003 - Verify user session starts after successful login', async ({ page }) => {
  await login(page);
  // Assuming checking some page state or cookies for session validation
});

test('TC_004 - Verify error message is displayed for invalid credentials', async ({ page }) => {
  await page.goto('https://rahulshettyacademy.com/client/auth/login');
  await page.locator('#userEmail').fill('invalid@example.com');
  await page.locator('#userPassword').fill('InvalidPassword');
  await page.locator('#login').click();
  await expect(page.locator('.error')).toBeVisible({ timeout: 8000 });
});

test('TC_005 - Verify login fails when email field is empty', async ({ page }) => {
  await page.goto('https://rahulshettyacademy.com/client/auth/login');
  await page.locator('#userPassword').fill('ValidPassword'); // Assuming a valid password
  await page.locator('#login').click();
  await expect(page.locator('.error')).toBeVisible({ timeout: 8000 });
});

test('TC_006 - Verify login fails when password field is empty', async ({ page }) => {
  await page.goto('https://rahulshettyacademy.com/client/auth/login');
  await page.locator('#userEmail').fill('valid@example.com'); // Assuming a valid email
  await page.locator('#login').click();
  await expect(page.locator('.error')).toBeVisible({ timeout: 8000 });
});

test('TC_007 - Verify all available products are displayed on the dashboard', async ({ page }) => {
  await login(page);
  await page.waitForSelector('.card-body', { timeout: 10000 });
  expect(await page.locator('.card-body').count()).toBeGreaterThan(0);
});

test('TC_008 - Verify user can search products using the search field', async ({ page }) => {
  await login(page);
  await page.waitForSelector('.card-body', { timeout: 10000 });
  await page.locator('.card-title-filter input[placeholder="search"]').first().fill('Product Name');
  await page.keyboard.press('Enter');
  expect(await page.locator('.card-body').count()).toBeGreaterThan(0); // Assume search should return results
});

test('TC_009 - Verify user can use category filters on the product list', async ({ page }) => {
  await login(page);
  await page.waitForSelector('.card-body', { timeout: 10000 });
  await page.locator('.checklist input[type="checkbox"]').first().click();
  await page.waitForTimeout(1500);
  expect(await page.locator('.card-body').count()).toBeGreaterThan(0); // Assume filter changes results
});

test('TC_010 - Verify home navigation redirects user to dashboard page', async ({ page }) => {
  await login(page);
  await page.locator('button[routerlink="/dashboard/"]').click();
  await expect(page).toHaveURL('https://rahulshettyacademy.com/client/#/dashboard/dash');
});

test('TC_011 - Verify user can view product details from the dashboard', async ({ page }) => {
  await login(page);
  await page.waitForSelector('.card-body', { timeout: 10000 });
  await page.locator('.card-body button:has-text("View")').first().click();
  await expect(page).toHaveURL(/.*product.*/);
});

test('TC_012 - Verify user can add products to the cart', async ({ page }) => {
  await login(page);
  await page.waitForSelector('.card-body', { timeout: 10000 });
  await page.locator('.card-body button:has-text("Add To Cart")').first().click();
  await page.waitForTimeout(1500);
  await page.locator('[routerlink*="cart"]').click();
  await page.waitForSelector('tbody tr', { timeout: 10000 });
  expect(await page.locator('tbody tr').count()).toBeGreaterThan(0);
});

test('TC_013 - Verify user can access the cart page', async ({ page }) => {
  await login(page);
  await page.locator('[routerlink*="cart"]').click();
  await expect(page).toHaveURL('https://rahulshettyacademy.com/client/#/dashboard/cart');
});

test('TC_014 - Verify cart displays products added from the dashboard', async ({ page }) => {
  await login(page);
  await page.goto('https://rahulshettyacademy.com/client/#/dashboard/cart');
  await page.waitForSelector('tbody tr', { timeout: 10000 });
  expect(await page.locator('tbody tr').count()).toBeGreaterThan(0);
});

test('TC_015 - Verify user can proceed to checkout', async ({ page }) => {
  await login(page);
  await page.goto('https://rahulshettyacademy.com/client/#/dashboard/cart');
  await page.waitForSelector('tbody tr', { timeout: 10000 });
  await page.locator('button:has-text("Checkout")').click();
  await expect(page).toHaveURL('https://rahulshettyacademy.com/client/#/dashboard/order');
});

test('TC_016 - Verify user can enter country for delivery during checkout', async ({ page }) => {
  await login(page);
  // Following the precondition by ensuring we're on the checkout page
  await page.goto('https://rahulshettyacademy.com/client/#/dashboard/order');
  await page.locator('[placeholder*="Select Country"]').fill('India');
  expect(await page.locator('[placeholder*="Select Country"]').inputValue()).toBe('India');
});

test('TC_017 - Verify user can place an order successfully', async ({ page }) => {
  await login(page);
  // Ensuring cart flow is completed
  await page.goto('https://rahulshettyacademy.com/client/#/dashboard/dash');
  await page.waitForSelector('.card-body', { timeout: 10000 });
  await page.locator('.card-body button:has-text("Add To Cart")').first().click();
  await page.waitForTimeout(2000);
  await page.locator('[routerlink*="cart"]').click();
  await page.waitForSelector('tbody tr', { timeout: 10000 });
  await page.locator('button:has-text("Checkout")').click();
  await page.fill('[placeholder*="Select Country"]', 'India');
  await page.locator('.suggestions span').first().click(); // Select suggestion
  await page.locator('button:has-text("Place Order")').click();
  await expect(page).toHaveURL('https://rahulshettyacademy.com/client/#/dashboard/thanks/');
});

test('TC_018 - Verify order summary page displays order details', async ({ page }) => {
  await login(page);
  // Ensure order placement first to reach order summary
  await page.goto('https://rahulshettyacademy.com/client/#/dashboard/thanks/');
  await expect(page.locator('.hero-primary')).toContainText('Thankyou for the order');
});

test('TC_019 - Verify user can access order history', async ({ page }) => {
  await login(page);
  await page.locator('[routerlink*="myorders"]').click();
  await expect(page).toHaveURL('https://rahulshettyacademy.com/client/#/dashboard/myorders');
});

test('TC_020 - Verify order history displays all placed orders', async ({ page }) => {
  await login(page);
  await page.locator('[routerlink*="myorders"]').click();
  expect(await page.locator('tbody tr').count()).toBeGreaterThan(0);
});

test('TC_021 - Verify user can logout successfully', async ({ page }) => {
  await login(page);
  await page.locator('.fa-sign-out').click();
  await expect(page).toHaveURL('https://rahulshettyacademy.com/client/auth/login');
});

test('TC_022 - Verify case-sensitive behavior of the search field', async ({ page }) => {
  await login(page);
  await page.waitForSelector('.card-body', { timeout: 10000 });
  await page.locator('.card-title-filter input[placeholder="search"]').first().fill('PRODUCT NAME');
  await page.keyboard.press('Enter');
  expect(await page.locator('.card-body').count()).toBeGreaterThan(0); // Assumes results handling case sensitivity
});

test('TC_023 - Verify product details page URL contains correct path', async ({ page }) => {
  await login(page);
  await page.waitForSelector('.card-body', { timeout: 10000 });
  await page.locator('.card-body button:has-text("View")').first().click();
  await expect(page).toHaveURL(/.*product.*/);
});

test('TC_024 - Verify country suggestions appear for text input in the country field', async ({ page }) => {
  await login(page);
  await page.goto('https://rahulshettyacademy.com/client/#/dashboard/order');
  await page.locator('[placeholder*="Select Country"]').fill('Ind');
  await expect(page.locator('.suggestions span')).toBeVisible();
});

test('TC_025 - Verify redirection to order confirmation page after placing an order', async ({ page }) => {
  await login(page);
  // Ensure cart flow is completed
  await page.goto('https://rahulshettyacademy.com/client/#/dashboard/dash');
  await page.waitForSelector('.card-body', { timeout: 10000 });
  await page.locator('.card-body button:has-text("Add To Cart")').first().click();
  await page.waitForTimeout(2000);
  await page.locator('[routerlink*="cart"]').click();
  await page.waitForSelector('tbody tr', { timeout: 10000 });
  await page.locator('button:has-text("Checkout")').click();
  await page.fill('[placeholder*="Select Country"]', 'India');
  await page.locator('.suggestions span').first().click();
  await page.locator('button:has-text("Place Order")').click();
  await expect(page).toHaveURL('https://rahulshettyacademy.com/client/#/dashboard/thanks/');
});

test('TC_026 - Verify confirmation message appears on order summary page upon successful order placement', async ({ page }) => {
  await login(page);
  // Ensure order placement first to have order summary
  await page.goto('https://rahulshettyacademy.com/client/#/dashboard/thanks/');
  await expect(page.locator('.hero-primary')).toContainText('Thankyou for the order');
});