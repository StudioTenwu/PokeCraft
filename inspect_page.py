#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto('http://localhost:3001')
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    # Take screenshot
    page.screenshot(path='/tmp/inspect.png', full_page=True)
    print("Screenshot: /tmp/inspect.png")

    # Get all textareas
    textareas = page.locator('textarea').all()
    print(f"\nFound {len(textareas)} textareas:")
    for i, ta in enumerate(textareas):
        placeholder = ta.get_attribute('placeholder')
        print(f"  {i+1}. placeholder='{placeholder}'")

    # Get all buttons
    buttons = page.locator('button').all()
    print(f"\nFound {len(buttons)} buttons:")
    for i, btn in enumerate(buttons):
        text = btn.text_content()
        print(f"  {i+1}. '{text}'")

    # Keep browser open
    print("\nBrowser will stay open for 10 seconds...")
    time.sleep(10)

    browser.close()
