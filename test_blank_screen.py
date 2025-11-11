#!/usr/bin/env python3
"""Direct test to reproduce the blank screen bug."""

from playwright.sync_api import sync_playwright
import requests
import time
import json

# First, create a test agent via API
print("Creating test agent via API...")
response = requests.post(
    'http://localhost:8000/api/agents/create',
    json={'description': 'A test pokemon for debugging'},
    headers={'Content-Type': 'application/json'}
)

if response.status_code != 200:
    print(f"Failed to create agent: {response.text}")
    exit(1)

agent = response.json()
print(f"✓ Created agent: {agent['name']} ({agent['id']})")

# Now test the frontend
console_logs = []

with sync_playwright() as p:
    browser = p.chromium.launch(
        channel='chromium',
        headless=False,
        slow_mo=200
    )

    page = browser.new_page()

    # Capture ALL console messages
    def log_console(msg):
        text = msg.text
        console_logs.append(text)
        # Print important ones
        if any(kw in text for kw in ['App.jsx', 'WorldCanvas', 'WorldCreation', 'grid', 'Error']):
            print(f"  🔍 {text}")

    page.on("console", log_console)
    page.on("pageerror", lambda err: print(f"  ❌ {err}"))

    # Track API responses
    world_created = {}
    def track_response(response):
        if '/api/worlds/create' in response.url:
            try:
                data = response.json()
                world_created['data'] = data
                print(f"\n  📡 World created via API:")
                print(f"     Keys: {list(data.keys())}")
                print(f"     Has grid: {'grid' in data}")
                if 'grid' in data:
                    print(f"     Grid type: {type(data['grid'])}")
                    print(f"     Grid is list: {isinstance(data['grid'], list)}")
                    if isinstance(data['grid'], list):
                        print(f"     Grid dimensions: {len(data['grid'])}x{len(data['grid'][0]) if data['grid'] else 0}")
            except Exception as e:
                print(f"     Error parsing: {e}")

    page.on("response", track_response)

    print("\n" + "="*80)
    print("TESTING WORLD CREATION BUG")
    print("="*80)

    print("\n[1] Loading app...")
    page.goto('http://localhost:3000')
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    print("\n[2] Selecting our test agent...")
    # Click on agent select dropdown
    select = page.locator('select').first
    if select.count() > 0:
        # Look for our agent by name
        select.select_option(label=agent['name'])
        print(f"   ✓ Selected {agent['name']}")
        time.sleep(1)
        page.screenshot(path='/tmp/blank_01_agent_selected.png')

    print("\n[3] Looking for 'Create World' button...")
    create_btn = page.locator('text="Create World"').first
    if create_btn.count() == 0:
        print("   ❌ Button not found! Taking screenshot...")
        page.screenshot(path='/tmp/blank_ERROR_no_button.png', full_page=True)
        # Wait a bit and try again
        time.sleep(3)
        create_btn = page.locator('text="Create World"').first

    if create_btn.count() > 0:
        print("   ✓ Found button, clicking...")
        create_btn.click()
        time.sleep(1)
        page.screenshot(path='/tmp/blank_02_form_opened.png')

        print("\n[4] Filling world description...")
        textarea = page.locator('textarea').first
        textarea.fill("a beautiful meadow with flowers and butterflies")
        time.sleep(0.5)

        print("\n[5] Submitting form...")
        submit = page.locator('button:has-text("Create World")').last
        submit.click()

        print("\n[6] MONITORING for blank screen...")
        print("   " + "-"*60)

        for i in range(15):
            time.sleep(1)

            # Get current state
            body = page.locator('body').inner_text()
            body_len = len(body.strip())
            has_canvas = page.locator('canvas').count() > 0
            has_world_canvas_div = page.locator('.pokemon-container:has-text("🗺️")').count() > 0
            is_blank = body_len < 100

            # Take screenshot every second
            page.screenshot(path=f'/tmp/blank_progress_{i:02d}.png')

            status = f"[{i+1:2d}s] chars:{body_len:4d} canvas:{has_canvas} worldDiv:{has_world_canvas_div} BLANK:{is_blank}"
            print(f"   {status}")

            # Check for blank screen
            if is_blank and i > 3:
                print(f"\n   ⚠️⚠️⚠️  BLANK SCREEN DETECTED! ⚠️⚠️⚠️")
                break

            # Check for success
            if has_canvas and has_world_canvas_div:
                print(f"\n   ✅ World canvas rendered successfully!")
                break

        print("\n" + "="*80)
        print("ANALYSIS")
        print("="*80)

        # Final screenshot
        page.screenshot(path='/tmp/blank_final.png', full_page=True)

        # Save HTML
        with open('/tmp/blank_final.html', 'w') as f:
            f.write(page.content())

        # Analyze console logs
        print(f"\n📊 Console logs ({len(console_logs)} total):")

        # Filter for our debug messages
        app_logs = [log for log in console_logs if 'App.jsx' in log]
        canvas_logs = [log for log in console_logs if 'WorldCanvas' in log]
        creation_logs = [log for log in console_logs if 'WorldCreation' in log]

        print(f"\n🔍 App.jsx logs ({len(app_logs)}):")
        for log in app_logs:
            print(f"   {log}")

        print(f"\n🔍 WorldCanvas logs ({len(canvas_logs)}):")
        for log in canvas_logs:
            print(f"   {log}")

        print(f"\n🔍 WorldCreation logs ({len(creation_logs)}):")
        for log in creation_logs:
            print(f"   {log}")

        # Check API response
        if 'data' in world_created:
            wd = world_created['data']
            print(f"\n✅ World API response received:")
            print(f"   id: {wd.get('id', 'N/A')[:20]}...")
            print(f"   name: {wd.get('name', 'N/A')}")
            print(f"   has grid: {'grid' in wd}")
            if 'grid' in wd:
                print(f"   grid valid: {isinstance(wd['grid'], list) and len(wd['grid']) > 0}")

        print(f"\n📁 Files saved:")
        print(f"   /tmp/blank_*.png")
        print(f"   /tmp/blank_final.html")

        print("\n✨ Browser staying open for inspection...")
        input("Press Enter to close...")

    browser.close()
