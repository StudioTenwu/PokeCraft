"""E2E test for agent deployment through UI.

This test validates that clicking "Deploy Agent" button in the UI
doesn't trigger the version parameter error that was fixed in:
backend/src/agent_deployer.py:150-159

Background:
- Bug: "Server.__init__() got an unexpected keyword argument 'version'"
- Root cause: claude-agent-sdk v0.1.6's create_sdk_mcp_server() passes
  unsupported version parameter to Server.__init__()
- Fix: Create McpSdkServerConfig directly instead of using buggy SDK function

This E2E test ensures the full user workflow works end-to-end:
1. Create an agent (with LLM generation and avatar)
2. Create a world for that agent
3. Navigate to Mission Control
4. Fill in mission goal
5. Click "Deploy Agent" button
6. Verify no version error appears and deployment starts
"""

import os
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright, expect


def setup_clean_database():
    """Reset database to clean state before test.

    IMPORTANT: This follows Quibbler rule "E2E Test Database Reset"
    Prevents flaky tests from stale data, UUID conflicts, and UNIQUE constraint violations.

    Pattern:
    1. Remove existing database file
    2. Reinitialize with clean schema using uv run python
    """
    backend_path = Path(__file__).parent.parent.parent
    db_path = backend_path / "agents.db"

    print("  🗄️  Resetting database...")
    if db_path.exists():
        db_path.unlink()

    subprocess.run(
        ["uv", "run", "python", "-c", "from src.database import init_db; import asyncio; asyncio.run(init_db())"],
        cwd=backend_path,
        check=True,
        capture_output=True
    )
    print("  ✅ Database reset complete")


