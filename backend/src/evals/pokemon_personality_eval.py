"""
Pokémon Personality Assessment using Inspect AI.

Implements TIPI-10 and IPIP-50 Big Five personality tests for Pokémon agents.
Tests the agent's own personality, not the human user.

Uses validated instruments from academic literature:
- TIPI-10: Gosling, Rentfrow, & Swann (2003)
- IPIP-50: Goldberg (1999)
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import Score, Scorer, Target, scorer
from inspect_ai.solver import generate

# TIPI-10 Questions (7-point scale)
TIPI_QUESTIONS = [
    {
        "text": "Extraverted, enthusiastic.",
        "dimension": "Extraversion",
        "reverse_scored": False,
        "item_number": 1,
    },
    {
        "text": "Critical, quarrelsome.",
        "dimension": "Agreeableness",
        "reverse_scored": True,
        "item_number": 2,
    },
    {
        "text": "Dependable, self-disciplined.",
        "dimension": "Conscientiousness",
        "reverse_scored": False,
        "item_number": 3,
    },
    {
        "text": "Anxious, easily upset.",
        "dimension": "Neuroticism",
        "reverse_scored": False,
        "item_number": 4,
    },
    {
        "text": "Open to new experiences, complex.",
        "dimension": "Openness",
        "reverse_scored": False,
        "item_number": 5,
    },
    {
        "text": "Reserved, quiet.",
        "dimension": "Extraversion",
        "reverse_scored": True,
        "item_number": 6,
    },
    {
        "text": "Sympathetic, warm.",
        "dimension": "Agreeableness",
        "reverse_scored": False,
        "item_number": 7,
    },
    {
        "text": "Disorganized, careless.",
        "dimension": "Conscientiousness",
        "reverse_scored": True,
        "item_number": 8,
    },
    {
        "text": "Calm, emotionally stable.",
        "dimension": "Neuroticism",
        "reverse_scored": True,
        "item_number": 9,
    },
    {
        "text": "Conventional, uncreative.",
        "dimension": "Openness",
        "reverse_scored": True,
        "item_number": 10,
    },
]


def create_tipi_samples() -> list[Sample]:
    """Create TIPI-10 samples for Inspect AI."""
    samples = []

    for q in TIPI_QUESTIONS:
        input_text = f"""Rate how well this describes you on a scale of 1-7:
(1=Disagree strongly, 7=Agree strongly)

I see myself as: {q['text']}

Think about your natural personality, your backstory, and how you typically behave.
What rating feels most accurate? Give a single number from 1 to 7.

For the output, please provide only the numeric rating.

