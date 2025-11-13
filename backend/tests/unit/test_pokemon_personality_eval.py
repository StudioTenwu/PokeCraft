"""
Tests for Pokémon personality assessment Inspect AI tasks.

Following TDD: Write tests before implementation.
Testing TIPI-10 and IPIP-50 Big Five personality assessments.
"""

import pytest
from inspect_ai import Task
from inspect_ai.dataset import Sample


class TestTIPITask:
    """Tests for TIPI-10 (Ten-Item Personality Inventory) task creation."""

    def test_pokemon_personality_tipi_creates_valid_task(self):
        """
        RED: Test that pokemon_personality_tipi() creates a valid Inspect AI Task.

        Expected:
        - Should return an inspect_ai.Task object
        - Task should have 10 samples (one per TIPI question)
        - Each sample should have proper input and target structure
        """
        from src.evals.pokemon_personality_eval import pokemon_personality_tipi

        task = pokemon_personality_tipi()

        # Should return a Task object
        assert isinstance(task, Task)

        # Task should have a dataset with 10 samples
        assert len(task.dataset) == 10

        # First sample should be properly structured
        first_sample = task.dataset[0]
        assert isinstance(first_sample, Sample)
        assert first_sample.input is not None
        assert first_sample.metadata is not None

    def test_tipi_samples_have_correct_structure(self):
        """
        RED: Test that TIPI samples have the correct Big Five structure.

        Expected:
        - Each sample input should contain the rating scale (1-7)
        - Each sample target should specify dimension and reverse scoring info
        """
        from src.evals.pokemon_personality_eval import pokemon_personality_tipi

        task = pokemon_personality_tipi()
        first_sample = task.dataset[0]

        # Input should mention 7-point scale
        assert "1" in first_sample.input
        assert "7" in first_sample.input

        # Metadata should have dimension info
        assert "dimension" in first_sample.metadata
        assert first_sample.metadata["dimension"] in [
            "Extraversion",
            "Agreeableness",
            "Conscientiousness",
            "Neuroticism",
            "Openness",
        ]

    def test_tipi_question_1_is_extraversion(self):
        """
        RED: Test that the first TIPI question tests Extraversion.

        Expected:
        - First question should be "Extraverted, enthusiastic."
        - Should map to Extraversion dimension
        - Should not be reverse-scored
        """
        from src.evals.pokemon_personality_eval import pokemon_personality_tipi

        task = pokemon_personality_tipi()
        first_sample = task.dataset[0]

        # Should mention "Extraverted, enthusiastic"
        assert "extraverted" in first_sample.input.lower() or "extravert" in first_sample.input.lower()
        assert "enthusiastic" in first_sample.input.lower()

        # Metadata should specify Extraversion
        assert first_sample.metadata["dimension"] == "Extraversion"
        assert first_sample.metadata.get("reverse_scored", False) is False

    def test_tipi_has_reverse_scored_items(self):
        """
        RED: Test that TIPI includes reverse-scored items.

        Expected:
        - Items 2, 6, 8, 10 should be marked as reverse_scored: True
        - Items 1, 3, 4, 5, 7, 9 should be reverse_scored: False
        """
        from src.evals.pokemon_personality_eval import pokemon_personality_tipi

        task = pokemon_personality_tipi()

        # Item 2 ("Critical, quarrelsome") should be reverse-scored
        item_2 = task.dataset[1]
        assert item_2.metadata.get("reverse_scored", False) is True

        # Item 6 ("Reserved, quiet") should be reverse-scored
        item_6 = task.dataset[5]
        assert item_6.metadata.get("reverse_scored", False) is True


