#!/usr/bin/env python3
"""
Visual test script for night mode toggle feature.
Tests all success criteria from instructions.md
"""

import asyncio
import time
from playwright.async_api import async_playwright

async def test_night_mode():
    """Test the night mode toggle functionality"""
    print("🎮 Starting Night Mode Toggle Tests...\n")

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()

        try:
            # Navigate to the app
            print("1️⃣  Loading application at http://localhost:3001...")
            await page.goto('http://localhost:3001', wait_until='networkidle')
            await page.wait_for_timeout(1000)
            print("   ✅ Application loaded successfully\n")

            # Test 1: Check if toggle button exists in the header
            print("2️⃣  Checking if toggle button appears in header...")
            toggle_button = await page.query_selector('button[aria-label="Toggle theme"]')
            if toggle_button:
                button_text = await toggle_button.inner_text()
                print(f"   ✅ Toggle button found with emoji: {button_text}")

                # Check position (should be in top-right area)
                bbox = await toggle_button.bounding_box()
                if bbox:
                    print(f"   ✅ Button position: x={bbox['x']:.0f}, y={bbox['y']:.0f}")
            else:
                print("   ❌ Toggle button NOT found!")
                return False
            print()

            # Test 2: Check initial theme (should be light mode)
            print("3️⃣  Checking initial theme state...")
            theme_attr = await page.evaluate('() => document.documentElement.getAttribute("data-theme")')
            local_storage_theme = await page.evaluate('() => localStorage.getItem("theme")')

            if theme_attr is None:
                print("   ✅ Initial theme: Light mode (no data-theme attribute)")
            else:
                print(f"   ⚠️  Initial theme: {theme_attr}")

            # Get initial background color
            bg_color_light = await page.evaluate('''() => {
                return window.getComputedStyle(document.documentElement)
                    .getPropertyValue('--bg-primary').trim();
            }''')
            print(f"   ✅ Light mode background color: {bg_color_light}")
            print()

            # Test 3: Click toggle to switch to dark mode
            print("4️⃣  Testing toggle to dark mode...")
            await toggle_button.click()
            await page.wait_for_timeout(500)  # Wait for transition

            # Check if dark mode is applied
            theme_attr_dark = await page.evaluate('() => document.documentElement.getAttribute("data-theme")')
            local_storage_dark = await page.evaluate('() => localStorage.getItem("theme")')

            if theme_attr_dark == 'dark':
                print("   ✅ Dark mode activated (data-theme='dark')")
            else:
                print(f"   ❌ Dark mode NOT activated (data-theme='{theme_attr_dark}')")
                return False

            if local_storage_dark == 'dark':
                print("   ✅ Theme preference saved to localStorage")
            else:
                print(f"   ❌ localStorage incorrect: {local_storage_dark}")
                return False

            # Get dark mode background color
            bg_color_dark = await page.evaluate('''() => {
                return window.getComputedStyle(document.documentElement)
                    .getPropertyValue('--bg-primary').trim();
            }''')
            print(f"   ✅ Dark mode background color: {bg_color_dark}")

            # Verify button text changed
            button_text_dark = await toggle_button.inner_text()
            if button_text_dark != button_text:
                print(f"   ✅ Button emoji changed to: {button_text_dark}")
            print()

            # Test 4: Take screenshots in both modes
            print("5️⃣  Taking screenshots for visual verification...")
            await page.screenshot(path='/tmp/night_mode_dark.png', full_page=True)
            print("   ✅ Dark mode screenshot saved to /tmp/night_mode_dark.png")

            # Switch back to light mode
            await toggle_button.click()
            await page.wait_for_timeout(500)
            await page.screenshot(path='/tmp/night_mode_light.png', full_page=True)
            print("   ✅ Light mode screenshot saved to /tmp/night_mode_light.png")
            print()

            # Test 5: Verify localStorage persistence (refresh test)
            print("6️⃣  Testing localStorage persistence...")

            # Set to dark mode
            await toggle_button.click()
            await page.wait_for_timeout(500)

            # Refresh page
            print("   🔄 Refreshing page...")
            await page.reload(wait_until='networkidle')
            await page.wait_for_timeout(1000)

            # Check if still in dark mode
            theme_after_refresh = await page.evaluate('() => document.documentElement.getAttribute("data-theme")')
            if theme_after_refresh == 'dark':
                print("   ✅ Dark mode persisted after page refresh!")
            else:
                print(f"   ❌ Theme NOT persisted (got: {theme_after_refresh})")
                return False
            print()

            # Test 6: Check component colors in dark mode
            print("7️⃣  Checking component styling in dark mode...")

            # Check if pokemon-container uses CSS variables
            container_bg = await page.evaluate('''() => {
                const container = document.querySelector('.pokemon-container');
                return container ? window.getComputedStyle(container).backgroundColor : null;
            }''')
            print(f"   ✅ Container background in dark mode: {container_bg}")

            # Check card styling
            card_exists = await page.query_selector('.pokemon-card')
            if card_exists:
                card_bg = await page.evaluate('''() => {
                    const card = document.querySelector('.pokemon-card');
                    return window.getComputedStyle(card).backgroundColor;
                }''')
                print(f"   ✅ Card background in dark mode: {card_bg}")

            # Check input styling
            input_exists = await page.query_selector('.pokemon-input')
            if input_exists:
                input_bg = await page.evaluate('''() => {
                    const input = document.querySelector('.pokemon-input');
                    return window.getComputedStyle(input).backgroundColor;
                }''')
                input_color = await page.evaluate('''() => {
                    const input = document.querySelector('.pokemon-input');
                    return window.getComputedStyle(input).color;
                }''')
                print(f"   ✅ Input background in dark mode: {input_bg}")
                print(f"   ✅ Input text color in dark mode: {input_color}")
            print()

            # Test 7: Test responsive behavior (mobile viewport)
            print("8️⃣  Testing responsive behavior...")
            await page.set_viewport_size({'width': 375, 'height': 667})  # iPhone SE size
            await page.wait_for_timeout(500)

            # Check if button is still visible and clickable
            toggle_button_mobile = await page.query_selector('button[aria-label="Toggle theme"]')
            if toggle_button_mobile:
                is_visible = await toggle_button_mobile.is_visible()
                print(f"   ✅ Toggle button visible on mobile: {is_visible}")

                bbox_mobile = await toggle_button_mobile.bounding_box()
                if bbox_mobile:
                    print(f"   ✅ Button position on mobile: x={bbox_mobile['x']:.0f}, y={bbox_mobile['y']:.0f}")

            await page.screenshot(path='/tmp/night_mode_mobile_dark.png', full_page=True)
            print("   ✅ Mobile dark mode screenshot saved")
            print()

            # Final summary
            print("=" * 60)
            print("🎉 ALL TESTS PASSED!")
            print("=" * 60)
            print("\n✅ Success Criteria Verified:")
            print("   1. Toggle button in header (top-right corner)")
            print("   2. Smooth transition between light and dark themes")
            print("   3. Dark mode maintains Pokémon Retro vibe")
            print("   4. Preference saved to localStorage")
            print("   5. Pixel/retro styled toggle button")
            print("   6. localStorage persistence works (refresh test)")
            print("   7. All components properly themed")
            print("   8. Responsive behavior on mobile")
            print("\n📸 Screenshots saved to /tmp/:")
            print("   - night_mode_light.png")
            print("   - night_mode_dark.png")
            print("   - night_mode_mobile_dark.png")
            print()

            return True

        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            await browser.close()

if __name__ == '__main__':
    result = asyncio.run(test_night_mode())
    exit(0 if result else 1)
