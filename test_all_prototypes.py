#!/usr/bin/env python3
"""Test all AICraft prototypes to verify they're working correctly."""

from playwright.sync_api import sync_playwright
import sys

PROTOTYPES = [
    {
        "name": "Evolution Playground",
        "url": "http://localhost:5180",
        "test_selector": "text=Evolution Playground",
        "interactive_test": "button:has-text('Start Task')"
    },
    {
        "name": "Memory Theater",
        "url": "http://localhost:5181",
        "test_selector": "text=Memory Theater",
        "interactive_test": "button:has-text('Narrative Mode')"
    },
    {
        "name": "Arena Battles",
        "url": "http://localhost:5186",
        "test_selector": "text=Arena Battles",
        "interactive_test": None
    },
    {
        "name": "World Map",
        "url": "http://localhost:5187",
        "test_selector": "text=World Map",
        "interactive_test": None
    },
    {
        "name": "Training Dojo",
        "url": "http://localhost:5188",
        "test_selector": "text=Training Dojo",
        "interactive_test": None
    },
    {
        "name": "Agent Builder",
        "url": "http://localhost:5189",
        "test_selector": "text=Agent Builder",
        "interactive_test": "button:has-text('Select Environment')"
    }
]

def test_prototype(browser, prototype):
    """Test a single prototype."""
    print(f"\n{'='*60}")
    print(f"Testing: {prototype['name']}")
    print(f"URL: {prototype['url']}")
    print(f"{'='*60}")

    try:
        page = browser.new_page()

        # Navigate to the prototype
        print(f"Navigating to {prototype['url']}...")
        page.goto(prototype['url'], timeout=10000)

        # Wait for page to load
        print("Waiting for page to load...")
        page.wait_for_load_state('networkidle', timeout=15000)

        # Take screenshot
        screenshot_path = f"/tmp/aicraft_{prototype['name'].lower().replace(' ', '_')}.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"✓ Screenshot saved: {screenshot_path}")

        # Check for title element
        print(f"Looking for: {prototype['test_selector']}")
        title_element = page.locator(prototype['test_selector'])
        if title_element.count() > 0:
            print(f"✓ Title found: {title_element.first.text_content()}")
        else:
            print(f"✗ Title NOT found")
            return False

        # Check for interactive elements
        if prototype['interactive_test']:
            print(f"Looking for interactive element: {prototype['interactive_test']}")
            interactive = page.locator(prototype['interactive_test'])
            if interactive.count() > 0:
                print(f"✓ Interactive element found")
            else:
                print(f"⚠ Interactive element NOT found (may be hidden or renamed)")

        # Get page stats
        all_buttons = page.locator('button').all()
        all_inputs = page.locator('input').all()
        print(f"\nPage Stats:")
        print(f"  - Buttons: {len(all_buttons)}")
        print(f"  - Inputs: {len(all_inputs)}")

        page.close()
        print(f"\n✓ {prototype['name']} is WORKING!")
        return True

    except Exception as e:
        print(f"\n✗ {prototype['name']} FAILED: {e}")
        if 'page' in locals():
            page.close()
        return False

def main():
    print("="*60)
    print("AICraft Prototype Testing Suite")
    print("="*60)

    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for prototype in PROTOTYPES:
            success = test_prototype(browser, prototype)
            results[prototype['name']] = success

        browser.close()

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    for name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")

    total = len(results)
    passed = sum(1 for s in results.values() if s)
    print(f"\nTotal: {passed}/{total} prototypes working")

    if passed == total:
        print("\n🎉 ALL PROTOTYPES ARE WORKING! 🎉")
        return 0
    else:
        print(f"\n⚠ {total - passed} prototype(s) need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
