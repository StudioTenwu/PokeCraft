#!/usr/bin/env python3
"""Test different prompt variations for avatar generation to find the best retro aesthetic."""

import sys
from pathlib import Path

# Add backend/src to path
sys.path.insert(0, str(Path(__file__).parent / "backend" / "src"))

from avatar_generator import AvatarGenerator

# Different prompt enhancement strategies to test
PROMPT_VARIATIONS = {
    "v1_current": "Game Boy Color style, retro pixel art, colorful, nostalgic 90s gaming aesthetic",

    "v2_frontal_retro": "frontal view portrait, retro pixel art style, 16-bit era, vibrant colors, character sprite, centered composition, clean background",

    "v3_cool_retro": "super cool character portrait, frontal view, 90s retro aesthetic, pixel art vibes, bold colors, facing camera directly, iconic pose",

    "v4_vintage_game": "vintage video game character, face forward, retro gaming art style, pixel-inspired, colorful palette, easy to read silhouette, centered portrait",

    "v5_modern_retro": "modern pixel art style, frontal character portrait, retro-futuristic, vibrant neon colors, clean geometric shapes, perfectly centered, cool and stylish",

    "v6_simple_retro": "simple retro character design, direct frontal view, flat colors, 80s-90s aesthetic, bold outlines, minimalist cool style, head-on perspective",

    "v7_pokemon_style": "Pokemon trading card art style, frontal character view, retro gaming aesthetic, bright colors, friendly and approachable, clean composition",

    "v8_arcade_style": "retro arcade game character, straight-on frontal view, 16-bit pixel art aesthetic, vibrant color palette, iconic character design, perfectly centered",
}

def test_prompt_variation(generator, variation_name, enhancement_prompt, base_prompt="cute robot character"):
    """Test a single prompt variation and generate an avatar."""
    print(f"\n{'='*60}")
    print(f"Testing: {variation_name}")
    print(f"Enhancement: {enhancement_prompt}")
    print(f"{'='*60}")

    # Temporarily modify the generator's enhancement
    original_generate = generator.generate_avatar

    def custom_generate(agent_id, prompt):
        output_path = generator.output_dir / f"{agent_id}.png"
        enhanced_prompt = f"{prompt}, {enhancement_prompt}"

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

            print(f"Full prompt: {enhanced_prompt}")
            print(f"Running mflux...")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                print(f"❌ mflux error: {result.stderr}")
                return generator._get_fallback_avatar()

            if output_path.exists():
                file_size = output_path.stat().st_size
                print(f"✓ Generated successfully: {output_path}")
                print(f"  File size: {file_size} bytes")
                return f"/static/avatars/{agent_id}.png"
            else:
                print(f"❌ Output file not created")
                return generator._get_fallback_avatar()

        except Exception as e:
            print(f"❌ Error: {e}")
            return generator._get_fallback_avatar()

    # Generate with custom enhancement
    generator.generate_avatar = custom_generate
    avatar_url = generator.generate_avatar(f"test_{variation_name}", base_prompt)
    generator.generate_avatar = original_generate

    return avatar_url

def main():
    print("Avatar Prompt Testing Suite")
    print("Testing different prompt variations for retro aesthetic avatars\n")

    generator = AvatarGenerator()

    # Verify model exists
    model_path = Path(generator.model_path)
    if not model_path.exists():
        print(f"❌ ERROR: Model path does not exist: {model_path}")
        print("Please ensure mflux model is installed at ~/.AICraft/models/schnell-3bit")
        return False

    print(f"✓ Model path: {model_path}")
    print(f"✓ Output directory: {generator.output_dir}\n")

    # Test each variation
    results = {}
    for var_name, enhancement in PROMPT_VARIATIONS.items():
        result = test_prompt_variation(generator, var_name, enhancement)
        results[var_name] = result

    # Summary
    print("\n" + "="*60)
    print("SUMMARY OF RESULTS")
    print("="*60)

    for var_name, result_url in results.items():
        status = "✓ SUCCESS" if result_url.startswith("/static/avatars/") else "❌ FALLBACK"
        print(f"{var_name}: {status}")

    print("\n" + "="*60)
    print("OUTPUT FILES LOCATION")
    print("="*60)
    print(f"Check generated avatars in: {generator.output_dir}")
    print("Files will be named: test_v1_current.png, test_v2_frontal_retro.png, etc.")
    print("\nCompare the images to choose which prompt style works best!")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
