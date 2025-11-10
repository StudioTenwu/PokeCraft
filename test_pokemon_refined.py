#!/usr/bin/env python3
"""Test refined Pokemon hand-drawn prompts (shorter to avoid timeouts)."""

import sys
from pathlib import Path

# Add backend/src to path
sys.path.insert(0, str(Path(__file__).parent / "backend" / "src"))

from avatar_generator import AvatarGenerator

# Refined shorter prompts focusing on hand-drawn Pokemon aesthetic
REFINED_PROMPTS = {
    "poke_handdrawn_v1": "Ken Sugimori official Pokemon art, hand-drawn watercolor, vibrant colors, frontal view, cute friendly",

    "poke_handdrawn_v2": "Pokemon anime cel animation style, soft rounded shapes, big eyes, pastel colors, frontal portrait",

    "poke_handdrawn_v3": "Pokemon card illustration, hand-painted digital art, vibrant colors, centered composition",

    "poke_handdrawn_v4": "hand-drawn Pokemon watercolor, soft brushstrokes, gentle gradients, kawaii cute, frontal",

    "poke_handdrawn_v5": "Pokemon concept sketch, hand-drawn linework, soft cel shading, adorable, warm colors",

    "poke_handdrawn_v6": "storybook Pokemon illustration, hand-painted gouache, soft edges, gentle friendly aesthetic",

    "poke_handdrawn_v7": "retro Pokemon 90s art, hand-drawn organic feel, soft colors, cute rounded character",

    "poke_handdrawn_v8": "modern Pokemon illustration, hand-drawn digital painting, smooth cheerful colors, frontal",
}

def test_prompt_variation(generator, variation_name, enhancement_prompt, base_prompt="cute friendly creature character"):
    """Test a single prompt variation and generate an avatar."""
    print(f"\n{'='*60}")
    print(f"Testing: {variation_name}")
    print(f"{'='*60}")

    output_path = generator.output_dir / f"{variation_name}.png"
    enhanced_prompt = f"{base_prompt}, {enhancement_prompt}"

    import subprocess

    try:
        cmd = [
            "mflux-generate",
            "--model", "schnell",
            "--path", generator.model_path,
            "--prompt", enhanced_prompt,
            "--steps", "2",
            "--output", str(output_path)
        ]

        print(f"Prompt: {enhanced_prompt}")
        print(f"Generating...")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=90
        )

        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return None

        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f"✓ Success! Size: {file_size} bytes")
            return f"/static/avatars/{variation_name}.png"
        else:
            print(f"❌ File not created")
            return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("🎨 Refined Pokemon Hand-Drawn Style Testing")
    print("="*60)

    generator = AvatarGenerator()

    # Verify model exists
    model_path = Path(generator.model_path)
    if not model_path.exists():
        print(f"❌ ERROR: Model path does not exist: {model_path}")
        return False

    print(f"✓ Model: {model_path}")
    print(f"✓ Output: {generator.output_dir}\n")

    # Test each variation
    results = {}
    for var_name, enhancement in REFINED_PROMPTS.items():
        result = test_prompt_variation(generator, var_name, enhancement)
        results[var_name] = result

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    successes = [k for k, v in results.items() if v]
    failures = [k for k, v in results.items() if not v]

    print(f"✓ Successful: {len(successes)}/8")
    for name in successes:
        print(f"  - {name}")

    if failures:
        print(f"\n❌ Failed: {len(failures)}/8")
        for name in failures:
            print(f"  - {name}")

    print(f"\n📁 Check: {generator.output_dir}")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
