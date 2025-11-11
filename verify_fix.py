#!/usr/bin/env python3
"""Quick verification that the world creation UI is working."""

from playwright.sync_api import sync_playwright
import time

def verify_fix():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        # Enable console logging to see debug messages
        page.on("console", lambda msg: print(f"  CONSOLE [{msg.type}]: {msg.text}"))
        page.on("pageerror", lambda err: print(f"  PAGE ERROR: {err}"))

        print("✓ Opening http://localhost:3000...")
        page.goto('http://localhost:3000')
        page.wait_for_load_state('networkidle')

        print("✓ Taking screenshot of initial state...")
        page.screenshot(path='/tmp/verify_01_initial.png', full_page=True)

        # Check if page has content (not blank)
        body_text = page.locator('body').inner_text()
        print(f"✓ Page has {len(body_text)} characters of content")

        if len(body_text) < 50:
            print("❌ Page appears to be blank!")
            page.screenshot(path='/tmp/verify_BLANK.png', full_page=True)
        else:
            print("✅ Page is NOT blank - has content!")

        # Look for key UI elements
        containers = page.locator('.pokemon-container').count()
        print(f"✓ Found {containers} pokemon-container elements")

        # Check for error messages (which is good - means WorldCanvas rendered something)
        error_messages = page.locator('text="Error:"').count()
        if error_messages > 0:
            print(f"✓ Found {error_messages} error message(s) - WorldCanvas is displaying errors instead of blank screen!")
            page.screenshot(path='/tmp/verify_02_errors.png', full_page=True)

        # Keep browser open for manual inspection
        print("\n✅ Verification complete!")
        print("   Screenshots saved to /tmp/verify_*.png")
        print("   Check the browser window to manually verify the UI")
        input("\nPress Enter to close browser...")
        browser.close()

if __name__ == "__main__":
    verify_fix()
