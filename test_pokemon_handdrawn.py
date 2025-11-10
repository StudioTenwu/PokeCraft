#!/usr/bin/env python3
"""Test hand-drawn cute Pokemon-style avatar prompts."""

import sys
from pathlib import Path

# Add backend/src to path
sys.path.insert(0, str(Path(__file__).parent / "backend" / "src"))

from avatar_generator import AvatarGenerator

# Pokemon-inspired hand-drawn style prompts
POKEMON_HANDDRAWN_PROMPTS = {
    "pokemon_v1_sugimori": "Ken Sugimori art style, official Pokemon artwork, hand-drawn illustration, soft watercolor, vibrant colors, friendly cute character, frontal view, clean white background",

    "pokemon_v2_anime": "Pokemon anime style, hand-painted cel animation, soft rounded shapes, big expressive eyes, cute and friendly, frontal portrait, pastel colors, wholesome aesthetic",

    "pokemon_v3_card": "Pokemon trading card illustration, hand-drawn digital art, glossy finish, vibrant saturated colors, cute character design, centered composition, professional game art",

    "pokemon_v4_watercolor": "cute Pokemon-style creature, hand-drawn watercolor illustration, soft brush strokes, gentle color gradients, friendly expression, frontal view, light background, kawaii aesthetic",

    "pokemon_v5_sketch": "Pokemon concept art style, hand-drawn character sketch with color, clean linework, soft shading, adorable features, facing forward, warm friendly colors, illustrated feel",

    "pokemon_v6_storybook": "children's storybook illustration, Pokemon-inspired character, hand-painted gouache style, soft edges, warm colors, cute and approachable, frontal portrait, gentle aesthetic",

    "pokemon_v7_retro_organic": "retro Pokemon Red/Blue official art style, hand-drawn with organic feel, soft cel-shaded colors, cute rounded character, friendly face, centered frontal view, nostalgic 90s illustration",

    "pokemon_v8_modern_handdrawn": "modern Pokemon Scarlet/Violet style, hand-illustrated digital painting, smooth gradients, vibrant cheerful colors, adorable character, direct frontal view, clean polished artwork",
}

def test_prompt_variation(generator, variation_name, enhancement_prompt, base_prompt="cute friendly creature"):
    """Test a single prompt variation and generate an avatar."""
    print(f"\n{'='*60}")
    print(f"Testing: {variation_name}")
    print(f"Enhancement: {enhancement_prompt}")
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
            return f"/static/avatars/{variation_name}.png"
        else:
            print(f"❌ Output file not created")
            return generator._get_fallback_avatar()

    except Exception as e:
        print(f"❌ Error: {e}")
        return generator._get_fallback_avatar()

def main():
    print("🎨 Pokemon Hand-Drawn Style Avatar Testing")
    print("="*60)

    generator = AvatarGenerator()

    # Verify model exists
    model_path = Path(generator.model_path)
    if not model_path.exists():
        print(f"❌ ERROR: Model path does not exist: {model_path}")
        return False

    print(f"✓ Model path: {model_path}")
    print(f"✓ Output directory: {generator.output_dir}\n")

    # Test each variation
    results = {}
    for var_name, enhancement in POKEMON_HANDDRAWN_PROMPTS.items():
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
    print("\nCompare the images to choose which hand-drawn Pokemon style works best!")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
