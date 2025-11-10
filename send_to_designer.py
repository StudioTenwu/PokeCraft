#!/usr/bin/env python3
"""Send continue.txt content to the designer agent via tmux send-keys"""

import sys
from pathlib import Path

# Add orchestra lib to path
sys.path.insert(0, '/opt/homebrew/lib/python3.11/site-packages')

from orchestra.lib.sessions import load_sessions, find_session

# Load continue.txt
continue_file = Path('/Users/wz/Desktop/zPersonalProjects/AICraft/continue.txt')
message = continue_file.read_text().strip()

# Load sessions for this project
project_dir = Path('/Users/wz/Desktop/zPersonalProjects/AICraft')
sessions = load_sessions(project_dir=project_dir)

# Find the main designer session
designer_session = find_session(sessions, 'main')

if not designer_session:
    print("Error: Could not find 'main' designer session")
    print("Available sessions:")
    for s in sessions:
        print(f"  - {s.session_name} (id: {s.session_id})")
    sys.exit(1)

# Send message using the session's protocol
print(f"Sending message to designer session: {designer_session.session_name}")
print(f"Session ID: {designer_session.session_id}")
print(f"\nMessage content:\n{message}\n")

# Use the session's send_message method (which uses tmux protocol under the hood)
designer_session.send_message(message, sender_name="user")

print("✅ Message sent successfully!")
