import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.supremecourt.ohio.gov")
        title = await page.title()
        print(f"[+] Internet Access Verified! Page Title: {title}")
        await browser.close()

asyncio.run(run())