Wrap in <rating> tags like this:
<rating>YOUR_NUMBER_HERE</rating>
"""

        sample = Sample(
            input=input_text,
            target="",  # No ground truth for personality assessment
            metadata={
                "dimension": q["dimension"],
                "item_number": q["item_number"],
                "reverse_scored": q["reverse_scored"],
            },
        )
        samples.append(sample)

    return samples


@task
def pokemon_personality_tipi() -> Task:
    """
    TIPI-10 (Ten-Item Personality Inventory) Big Five assessment.

    Time: ~1 minute
    Scale: 7-point (1=Disagree strongly, 7=Agree strongly)
    Items: 10 questions (2 per Big Five dimension)

    The Pokémon agent answers questions about itself.
    """
    return Task(
        dataset=create_tipi_samples(),
        solver=[generate()],
        scorer=big_five_scorer(),
    )


# IPIP-50 Questions (5-point scale)
IPIP50_QUESTIONS = [
    # Extraversion (10 items)
    {
        "text": "Am the life of the party.",
        "dimension": "Extraversion",
        "reverse": False,
        "num": 1,
    },
    {
        "text": "Don't talk a lot.",
        "dimension": "Extraversion",
        "reverse": True,
        "num": 6,
    },
    {
        "text": "Feel comfortable around people.",
        "dimension": "Extraversion",
        "reverse": False,
        "num": 11,
    },
    {
        "text": "Keep in the background.",
        "dimension": "Extraversion",
        "reverse": True,
        "num": 16,
    },
    {
        "text": "Start conversations.",
        "dimension": "Extraversion",
        "reverse": False,
        "num": 21,
    },
    {
        "text": "Have little to say.",
        "dimension": "Extraversion",
        "reverse": True,
        "num": 26,
    },
    {
        "text": "Talk to a lot of different people at parties.",
        "dimension": "Extraversion",
        "reverse": False,
        "num": 31,
    },
    {
        "text": "Don't like to draw attention to myself.",
        "dimension": "Extraversion",
        "reverse": True,
        "num": 36,
    },
    {
        "text": "Don't mind being the center of attention.",
        "dimension": "Extraversion",
        "reverse": False,
        "num": 41,
    },
    {
        "text": "Am quiet around strangers.",
        "dimension": "Extraversion",
        "reverse": True,
        "num": 46,
    },
    # Agreeableness (10 items)
    {
        "text": "Feel little concern for others.",
        "dimension": "Agreeableness",
        "reverse": True,
        "num": 2,
    },
    {
        "text": "Am interested in people.",
        "dimension": "Agreeableness",
        "reverse": False,
        "num": 7,
    },
    {
        "text": "Insult people.",
        "dimension": "Agreeableness",
        "reverse": True,
        "num": 12,
    },
    {
        "text": "Sympathize with others' feelings.",
        "dimension": "Agreeableness",
        "reverse": False,
        "num": 17,
    },
    {
        "text": "Am not interested in other people's problems.",
        "dimension": "Agreeableness",
        "reverse": True,
        "num": 22,
    },
    {
        "text": "Have a soft heart.",
        "dimension": "Agreeableness",
        "reverse": False,
        "num": 27,
    },
    {
        "text": "Am not really interested in others.",
        "dimension": "Agreeableness",
        "reverse": True,
        "num": 32,
    },
    {
        "text": "Take time out for others.",
        "dimension": "Agreeableness",
        "reverse": False,
        "num": 37,
    },
    {
        "text": "Feel others' emotions.",
        "dimension": "Agreeableness",
        "reverse": False,
        "num": 42,
    },
    {
        "text": "Make people feel at ease.",
        "dimension": "Agreeableness",
        "reverse": False,
        "num": 47,
    },
    # Conscientiousness (10 items)
    {
        "text": "Am always prepared.",
        "dimension": "Conscientiousness",
        "reverse": False,
        "num": 3,
    },
    {
        "text": "Leave my belongings around.",
        "dimension": "Conscientiousness",
        "reverse": True,
        "num": 8,
    },
    {
        "text": "Pay attention to details.",
        "dimension": "Conscientiousness",
        "reverse": False,
        "num": 13,
    },
    {
        "text": "Make a mess of things.",
        "dimension": "Conscientiousness",
        "reverse": True,
        "num": 18,
    },
    {
        "text": "Get chores done right away.",
        "dimension": "Conscientiousness",
        "reverse": False,
        "num": 23,
    },
    {
        "text": "Often forget to put things back in their proper place.",
        "dimension": "Conscientiousness",
        "reverse": True,
        "num": 28,
    },
    {
        "text": "Like order.",
        "dimension": "Conscientiousness",
        "reverse": False,
        "num": 33,
    },
    {
        "text": "Shirk my duties.",
        "dimension": "Conscientiousness",
        "reverse": True,
        "num": 38,
    },
    {
        "text": "Follow a schedule.",
        "dimension": "Conscientiousness",
        "reverse": False,
        "num": 43,
    },
    {
        "text": "Am exacting in my work.",
        "dimension": "Conscientiousness",
        "reverse": False,
        "num": 48,
    },
    # Neuroticism (10 items)
    {
        "text": "Get stressed out easily.",
        "dimension": "Neuroticism",
        "reverse": False,
        "num": 4,
    },
    {
        "text": "Am relaxed most of the time.",
        "dimension": "Neuroticism",
        "reverse": True,
        "num": 9,
    },
    {
        "text": "Worry about things.",
        "dimension": "Neuroticism",
        "reverse": False,
        "num": 14,
    },
    {
        "text": "Seldom feel blue.",
        "dimension": "Neuroticism",
        "reverse": True,
        "num": 19,
    },
    {
        "text": "Am easily disturbed.",
        "dimension": "Neuroticism",
        "reverse": False,
        "num": 24,
    },
    {
        "text": "Get upset easily.",
        "dimension": "Neuroticism",
        "reverse": False,
        "num": 29,
    },
    {
        "text": "Change my mood a lot.",
        "dimension": "Neuroticism",
        "reverse": False,
        "num": 34,
    },
    {
        "text": "Have frequent mood swings.",
        "dimension": "Neuroticism",
        "reverse": False,
        "num": 39,
    },
    {
        "text": "Get irritated easily.",
        "dimension": "Neuroticism",
        "reverse": False,
        "num": 44,
    },
    {
        "text": "Often feel blue.",
        "dimension": "Neuroticism",
        "reverse": False,
        "num": 49,
    },
    # Openness (10 items)
    {
        "text": "Have a rich vocabulary.",
        "dimension": "Openness",
        "reverse": False,
        "num": 5,
    },
    {
        "text": "Have difficulty understanding abstract ideas.",
        "dimension": "Openness",
        "reverse": True,
        "num": 10,
    },
    {
        "text": "Have a vivid imagination.",
        "dimension": "Openness",
        "reverse": False,
        "num": 15,
    },
    {
        "text": "Am not interested in abstract ideas.",
        "dimension": "Openness",
        "reverse": True,
        "num": 20,
    },
    {
        "text": "Have excellent ideas.",
        "dimension": "Openness",
        "reverse": False,
        "num": 25,
    },
    {
        "text": "Do not have a good imagination.",
        "dimension": "Openness",
        "reverse": True,
        "num": 30,
    },
    {
        "text": "Am quick to understand things.",
        "dimension": "Openness",
        "reverse": False,
        "num": 35,
    },
    {
        "text": "Use difficult words.",
        "dimension": "Openness",
        "reverse": False,
        "num": 40,
    },
    {
        "text": "Spend time reflecting on things.",
        "dimension": "Openness",
        "reverse": False,
        "num": 45,
    },
    {"text": "Am full of ideas.", "dimension": "Openness", "reverse": False, "num": 50},
]


def create_ipip50_samples() -> list[Sample]:
    """Create IPIP-50 samples for Inspect AI."""
    samples = []

    for q in IPIP50_QUESTIONS:
        input_text = f"""Rate how accurately this describes you on a scale of 1-5:
