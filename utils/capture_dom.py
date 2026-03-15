from playwright.async_api import async_playwright


async def capture_page_dom(url: str) -> str:
    """Opens the URL with a real browser and returns the full HTML for AI to inspect."""
    print(f"\n🔍 Capturing DOM from: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        html = await page.content()
        await browser.close()
    print("✓ DOM captured\n")
    return html