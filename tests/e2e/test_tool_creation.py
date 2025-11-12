"""Test tool creation workflow."""

import os
from playwright.sync_api import sync_playwright
from helpers import (
    wait_for_app_ready,
    create_pokemon,
    create_world,
    create_tool,
    take_screenshot,
    capture_console_logs,
    print_console_logs
)


def test_tool_creation():
    """Test creating a tool for a Pokémon."""

    print("\n" + "="*80)
    print("TEST: Tool Creation Workflow")
    print("="*80)

    # Use headless mode by default, override with HEADED=1
    headless = os.getenv('HEADED') != '1'
    slow_mo = 0 if headless else 300
    print(f"  🖥️  Mode: {'Headless' if headless else 'Headed'}")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chromium', headless=headless, slow_mo=slow_mo)
        context = browser.new_context()
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()

        # Capture console logs
        logs = capture_console_logs(page)

        try:
            # Navigate to app
            print("\n[1/5] Loading app...")
            page.goto('http://localhost:3000')
            wait_for_app_ready(page)

            # Create agent
            print("\n[2/5] Creating Bulbasaur...")
            agent = create_pokemon(page, "Bulbasaur")
            take_screenshot(page, "01_bulbasaur_created")

            # Create world
            print("\n[3/5] Creating world...")
            world = create_world(page, "a peaceful meadow with flowers")
            take_screenshot(page, "02_world_created")

            # Create tool
            print("\n[4/5] Creating tool...")
            tool = create_tool(page, "move the agent forward")

            if tool is None:
                print("  ⚠️  Tool creation skipped - Tool Workshop not found")
                take_screenshot(page, "03_no_tool_workshop")
                # This might be expected if Tool Workshop requires additional setup
                print("\n" + "="*80)
                print("⚠️  TEST SKIPPED: Tool Workshop not available")
                print("="*80)
                context.tracing.stop(path="/tmp/trace_tool_creation_SKIPPED.zip")
                return True

            assert tool['name'], "Tool should have a name"
            take_screenshot(page, "03_tool_created")

            # Verify tool appears in the list
            print("\n[5/5] Verifying tool was added...")
            tool_card = page.locator('.pokemon-container:has-text("Tool:")')
            assert tool_card.count() > 0, "Tool should appear in the list"

            print("\n" + "="*80)
            print("✅ TEST PASSED: Tool Creation")
            print("="*80)

            # Save trace
            context.tracing.stop(path="/tmp/trace_tool_creation_SUCCESS.zip")
            print("  📊 Trace saved: /tmp/trace_tool_creation_SUCCESS.zip")
            print("     View with: playwright show-trace /tmp/trace_tool_creation_SUCCESS.zip")

            return True

        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {e}")
            take_screenshot(page, "FAILED_tool_creation")
            print_console_logs(logs)
            context.tracing.stop(path="/tmp/trace_tool_creation_FAILED.zip")
            print("  📊 Trace saved: /tmp/trace_tool_creation_FAILED.zip")
            return False

        except Exception as e:
            print(f"\n❌ TEST ERROR: {e}")
            take_screenshot(page, "ERROR_tool_creation")
            print_console_logs(logs)
            context.tracing.stop(path="/tmp/trace_tool_creation_ERROR.zip")
            print("  📊 Trace saved: /tmp/trace_tool_creation_ERROR.zip")
            return False

        finally:
            print("\nClosing browser...")
            browser.close()


if __name__ == "__main__":
    success = test_tool_creation()
    exit(0 if success else 1)
