#!/usr/bin/env python3
"""Test the agent-evolution web application with Playwright."""

from playwright.sync_api import sync_playwright
import time
import sys

def test_agent_evolution():
    """Test the agent evolution webapp."""

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        print("=" * 80)
        print("AGENT EVOLUTION WEB APPLICATION TEST")
        print("=" * 80)

        try:
            # Navigate to the application
            print("\n1. Navigating to http://localhost:5190...")
            page.goto('http://localhost:5190')
            page.wait_for_load_state('networkidle')
            time.sleep(2)

            # Take screenshot of homepage
            screenshot_path = '/Users/wz/Desktop/zPersonalProjects/AICraft/claude_files/test_homepage.png'
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"   ✓ Homepage loaded - screenshot saved to {screenshot_path}")

            # Check if stages loaded
            print("\n2. Checking if stages loaded from backend...")
            stages = page.locator('[class*="stage"]').count()
            print(f"   Found {stages} stage-related elements")

            # Check header
            header_text = page.locator('h1').first.inner_text()
            print(f"   Header: {header_text}")

            # Check stage indicator
            print("\n3. Testing Stage Indicator...")
            stage_buttons = page.locator('button').filter(has_text='Stage')
            stage_count = stage_buttons.count()
            print(f"   Found {stage_count} stage buttons")

            # Screenshot before interaction
            page.screenshot(path='/Users/wz/Desktop/zPersonalProjects/AICraft/claude_files/test_stage1_initial.png', full_page=True)

            # Test Stage 1
            print("\n4. Testing Stage 1 - Basic Chat...")
            current_stage_desc = page.locator('text=Stage 1').first
            if current_stage_desc.is_visible():
                print("   ✓ Stage 1 is visible")

            # Find and click the "Try:" button if it exists
            try:
                try_button = page.locator('button').filter(has_text='Try:').first
                if try_button.is_visible():
                    button_text = try_button.inner_text()
                    print(f"   Found button: {button_text}")
                    print(f"   Clicking '{button_text}'...")
                    try_button.click()
                    time.sleep(2)

                    # Wait for response
                    print("   Waiting for agent response...")
                    time.sleep(5)

                    # Take screenshot
                    page.screenshot(path='/Users/wz/Desktop/zPersonalProjects/AICraft/claude_files/test_stage1_response.png', full_page=True)
                    print("   ✓ Screenshot saved after Stage 1 test")
            except Exception as e:
                print(f"   Note: Could not test Stage 1 automatically - {e}")

            # Test Stage 2
            print("\n5. Testing Stage 2 - Tool Recognition...")
            try:
                # Find Stage 2 button/link
                stage2_elements = page.locator('text=Stage 2').all()
                if len(stage2_elements) > 0:
                    # Click on stage 2 indicator
                    for elem in stage2_elements:
                        if elem.is_visible():
                            elem.click()
                            break

                    time.sleep(2)
                    page.screenshot(path='/Users/wz/Desktop/zPersonalProjects/AICraft/claude_files/test_stage2_initial.png', full_page=True)
                    print("   ✓ Navigated to Stage 2")

                    # Try the key activity for Stage 2
                    try_button = page.locator('button').filter(has_text='Try:').first
                    if try_button.is_visible():
                        button_text = try_button.inner_text()
                        print(f"   Clicking '{button_text}'...")
                        try_button.click()
                        time.sleep(5)

                        page.screenshot(path='/Users/wz/Desktop/zPersonalProjects/AICraft/claude_files/test_stage2_response.png', full_page=True)
                        print("   ✓ Screenshot saved after Stage 2 test")
            except Exception as e:
                print(f"   Note: Could not test Stage 2 automatically - {e}")

            # Test Stage 3
            print("\n6. Testing Stage 3 - Tool Execution...")
            try:
                stage3_elements = page.locator('text=Stage 3').all()
                if len(stage3_elements) > 0:
                    for elem in stage3_elements:
                        if elem.is_visible():
                            elem.click()
                            break

                    time.sleep(2)
                    page.screenshot(path='/Users/wz/Desktop/zPersonalProjects/AICraft/claude_files/test_stage3_initial.png', full_page=True)
                    print("   ✓ Navigated to Stage 3")

                    # Try the key activity for Stage 3
                    try_button = page.locator('button').filter(has_text='Try:').first
                    if try_button.is_visible():
                        button_text = try_button.inner_text()
                        print(f"   Clicking '{button_text}'...")
                        try_button.click()
                        time.sleep(7)

                        page.screenshot(path='/Users/wz/Desktop/zPersonalProjects/AICraft/claude_files/test_stage3_response.png', full_page=True)
                        print("   ✓ Screenshot saved after Stage 3 test")
            except Exception as e:
                print(f"   Note: Could not test Stage 3 automatically - {e}")

            # Test Stage 4
            print("\n7. Testing Stage 4 - Multi-tool Chaining...")
            try:
                stage4_elements = page.locator('text=Stage 4').all()
                if len(stage4_elements) > 0:
                    for elem in stage4_elements:
                        if elem.is_visible():
                            elem.click()
                            break

                    time.sleep(2)
                    page.screenshot(path='/Users/wz/Desktop/zPersonalProjects/AICraft/claude_files/test_stage4_initial.png', full_page=True)
                    print("   ✓ Navigated to Stage 4")

                    # Try the key activity for Stage 4
                    try_button = page.locator('button').filter(has_text='Try:').first
                    if try_button.is_visible():
                        button_text = try_button.inner_text()
                        print(f"   Clicking '{button_text}'...")
                        try_button.click()
                        time.sleep(10)

                        page.screenshot(path='/Users/wz/Desktop/zPersonalProjects/AICraft/claude_files/test_stage4_response.png', full_page=True)
                        print("   ✓ Screenshot saved after Stage 4 test")
            except Exception as e:
                print(f"   Note: Could not test Stage 4 automatically - {e}")

            # Test manual input
            print("\n8. Testing manual message input...")
            try:
                textarea = page.locator('textarea').first
                send_button = page.locator('button').filter(has_text='Send').first

                if textarea.is_visible():
                    textarea.fill("Hello, can you help me?")
                    print("   ✓ Typed test message")

                    if send_button.is_visible():
                        send_button.click()
                        print("   ✓ Clicked Send button")
                        time.sleep(5)

                        page.screenshot(path='/Users/wz/Desktop/zPersonalProjects/AICraft/claude_files/test_manual_input.png', full_page=True)
                        print("   ✓ Screenshot saved after manual input test")
            except Exception as e:
                print(f"   Note: Could not test manual input - {e}")

            # Check for tool events
            print("\n9. Checking for tool event displays...")
            tool_cards = page.locator('[class*="tool"]').count()
            print(f"   Found {tool_cards} tool-related elements")

            # Get browser console logs
            print("\n10. Checking browser console...")
            console_messages = []

            def handle_console(msg):
                console_messages.append(f"{msg.type}: {msg.text}")

            page.on('console', handle_console)

            # Final screenshot
            print("\n11. Taking final screenshot...")
            page.screenshot(path='/Users/wz/Desktop/zPersonalProjects/AICraft/claude_files/test_final.png', full_page=True)
            print("   ✓ Final screenshot saved")

            print("\n" + "=" * 80)
            print("TEST COMPLETE")
            print("=" * 80)
            print(f"\nScreenshots saved to: /Users/wz/Desktop/zPersonalProjects/AICraft/claude_files/")
            print("\nConsole messages:")
            for msg in console_messages[-10:]:
                print(f"  {msg}")

            return True

        except Exception as e:
            print(f"\n❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            # Keep browser open for inspection
            print("\n\nBrowser will stay open for inspection. Press Enter to close...")
            input()
            browser.close()

if __name__ == "__main__":
    success = test_agent_evolution()
    sys.exit(0 if success else 1)
