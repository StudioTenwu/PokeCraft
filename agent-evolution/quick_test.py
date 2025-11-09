#!/usr/bin/env python3
"""Quick test to check if servers are running and take screenshots."""

from playwright.sync_api import sync_playwright
import time

def quick_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        print("Navigating to http://localhost:5190...")
        page.goto('http://localhost:5190')
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        print("Taking screenshot of homepage...")
        page.screenshot(path='/Users/wz/Desktop/zPersonalProjects/AICraft/claude_files/homepage.png', full_page=True)
        print("✓ Homepage screenshot saved")

        # Get page title
        title = page.title()
        print(f"Page title: {title}")

        # Get header text
        try:
            header = page.locator('h1').first.inner_text()
            print(f"Header: {header}")
        except:
            print("Could not find header")

        # Check if stages loaded
        try:
            stage_info = page.locator('text=Stage 1').first
            if stage_info.is_visible():
                print("✓ Stage information is visible")
        except:
            print("Could not find stage information")

        # Check for API connection
        print("\nWaiting 5 seconds to see if page loads data...")
        time.sleep(5)
        page.screenshot(path='/Users/wz/Desktop/zPersonalProjects/AICraft/claude_files/after_load.png', full_page=True)
        print("✓ After load screenshot saved")

        print("\n✓ Test complete! Browser will close in 10 seconds...")
        time.sleep(10)
        browser.close()

if __name__ == "__main__":
    quick_test()
