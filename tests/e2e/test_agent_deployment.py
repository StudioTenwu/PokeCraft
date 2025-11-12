"""Test agent deployment workflow."""

import os
from playwright.sync_api import sync_playwright
from helpers import (
    wait_for_app_ready,
    create_pokemon,
    create_world,
    deploy_agent,
    click_deploy_agent_button,
    take_screenshot,
    capture_console_logs,
    print_console_logs
)


def test_agent_deployment():
    """Test deploying an agent in a world."""

    print("\n" + "="*80)
    print("TEST: Agent Deployment Workflow")
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
            print("\n[2/5] Creating Squirtle...")
            agent = create_pokemon(page, "Squirtle")
            take_screenshot(page, "01_squirtle_created")

            # Create world
            print("\n[3/5] Creating world...")
            world = create_world(page, "an ocean with islands")
            take_screenshot(page, "02_world_created")

            # Click Deploy button
            print("\n[4/5] Opening deployment view...")
            success = deploy_agent(page)
            assert success, "Deployment UI should load"
            take_screenshot(page, "03_deployment_ui")

            # Click Deploy Agent button
            print("\n[5/5] Starting agent deployment...")
            started = click_deploy_agent_button(page)

            if not started:
                print("  ⚠️  Deployment may not have started - checking logs")
                print_console_logs(logs, limit=30)

            take_screenshot(page, "04_agent_deployed")

            # Verify Mission Control UI is still visible
            mission_control = page.locator('text=/Mission Control/')
            assert mission_control.count() > 0, "Mission Control should remain visible"

            print("\n" + "="*80)
            print("✅ TEST PASSED: Agent Deployment")
            print("="*80)

            # Save trace
            context.tracing.stop(path="/tmp/trace_agent_deployment_SUCCESS.zip")
            print("  📊 Trace saved: /tmp/trace_agent_deployment_SUCCESS.zip")
            print("     View with: playwright show-trace /tmp/trace_agent_deployment_SUCCESS.zip")

            return True

        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {e}")
            take_screenshot(page, "FAILED_agent_deployment")
            print_console_logs(logs)
            context.tracing.stop(path="/tmp/trace_agent_deployment_FAILED.zip")
            print("  📊 Trace saved: /tmp/trace_agent_deployment_FAILED.zip")
            return False

        except Exception as e:
            print(f"\n❌ TEST ERROR: {e}")
            take_screenshot(page, "ERROR_agent_deployment")
            print_console_logs(logs)
            context.tracing.stop(path="/tmp/trace_agent_deployment_ERROR.zip")
            print("  📊 Trace saved: /tmp/trace_agent_deployment_ERROR.zip")
            return False

        finally:
            print("\nClosing browser...")
            browser.close()


if __name__ == "__main__":
    success = test_agent_deployment()
    exit(0 if success else 1)
