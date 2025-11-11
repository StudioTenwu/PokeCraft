"""Test script to verify mflux progress streaming with logging.

Run this to see detailed logs of the avatar generation progress.
"""
import asyncio
import sys
import logging

# Setup logging to see all debug messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add backend to path
sys.path.insert(0, 'backend/src')

from avatar_generator import AvatarGenerator


async def test_avatar_streaming():
    """Test avatar generation with progress streaming."""
    print("=" * 80)
    print("Testing Avatar Progress Streaming")
    print("=" * 80)
    print()

    generator = AvatarGenerator()
    test_agent_id = "test_progress_123"
    test_prompt = "cute pikachu, game boy color style"

    print(f"Agent ID: {test_agent_id}")
    print(f"Prompt: {test_prompt}")
    print()
    print("Starting avatar generation...")
    print("-" * 80)

    progress_events = []

    async for event in generator.generate_avatar_stream(test_agent_id, test_prompt):
        progress_events.append(event)

        if event["type"] == "avatar_progress":
            print(f"📊 Progress Event: {event['progress']}% - {event['message']}")
        elif event["type"] == "avatar_complete":
            print(f"✅ Complete Event: {event['avatar_url']}")

    print("-" * 80)
    print()
    print("Summary:")
    print(f"  Total events: {len(progress_events)}")
    print(f"  Progress events: {len([e for e in progress_events if e['type'] == 'avatar_progress'])}")
    print(f"  Complete events: {len([e for e in progress_events if e['type'] == 'avatar_complete'])}")
    print()

    # Show progress sequence
    progress_values = [e['progress'] for e in progress_events if e['type'] == 'avatar_progress']
    if progress_values:
        print("Progress sequence:")
        for i, pct in enumerate(progress_values, 1):
            print(f"  {i}. {pct}%")
    else:
        print("⚠️  WARNING: No progress events received!")
        print("   This means mflux didn't output progress or parsing failed.")

    print()
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_avatar_streaming())
