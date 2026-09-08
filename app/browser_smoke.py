from playwright.sync_api import sync_playwright


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("data:text/html,<html><body>browser smoke</body></html>")
        page.screenshot(path="/tmp/browser-smoke.png")
        browser.close()