class TestIPIP50Task:
    """Tests for IPIP-50 Big Five Markers task creation."""

    def test_pokemon_personality_ipip50_creates_valid_task(self):
        """
        RED: Test that pokemon_personality_ipip50() creates a valid Inspect AI Task.

        Expected:
        - Should return an inspect_ai.Task object
        - Task should have 50 samples (one per IPIP-50 question)
        """
        from src.evals.pokemon_personality_eval import pokemon_personality_ipip50

        task = pokemon_personality_ipip50()

        # Should return a Task object
        assert isinstance(task, Task)

        # Task should have 50 samples
        assert len(task.dataset) == 50

    def test_ipip50_samples_use_5point_scale(self):
        """
        RED: Test that IPIP-50 samples use 5-point scale.

        Expected:
        - Each sample input should mention 1-5 scale
        - Scale should be "Very Inaccurate" to "Very Accurate"
        """
        from src.evals.pokemon_personality_eval import pokemon_personality_ipip50

        task = pokemon_personality_ipip50()
        first_sample = task.dataset[0]

        # Input should mention 5-point scale
        assert "1" in first_sample.input
        assert "5" in first_sample.input

        # Should mention accuracy scale
        input_lower = first_sample.input.lower()
        assert "inaccurate" in input_lower or "accurate" in input_lower

    def test_ipip50_covers_all_five_dimensions(self):
        """
        RED: Test that IPIP-50 covers all Big Five dimensions evenly.

        Expected:
        - Should have 10 items per dimension
        - All 5 dimensions represented
        """
        from src.evals.pokemon_personality_eval import pokemon_personality_ipip50

        task = pokemon_personality_ipip50()

        # Count items per dimension
        dimension_counts = {}
        for sample in task.dataset:
            dim = sample.metadata["dimension"]
            dimension_counts[dim] = dimension_counts.get(dim, 0) + 1

        # Should have all 5 dimensions
        assert len(dimension_counts) == 5

        # Each dimension should have exactly 10 items
        for dim, count in dimension_counts.items():
            assert count == 10, f"{dim} has {count} items, expected 10"


class TestBigFiveScorer:
    """Tests for Big Five scoring logic."""

    def test_big_five_scorer_exists(self):
        """
        RED: Test that big_five_scorer function exists and is callable.

        Expected:
        - Function should exist
        - Should be a valid Inspect AI scorer
        """
        from src.evals.pokemon_personality_eval import big_five_scorer

        scorer = big_five_scorer()
        assert scorer is not None

    def test_scorer_extracts_numeric_rating(self):
        """
        RED: Test that scorer can extract numeric rating from agent response.

        Expected:
        - Should handle "7" -> 7.0
        - Should handle "I would rate myself a 6" -> 6.0
        - Should handle "Rating: 4" -> 4.0
        """
        from src.evals.pokemon_personality_eval import extract_rating

        # Simple number
        assert extract_rating("7") == 7.0

        # Embedded in text
        assert extract_rating("I would rate myself a 6") == 6.0

        # With label
        assert extract_rating("Rating: 4") == 4.0

    def test_scorer_calculates_dimension_scores(self):
        """
        RED: Test that scorer calculates Big Five dimension scores correctly.

        Expected:
        - Given 10 ratings for TIPI, should output 5 dimension scores
        - Each score should be 1.0-7.0 for TIPI
        - Should handle reverse scoring
        """
        from src.evals.pokemon_personality_eval import calculate_tipi_scores

        # Example: all items rated 5 (middle)
        ratings = {i: 5.0 for i in range(1, 11)}

        scores = calculate_tipi_scores(ratings)

        # Should have all 5 dimensions
        assert len(scores) == 5
        assert "Extraversion" in scores
        assert "Agreeableness" in scores
        assert "Conscientiousness" in scores
        assert "Neuroticism" in scores
        assert "Openness" in scores

        # All scores should be in valid range
        for dim, score in scores.items():
            assert 1.0 <= score <= 7.0

    def test_reverse_scoring_applied_correctly(self):
        """
        RED: Test that reverse scoring is applied correctly.

        Expected:
        - Item rated 7 when reverse=True should become 1
        - Item rated 1 when reverse=True should become 7
        - Formula: reversed = (scale_max + 1) - original
        """
        from src.evals.pokemon_personality_eval import reverse_score

        # For 7-point scale (TIPI)
        assert reverse_score(7, scale_max=7) == 1
        assert reverse_score(1, scale_max=7) == 7
        assert reverse_score(4, scale_max=7) == 4  # Middle stays middle

        # For 5-point scale (IPIP-50)
        assert reverse_score(5, scale_max=5) == 1
        assert reverse_score(1, scale_max=5) == 5
        assert reverse_score(3, scale_max=5) == 3
