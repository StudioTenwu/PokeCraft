#!/usr/bin/env python3
"""Automated test for world creation bug - uses existing agent."""

from playwright.sync_api import sync_playwright
import time
import sqlite3

def get_first_agent():
    """Get the first agent from the database."""
    conn = sqlite3.connect('/Users/wz/Desktop/zPersonalProjects/AICraft/backend/agents.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM agents LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result if result else None

def test_world_creation():
    """Test world creation with existing agent."""

    agent = get_first_agent()
    if not agent:
        print("❌ No agents in database - please create one first")
        return

    agent_id, agent_name = agent
    print(f"✅ Using agent: {agent_name} ({agent_id})")

    console_logs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel='chromium',
            headless=False,
            slow_mo=300
        )

        context = browser.new_context()
        page = context.new_page()

        # Capture console
        def handle_console(msg):
            log = f"[{msg.type}] {msg.text}"
            console_logs.append(log)
            # Only print important logs
            if any(keyword in log for keyword in ['App.jsx', 'WorldCanvas', 'Error', 'grid']):
                print(f"  📝 {log}")

        page.on("console", handle_console)
        page.on("pageerror", lambda err: print(f"  ❌ PAGE ERROR: {err}"))

        # Capture API responses
        world_response = {}
        def handle_response(response):
            if '/api/worlds/create' in response.url:
                try:
                    world_response['data'] = response.json()
                    print(f"\n  📡 API Response from /api/worlds/create:")
                    print(f"     Status: {response.status}")
                    print(f"     Has 'grid': {'grid' in world_response['data']}")
                except Exception as e:
                    print(f"     Error: {e}")

        page.on("response", handle_response)

        print("\n" + "=" * 80)
        print("TEST: World Creation Bug")
        print("=" * 80)

        print("\n[1/7] Loading app...")
        page.goto('http://localhost:3000')
        page.wait_for_load_state('networkidle')
        time.sleep(2)
        page.screenshot(path='/tmp/auto_01_loaded.png')

        print("\n[2/7] Selecting agent...")
        # Try to select the agent from dropdown
        agent_select = page.locator('select').first
        if agent_select.count() > 0:
            # Get all options
            options = agent_select.locator('option').all()
            for i, option in enumerate(options):
                value = option.get_attribute('value')
                if value == agent_id:
                    agent_select.select_option(value=value)
                    print(f"  ✓ Selected {agent_name}")
                    time.sleep(1)
                    break
        page.screenshot(path='/tmp/auto_02_agent_selected.png')

        print("\n[3/7] Opening world creation form...")
        create_world_btn = page.locator('text="Create World"')
        if create_world_btn.count() == 0:
            print("  ❌ 'Create World' button not found!")
            page.screenshot(path='/tmp/auto_ERROR_no_button.png')
            browser.close()
            return

        create_world_btn.first.click()
        time.sleep(1)
        page.screenshot(path='/tmp/auto_03_form_opened.png')

        print("\n[4/7] Filling world description...")
        textarea = page.locator('textarea').first
        test_desc = "a simple grass field with a winding path"
        textarea.fill(test_desc)
        print(f"  Filled: '{test_desc}'")
        time.sleep(0.5)
        page.screenshot(path='/tmp/auto_04_filled.png')

        print("\n[5/7] Submitting world creation...")
        submit_btn = page.locator('button:has-text("Create World")').last
        submit_btn.click()

        print("\n[6/7] Monitoring world creation...")
        blank_screen_detected = False
        canvas_detected = False

        for i in range(12):  # Monitor for 12 seconds
            time.sleep(1)
            page.screenshot(path=f'/tmp/auto_progress_{i:02d}.png')

            # Check page state
            body_text = page.locator('body').inner_text()
            body_len = len(body_text.strip())
            has_canvas = page.locator('canvas').count() > 0
            is_blank = body_len < 100

            print(f"  [{i+1}s] Body:{body_len}chars Canvas:{has_canvas} Blank:{is_blank}")

            if is_blank and i > 2:
                blank_screen_detected = True
                print(f"\n  ⚠️  BLANK SCREEN DETECTED at {i+1}s!")
                break

            if has_canvas:
                canvas_detected = True
                print(f"\n  ✅ Canvas rendered at {i+1}s!")
                break

        print("\n[7/7] Final analysis...")
        page.screenshot(path='/tmp/auto_final.png', full_page=True)

        # Save final HTML
        with open('/tmp/auto_final.html', 'w') as f:
            f.write(page.content())

        # Analyze results
        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80)

        # Check debug logs
        app_logs = [log for log in console_logs if 'App.jsx' in log and ('handleWorldCreated' in log or 'selectedWorld' in log)]
        canvas_logs = [log for log in console_logs if 'WorldCanvas' in log]

        print(f"\n🔍 App.jsx debug logs ({len(app_logs)}):")
        for log in app_logs[-10:]:  # Last 10
            print(f"  {log}")

        print(f"\n🔍 WorldCanvas debug logs ({len(canvas_logs)}):")
        for log in canvas_logs[-10:]:
            print(f"  {log}")

        if 'data' in world_response:
            wd = world_response['data']
            print(f"\n🌍 World API Response:")
            print(f"  Keys: {list(wd.keys())}")
            print(f"  Has 'grid': {'grid' in wd}")
            if 'grid' in wd:
                print(f"  Grid type: {type(wd['grid'])}")
                print(f"  Grid valid: {isinstance(wd['grid'], list)}")

        print(f"\n📊 Final State:")
        print(f"  Canvas rendered: {canvas_detected}")
        print(f"  Blank screen: {blank_screen_detected}")
        print(f"  Total console logs: {len(console_logs)}")

        if blank_screen_detected:
            print("\n❌ BUG REPRODUCED: Blank screen after world creation!")
        elif canvas_detected:
            print("\n✅ SUCCESS: World canvas rendered!")
        else:
            print("\n⚠️  UNCLEAR: Neither blank nor canvas detected")

        print("\n📁 Files saved:")
        print("  /tmp/auto_*.png - Screenshots")
        print("  /tmp/auto_final.html - Final HTML")

        print("\nKeeping browser open for inspection...")
        input("Press Enter to close...")

        browser.close()

if __name__ == "__main__":
    test_world_creation()
