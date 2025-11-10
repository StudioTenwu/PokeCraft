#!/usr/bin/env python3
"""Test Phaser 3 tutorial HTML file for interactivity issues."""

from playwright.sync_api import sync_playwright
import time

def test_phaser_tutorial():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False to see what's happening
        page = browser.new_page()

        # Open the HTML file
        file_path = 'file:///Users/wz/Desktop/zPersonalProjects/AICraft/claude_files/html/phaser3-tutorial.html'
        print(f"Loading: {file_path}")
        page.goto(file_path)

        # Wait for page to load
        page.wait_for_load_state('networkidle')
        time.sleep(2)  # Extra wait for Phaser to initialize

        # Take screenshot of full page
        print("Taking full page screenshot...")
        page.screenshot(path='/tmp/phaser_tutorial_full.png', full_page=True)

        # Check if Phaser loaded
        phaser_loaded = page.evaluate("typeof Phaser !== 'undefined'")
        print(f"Phaser loaded: {phaser_loaded}")

        # Check for JavaScript errors in console
        console_messages = []
        page.on('console', lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))

        # Check if game canvas exists
        game_canvas = page.locator('#game-canvas')
        canvas_visible = game_canvas.is_visible()
        print(f"Game canvas visible: {canvas_visible}")

        # Check if there are any canvas elements
        canvases = page.locator('canvas').all()
        print(f"Number of canvas elements: {len(canvases)}")

        if len(canvases) > 0:
            for i, canvas in enumerate(canvases):
                bbox = canvas.bounding_box()
                print(f"Canvas {i}: {bbox}")

        # Scroll to the game demo section
        print("Scrolling to demo section...")
        page.locator('#demo').scroll_into_view_if_needed()
        time.sleep(1)

        # Take screenshot of game area
        print("Taking demo section screenshot...")
        page.screenshot(path='/tmp/phaser_tutorial_demo.png')

        # Check console for errors
        time.sleep(2)
        if console_messages:
            print("\nConsole messages:")
            for msg in console_messages:
                print(f"  {msg}")

        # Get page errors
        errors = page.evaluate("""
            () => {
                const errors = [];
                const origError = console.error;
                console.error = function(...args) {
                    errors.push(args.join(' '));
                    origError.apply(console, args);
                };
                return errors;
            }
        """)

        if errors:
            print("\nJavaScript errors:")
            for error in errors:
                print(f"  {error}")

        # Check if game is actually running
        game_exists = page.evaluate("typeof demoGame !== 'undefined'")
        print(f"\nGame object exists: {game_exists}")

        if game_exists:
            game_config = page.evaluate("demoGame.config")
            print(f"Game config: {game_config}")

        # Wait a bit before closing to see the page
        print("\nWaiting 5 seconds before closing...")
        time.sleep(5)

        browser.close()

        print("\nScreenshots saved:")
        print("  /tmp/phaser_tutorial_full.png")
        print("  /tmp/phaser_tutorial_demo.png")

if __name__ == '__main__':
    test_phaser_tutorial()
