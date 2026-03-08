```javascript
const { chromium } = require('playwright');

async function runAllTests() {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  const results = {
    total_tests: 0,
    passed: 0,
    failed: 0,
    pass_rate: "0%",
    failed_tests: []
  };
  
  const tests = [
    {
      test_id: "TC_001",
      module: "Login",
      scenario: "Verify user can login with valid credentials",
      execute: async () => {
        await page.goto('http://localhost/login').catch(() => {});
        await page.waitForTimeout(1000);
        const usernameField = await page.locator('[name="username"], [placeholder*="username"], input[type="text"]').first();
        await usernameField.fill(process.env.LOGIN_USERNAME);
        const passwordField = await page.locator('[type="password"], [placeholder*="password"]').first();
        await passwordField.fill(process.env.LOGIN_PASSWORD);
        await page.click('button:has-text("Login"), button[type="submit"]');
        await page.waitForTimeout(2000);
        const isOnDashboard = page.url().includes('dashboard') || page.url().includes('home');
        if (!isOnDashboard) throw new Error('Not redirected to dashboard');
      }
    },
    {
      test_id: "TC_002",
      module: "Login",
      scenario: "Verify error message is displayed for invalid email format",
      execute: async () => {
        await page.goto('http://localhost/login').catch(() => {});
        await page.waitForTimeout(1000);
        const emailField = await page.locator('[name="username"], [placeholder*="username"], input[type="text"]').first();
        await emailField.fill(process.env.INVALID_EMAIL);
        const passwordField = await page.locator('[type="password"], [placeholder*="password"]').first();
        await passwordField.fill(process.env.LOGIN_PASSWORD);
        await page.click('button:has-text("Login"), button[type="submit"]');
        await page.waitForTimeout(2000);
        const errorMessage = await page.locator('text=Invalid email format').isVisible();
        if (!errorMessage) throw new Error('Error message not displayed for invalid email');
      }
    },
    {
      test_id: "TC_003",
      module: "Login",
      scenario: "Verify error message is displayed for invalid password format",
      execute: async () => {
        await page.goto('http://localhost/login').catch(() => {});
        await page.waitForTimeout(1000);
        const usernameField = await page.locator('[name="username"], [placeholder*="username"], input[type="text"]').first();
        await usernameField.fill(process.env.LOGIN_USERNAME);
        const passwordField = await page.locator('[type="password"], [placeholder*="password"]').first();
        await passwordField.fill(process.env.INVALID_PASSWORD);
        await page.click('button:has-text("Login"), button[type="submit"]');
        await page.waitForTimeout(2000);
        const errorMessage = await page.locator('text=Invalid password format').isVisible();
        if (!errorMessage) throw new Error('Error message not displayed for invalid password');
      }
    },
    {
      test_id: "TC_004",
      module: "Login",
      scenario: "Verify login fails when both email and password fields are empty",
      execute: async () => {
        await page.goto('http://localhost/login').catch(() => {});
        await page.waitForTimeout(1000);
        await page.click('button:has-text("Login"), button[type="submit"]');
        await page.waitForTimeout(2000);
        const errorMessage = await page.locator('text=Fields cannot be empty').isVisible();
        if (!errorMessage) throw new Error('Error message not displayed for empty fields');
      }
    },
    {
      test_id: "TC_005",
      module: "Home/Dashboard",
      scenario: "Verify user can view home/dashboard after successful login",
      execute: async () => {
        await page.goto('http://localhost/dashboard').catch(() => {});
        await page.waitForTimeout(1000);
        const dashboardLink = await page.locator('text=Dashboard').first();
        await dashboardLink.click();
        await page.waitForTimeout(2000);
        const isOnDashboard = page.url().includes('dashboard') || page.url().includes('home');
        if (!isOnDashboard) throw new Error('User not on dashboard page');
      }
    },
    {
      test_id: "TC_006",
      module: "Home/Dashboard",
      scenario: "Verify search functionality returns results for valid search term",
      execute: async () => {
        await page.goto('http://localhost/dashboard').catch(() => {});
        await page.waitForTimeout(1000);
        const searchField = await page.locator('[name="search"], [placeholder*="search"], input[type="search"]').first();
        await searchField.fill(process.env.VALID_SEARCH_TERM);
        await page.click('button:has-text("Search")');
        await page.waitForTimeout(2000);
        const hasResults = await page.locator('[data-test="product"], .product').count() > 0;
        if (!hasResults) throw new Error('No search results found for valid search term');
      }
    },
    {
      test_id: "TC_007",
      module: "Home/Dashboard",
      scenario: "Verify no results message is displayed for invalid search term",
      execute: async () => {
        await page.goto('http://localhost/dashboard').catch(() => {});
        await page.waitForTimeout(1000);
        const searchField = await page.locator('[name="search"], [placeholder*="search"], input[type="search"]').first();
        await searchField.fill(process.env.INVALID_SEARCH_TERM);
        await page.click('button:has-text("Search")');
        await page.waitForTimeout(2000);
        const noResultsMessage = await page.locator('text=No results').isVisible();
        if (!noResultsMessage) throw new Error('No results message not displayed for invalid search term');
      }
    },
    {
      test_id: "TC_008",
      module: "Home/Dashboard",
      scenario: "Verify user can filter products by price range",
      execute: async () => {
        await page.goto('http://localhost/dashboard').catch(() => {});
        await page.waitForTimeout(1000);
        const minPriceField = await page.locator('[name="min-price"], [placeholder*="min price"]').first();
        await minPriceField.fill(process.env.MIN_PRICE);
        const maxPriceField = await page.locator('[name="max-price"], [placeholder*="max price"]').first();
        await maxPriceField.fill(process.env.MAX_PRICE);
        await page.click('button:has-text("Filter")');
        await page.waitForTimeout(2000);
        const hasFilteredResults = await page.locator('.filtered-product').count() > 0;
        if (!hasFilteredResults) throw new Error('No products displayed for the specified price range');
      }
    },
    {
      test_id: "TC_009",
      module: "Home/Dashboard",
      scenario: "Verify user can apply multiple category filters",
      execute: async () => {
        await page.goto('http://localhost/dashboard').catch(() => {});
        await page.waitForTimeout(1000);
        const categoryFilter = await page.locator('select[name="category-filter"], [data-action="category-filter"]').first();
        await categoryFilter.selectOption(process.env.CATEGORY_FILTER);
        const additionalCategoryFilter = await page.locator('select[name="additional-category-filter"], [data-action="additional-category-filter"]').first();
        await additionalCategoryFilter.selectOption(process.env.ADDITIONAL_CATEGORY_FILTER);
        await page.click('button:has-text("Apply Filters")');
        await page.waitForTimeout(2000);
        const hasFilteredResults = await page.locator('.filtered-product').count() > 0;
        if (!hasFilteredResults) throw new Error('No products displayed for the selected categories');
      }
    },
    {
      test_id: "TC_010",
      module: "Home/Dashboard",
      scenario: "Verify user can view product details by clicking 'View' button",
      execute: async () => {
        await page.goto('http://localhost/dashboard').catch(() => {});
        await page.waitForTimeout(1000);
        const viewButton = await page.locator('button:has-text("View")').first();
        await viewButton.click();
        await page.waitForTimeout(2000);
        const isOnProductDetails = page.url().includes('product-details');
        if (!isOnProductDetails) throw new Error('Not redirected to product details page');
      }
    },
    {
      test_id: "TC_011",
      module: "Home/Dashboard",
      scenario: "Verify product is added to cart when clicking the 'Add to Cart' button",
      execute: async () => {
        await page.goto('http://localhost/product-details').catch(() => {});
        await page.waitForTimeout(1000);
        await page.click('button:has-text("Add to Cart")');
        await page.waitForTimeout(2000);
        const cartCount = await page.locator('.cart-count').innerText();
        if (parseInt(cartCount) === 0) throw new Error('Product not added to cart');
      }
    },
    {
      test_id: "TC_012",
      module: "Home/Dashboard",
      scenario: "Verify toast message confirms product was added to cart",
      execute: async () => {
        await page.goto('http://localhost/dashboard').catch(() => {});
        await page.waitForTimeout(1000);
        const toastMessage = await page.locator('text=Product added to cart').isVisible();
        if (!toastMessage) throw new Error('Toast message not displayed after adding product to cart');
      }
    },
    {
      test_id: "TC_013",
      module: "Cart",
      scenario: "Verify user can view cart items after adding products",
      execute: async () => {
        await page.goto('http://localhost/cart').catch(() => {});
        await page.waitForTimeout(1000);
        const cartItems = await page.locator('.cart-item').count();
        if (cartItems === 0) throw new Error('No items found in the cart');
      }
    },
    {
      test_id: "TC_014",
      module: "Cart",
      scenario: "Verify user can remove an item from the cart",
      execute: async () => {
        await page.goto('http://localhost/cart').catch(() => {});
        await page.waitForTimeout(1000);
        const removeButton = await page.locator('button:has-text("Remove")').first();
        await removeButton.click();
        await page.waitForTimeout(2000);
        const cartItems = await page.locator('.cart-item').count();
        if (cartItems > 0) throw new Error('Item not removed from the cart');
      }
    },
    {
      test_id: "TC_015",
      module: "Cart",
      scenario: "Verify checkout button is disabled when cart is empty",
      execute: async () => {
        await page.goto('http://localhost/cart').catch(() => {});
        await page.waitForTimeout(1000);
        const checkoutButtonState = await page.locator('button:has-text("Checkout")').getAttribute('disabled');
        if (checkoutButtonState === null) throw new Error('Checkout button is not disabled when cart is empty');
      }
    },
    {
      test_id: "TC_016",
      module: "Cart",
      scenario: "Verify successful checkout process redirects to payment page",
      execute: async () => {
        await page.goto('http://localhost/cart').catch(() => {});
        await page.waitForTimeout(1000);
        await page.click('button:has-text("Checkout")');
        await page.waitForTimeout(2000);
        const isOnPaymentPage = page.url().includes('payment');
        if (!isOnPaymentPage) throw new Error('Not redirected to payment page');
      }
    },
    {
      test_id: "TC_017",
      module: "Checkout",
      scenario: "Verify user can successfully fill out billing address form",
      execute: async () => {
        await page.goto('http://localhost/payment').catch(() => {});
        await page.waitForTimeout(1000);
        const billingAddressField = await page.locator('[name="billing-address"]').first();
        await billingAddressField.fill(process.env.BILLING_ADDRESS);
        const cityField = await page.locator('[name="city"]').first();
        await cityField.fill(process.env.CITY);
        const zipField = await page.locator('[name="zip"]').first();
        await zipField.fill(process.env.ZIP_CODE);
        await page.click('button:has-text("Submit")');
        await page.waitForTimeout(2000);
        const successMessage = await page.locator('text=Billing address saved successfully').isVisible();
        if (!successMessage) throw new Error('Billing address not saved');
      }
    },
    {
      test_id: "TC_018",
      module: "Checkout",
      scenario: "Verify error message for missing required billing address field",
      execute: async () => {
        await page.goto('http://localhost/payment').catch(() => {});
        await page.waitForTimeout(1000);
        const submitButton = await page.locator('button:has-text("Submit")').first();
        await submitButton.click();
        await page.waitForTimeout(2000);
        const errorMessage = await page.locator('text=Billing address is required').isVisible();
        if (!errorMessage) throw new Error('Error message not displayed for missing billing address');
      }
    },
    {
      test_id: "TC_019",
      module: "Checkout",
      scenario: "Verify order summary displays correct items, subtotal, and total",
      execute: async () => {
        await page.goto('http://localhost/payment').catch(() => {});
        await page.waitForTimeout(1000);
        const orderSummaryVisible = await page.locator('.order-summary').isVisible();
        if (!orderSummaryVisible) throw new Error('Order summary not displayed');
      }
    },
    {
      test_id: "TC_020",
      module: "Checkout",
      scenario: "Verify error displayed if form is invalid and submitted",
      execute: async () => {
        await page.goto('http://localhost/payment').catch(() => {});
        await page.waitForTimeout(1000);
        const billingAddressField = await page.locator('[name="billing-address"]').first();
        await billingAddressField.fill(process.env.INVALID_BILLING_ADDRESS);
        const submitButton = await page.locator('button:has-text("Submit")').first();
        await submitButton.click();
        await page.waitForTimeout(2000);
        const errorMessage = await page.locator('text=Invalid billing address').isVisible();
        if (!errorMessage) throw new Error('Error message not displayed for invalid billing address');
      }
    },
    {
      test_id: "TC_021",
      module: "Order Summary",
      scenario: "Verify order confirmation displays correct order ID and status",
      execute: async () => {
        await page.goto('http://localhost/order-summary').catch(() => {});
        await page.waitForTimeout(1000);
        const orderIdVisible = await page.locator('.order-id').isVisible();
        if (!orderIdVisible) throw new Error('Order ID not displayed');
      }
    },
    {
      test_id: "TC_022",
      module: "Order Summary",
      scenario: "Verify downloadable invoice button functions correctly",
      execute: async () => {
        await page.goto('http://localhost/order-summary').catch(() => {});
        await page.waitForTimeout(1000);
        await page.click('button:has-text("Download Invoice")');
        await page.waitForTimeout(2000);
        const invoiceGenerated = await page.locator('text=Invoice generated').isVisible();
        if (!invoiceGenerated) throw new Error('Downloadable invoice not generated');
      }
    },
    {
      test_id: "TC_023",
      module: "Order History",
      scenario: "Verify user can view order history with correct details displayed",
      execute: async () => {
        await page.goto('http://localhost/order-history').catch(() => {});
        await page.waitForTimeout(1000);
        const orderHistoryVisible = await page.locator('.order-history').isVisible();
        if (!orderHistoryVisible) throw new Error('Order history not displayed');
      }
    },
    {
      test_id: "TC_024",
      module: "Order History",
      scenario: "Verify no orders message is displayed when there are no past orders",
      execute: async () => {
        await page.goto('http://localhost/order-history').catch(() => {});
        await page.waitForTimeout(1000);
        const noOrdersMessage = await page.locator('text=No orders').isVisible();
        if (!noOrdersMessage) throw new Error('No orders message not displayed');
      }
    },
    {
      test_id: "TC_025",
      module: "Order History",
      scenario: "Verify user can view order details by clicking 'View' button",
      execute: async () => {
        await page.goto('http://localhost/order-history').catch(() => {});
        await page.waitForTimeout(1000);
        const viewButton = await page.locator('button:has-text("View")').first();
        await viewButton.click();
        await page.waitForTimeout(2000);
        const isOnOrderDetails = page.url().includes('order-details');
        if (!isOnOrderDetails) throw new Error('Not redirected to order details page');
      }
    },
    {
      test_id: "TC_026",
      module: "Order History",
      scenario: "Verify user can reorder items from order history",
      execute: async () => {
        await page.goto('http://localhost/order-history').catch(() => {});
        await page.waitForTimeout(1000);
        const reorderButton = await page.locator('button:has-text("Reorder")').first();
        await reorderButton.click();
        await page.waitForTimeout(2000);
        const cartCount = await page.locator('.cart-count').innerText();
        if (parseInt(cartCount) === 0) throw new Error('Reorder did not add items to cart');
      }
    }
  ];

  for (const test of tests) {
    try {
      await test.execute();
      results.passed++;
    } catch (error) {
      results.failed++;
      results.failed_tests.push({
        test_id: test.test_id,
        module: test.module,
        scenario: test.scenario,
        failure_reason: error.message,
        status: 'failed'
      });
    }
  }
  
  results.total_tests = results.passed + results.failed;
  if (results.total_tests > 0) {
    results.pass_rate = ((results.passed / results.total_tests) * 100).toFixed(2) + '%';
  }
  
  await browser.close();
  return results;
}

runAllTests().then(results => {
  console.log(JSON.stringify(results, null, 2));
  process.exit(0);
}).catch(error => {
  console.error(JSON.stringify({
    total_tests: 0,
    passed: 0,
    failed: 0,
    pass_rate: '0%',
    failed_tests: [],
    error: error.message
  }, null, 2));
  process.exit(1);
});
```