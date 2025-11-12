#!/usr/bin/env python3
"""Simple headless Playwright test for agent deployment.

Tests the full deployment flow to catch bugs like:
- async for iterator errors
- Connection failures
- SSE stream issues

Run: python3 test_deploy_simple.py
"""

import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright, expect


def reset_db():
    """Reset database for clean test."""
    backend = Path(__file__).parent / "backend"
    db = backend / "agents.db"

    print("🗄️  Resetting database...")
    if db.exists():
        db.unlink()

    subprocess.run(
        ["uv", "run", "python", "-c",
         "from src.database import init_db; import asyncio; asyncio.run(init_db())"],
        cwd=backend,
        check=True,
        capture_output=True
    )
    print("✅ Database reset\n")


def test_deploy():
    """Test deployment flow - should complete without errors."""

    print("="*60)
    print("🧪 DEPLOYMENT TEST (Headless)")
    print("="*60 + "\n")

    reset_db()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()

        # Capture errors
        errors = []
        page.on("console", lambda msg: errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None)
        page.on("pageerror", lambda err: errors.append(f"PAGE ERROR: {err}"))

        try:
            # 1. Load app
            print("[1/5] Loading app...")
            page.goto('http://localhost:3000')
            page.wait_for_load_state('networkidle')

            # 2. Create agent
            print("[2/5] Creating agent...")
            textarea = page.locator('textarea[placeholder*="brave explorer"]')
            expect(textarea).to_be_visible(timeout=5000)
            textarea.fill("Test deployment agent")

            hatch_btn = page.locator('button:has-text("Hatch")')
            expect(hatch_btn).to_be_enabled(timeout=5000)
            hatch_btn.click()

            print("  ⏳ Waiting for hatch...")
            expect(page.locator('text=/Create World/')).to_be_visible(timeout=60000)
            print("  ✅ Agent hatched")

            # 3. Create world
            print("[3/5] Creating world...")
            world_textarea = page.locator('textarea[placeholder*="peaceful meadow"]')
            expect(world_textarea).to_be_visible(timeout=5000)
            world_textarea.fill("Test world")

            create_world_btn = page.locator('button:has-text("Create World")')
            expect(create_world_btn).to_be_enabled(timeout=5000)
            create_world_btn.click()

            print("  ⏳ Waiting for world...")
            deploy_btn = page.locator('button:has-text("🚀 Deploy")')
            expect(deploy_btn).to_be_visible(timeout=30000)
            print("  ✅ World created")

            # 4. Open deployment
            print("[4/5] Opening deployment...")
            deploy_btn.click()

            goal_input = page.locator('input[placeholder*="treasure"]')
            expect(goal_input).to_be_visible(timeout=10000)
            goal_input.fill("Find the treasure")
            print("  ✅ Deployment UI loaded")

            # 5. Deploy agent
            print("[5/5] Deploying agent...")
            deploy_agent_btn = page.locator('button:has-text("Deploy Agent")')
            expect(deploy_agent_btn).to_be_enabled(timeout=5000)
            deploy_agent_btn.click()

            # Wait and check for errors
            print("  ⏳ Checking for errors (5s)...")
            page.wait_for_timeout(5000)

            # Check for error message in UI
            error_box = page.locator('text=/Connection lost|async for|__aiter__|Error/')
            has_error = error_box.is_visible(timeout=1000)

            # Check console errors
            async_errors = [e for e in errors if 'async for' in e or '__aiter__' in e or 'Connection lost' in e]

            print("\n" + "="*60)
            if has_error or async_errors:
                print("❌ TEST FAILED")
                print("="*60)
                print(f"\n🔍 Error in UI: {has_error}")
                print(f"🔍 Console errors: {len(async_errors)}")
                if async_errors:
                    print("\n📋 Errors:")
                    for err in async_errors[:5]:
                        print(f"  • {err}")

                page.screenshot(path='/tmp/deploy_FAILED.png')
                context.tracing.stop(path="/tmp/trace_deploy_FAILED.zip")
                print(f"\n📊 Trace: /tmp/trace_deploy_FAILED.zip")
                return False
            else:
                print("✅ TEST PASSED")
                print("="*60)
                print("\n✓ No async for errors")
                print("✓ No connection errors")
                print("✓ Deployment started successfully")

                page.screenshot(path='/tmp/deploy_SUCCESS.png')
                context.tracing.stop(path="/tmp/trace_deploy_SUCCESS.zip")
                return True

        except Exception as e:
            print(f"\n❌ EXCEPTION: {e}")
            page.screenshot(path='/tmp/deploy_ERROR.png')
            context.tracing.stop(path="/tmp/trace_deploy_ERROR.zip")
            return False
        finally:
            browser.close()


if __name__ == "__main__":
    success = test_deploy()
    exit(0 if success else 1)
