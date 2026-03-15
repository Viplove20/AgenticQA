from playwright.async_api import async_playwright


async def capture_authenticated_dom(url: str, username: str, password: str) -> str:
    """Logs in first, then captures DOM from an authenticated page."""
    print(f"\n🔍 Capturing authenticated DOM from: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Login first
        await page.goto('https://rahulshettyacademy.com/client/auth/login', wait_until="networkidle")
        await page.locator('#userEmail').fill(username)
        await page.locator('#userPassword').fill(password)
        await page.locator('#login').click()
        await page.wait_for_url('**/dashboard**', timeout=15000)

        # Now navigate to target page
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(2000)  # wait for Angular to render
        html = await page.content()
        await browser.close()
    print(f"✓ Authenticated DOM captured from {url}\n")
    return html