(1=Very Inaccurate, 5=Very Accurate)

I {q['text']}

Think about your personality and how you typically behave.
Give a single number from 1 to 5."""

        sample = Sample(
            input=input_text,
            target="",  # No ground truth for personality assessment
            metadata={
                "dimension": q["dimension"],
                "item_number": q["num"],
                "reverse_scored": q["reverse"],
            },
        )
        samples.append(sample)

    return samples


@task
def pokemon_personality_ipip50() -> Task:
    """
    IPIP-50 Big Five Markers assessment.

    Time: ~5 minutes
    Scale: 5-point (1=Very Inaccurate, 5=Very Accurate)
    Items: 50 questions (10 per Big Five dimension)

    The Pokémon agent answers questions about itself.
    """
    return Task(
        dataset=create_ipip50_samples(),
        solver=[generate()],
        scorer=big_five_scorer(),
    )


# Scoring functions
def reverse_score(rating: float, scale_max: int) -> float:
    """
    Reverse score an item.

    Formula: (scale_max + 1) - original
    Example (7-point): 7 becomes 1, 1 becomes 7
    """
    return float((scale_max + 1) - rating)


def extract_rating(response: str) -> float:
    """
    Extract numeric rating from agent response using proper XML parsing.

    Handles:
    - XML format: "<rating>7</rating>" -> 7.0
    - Fallback to regex for non-XML responses
    - Simple numbers: "7" -> 7.0
    - Embedded: "I would rate myself a 6" -> 6.0

    Uses xml.etree.ElementTree for safe, efficient XML parsing.
    Falls back to regex if XML parsing fails.
    """
    import re
    import xml.etree.ElementTree as ET

    # Try XML parsing first (preferred format)
    try:
        # Wrap in root element if not already XML-formatted
        if "<rating>" in response:
            # Extract the rating tag content
            xml_text = response
            if not xml_text.strip().startswith("<"):
                # Find and extract just the <rating> tag
                start = response.find("<rating>")
                end = response.find("</rating>") + len("</rating>")
                xml_text = response[start:end]

            # Parse the XML
            root = ET.fromstring(xml_text)
            rating_text = root.text.strip()
            rating = float(rating_text)

            # Validate rating is in reasonable range (1-10)
            if 1 <= rating <= 10:
                return rating
    except (ET.ParseError, ValueError, AttributeError):
        # XML parsing failed, fall through to regex
        pass

    # Fallback: Try to find a number in the response using regex
    numbers = re.findall(r"\b([1-9]|10)\b", response)
    if numbers:
        return float(numbers[0])

    # Ultimate fallback: middle of 7-point scale
    return 4.0


def calculate_tipi_scores(ratings: dict[int, float]) -> dict[str, float]:
    """
    Calculate Big Five scores from TIPI-10 ratings.

    Args:
        ratings: Dict mapping item_number (1-10) to rating (1.0-7.0)

    Returns:
        Dict with 5 dimension scores (1.0-7.0 range)

    Scoring:
    - Extraversion: (Item 1 + [8 - Item 6]) / 2
    - Agreeableness: ([8 - Item 2] + Item 7) / 2
    - Conscientiousness: (Item 3 + [8 - Item 8]) / 2
    - Neuroticism: ([8 - Item 4] + Item 9) / 2
    - Openness: (Item 5 + [8 - Item 10]) / 2
    """
    return {
        "Extraversion": (ratings[1] + reverse_score(ratings[6], 7)) / 2,
        "Agreeableness": (reverse_score(ratings[2], 7) + ratings[7]) / 2,
        "Conscientiousness": (ratings[3] + reverse_score(ratings[8], 7)) / 2,
        "Neuroticism": (reverse_score(ratings[4], 7) + ratings[9]) / 2,
        "Openness": (ratings[5] + reverse_score(ratings[10], 7)) / 2,
    }


@scorer(
    metrics=[
        "extraversion",
        "agreeableness",
        "conscientiousness",
        "neuroticism",
        "openness",
    ],
)
def big_five_scorer() -> Scorer:
    """
    Scorer for Big Five personality assessment.

    Extracts ratings from agent responses and calculates dimension scores.
    """

    async def score(state: any, _target: Target) -> Score:
        """Score a single item response."""
        # Extract rating from agent's last message
        if not state.messages:
            return Score(value=0.0)

        last_message = state.messages[-1]
        response = (
            last_message.text
            if hasattr(last_message, "text")
            else str(last_message.content)
        )

        rating = extract_rating(response)

        # For now, just return the rating as the score
        # Full scoring will aggregate across all items
        return Score(value=rating)

    return score
