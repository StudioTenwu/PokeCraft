#!/usr/bin/env python3
"""Test script to verify avatar generator works with new model path."""

import sys
from pathlib import Path

# Add backend/src to path
sys.path.insert(0, str(Path(__file__).parent / "backend" / "src"))

from avatar_generator import AvatarGenerator

def test_avatar_generator():
    print("Testing AvatarGenerator with new model path...")

    # Initialize generator (should use ~/.AICraft/models/schnell-3bit by default)
    generator = AvatarGenerator()
    print(f"Model path: {generator.model_path}")
    print(f"Output directory: {generator.output_dir}")

    # Verify model path exists
    model_path = Path(generator.model_path)
    if not model_path.exists():
        print(f"❌ ERROR: Model path does not exist: {model_path}")
        return False

    print(f"✓ Model path exists: {model_path}")

    # Try to generate a test avatar
    print("\nGenerating test avatar...")
    test_prompt = "cute robot character"
    avatar_url = generator.generate_avatar("test_agent", test_prompt)

    print(f"Generated avatar URL: {avatar_url}")

    # Check if it's a real file or fallback
    if avatar_url.startswith("data:image/svg"):
        print("⚠️  Fallback avatar was used (mflux may not have run successfully)")
    elif avatar_url.startswith("/static/avatars/"):
        output_file = generator.output_dir / "test_agent.png"
        if output_file.exists():
            print(f"✓ Avatar file created successfully: {output_file}")
            print(f"  File size: {output_file.stat().st_size} bytes")
            return True
        else:
            print(f"❌ Avatar URL returned but file not found: {output_file}")
            return False

    return False

if __name__ == "__main__":
    success = test_avatar_generator()
    sys.exit(0 if success else 1)
