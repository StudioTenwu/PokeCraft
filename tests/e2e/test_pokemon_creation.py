"""Test Pokémon creation workflow."""

import os
from playwright.sync_api import sync_playwright
from helpers import (
    wait_for_app_ready,
    create_pokemon,
    take_screenshot,
    capture_console_logs,
    print_console_logs
)


def test_pokemon_creation():
    """Test creating a Pokémon from default templates."""

    print("\n" + "="*80)
    print("TEST: Pokémon Creation Workflow")
    print("="*80)

    # Use headless mode by default, override with HEADED=1
    headless = os.getenv('HEADED') != '1'
    slow_mo = 0 if headless else 300

    print(f"  🖥️  Mode: {'Headless' if headless else 'Headed'}")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chromium', headless=headless, slow_mo=slow_mo)
        context = browser.new_context()

        # Enable tracing for debugging
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

        page = context.new_page()

        # Capture console logs
        logs = capture_console_logs(page)

        try:
            # Navigate to app
            print("\n[1/3] Loading app...")
            page.goto('http://localhost:3000')
            wait_for_app_ready(page)
            take_screenshot(page, "01_app_loaded")

            # Create Pikachu
            print("\n[2/3] Creating Pikachu...")
            agent = create_pokemon(page, "Pikachu")
            assert agent['name'] == "Pikachu"
            take_screenshot(page, "02_pikachu_created")

            # Verify "Create World" button appears
            print("\n[3/3] Verifying agent is ready...")
            create_world_btn = page.locator('button:has-text("Create World")')
            assert create_world_btn.count() > 0, "Create World button should be visible"

            print("\n" + "="*80)
            print("✅ TEST PASSED: Pokémon Creation")
            print("="*80)

            # Save trace on success
            context.tracing.stop(path="/tmp/trace_pokemon_creation_SUCCESS.zip")
            print("  📊 Trace saved: /tmp/trace_pokemon_creation_SUCCESS.zip")
            print("     View with: playwright show-trace /tmp/trace_pokemon_creation_SUCCESS.zip")

            return True

        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {e}")
            take_screenshot(page, "FAILED_pokemon_creation")
            print_console_logs(logs)

            # Save trace on failure
            context.tracing.stop(path="/tmp/trace_pokemon_creation_FAILED.zip")
            print("  📊 Trace saved: /tmp/trace_pokemon_creation_FAILED.zip")

            return False

        except Exception as e:
            print(f"\n❌ TEST ERROR: {e}")
            take_screenshot(page, "ERROR_pokemon_creation")
            print_console_logs(logs)

            # Save trace on error
            context.tracing.stop(path="/tmp/trace_pokemon_creation_ERROR.zip")
            print("  📊 Trace saved: /tmp/trace_pokemon_creation_ERROR.zip")

            return False

        finally:
            print("\nClosing browser...")
            browser.close()


if __name__ == "__main__":
    success = test_pokemon_creation()
    exit(0 if success else 1)
