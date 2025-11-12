# Quibbler Rules for AICraft

Project-specific rules for code quality and testing.

### Rule: E2E Test Database Reset

Before running E2E tests, explicitly reset database state to prevent flaky tests from stale data.

**Pattern:**
```bash
rm -f backend/agents.db
cd backend && uv run python -c "from src.database import init_db; import asyncio; asyncio.run(init_db())"
```

**Why:** Prevents UNIQUE constraint violations, UUID conflicts, and non-repeatable test failures.

**Check:** Before claiming E2E tests pass, verify database was reset in test setup.

### Rule: Playwright Selector Specificity

Avoid generic selectors without context in E2E tests. Generic selectors are fragile and break when DOM structure changes.

**Bad:**
```python
page.locator('textarea').first
page.locator('button').last
page.locator('input').nth(2)
```

**Good:**
```python
page.locator('textarea[placeholder="World description"]')
page.locator('button:has-text("Create World")')
page.locator('input[placeholder*="treasure"]')
```

**Why:** Attribute-based selectors are robust to DOM structure changes and make tests self-documenting.

**Check:** Flag any `.first`, `.last`, `.nth()` usage without accompanying attribute selector.

### Rule: Form Button Pattern in Tests

When testing forms, always fill input fields BEFORE clicking submit buttons. Buttons are typically disabled until form validation passes.

**Pattern:**
```python
# 1. Fill all required fields first
input_field.fill("value")
textarea_field.fill("description")

# 2. Wait for button to be enabled
button = page.locator('button:has-text("Submit")')
expect(button).to_be_enabled(timeout=5000)

# 3. Then click
button.click()
```

**Why:** Prevents "element not enabled" timeout failures. This pattern eliminates 75% of E2E test timing issues.

**Check:** Flag any `button.click()` that happens before corresponding form fields are filled.

### Rule: Frontend UUID Generation

When sending data to POST endpoints that accept optional `id` fields, DO NOT send hardcoded or template IDs. Let the backend generate UUIDs.

**Bad:**
```javascript
const pokemon = { id: "pikachu", name: "Pikachu", ... }
fetch('/api/agents', { body: JSON.stringify(pokemon) })
```

**Good:**
```javascript
const { id, ...pokemonData } = pokemon  // Omit id field
fetch('/api/agents', { body: JSON.stringify(pokemonData) })
```

**Why:** Prevents UNIQUE constraint violations on subsequent runs when same template data is used multiple times.

**Check:** When creating entities from templates/defaults, verify `id` field is omitted from request body.

### Rule: Type Completeness

All Python functions must have complete type hints including return types. No bare `def` declarations.

**Bad:**
```python
def create_agent(name):
    return agent_data
```

**Good:**
```python
def create_agent(name: str) -> dict[str, Any]:
    return agent_data
```

**Why:** Type hints catch errors at development time and serve as inline documentation.

**Check:** Every function definition must have parameter types and `-> ReturnType`.

### Rule: API Contract Verification

When modifying backend API endpoints (request/response structure), verify frontend compatibility before claiming completion.

**Process:**
1. Make backend changes
2. Check frontend code that calls the endpoint
3. Verify request structure matches new Pydantic models
4. Verify response handling expects new structure
5. Run E2E tests that exercise the endpoint

**Why:** API contract mismatches cause silent failures that are hard to debug.

**Check:** Before marking API endpoint changes complete, confirm corresponding frontend code was reviewed.

### Rule: Check Full Error Tracebacks for SDK Failures

When encountering SDK-related errors (Claude Agent SDK, MCP, etc.), always check full error tracebacks in log files, not just user-facing error messages.

**Process:**
1. Check `logs/errors.log` for FULL traceback with complete stack trace
2. Identify exact failure point in SDK source code (file and line number)
3. Read SDK source code at the failure point to understand what it expects
4. Compare agent's implementation against SDK's internal processing logic
5. Trace back through call stack to find root cause

**Why:** SDK errors often surface deep in internal SDK code. User-facing error messages (e.g., "JSON serialization failed") don't reveal the root cause (e.g., wrong TypedDict keys). Full tracebacks show the exact SDK code path and failure point.

**Example:** Error message "Object of type Server is not JSON serializable" → Check `logs/errors.log` → Find traceback pointing to `subprocess_cli.py:169` → Read SDK source → Discover TypedDict key mismatch (`server` vs `instance`).

**Check:** Before claiming SDK-related bugs are fixed, verify the fix addresses the root cause identified in the full traceback, not just the user-facing symptom.