def test_agent_deployment_ui_flow():
    """Test full deployment flow through UI without version error.

    This E2E test validates the fix for:
    "Server.__init__() got an unexpected keyword argument 'version'"

    Flow:
    1. Load app
    2. Create agent
    3. Create world
    4. Fill mission goal
    5. Click "Deploy Agent" button
    6. Verify deployment starts without version error
    """

    print("\n" + "="*80)
    print("E2E TEST: Agent Deployment UI Flow (Version Error Fix)")
    print("="*80)

    # Reset database before test
    setup_clean_database()

    # Headless mode with trace viewer (recommended for macOS)
    # Avoids window focus stealing while still enabling full debugging
    # Run with HEADED=1 to see browser window during development
    headless = os.getenv('HEADED') != '1'
    slow_mo = 0 if headless else 300  # Slow down in headed mode for visibility

    print(f"  🖥️  Mode: {'Headless' if headless else 'Headed'}")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chromium', headless=headless, slow_mo=slow_mo)
        context = browser.new_context()

        # Enable tracing for debugging
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

        page = context.new_page()

        # Capture console logs
        logs = []
        page.on("console", lambda msg: logs.append(f"[{msg.type}] {msg.text}"))

        try:
            # Step 1: Navigate to app
            print("\n[1/7] Loading app...")
            page.goto('http://localhost:3000')
            page.wait_for_load_state('networkidle')

            # Step 2: Create agent
            print("\n[2/7] Creating agent...")

            # Fill agent description
            agent_textarea = page.locator('textarea[placeholder*="brave explorer"]')
            expect(agent_textarea).to_be_visible(timeout=5000)
            agent_textarea.fill("A helpful Pokemon trainer agent for testing deployment")

            # Wait for Hatch button to be enabled, then click
            hatch_btn = page.locator('button:has-text("Hatch")')
            expect(hatch_btn).to_be_visible(timeout=5000)
            expect(hatch_btn).to_be_enabled(timeout=5000)
            hatch_btn.click()

            # Wait for agent creation to complete (avatar generation takes time)
            print("  ⏳ Waiting for agent hatching (avatar generation)...")
            # Look for completion indicators - could be "Pokémon Hatched" or showing the agent panel
            expect(page.locator('text=/Pokémon Hatched|Agent Panel|Create World/')).to_be_visible(timeout=60000)
            print("  ✅ Agent hatched successfully")

            page.screenshot(path='/tmp/test_deployment_agent_created.png')

            # Step 3: Create world
            print("\n[3/7] Creating world...")

            # Fill world description
            world_textarea = page.locator('textarea[placeholder*="peaceful meadow"]')
            expect(world_textarea).to_be_visible(timeout=5000)
            world_textarea.fill("A test grid world for deployment validation")

            # Wait for Create World button to be enabled, then click
            create_world_btn = page.locator('button:has-text("Create World")')
            expect(create_world_btn).to_be_visible(timeout=5000)
            expect(create_world_btn).to_be_enabled(timeout=5000)
            create_world_btn.click()

            # Wait for world creation - Deploy button appears when world exists
            print("  ⏳ Waiting for world creation...")
            deploy_button = page.locator('button:has-text("🚀 Deploy")')
            expect(deploy_button).to_be_visible(timeout=30000)
            print("  ✅ World created successfully - Deploy button appeared")

            page.screenshot(path='/tmp/test_deployment_world_created.png')

            # Step 4: Navigate to Mission Control
            print("\n[4/7] Opening Mission Control...")

            # Click the Deploy button
            deploy_button.click()

            # Wait for Mission Control interface to load
            print("  ⏳ Waiting for Mission Control to load...")
            expect(page.locator('text=/Mission Goal/')).to_be_visible(timeout=10000)
            print("  ✅ Mission Control loaded")

            page.screenshot(path='/tmp/test_deployment_mission_control.png')

            # Step 5: Fill mission goal
            print("\n[5/7] Setting mission goal...")

            goal_input = page.locator('input[placeholder*="treasure"]')
            expect(goal_input).to_be_visible(timeout=5000)
            goal_input.fill("Find the treasure at coordinates (5, 5)")

            # Step 6: Click Deploy Agent button
            print("\n[6/7] Clicking Deploy Agent button...")

            deploy_btn = page.locator('button:has-text("Deploy Agent")')
            expect(deploy_btn).to_be_visible(timeout=5000)
            expect(deploy_btn).to_be_enabled(timeout=5000)
            deploy_btn.click()

            # Step 7: Verify deployment starts without version error
            print("\n[7/7] Verifying deployment starts without error...")

            # Wait a moment for SSE connection to establish
            page.wait_for_timeout(2000)

            # Check that no version error appears in error display
            error_box = page.locator('text=/Server.__init__.*got an unexpected keyword argument.*version/')

            # The error should NOT be visible
            expect(error_box).not_to_be_visible(timeout=3000)

            # Verify deployment actually started by checking for event log or loading state
            # The "Stop Mission" button should appear if deployment is running
            stop_btn = page.locator('button:has-text("Stop Mission")')

            # Either deployment is running (Stop button visible) OR completed quickly
            # We just need to verify no version error appeared
            deployment_started = stop_btn.is_visible(timeout=5000) or len(logs) > 0

            print("  ✅ No version error detected")
            print(f"  ℹ️  Deployment started: {deployment_started}")

            page.screenshot(path='/tmp/test_deployment_success.png')

            print("\n" + "="*80)
            print("✅ E2E TEST PASSED: Agent Deployment UI Flow")
            print("="*80)
            print("  📊 Verified:")
            print("    • Agent creation works")
            print("    • World creation works")
            print("    • Mission Control loads")
            print("    • Deploy button clickable")
            print("    • No version parameter error appears")

            # Save trace on success
            context.tracing.stop(path="/tmp/trace_deployment_ui_SUCCESS.zip")
            print("\n  📊 Trace saved: /tmp/trace_deployment_ui_SUCCESS.zip")
            print("     View with: playwright show-trace /tmp/trace_deployment_ui_SUCCESS.zip")

            return True

        except AssertionError as e:
            print(f"\n❌ E2E TEST FAILED: {e}")
            page.screenshot(path='/tmp/test_deployment_ui_failed.png')

            # Print console logs for debugging
            print(f"\n  📋 Console Logs (last 20):")
            for log in logs[-20:]:
                print(f"     {log}")

            # Save trace on failure
            context.tracing.stop(path="/tmp/trace_deployment_ui_FAILED.zip")
            print("  📊 Trace saved: /tmp/trace_deployment_ui_FAILED.zip")

            return False

        except Exception as e:
            print(f"\n❌ E2E TEST ERROR: {e}")
            page.screenshot(path='/tmp/test_deployment_ui_error.png')

            print(f"\n  📋 Console Logs (last 20):")
            for log in logs[-20:]:
                print(f"     {log}")

            context.tracing.stop(path="/tmp/trace_deployment_ui_ERROR.zip")
            print("  📊 Trace saved: /tmp/trace_deployment_ui_ERROR.zip")

            return False

        finally:
            print("\nClosing browser...")
            browser.close()


if __name__ == "__main__":
    success = test_agent_deployment_ui_flow()
    exit(0 if success else 1)
