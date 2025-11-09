#!/usr/bin/env python3
"""
Test the currently running webapp on localhost:5173
"""
from playwright.sync_api import sync_playwright, expect
import sys

def test_webapp():
    """Test what's running on port 5173"""
    print("🧪 Testing webapp on http://localhost:5173...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Navigate to the app
            page.goto('http://localhost:5173')
            page.wait_for_load_state('networkidle')

            # Take screenshot
            page.screenshot(path='/tmp/webapp_5173.png', full_page=True)
            print("  📸 Screenshot saved to /tmp/webapp_5173.png")

            # Check page title
            title = page.title()
            print(f"  📄 Page title: {title}")

            # Get all text content
            body_text = page.locator('body').text_content()
            print(f"\n  📝 First 500 characters of page:")
            print(f"  {body_text[:500]}")

            # Check for specific elements
            print("\n  🔍 Looking for key elements...")

            # Look for headings
            h1_elements = page.locator('h1').all()
            if h1_elements:
                print(f"  ✅ Found {len(h1_elements)} h1 elements:")
                for i, h1 in enumerate(h1_elements[:3]):
                    print(f"     - {h1.text_content()}")

            # Look for buttons
            buttons = page.locator('button').all()
            if buttons:
                print(f"  ✅ Found {len(buttons)} buttons:")
                for i, btn in enumerate(buttons[:5]):
                    text = btn.text_content()
                    if text.strip():
                        print(f"     - '{text.strip()}'")

            # Look for links
            links = page.locator('a').all()
            if links:
                print(f"  ✅ Found {len(links)} links")

            # Check console for errors
            errors = []
            def handle_console(msg):
                if msg.type == 'error':
                    errors.append(msg.text)

            page.on('console', handle_console)
            page.reload()
            page.wait_for_load_state('networkidle')

            if errors:
                print(f"\n  ⚠️  Console errors found:")
                for err in errors[:3]:
                    print(f"     - {err}")
            else:
                print("\n  ✅ No console errors")

            # Get HTML structure
            html = page.content()
            print(f"\n  📊 HTML size: {len(html)} bytes")

            # Check if it's a markdown editor
            if 'markdown' in body_text.lower() or 'editor' in body_text.lower():
                print("\n  ℹ️  This appears to be a markdown editor")

                # Look for textarea or editor
                textareas = page.locator('textarea').all()
                if textareas:
                    print(f"  ✅ Found {len(textareas)} textarea elements")

            browser.close()
            return True

        except Exception as e:
            print(f"  ❌ Error: {e}")
            page.screenshot(path='/tmp/webapp_5173_error.png', full_page=True)
            browser.close()
            return False

if __name__ == '__main__':
    success = test_webapp()
    sys.exit(0 if success else 1)
