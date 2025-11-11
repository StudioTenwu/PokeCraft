#!/usr/bin/env python3
"""Simple script to capture console output during world creation."""

from playwright.sync_api import sync_playwright
import sqlite3
import time

# Get first agent from DB
conn = sqlite3.connect('backend/agents.db')
cursor = conn.cursor()
cursor.execute("SELECT id, name FROM agents LIMIT 1")
result = cursor.fetchone()
conn.close()

if not result:
    print("❌ No agents found in database")
    exit(1)

agent_id, agent_name = result
print(f"Using agent: {agent_name} ({agent_id})")

console_logs = []

with sync_playwright() as p:
    browser = p.chromium.launch(channel='chromium', headless=False)
    page = browser.new_page()

    # Capture ALL console messages
    page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

    print("\n1. Loading app...")
    page.goto('http://localhost:3000')
    page.wait_for_load_state('networkidle')
    time.sleep(2)

    print("2. Selecting agent...")
    page.select_option('select', value=agent_id)
    time.sleep(2)

    print("3. Clicking Create World...")
    page.click('text="Create World"')
    time.sleep(1)

    print("4. Filling description...")
    page.fill('textarea', 'a simple test world')
    time.sleep(0.5)

    print("5. Submitting...")
    page.click('button:has-text("Create World"):last-child')

    print("6. Waiting 10 seconds for world creation...")
    time.sleep(10)

    print("\n" + "="*80)
    print("CONSOLE OUTPUT:")
    print("="*80)
    for log in console_logs:
        print(log)

    print("\n" + "="*80)
    print("Keeping browser open - check the screen!")
    input("Press Enter to close...")

    browser.close()
