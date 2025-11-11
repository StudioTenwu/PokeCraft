#!/usr/bin/env python3
"""Test world creation flow to reproduce blank screen bug."""

from playwright.sync_api import sync_playwright
import time

def test_world_creation():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Enable console logging
        page.on("console", lambda msg: print(f"CONSOLE [{msg.type}]: {msg.text}"))
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))

        print("1. Navigating to localhost:3000...")
        page.goto('http://localhost:3000')
        page.wait_for_load_state('networkidle')

        print("2. Taking initial screenshot...")
        page.screenshot(path='/tmp/01_initial.png', full_page=True)

        print("3. Looking for agents...")
        # Wait for agents to load
        time.sleep(2)

        # Check if we have agents
        agents = page.locator('.pokemon-container').all()
        print(f"   Found {len(agents)} containers")

        # Look for "Create World" button
        create_world_buttons = page.locator('text="Create World"').all()
        print(f"   Found {len(create_world_buttons)} 'Create World' buttons")

        if len(create_world_buttons) == 0:
            print("   No 'Create World' button found - checking page content...")
            print(f"   Page title: {page.title()}")
            page.screenshot(path='/tmp/02_no_button.png', full_page=True)

            # Check if we need to create an agent first
            create_agent_button = page.locator('text="Create Agent"')
            if create_agent_button.count() > 0:
                print("4. Creating an agent first...")
                create_agent_button.click()
                time.sleep(1)

                # Fill in agent description
                textarea = page.locator('textarea[placeholder*="Describe"]')
                if textarea.count() > 0:
                    textarea.fill("A test Pokémon trainer")
                    page.screenshot(path='/tmp/03_agent_form.png', full_page=True)

                    # Submit
                    submit_button = page.locator('button[type="submit"]:has-text("Generate")')
                    if submit_button.count() > 0:
                        print("   Submitting agent creation...")
                        submit_button.click()

                        # Wait for agent creation (this might take a while)
                        print("   Waiting for agent creation (max 60s)...")
                        try:
                            page.wait_for_selector('text="Create World"', timeout=60000)
                            print("   Agent created successfully!")
                            page.screenshot(path='/tmp/04_agent_created.png', full_page=True)
                        except:
                            print("   Timeout waiting for agent creation")
                            page.screenshot(path='/tmp/04_timeout.png', full_page=True)
                            browser.close()
                            return

        # Now try to create a world
        print("5. Clicking 'Create World' button...")
        create_world_buttons = page.locator('text="Create World"')
        if create_world_buttons.count() > 0:
            create_world_buttons.first.click()
            time.sleep(1)
            page.screenshot(path='/tmp/05_world_form.png', full_page=True)

            # Fill in world creation form
            print("6. Filling world creation form...")
            world_theme = page.locator('input[placeholder*="theme"]')
            if world_theme.count() > 0:
                world_theme.fill("A mystical forest")

            constraints = page.locator('textarea[placeholder*="constraints"]')
            if constraints.count() > 0:
                constraints.fill("Must have trees and a lake")

            page.screenshot(path='/tmp/06_form_filled.png', full_page=True)

            # Submit world creation
            generate_button = page.locator('button:has-text("Generate World")')
            if generate_button.count() > 0:
                print("7. Submitting world creation...")
                generate_button.click()

                # Wait a bit for the loading to start
                time.sleep(2)
                page.screenshot(path='/tmp/07_loading.png', full_page=True)

                # Wait for world creation to complete (max 60s)
                print("8. Waiting for world creation to complete...")
                time.sleep(5)

                # Take screenshots at intervals
                for i in range(12):  # Check every 5 seconds for 60 seconds
                    time.sleep(5)
                    page.screenshot(path=f'/tmp/08_progress_{i:02d}.png', full_page=True)

                    # Check page content
                    content = page.content()
                    print(f"   [{i*5}s] Page title: {page.title()}")

                    # Look for signs of completion or blank screen
                    if 'WorldCanvas' in content or 'world' in page.title().lower():
                        print(f"   [{i*5}s] World canvas detected!")
                        break

                    if page.locator('body').evaluate('el => el.innerText').strip() == '':
                        print(f"   [{i*5}s] ⚠️  BLANK SCREEN DETECTED!")
                        break

                print("9. Final screenshot...")
                page.screenshot(path='/tmp/09_final.png', full_page=True)

                # Get final page content
                final_html = page.content()
                with open('/tmp/final_page.html', 'w') as f:
                    f.write(final_html)
                print("   Saved final HTML to /tmp/final_page.html")

        print("\n✅ Test complete! Screenshots saved to /tmp/")
        print("   Check /tmp/01_initial.png through /tmp/09_final.png")

        # Keep browser open for manual inspection
        input("\nPress Enter to close browser...")
        browser.close()

if __name__ == "__main__":
    test_world_creation()
