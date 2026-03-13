from playwright.sync_api import sync_playwright
import time

url = "http://127.0.0.1:8000/ui_kit/login_mockup/"
out = "login_4k.png"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width":3840, "height":2160})
    page.goto(url)
    # wait for main content to render
    time.sleep(1)
    page.screenshot(path=out, full_page=True)
    browser.close()
    print('Saved', out)
