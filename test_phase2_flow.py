#!/usr/bin/env python3
"""
End-to-end test for Phase 2: World Creation

Tests the complete flow:
1. Navigate to app
2. Create an agent
3. Create a world for the agent
4. Verify world canvas renders
"""
from playwright.sync_api import sync_playwright
import time

def test_phase2_world_creation():
    with sync_playwright() as p:
        # Launch browser in headed mode so we can see what's happening
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("🚀 Starting Phase 2 E2E Test...")

        # Step 1: Navigate to app
        print("\n1️⃣ Navigating to http://localhost:3001...")
        page.goto('http://localhost:3001')
        page.wait_for_load_state('networkidle')
        time.sleep(2)  # Give React time to render

        # Take initial screenshot
        page.screenshot(path='/tmp/phase2_01_initial.png', full_page=True)
        print("   📸 Screenshot saved: /tmp/phase2_01_initial.png")

        # Step 2: Create an agent
        print("\n2️⃣ Creating an agent...")

        # Find and fill agent description textarea
        agent_textarea = page.locator('textarea')
        if agent_textarea.count() == 0:
            print("   ❌ ERROR: Could not find agent description textarea")
            browser.close()
            return False

        agent_textarea.fill("a friendly wizard who loves nature and magic")
        print("   ✅ Filled agent description")

        # Click create agent button ("Hatch Companion")
        create_agent_btn = page.locator('button:has-text("Hatch Companion")')
        if create_agent_btn.count() == 0:
            print("   ❌ ERROR: Could not find Hatch Companion button")
            browser.close()
            return False

        create_agent_btn.click()
        print("   ✅ Clicked Hatch Companion button")

        # Wait for agent to be created (look for agent card or world creation section)
        print("   ⏳ Waiting for agent creation (up to 30 seconds)...")
        try:
            page.wait_for_selector('text=Create a World', timeout=30000)
            print("   ✅ Agent created successfully!")
        except Exception as e:
            print(f"   ❌ ERROR: Agent creation timed out: {e}")
            page.screenshot(path='/tmp/phase2_02_agent_timeout.png', full_page=True)
            browser.close()
            return False

        time.sleep(2)
        page.screenshot(path='/tmp/phase2_02_agent_created.png', full_page=True)
        print("   📸 Screenshot saved: /tmp/phase2_02_agent_created.png")

        # Step 3: Create a world
        print("\n3️⃣ Creating a world...")

        # Find world description textarea
        world_textarea = page.locator('textarea[placeholder*="peaceful meadow"]')
        if world_textarea.count() == 0:
            print("   ❌ ERROR: Could not find world description textarea")
            browser.close()
            return False

        world_textarea.fill("a magical forest with ancient trees and a crystal clear stream")
        print("   ✅ Filled world description")

        # Click create world button
        create_world_btn = page.locator('button:has-text("Create World")')
        if create_world_btn.count() == 0:
            print("   ❌ ERROR: Could not find Create World button")
            browser.close()
            return False

        create_world_btn.click()
        print("   ✅ Clicked Create World button")

        # Wait for world to be created (look for canvas)
        print("   ⏳ Waiting for world creation (up to 60 seconds)...")
        try:
            page.wait_for_selector('canvas', timeout=60000)
            print("   ✅ World created successfully!")
        except Exception as e:
            print(f"   ❌ ERROR: World creation timed out: {e}")
            page.screenshot(path='/tmp/phase2_03_world_timeout.png', full_page=True)
            browser.close()
            return False

        time.sleep(3)
        page.screenshot(path='/tmp/phase2_03_world_created.png', full_page=True)
        print("   📸 Screenshot saved: /tmp/phase2_03_world_created.png")

        # Step 4: Verify canvas exists and has content
        print("\n4️⃣ Verifying world canvas...")

        canvas = page.locator('canvas')
        if canvas.count() == 0:
            print("   ❌ ERROR: Canvas not found")
            browser.close()
            return False

        # Get canvas dimensions to verify it's not empty
        canvas_width = canvas.evaluate('el => el.width')
        canvas_height = canvas.evaluate('el => el.height')
        print(f"   ✅ Canvas found with dimensions: {canvas_width}x{canvas_height}")

        if canvas_width == 0 or canvas_height == 0:
            print("   ❌ ERROR: Canvas has zero dimensions")
            browser.close()
            return False

        # Expected: 10x10 grid with 32px tiles = 320x320
        expected_size = 10 * 32
        if canvas_width == expected_size and canvas_height == expected_size:
            print(f"   ✅ Canvas has correct size for 10x10 grid ({expected_size}x{expected_size})")
        else:
            print(f"   ⚠️  WARNING: Canvas size ({canvas_width}x{canvas_height}) doesn't match expected ({expected_size}x{expected_size})")

        # Check for world name/description
        world_name = page.locator('text=/🗺️/')
        if world_name.count() > 0:
            print(f"   ✅ World name found: {world_name.text_content()}")

        # Final screenshot
        page.screenshot(path='/tmp/phase2_04_final.png', full_page=True)
        print("   📸 Screenshot saved: /tmp/phase2_04_final.png")

        print("\n✅ ✅ ✅ PHASE 2 E2E TEST PASSED! ✅ ✅ ✅")
        print("\nScreenshots saved:")
        print("  - /tmp/phase2_01_initial.png")
        print("  - /tmp/phase2_02_agent_created.png")
        print("  - /tmp/phase2_03_world_created.png")
        print("  - /tmp/phase2_04_final.png")

        # Keep browser open for 5 seconds to see the result
        print("\nKeeping browser open for 5 seconds...")
        time.sleep(5)

        browser.close()
        return True

if __name__ == '__main__':
    success = test_phase2_world_creation()
    exit(0 if success else 1)
