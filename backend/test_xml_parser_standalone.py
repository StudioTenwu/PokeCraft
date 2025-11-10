"""
Standalone test for XML parsing logic.
Tests the _parse_xml_output method without requiring claude_agent_sdk.
"""
import json
import re
import xml.etree.ElementTree as ET


def parse_xml_output(response_text: str) -> dict:
    """
    Parse JSON from XML-wrapped output using XML parser.

    Expects format: <output>{json}</output>

    Args:
        response_text: The raw response containing XML-wrapped JSON

    Returns:
        Parsed JSON as dict

    Raises:
        ValueError: If no valid <output> tag is found or JSON is invalid
    """
    try:
        # Strip whitespace and wrap in root element if needed
        response_text = response_text.strip()
        if not response_text.startswith('<'):
            response_text = f"<root>{response_text}</root>"

        # Parse XML using ElementTree
        root = ET.fromstring(response_text)

        # Find the output element - check if root is already 'output'
        if root.tag == 'output':
            output_element = root
        else:
            output_element = root.find('.//output')

        if output_element is None:
            raise ValueError("No <output> tag found in response")

        # ElementTree may split text content, so we need to get all text
        # Use itertext() to get all text content including from child elements
        json_content = ''.join(output_element.itertext()).strip()

        if not json_content:
            raise ValueError("<output> tag is empty")

        print(f"[INFO] Found JSON in <output> tag")

        # Clean up markdown code blocks if present
        json_content = re.sub(r'```json\s*', '', json_content)
        json_content = re.sub(r'```\s*', '', json_content)
        json_content = json_content.strip()

        # Parse JSON
        try:
            data = json.loads(json_content)
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in <output> tag: {e}")

    except ET.ParseError as e:
        raise ValueError(f"XML parsing failed: {e}. Response must contain valid <output> tag.")


# Example 1: Clean XML-wrapped response
def test_example_1_clean_xml():
    """
    Example 1: Clean XML-wrapped JSON (ideal case)

    This is the expected format from the LLM when it follows instructions.
    """
    response = """
    <output>
    {
        "name": "Sparkle",
        "backstory": "Born in a digital meadow, Sparkle loves to explore and help friends solve puzzles. With a heart full of curiosity, this little companion brings joy wherever it goes.",
        "personality_traits": ["curious", "playful", "helpful"],
        "avatar_prompt": "cute electric mouse pokemon-style creature, yellow fur with rosy cheeks, large expressive eyes, Game Boy Color pixel art style, 16-bit retro aesthetic, colorful and cheerful"
    }
    </output>
    """

    try:
        result = parse_xml_output(response)
        print("✅ Example 1 PASSED - Clean XML parsing")
        print(f"   Name: {result['name']}")
        print(f"   Traits: {', '.join(result['personality_traits'])}")
        print(f"   Backstory: {result['backstory'][:60]}...")
        print()
        return True
    except Exception as e:
        print(f"❌ Example 1 FAILED: {e}")
        print()
        return False


# Example 2: Messy response with markdown and extra text
def test_example_2_messy_response():
    """
    Example 2: Messy response with markdown blocks and extra text

    This simulates when the LLM adds extra commentary or markdown formatting
    despite instructions to use clean XML.
    """
    response = """
    Here's your AI companion! I've created it based on your description.

    <output>
    ```json
    {
        "name": "Bubbles",
        "backstory": "Found floating in a crystal stream, Bubbles is a gentle water companion who loves to splash and play. This bubbly friend helps others stay calm and find creative solutions.",
        "personality_traits": ["gentle", "creative", "calming"],
        "avatar_prompt": "adorable water-type pokemon creature, blue rounded body with bubble patterns, big friendly eyes, Game Boy Color style pixel art, retro 16-bit aesthetic, aquatic theme with water droplets"
    }
    ```
    </output>

    I hope you like it! The avatar should look great in retro style.
    """

    try:
        result = parse_xml_output(response)
        print("✅ Example 2 PASSED - Messy response with markdown parsing")
        print(f"   Name: {result['name']}")
        print(f"   Traits: {', '.join(result['personality_traits'])}")
        print(f"   Backstory: {result['backstory'][:60]}...")
        print()
        return True
    except Exception as e:
        print(f"❌ Example 2 FAILED: {e}")
        print()
        return False


# Example 3: Malformed response (should fail gracefully)
def test_example_3_malformed():
    """
    Example 3: Malformed response that should fail

    This tests the parser's error handling when given invalid input.
    """
    response = """
    <output>
    This is not valid JSON at all!
    Just some random text.
    </output>
    """

    try:
        result = parse_xml_output(response)
        print("❌ Example 3 UNEXPECTED: Should have failed but parsed something")
        print()
        return False
    except ValueError as e:
        print("✅ Example 3 PASSED - Correctly failed on invalid input")
        print(f"   Error: {str(e)[:80]}...")
        print()
        return True


if __name__ == "__main__":
    print("=" * 70)
    print("XML-Based LLM Client Parser - Test Examples")
    print("=" * 70)
    print()

    results = []

    print("Running tests...\n")
    results.append(test_example_1_clean_xml())
    results.append(test_example_2_messy_response())
    results.append(test_example_3_malformed())

    print("=" * 70)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 70)
