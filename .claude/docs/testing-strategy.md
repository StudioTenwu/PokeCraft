# AICraft Testing Strategy

## Problem
Need to test complete user workflows (Create Pokémon, Create World, Create Tool, Deploy Agent) without clicking through the UI manually every time.

## Two Approaches

### Approach 1: E2E Testing with Playwright (Recommended)
**Pros:**
- Tests the actual user experience
- Catches UI bugs (like the blank screen issue)
- Verifies frontend-backend integration
- Can capture screenshots/videos
- Validates complete workflows

**Cons:**
- Slower (requires browser)
- More complex setup
- Harder to debug

### Approach 2: Direct API Testing
**Pros:**
- Fast execution
- Easy to debug
- Can test edge cases
- No browser required

**Cons:**
- Doesn't test UI
- Misses integration issues
- May not catch real user problems

## Recommended: Hybrid Approach

Use **Playwright for happy path workflows** + **Direct API for edge cases**.

### Test Structure

```
tests/
├── e2e/                    # Playwright E2E tests
│   ├── test_pokemon_creation.py
│   ├── test_world_creation.py
│   ├── test_tool_creation.py
│   └── test_agent_deployment.py
├── api/                    # Direct API tests
│   ├── test_agents_api.py
│   ├── test_worlds_api.py
│   └── test_tools_api.py
└── fixtures/
    └── test_data.py        # Shared test data
```

## Implementation Plan

### Phase 1: Playwright Test Helpers
Create reusable helper functions for common workflows:

```python
# tests/e2e/helpers.py

def create_pokemon(page, pokemon_name="Pikachu"):
    """Click default Pokémon and wait for creation."""
    page.click(f'button:has-text("{pokemon_name}")')
    page.wait_for_selector('.pokemon-container:has-text("Create World")')
    return get_selected_agent(page)

def create_world(page, description="a test world"):
    """Create a world for selected agent."""
    page.click('text="Create World"')
    page.fill('textarea', description)
    page.click('button:has-text("Create World"):last-child')
    page.wait_for_selector('canvas')
    return get_world_from_page(page)

def create_tool(page, tool_description):
    """Create a tool for selected agent."""
    page.click('text="Create Tool"')
    page.fill('textarea[placeholder*="tool"]', tool_description)
    page.click('button:has-text("Generate Tool")')
    page.wait_for_selector('.tool-card')  # Wait for tool to appear

def deploy_agent(page):
    """Click Deploy button and wait for deployment."""
    page.click('text="Deploy"')
    page.wait_for_selector('text="Mission Control"')
```

### Phase 2: E2E Test Suite

```python
# tests/e2e/test_complete_workflow.py

def test_full_pokemon_workflow(page):
    """Test complete workflow: Create Pokémon → World → Tool → Deploy"""

    # 1. Create Pokémon
    page.goto('http://localhost:3000')
    agent = create_pokemon(page, "Pikachu")
    assert agent['name'] == 'Pikachu'

    # 2. Create World
    world = create_world(page, "a mystical forest")
    assert 'grid' in world

    # 3. Create Tool
    create_tool(page, "move forward")
    assert page.locator('.tool-card').count() > 0

    # 4. Deploy Agent
    deploy_agent(page)
    assert page.locator('text="Mission Control"').is_visible()
```

### Phase 3: API Endpoint Testing

**Option A: Keep existing endpoints (no changes)**
- Test via HTTP requests
- Use `requests` or `httpx` library

**Option B: Add convenience endpoints for testing**
- Add `/api/test/` routes that bypass UI
- Example: `POST /api/test/quick-deploy` that creates agent + world + deploys in one call

## Recommendation: Option A (Keep Existing)

**Why:**
- Testing should test what users actually do
- Adding test-only endpoints adds maintenance burden
- Playwright tests are better for catching real issues

## Test Implementation

### 1. Create Test Runner Script

```python
# tests/run_e2e_tests.py

import subprocess
import sys
from playwright.sync_api import sync_playwright

def start_servers():
    """Start backend and frontend servers."""
    backend = subprocess.Popen(
        ['uv', 'run', 'uvicorn', 'src.main:app'],
        cwd='backend'
    )
    frontend = subprocess.Popen(
        ['npm', 'run', 'dev'],
        cwd='frontend'
    )
    return backend, frontend

def run_tests():
    """Run E2E tests with Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Run tests...
        test_pokemon_creation(page)
        test_world_creation(page)
        test_tool_creation(page)
        test_deployment(page)

        browser.close()

if __name__ == '__main__':
    backend, frontend = start_servers()
    try:
        time.sleep(3)  # Wait for servers to start
        run_tests()
    finally:
        backend.terminate()
        frontend.terminate()
```

### 2. Add Logging to Track Progress

```python
def test_with_logging(page, test_name):
    """Wrapper that logs test progress."""
    print(f"\n{'='*60}")
    print(f"Running: {test_name}")
    print(f"{'='*60}")

    # Capture console logs
    console_logs = []
    page.on('console', lambda msg: console_logs.append(msg.text))

    try:
        yield  # Run test
        print(f"✅ {test_name} PASSED")
    except Exception as e:
        print(f"❌ {test_name} FAILED: {e}")
        print(f"\nConsole logs:")
        for log in console_logs[-10:]:
            print(f"  {log}")
        raise
```

## What's Failing Now?

You mentioned "Create Tool button doesn't work". Let me check what the actual error is.

### Debug Steps:
1. Open browser console when clicking "Create Tool"
2. Check backend logs for errors
3. Check if API call is being made
4. Verify endpoint exists and works

Would you like me to:
- **A)** Write the Playwright test suite now
- **B)** Debug the "Create Tool" issue first
- **C)** Add test-only API endpoints for easier testing
