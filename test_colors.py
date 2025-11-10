#!/usr/bin/env python3
"""Test personality colors by taking a screenshot"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Navigate to the app
    page.goto('http://localhost:3002')

    # Wait for the page to fully load
    page.wait_for_load_state('networkidle')

    # Take a screenshot
    page.screenshot(path='/tmp/personality-colors-test.png', full_page=True)

    print("✅ Screenshot saved to /tmp/personality-colors-test.png")

    # Get some info about the personality badges
    badges = page.locator('span[class*="personality-badge"]').all()
    print(f"✅ Found {len(badges)} personality badges")

    # Print the classes of each badge to verify cycling
    for i, badge in enumerate(badges):
        class_name = badge.get_attribute('class')
        text = badge.text_content()
        print(f"  Badge {i+1}: '{text}' -> {class_name}")

    browser.close()
