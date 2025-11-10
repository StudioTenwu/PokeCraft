"""End-to-end test for Phase 1: Agent Birth.

Tests the complete user flow:
1. User enters agent description
2. Loading state appears
3. Agent card displays with all data
4. Personality badges have colors
5. Night mode toggle works
"""
from playwright.sync_api import sync_playwright, expect
import time

def test_agent_creation():
    """Test creating an agent and verifying all Phase 1 features."""
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False, slow_mo=500)  # Slow for visual verification
        page = browser.new_page()

        # Navigate to app
        page.goto('http://localhost:5173')
        page.wait_for_load_state('networkidle')

        print("✓ App loaded")

        # Take initial screenshot
        page.screenshot(path='/tmp/phase1_initial.png', full_page=True)

        # Find and fill agent description input
        description_input = page.get_by_placeholder('Describe your agent companion...')
        expect(description_input).to_be_visible()

        description_input.fill("A brave knight who protects the kingdom")
        print("✓ Description entered")

        # Click hatch button
        hatch_button = page.get_by_role('button', name='Hatch Companion')
        hatch_button.click()
        print("✓ Hatch button clicked")

        # Verify loading state appears
        loading_text = page.get_by_text('Hatching your companion...')
        expect(loading_text).to_be_visible(timeout=2000)
        print("✓ Loading state visible")

        # Wait for agent card to appear (may take 30-40s for avatar generation)
        agent_card = page.locator('.pokemon-card').first
        expect(agent_card).to_be_visible(timeout=60000)  # 60s timeout for mflux
        print("✓ Agent card appeared")

        # Take screenshot of created agent
        page.screenshot(path='/tmp/phase1_agent_created.png', full_page=True)

        # Verify agent name is displayed
        agent_name = page.locator('.pokemon-card h2').first
        expect(agent_name).to_be_visible()
        name_text = agent_name.inner_text()
        print(f"✓ Agent name: {name_text}")

        # Verify personality badges exist
        personality_badges = page.locator('.pokemon-card [class*="personality-badge"]')
        badge_count = personality_badges.count()
        assert badge_count > 0, f"Expected personality badges, found {badge_count}"
        print(f"✓ Found {badge_count} personality badges")

        # Verify badges have different colors (check class names)
        badge_classes = []
        for i in range(min(3, badge_count)):  # Check first 3 badges
            badge = personality_badges.nth(i)
            badge_class = badge.get_attribute('class')
            badge_classes.append(badge_class)

        # Should have varied classes (not all the same)
        unique_classes = len(set(badge_classes))
        assert unique_classes > 1, f"Expected varied badge colors, found {unique_classes} unique classes"
        print(f"✓ Personality badges have varied colors ({unique_classes} unique)")

        # Test night mode toggle
        night_mode_button = page.get_by_role('button', name='Toggle theme')
        expect(night_mode_button).to_be_visible()

        # Click to enable dark mode
        night_mode_button.click()
        time.sleep(0.5)  # Wait for transition

        # Check if dark theme is applied (data-theme attribute on html)
        html_theme = page.locator('html').get_attribute('data-theme')
        assert html_theme == 'dark', f"Expected dark theme, got {html_theme}"
        print("✓ Night mode enabled")

        # Take dark mode screenshot
        page.screenshot(path='/tmp/phase1_dark_mode.png', full_page=True)

        # Toggle back to light mode
        night_mode_button.click()
        time.sleep(0.5)

        html_theme = page.locator('html').get_attribute('data-theme')
        assert html_theme != 'dark', "Expected light theme after toggle"
        print("✓ Night mode toggled back to light")

        # Final screenshot
        page.screenshot(path='/tmp/phase1_final.png', full_page=True)

        print("\n=== Phase 1 E2E Test PASSED ===")
        print("Screenshots saved to /tmp/phase1_*.png")

        browser.close()

if __name__ == "__main__":
    test_agent_creation()
