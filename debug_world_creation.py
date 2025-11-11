#!/usr/bin/env python3
"""Debug world creation to see exactly what happens."""

from playwright.sync_api import sync_playwright
import time

def debug_world_creation():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context()
        page = context.new_page()

        # Capture console messages
        console_messages = []
        def handle_console(msg):
            console_messages.append(f"[{msg.type}] {msg.text}")
            print(f"  CONSOLE [{msg.type}]: {msg.text}")

        page.on("console", handle_console)
        page.on("pageerror", lambda err: print(f"  PAGE ERROR: {err}"))

        # Intercept network requests to see API responses
        def handle_response(response):
            if '/api/worlds/create' in response.url:
                print(f"\n  ✓ API Response from {response.url}")
                print(f"    Status: {response.status}")
                try:
                    body = response.json()
                    print(f"    Body keys: {list(body.keys())}")
                    print(f"    Has 'grid': {'grid' in body}")
                    print(f"    Grid value: {type(body.get('grid'))}")
                    if 'grid' in body:
                        print(f"    Grid length: {len(body['grid'])}")
                except:
                    print(f"    Body: {response.text()[:200]}")

        page.on("response", handle_response)

        print("1. Opening app...")
        page.goto('http://localhost:3000')
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        # Check if there's an agent already, if not create one quickly
        create_world_btn = page.locator('text="Create World"')
        if create_world_btn.count() == 0:
            print("2. No agent found - need to create one first")
            print("   Please manually create an agent, then I'll continue...")
            input("   Press Enter when agent is created...")
            page.reload()
            page.wait_for_load_state('networkidle')
            time.sleep(2)

        # Now create a world
        print("\n3. Looking for 'Create World' button...")
        create_world_btn = page.locator('text="Create World"').first
        if create_world_btn.count() > 0:
            print("4. Clicking 'Create World'...")
            create_world_btn.click()
            time.sleep(1)
            page.screenshot(path='/tmp/debug_01_form.png')

            # Fill in world description
            print("5. Filling world description...")
            textarea = page.locator('textarea[placeholder*="peaceful"]')
            if textarea.count() > 0:
                textarea.fill("a simple test world with grass and paths")
                time.sleep(0.5)

            # Submit
            print("6. Clicking 'Create World' button...")
            submit_btn = page.locator('button:has-text("Create World")')
            if submit_btn.count() > 0:
                submit_btn.click()
                print("7. Waiting for world creation...")

                # Wait and take screenshots
                for i in range(10):
                    time.sleep(1)
                    page.screenshot(path=f'/tmp/debug_progress_{i:02d}.png')

                    # Check page state
                    body_html = page.content()

                    # Look for key indicators
                    has_error = 'Error:' in body_html or 'error' in body_html.lower()
                    has_canvas = '<canvas' in body_html
                    is_blank = len(page.locator('body').inner_text().strip()) < 100

                    print(f"   [{i}s] Error: {has_error}, Canvas: {has_canvas}, Blank: {is_blank}")

                    if has_canvas:
                        print(f"   [{i}s] ✓ Canvas found!")
                        break
                    if is_blank:
                        print(f"   [{i}s] ⚠️  BLANK SCREEN!")
                        break

                # Final state
                print("\n8. Final state:")
                print(f"   Console messages: {len(console_messages)}")
                for msg in console_messages[-10:]:
                    print(f"     {msg}")

                page.screenshot(path='/tmp/debug_final.png', full_page=True)

                # Save HTML
                with open('/tmp/debug_final.html', 'w') as f:
                    f.write(page.content())

                print("\n✅ Debug complete!")
                print("   Screenshots: /tmp/debug_*.png")
                print("   HTML: /tmp/debug_final.html")

        input("\nPress Enter to close...")
        browser.close()

if __name__ == "__main__":
    debug_world_creation()
