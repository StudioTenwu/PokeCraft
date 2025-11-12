#!/usr/bin/env python3
"""Test world creation bug using Playwright with Chrome."""

from playwright.sync_api import sync_playwright
import time
import json

def test_world_creation_bug():
    """Test the world creation flow and capture console logs."""

    console_logs = []
    network_responses = {}

    with sync_playwright() as p:
        # Launch browser in headed mode for visibility
        browser = p.chromium.launch(
            channel='chromium',
            headless=False,
            slow_mo=500
        )

        # Create a new context and page
        context = browser.new_context()
        page = context.new_page()

        # Capture console messages
        def handle_console(msg):
            log_entry = f"[{msg.type}] {msg.text}"
            console_logs.append(log_entry)
            print(f"  CONSOLE: {log_entry}")

        page.on("console", handle_console)

        # Capture page errors
        def handle_error(err):
            error_msg = f"PAGE ERROR: {err}"
            console_logs.append(error_msg)
            print(f"  {error_msg}")

        page.on("pageerror", handle_error)

        # Capture network responses (especially API calls)
        def handle_response(response):
            url = response.url
            if '/api/' in url:
                try:
                    status = response.status
                    print(f"\n  📡 API Response: {url}")
                    print(f"     Status: {status}")

                    if '/api/worlds/create' in url and status == 200:
                        body = response.json()
                        network_responses['world_create'] = body
                        print(f"     Response keys: {list(body.keys())}")
                        print(f"     Has 'grid': {'grid' in body}")
                        if 'grid' in body:
                            print(f"     Grid type: {type(body['grid'])}")
                            print(f"     Grid length: {len(body['grid']) if isinstance(body['grid'], list) else 'N/A'}")
                except Exception as e:
                    print(f"     Error parsing response: {e}")

        page.on("response", handle_response)

        print("=" * 80)
        print("STEP 1: Navigate to http://localhost:3000")
        print("=" * 80)
        page.goto('http://localhost:3000')
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        page.screenshot(path='/tmp/test_01_initial.png', full_page=True)

        # Check for agents
        print("\nSTEP 2: Check for existing agents")
        create_world_btn = page.locator('text="Create World"')

        if create_world_btn.count() == 0:
            print("  ⚠️  No 'Create World' button - need to select/create agent first")

            # Try to select an agent from dropdown if available
            agent_select = page.locator('select')
            if agent_select.count() > 0:
                options = agent_select.locator('option').all()
                if len(options) > 1:  # More than just "Select Agent"
                    print(f"  Found {len(options)} agents in dropdown")
                    agent_select.select_option(index=1)
                    time.sleep(1)
                    page.screenshot(path='/tmp/test_02_agent_selected.png')

            # Check again
            create_world_btn = page.locator('text="Create World"')
            if create_world_btn.count() == 0:
                print("  ❌ Still no agent - please create one manually")
                input("  Press Enter when agent is ready...")
                page.reload()
                page.wait_for_load_state('networkidle')
                time.sleep(1)

        print("\nSTEP 3: Click 'Create World' button")
        create_world_btn = page.locator('text="Create World"').first
        if create_world_btn.count() > 0:
            create_world_btn.click()
            time.sleep(1)
            page.screenshot(path='/tmp/test_03_form_opened.png')

            print("\nSTEP 4: Fill in world description")
            textarea = page.locator('textarea[placeholder*="peaceful"]')
            if textarea.count() > 0:
                test_description = "a mystical forest with winding paths and a hidden treasure"
                textarea.fill(test_description)
                print(f"  Filled: {test_description}")
                time.sleep(0.5)
                page.screenshot(path='/tmp/test_04_form_filled.png')

            print("\nSTEP 5: Submit world creation")
            submit_btn = page.locator('button:has-text("Create World")').last
            if submit_btn.count() > 0:
                print("  Clicking submit button...")
                submit_btn.click()

                print("\nSTEP 6: Wait for world creation and monitor state")

                # Monitor for 15 seconds
                for i in range(15):
                    time.sleep(1)

                    # Take screenshot
                    page.screenshot(path=f'/tmp/test_progress_{i:02d}.png')

                    # Get page state
                    body_text = page.locator('body').inner_text()
                    body_length = len(body_text.strip())

                    # Check for key indicators
                    has_canvas = page.locator('canvas').count() > 0
                    has_error = 'Error:' in body_text or 'error' in body_text.lower()
                    is_blank = body_length < 100

                    status = f"[{i:02d}s] Canvas:{has_canvas} Error:{has_error} Blank:{is_blank} BodyLen:{body_length}"
                    print(f"  {status}")

                    # Check if we have the debug logs we added
                    relevant_logs = [log for log in console_logs if 'App.jsx' in log or 'WorldCanvas' in log]
                    if relevant_logs and i > 3:
                        print(f"  📝 Recent debug logs:")
                        for log in relevant_logs[-5:]:
                            print(f"     {log}")

                    # Stop if we detect completion or blank screen
                    if has_canvas or is_blank:
                        print(f"\n  {'✅ Canvas detected!' if has_canvas else '❌ BLANK SCREEN DETECTED!'}")
                        break

                print("\nSTEP 7: Final state analysis")
                page.screenshot(path='/tmp/test_final.png', full_page=True)

                # Save HTML
                html = page.content()
                with open('/tmp/test_final.html', 'w') as f:
                    f.write(html)
                print("  Saved HTML to /tmp/test_final.html")

                # Analyze console logs
                print(f"\n📊 CONSOLE LOG ANALYSIS ({len(console_logs)} total messages)")
                print("=" * 80)

                # Filter for our debug messages
                app_logs = [log for log in console_logs if 'App.jsx' in log]
                canvas_logs = [log for log in console_logs if 'WorldCanvas' in log]

                print(f"\n🔍 App.jsx debug logs ({len(app_logs)}):")
                for log in app_logs:
                    print(f"  {log}")

                print(f"\n🔍 WorldCanvas debug logs ({len(canvas_logs)}):")
                for log in canvas_logs:
                    print(f"  {log}")

                # Check API response
                if 'world_create' in network_responses:
                    print(f"\n🌍 API /api/worlds/create response:")
                    world_data = network_responses['world_create']
                    print(f"  Keys: {list(world_data.keys())}")
                    print(f"  Has grid: {'grid' in world_data}")
                    if 'grid' in world_data:
                        print(f"  Grid is valid: {isinstance(world_data['grid'], list)}")

                print("\n" + "=" * 80)
                print("✅ TEST COMPLETE")
                print("=" * 80)
                print(f"Screenshots: /tmp/test_*.png")
                print(f"Console logs: {len(console_logs)} messages")
                print(f"Network responses captured: {len(network_responses)}")

                # Keep browser open for inspection
                print("\nBrowser will stay open for manual inspection...")
                input("Press Enter to close browser and exit...")

        browser.close()

if __name__ == "__main__":
    test_world_creation_bug()
