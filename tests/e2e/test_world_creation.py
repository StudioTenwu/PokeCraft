"""Test world creation workflow."""

import os
from playwright.sync_api import sync_playwright
from helpers import (
    wait_for_app_ready,
    create_pokemon,
    create_world,
    take_screenshot,
    capture_console_logs,
    print_console_logs
)


def test_world_creation():
    """Test creating a world for a Pokémon."""

    print("\n" + "="*80)
    print("TEST: World Creation Workflow")
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
            print("\n[1/4] Loading app...")
            page.goto('http://localhost:3000')
            wait_for_app_ready(page)

            # Create agent
            print("\n[2/4] Creating Charmander...")
            agent = create_pokemon(page, "Charmander")
            take_screenshot(page, "01_charmander_created")

            # Create world
            print("\n[3/4] Creating world...")
            world = create_world(page, "a volcanic landscape with lava rivers")
            assert world['name'], "World should have a name"
            take_screenshot(page, "02_world_created")

            # Verify canvas appears
            print("\n[4/4] Verifying world rendered...")
            canvas = page.locator('canvas')
            assert canvas.count() > 0, "Canvas should be visible"

            # Verify world name appears
            world_name_el = page.locator('h3:has-text("🗺️")')
            assert world_name_el.count() > 0, "World name should be displayed"

            print("\n" + "="*80)
            print("✅ TEST PASSED: World Creation")
            print("="*80)

            # Save trace
            context.tracing.stop(path="/tmp/trace_world_creation_SUCCESS.zip")
            print("  📊 Trace saved: /tmp/trace_world_creation_SUCCESS.zip")
            print("     View with: playwright show-trace /tmp/trace_world_creation_SUCCESS.zip")

            return True

        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {e}")
            take_screenshot(page, "FAILED_world_creation")
            print_console_logs(logs)
            context.tracing.stop(path="/tmp/trace_world_creation_FAILED.zip")
            print("  📊 Trace saved: /tmp/trace_world_creation_FAILED.zip")
            return False

        except Exception as e:
            print(f"\n❌ TEST ERROR: {e}")
            take_screenshot(page, "ERROR_world_creation")
            print_console_logs(logs)
            context.tracing.stop(path="/tmp/trace_world_creation_ERROR.zip")
            print("  📊 Trace saved: /tmp/trace_world_creation_ERROR.zip")
            return False

        finally:
            print("\nClosing browser...")
            browser.close()


if __name__ == "__main__":
    success = test_world_creation()
    exit(0 if success else 1)
