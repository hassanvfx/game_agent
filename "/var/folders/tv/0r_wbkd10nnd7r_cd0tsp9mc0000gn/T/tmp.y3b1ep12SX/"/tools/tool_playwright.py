import os

from playwright.sync_api import sync_playwright


def run_playwright_check() -> dict:
    browser_name = os.getenv("PLAYWRIGHT_BROWSER", "chromium").lower()
    headless = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"

    with sync_playwright() as playwright:
        browser_launcher = getattr(playwright, browser_name)
        browser = browser_launcher.launch(headless=headless)
        page = browser.new_page()
        page.set_content("<html><head><title>playwright-ok</title></head><body>ready</body></html>")
        title = page.title()
        body_text = page.locator("body").inner_text()
        browser.close()

    return {
        "tool": "playwright",
        "status": "success",
        "browser": browser_name,
        "headless": headless,
        "title": title,
        "body_text": body_text,
    }