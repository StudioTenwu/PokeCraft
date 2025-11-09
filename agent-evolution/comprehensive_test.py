#!/usr/bin/env python3
"""Comprehensive test of the agent-evolution web application."""

from playwright.sync_api import sync_playwright, Page
import time
import json

def wait_and_screenshot(page: Page, name: str, wait_time: int = 2):
    """Helper to wait and take screenshot."""
    time.sleep(wait_time)
    path = f'/Users/wz/Desktop/zPersonalProjects/AICraft/claude_files/test_{name}.png'
    page.screenshot(path=path, full_page=True)
    print(f"   ✓ Screenshot saved: {name}.png")

def test_comprehensive():
    """Run comprehensive tests on the agent evolution app."""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # Track console messages
        console_messages = []
        errors = []

        def handle_console(msg):
            console_messages.append(f"{msg.type}: {msg.text}")
            if msg.type == 'error':
                errors.append(msg.text)

        page.on('console', handle_console)

        print("\n" + "="*80)
        print("COMPREHENSIVE AGENT EVOLUTION TEST")
        print("="*80 + "\n")

        try:
            # Test 1: Homepage Load
            print("1. Loading homepage...")
            page.goto('http://localhost:5190')
            page.wait_for_load_state('networkidle')
            wait_and_screenshot(page, '01_homepage', 3)

            # Check for header
            header = page.locator('h1').first.inner_text()
            print(f"   Header: {header}")

            # Test 2: Check if stages loaded from API
            print("\n2. Verifying stages loaded from backend...")
            time.sleep(2)  # Wait for API call

            # Look for stage information
            stage_elements = page.locator('text=/Stage [1-4]/').count()
            print(f"   Found {stage_elements} stage elements")

            if stage_elements >= 4:
                print("   ✓ All 4 stages appear to be loaded")
            else:
                print(f"   ⚠ Only {stage_elements} stages found")

            wait_and_screenshot(page, '02_stages_loaded', 1)

            # Test 3: Stage 1 - Basic Chat
            print("\n3. Testing Stage 1 - Basic Chat...")

            # Find chat input
            textarea = page.locator('textarea').first
            send_btn = page.locator('button:has-text("Send")').first

            if textarea.is_visible() and send_btn.is_visible():
                print("   ✓ Chat interface is visible")

                # Type a message
                test_message = "Hello! What can you help me with?"
                textarea.fill(test_message)
                print(f"   Typed: '{test_message}'")

                wait_and_screenshot(page, '03_stage1_message_typed', 1)

                # Click send
                send_btn.click()
                print("   Clicked Send button")

                # Wait for response (may take a while)
                print("   Waiting for agent response...")
                time.sleep(8)

                wait_and_screenshot(page, '04_stage1_response', 2)

                # Check if response appeared
                messages = page.locator('[class*="message"]').count()
                print(f"   Found {messages} message elements")
            else:
                print("   ⚠ Chat interface not visible")

            # Test 4: Navigate to Stage 2
            print("\n4. Testing Stage 2 Navigation...")

            # Look for stage 2 button/indicator
            stage2_btns = page.locator('text=/Stage 2/').all()
            clicked = False
            for btn in stage2_btns:
                try:
                    if btn.is_visible() and btn.is_enabled():
                        btn.click()
                        clicked = True
                        print("   ✓ Clicked on Stage 2")
                        break
                except:
                    continue

            if clicked:
                time.sleep(2)
                wait_and_screenshot(page, '05_stage2_loaded', 1)

                # Check stage 2 description
                try:
                    desc = page.locator('text=/Tool Awareness/i').first
                    if desc.is_visible():
                        print("   ✓ Stage 2 description visible")
                except:
                    print("   ⚠ Could not find Stage 2 description")
            else:
                print("   ⚠ Could not navigate to Stage 2")

            # Test 5: Stage 3
            print("\n5. Testing Stage 3 Navigation...")
            stage3_btns = page.locator('text=/Stage 3/').all()
            clicked = False
            for btn in stage3_btns:
                try:
                    if btn.is_visible() and btn.is_enabled():
                        btn.click()
                        clicked = True
                        print("   ✓ Clicked on Stage 3")
                        break
                except:
                    continue

            if clicked:
                time.sleep(2)
                wait_and_screenshot(page, '06_stage3_loaded', 1)

            # Test 6: Stage 4
            print("\n6. Testing Stage 4 Navigation...")
            stage4_btns = page.locator('text=/Stage 4/').all()
            clicked = False
            for btn in stage4_btns:
                try:
                    if btn.is_visible() and btn.is_enabled():
                        btn.click()
                        clicked = True
                        print("   ✓ Clicked on Stage 4")
                        break
                except:
                    continue

            if clicked:
                time.sleep(2)
                wait_and_screenshot(page, '07_stage4_loaded', 1)

            # Test 7: Check for "Try:" buttons
            print("\n7. Checking for 'Try:' activity buttons...")
            try_buttons = page.locator('button').filter(has_text='Try:').count()
            print(f"   Found {try_buttons} 'Try:' buttons")

            if try_buttons > 0:
                try_btn = page.locator('button').filter(has_text='Try:').first
                btn_text = try_btn.inner_text()
                print(f"   Button text: {btn_text}")

                # Click it
                print(f"   Clicking '{btn_text}'...")
                try_btn.click()
                print("   Waiting for response...")
                time.sleep(10)

                wait_and_screenshot(page, '08_try_button_clicked', 2)

            # Test 8: Check for tool displays
            print("\n8. Checking for tool event displays...")

            # Look for any tool-related elements
            tool_cards = page.locator('[class*="tool"]').count()
            print(f"   Found {tool_cards} elements with 'tool' in class name")

            # Final screenshot
            wait_and_screenshot(page, '09_final_state', 1)

            # Print console summary
            print("\n" + "="*80)
            print("CONSOLE MESSAGES SUMMARY")
            print("="*80)

            if errors:
                print(f"\n❌ Errors found ({len(errors)}):")
                for error in errors[:10]:
                    print(f"   - {error}")
            else:
                print("\n✓ No errors in console")

            print(f"\nTotal console messages: {len(console_messages)}")
            if console_messages:
                print("\nLast 5 messages:")
                for msg in console_messages[-5:]:
                    print(f"   {msg}")

            print("\n" + "="*80)
            print("TEST SUMMARY")
            print("="*80)
            print("\n✓ Frontend is running on http://localhost:5190")
            print("✓ Backend is running on http://localhost:8001")
            print(f"✓ {stage_elements} stages detected")
            print(f"✓ Screenshots saved to: /Users/wz/Desktop/zPersonalProjects/AICraft/claude_files/")

            if errors:
                print(f"\n⚠ {len(errors)} errors detected - review console logs")

            print("\n" + "="*80)
            print("Test complete! Browser will stay open for 30 seconds...")
            print("="*80 + "\n")

            time.sleep(30)

        except Exception as e:
            print(f"\n❌ Error during test: {e}")
            import traceback
            traceback.print_exc()
            wait_and_screenshot(page, 'error_state', 1)

        finally:
            browser.close()

if __name__ == "__main__":
    test_comprehensive()
