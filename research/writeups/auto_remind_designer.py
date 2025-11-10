#!/usr/bin/env python3
"""
Auto-reminder script for designer sessions.
Sends periodic reminders to keep the designer agent active.
"""

import time
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path to import orchestra modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.orchestra.mcp_client import send_message_to_session
except ImportError:
    print("❌ Error: Could not import orchestra modules")
    print("Make sure you're running from the AICraft project root")
    sys.exit(1)


def send_reminder(session_name: str, message_file: Path):
    """Send reminder message to designer session."""
    try:
        with open(message_file, 'r') as f:
            message = f.read()

        send_message_to_session(
            session_name=session_name,
            message=message,
            source_path=str(Path(__file__).parent.parent.parent),
            sender_name="auto-reminder"
        )
        return True
    except Exception as e:
        print(f"❌ Error sending reminder: {e}")
        return False


def format_time(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%H:%M")


def main():
    """Main loop for auto-reminder."""
    # Configuration
    SESSION_NAME = "designer"
    INTERVAL_MINUTES = 20
    MESSAGE_FILE = Path(__file__).parent / "continue.txt"

    # Validate message file exists
    if not MESSAGE_FILE.exists():
        print(f"❌ Error: Message file not found: {MESSAGE_FILE}")
        print("Please create continue.txt with your reminder message")
        sys.exit(1)

    print("🤖 Auto-reminder started")
    print(f"📝 Will send {MESSAGE_FILE.name} to {SESSION_NAME} every {INTERVAL_MINUTES} minutes")

    # Send first reminder immediately
    print("Sending first reminder immediately...")
    if send_reminder(SESSION_NAME, MESSAGE_FILE):
        print("✅ Initial reminder sent")

    try:
        while True:
            # Calculate next reminder time
            now = datetime.now()
            next_time = now + timedelta(minutes=INTERVAL_MINUTES)
            print(f"⏰ Next reminder in {INTERVAL_MINUTES} minutes at {format_time(next_time)}")

            # Sleep until next reminder
            time.sleep(INTERVAL_MINUTES * 60)

            # Send reminder
            current_time = datetime.now()
            if send_reminder(SESSION_NAME, MESSAGE_FILE):
                print(f"[{format_time(current_time)}] ✅ Reminder sent to {SESSION_NAME}")
            else:
                print(f"[{format_time(current_time)}] ❌ Failed to send reminder")

    except KeyboardInterrupt:
        print("\n\n👋 Auto-reminder stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
