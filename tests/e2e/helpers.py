"""Helper functions for E2E tests."""

import time
from playwright.sync_api import Page, expect


def wait_for_app_ready(page: Page):
    """Wait for the React app to fully load."""
    page.wait_for_load_state('networkidle')
    # Wait for at least one pokemon-container to appear
    page.wait_for_selector('.pokemon-container', timeout=10000)
    time.sleep(1)  # Additional buffer for React rendering


def create_pokemon(page: Page, pokemon_name: str = "Pikachu") -> dict:
    """
    Click a default Pokémon button and wait for creation.

    Args:
        page: Playwright page object
        pokemon_name: Name of Pokémon to create (Pikachu, Charmander, Bulbasaur, Squirtle)

    Returns:
        dict with agent info: {'id': str, 'name': str}
    """
    print(f"  📝 Creating Pokémon: {pokemon_name}")

    # Click the Pokémon button
    pokemon_button = page.locator(f'button:has-text("{pokemon_name}")')
    expect(pokemon_button).to_be_visible(timeout=5000)
    pokemon_button.click()

    # Wait for agent creation (avatar generation takes time)
    print("  ⏳ Waiting for agent creation...")
    page.wait_for_selector('button:has-text("Create World")', timeout=60000)

    # Get the agent ID from the dropdown
    select = page.locator('select').first
    agent_id = select.input_value()

    print(f"  ✅ Pokémon created: {pokemon_name} (ID: {agent_id[:8]}...)")
    return {'id': agent_id, 'name': pokemon_name}


def select_agent(page: Page, agent_id: str):
    """Select an agent from the dropdown."""
    print(f"  📝 Selecting agent: {agent_id[:8]}...")
    select = page.locator('select').first
    select.select_option(value=agent_id)
    time.sleep(1)


def create_world(page: Page, description: str = "a mystical forest with glowing trees") -> dict:
    """
    Create a world for the selected agent.

    Args:
        page: Playwright page object
        description: World description

    Returns:
        dict with world info: {'id': str, 'name': str}
    """
    print(f"  📝 Creating world: {description[:50]}...")

    # Fill in world description first (button is disabled until this is filled)
    textarea = page.locator('textarea').first
    expect(textarea).to_be_visible(timeout=5000)
    textarea.fill(description)

    # Submit - button should now be enabled since textarea is filled
    print("  ⏳ Waiting for world generation...")
    submit_btn = page.locator('button:has-text("Create World")').first
    expect(submit_btn).to_be_enabled(timeout=5000)
    submit_btn.click()

    # Wait for world canvas to appear
    page.wait_for_selector('canvas', timeout=60000)

    # Get world name from the page
    world_name_el = page.locator('h3:has-text("🗺️")').first
    world_name = world_name_el.inner_text().replace('🗺️ ', '')

    print(f"  ✅ World created: {world_name}")
    return {'name': world_name}


def create_tool(page: Page, tool_description: str = "move the agent forward one step") -> dict:
    """
    Create a tool for the selected agent.

    Args:
        page: Playwright page object
        tool_description: Tool description

    Returns:
        dict with tool info: {'name': str}
    """
    print(f"  📝 Creating tool: {tool_description[:50]}...")

    # Scroll to tool workshop section
    tool_workshop = page.locator('text="Tool Workshop"')
    if tool_workshop.count() == 0:
        print("  ⚠️  Tool Workshop not visible - need to create world first?")
        return None

    # Fill in tool description
    textarea = page.locator('textarea[placeholder*="tool"]').or_(
        page.locator('textarea').nth(1)  # Second textarea on page
    )
    expect(textarea).to_be_visible(timeout=5000)
    textarea.fill(tool_description)

    # Submit
    print("  ⏳ Waiting for tool generation...")
    generate_btn = page.locator('button:has-text("Generate Tool")')
    generate_btn.click()

    # Wait for tool to appear
    page.wait_for_selector('.pokemon-container:has-text("Tool:")', timeout=60000)

    # Get tool name
    tool_card = page.locator('.pokemon-container:has-text("Tool:")').first
    tool_text = tool_card.inner_text()
    tool_name = tool_text.split('\n')[0].replace('Tool: ', '')

    print(f"  ✅ Tool created: {tool_name}")
    return {'name': tool_name}


def deploy_agent(page: Page) -> bool:
    """
    Click Deploy button and verify deployment UI appears.

    Args:
        page: Playwright page object

    Returns:
        bool: True if deployment started successfully
    """
    print("  📝 Deploying agent...")

    # Click Deploy button
    deploy_btn = page.locator('button:has-text("Deploy")')
    expect(deploy_btn).to_be_visible(timeout=5000)
    deploy_btn.click()

    # Wait for Mission Control to appear
    print("  ⏳ Waiting for deployment UI...")
    page.wait_for_selector('text=/Mission Control/', timeout=10000)

    # Verify deployment UI elements
    has_mission_control = page.locator('text=/Mission Control/').count() > 0
    has_deploy_button = page.locator('button:has-text("Deploy Agent")').count() > 0

    if has_mission_control and has_deploy_button:
        print("  ✅ Deployment UI loaded successfully")
        return True
    else:
        print("  ❌ Deployment UI incomplete")
        return False


def click_deploy_agent_button(page: Page, goal: str = "Explore the world and complete tasks") -> bool:
    """
    Fill in mission goal and click 'Deploy Agent' button.

    Args:
        page: Playwright page object
        goal: Mission goal for the agent (default: generic exploration goal)

    Returns:
        bool: True if deployment started
    """
    print("  📝 Starting agent deployment...")

    # Fill in mission goal (button is disabled until this is filled)
    # Look for input with placeholder containing "treasure"
    goal_input = page.locator('input[placeholder*="treasure"]').first
    expect(goal_input).to_be_visible(timeout=5000)
    goal_input.fill(goal)

    # Click Deploy Agent button
    deploy_agent_btn = page.locator('button:has-text("Deploy Agent")')
    expect(deploy_agent_btn).to_be_visible(timeout=5000)
    expect(deploy_agent_btn).to_be_enabled(timeout=5000)
    deploy_agent_btn.click()

    # Wait for deployment to start (check for thinking/tool/success indicators)
    time.sleep(2)

    # Check if event log has any entries
    event_log = page.locator('text="Event Log"')
    if event_log.count() > 0:
        print("  ✅ Agent deployment started")
        return True
    else:
        print("  ⚠️  Deployment may not have started")
        return False


def take_screenshot(page: Page, name: str):
    """Take a screenshot for debugging."""
    filename = f"/tmp/e2e_{name}_{int(time.time())}.png"
    page.screenshot(path=filename, full_page=True)
    print(f"  📸 Screenshot saved: {filename}")
    return filename


def capture_console_logs(page: Page) -> list[str]:
    """
    Set up console log capture for debugging.

    Args:
        page: Playwright page object

    Returns:
        list of console log messages
    """
    logs = []

    def handle_console(msg):
        logs.append(f"[{msg.type}] {msg.text}")

    page.on("console", handle_console)
    return logs


def print_console_logs(logs: list[str], limit: int = 20):
    """Print captured console logs."""
    if not logs:
        print("  ℹ️  No console logs captured")
        return

    print(f"\n  📋 Console Logs (last {limit}):")
    for log in logs[-limit:]:
        print(f"     {log}")
