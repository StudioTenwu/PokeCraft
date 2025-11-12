# AICraft E2E Test Suite

Comprehensive end-to-end tests for all core user workflows using Playwright.

## Prerequisites

```bash
# Install Playwright
pip install playwright
playwright install chromium

# Or with uv
uv pip install playwright
playwright install chromium
```

## Quick Start

### Run All Tests (Headless - No Window Disruption)

```bash
python tests/e2e/run_all_tests.py
```

Tests run in **headless mode** by default - no browser windows will appear or steal focus from your work!

### Run With Visible Browser (For Development)

```bash
HEADED=1 python tests/e2e/run_all_tests.py
```

### Run Individual Tests

```bash
# Headless (default)
python tests/e2e/test_pokemon_creation.py
python tests/e2e/test_world_creation.py
python tests/e2e/test_tool_creation.py
python tests/e2e/test_agent_deployment.py

# With visible browser
HEADED=1 python tests/e2e/test_pokemon_creation.py
```

## Test Workflows

1. **Pokémon Creation** - Test creating Pikachu from default template
2. **World Creation** - Test creating Charmander and a volcanic world
3. **Tool Creation** - Test creating Bulbasaur, world, and a tool
4. **Agent Deployment** - Test creating Squirtle, world, and deployment

## Debugging Failed Tests

### View Trace Files (Recommended)

Every test automatically captures a **trace** that you can replay visually:

```bash
# View the trace file
playwright show-trace /tmp/trace_pokemon_creation_FAILED.zip
```

The Trace Viewer shows:
- Screenshot at every step
- DOM snapshots
- Network requests
- Console logs
- Timeline of all actions

**This is the best way to debug without browser window disruption!**

### Screenshots

Screenshots are saved to `/tmp/` with descriptive names:
- `/tmp/e2e_01_pikachu_created_<timestamp>.png`
- `/tmp/e2e_FAILED_pokemon_creation_<timestamp>.png`
- `/tmp/e2e_ERROR_world_creation_<timestamp>.png`

### Console Logs

Console logs from the browser are captured and printed on test failure.

## Test Architecture

### Helper Functions (`helpers.py`)

Reusable functions for common test actions:

- `wait_for_app_ready(page)` - Wait for React app to fully load
- `create_pokemon(page, name)` - Click Pokémon button and wait for creation
- `create_world(page, description)` - Fill world form and submit
- `create_tool(page, description)` - Generate a tool
- `deploy_agent(page)` - Open deployment UI
- `click_deploy_agent_button(page)` - Start deployment
- `take_screenshot(page, name)` - Capture screenshot for debugging
- `capture_console_logs(page)` - Set up console log capture
- `print_console_logs(logs)` - Print captured logs

### Test Structure

Each test follows this pattern:

1. **Setup**: Launch browser, enable tracing
2. **Test Steps**: Execute user workflow
3. **Assertions**: Verify expected outcomes
4. **Teardown**: Save trace, close browser

## Requirements

- Backend running on `http://localhost:8000`
- Frontend running on `http://localhost:3000`
- Chromium browser (auto-installed by Playwright)

## Environment Variables

- `HEADED=1` - Run tests with visible browser windows (default: headless)

## Tips

### Best Practices

1. **Default to headless** - Faster, no window disruption
2. **Use trace viewer for debugging** - Visual debugging without browser windows
3. **Check console logs** - Often reveals the root cause
4. **Run individual tests** - Faster iteration during development

### Common Issues

**Tests timeout waiting for elements:**
- Check that both backend and frontend are running
- Look at console logs for JavaScript errors
- View trace file to see what the page looked like

**"UNIQUE constraint failed" errors:**
- Default Pokémon IDs cause duplicate key errors
- Fixed: Frontend now omits `id` field to let backend generate UUIDs

**Browser takes focus on macOS:**
- Use headless mode (default)
- No workaround exists for headed mode on macOS

## Example Output

```
================================================================================
AICRAFT E2E TEST SUITE
================================================================================
Started at: 2025-11-11 12:15:30

[Pre-flight Check] Verifying servers are running...
✅ Both servers are running

================================================================================
[1/4] Running: test_pokemon_creation.py
================================================================================
  🖥️  Mode: Headless
✅ test_pokemon_creation.py completed in 15.23s

...

================================================================================
E2E TEST SUITE SUMMARY
================================================================================

Total Tests: 4
✅ Passed: 4
❌ Failed: 0

Success Rate: 100.0%
```

## Trace Viewer Demo

After running a test, open the trace:

```bash
playwright show-trace /tmp/trace_pokemon_creation_SUCCESS.zip
```

You'll see:
- Interactive timeline
- Screenshots at every step
- Network activity
- Console messages
- Full DOM snapshots
- Ability to inspect any element at any point in time

This is **more powerful than watching the test run** because you can step through it at your own pace!
