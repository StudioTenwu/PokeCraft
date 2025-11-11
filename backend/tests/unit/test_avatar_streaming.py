import pytest
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from avatar_generator import parse_mflux_progress, map_mflux_to_overall


# Test pure function: parse_mflux_progress
def test_parse_mflux_progress_valid_lines():
    """Test parsing valid mflux progress lines."""
    assert parse_mflux_progress("0%|          | 0/2 [00:00<?, ?it/s]") == 0
    assert parse_mflux_progress("50%|█████     | 1/2 [00:14<00:14, 14.32s/it]") == 50
    assert parse_mflux_progress("100%|██████████| 2/2 [00:28<00:00, 14.01s/it]") == 100
    assert parse_mflux_progress("75%|███████▌  | 3/4 [00:20<00:05, 5.32s/it]") == 75
    assert parse_mflux_progress("1%|          | 0/100 [00:00<?, ?it/s]") == 1


def test_parse_mflux_progress_invalid_lines():
    """Test parsing lines without progress information."""
    assert parse_mflux_progress("no progress here") is None
    assert parse_mflux_progress("Loading model...") is None
    assert parse_mflux_progress("") is None
    assert parse_mflux_progress("Just some random text") is None
    assert parse_mflux_progress("Error: something went wrong") is None


def test_parse_mflux_progress_edge_cases():
    """Test edge cases in progress parsing."""
    # Progress at boundaries
    assert parse_mflux_progress("0%|") == 0
    assert parse_mflux_progress("100%|") == 100

    # Multiple percentage signs (should get first match)
    assert parse_mflux_progress("50%| something 75% else") == 50


def test_parse_mflux_progress_multiline_input():
    """Test that parsing works with multiline stderr."""
    lines = [
        "0%|          | 0/2 [00:00<?, ?it/s]",
        "some other output",
        "50%|█████     | 1/2 [00:14<00:14, 14.32s/it]",
        "more output",
        "100%|██████████| 2/2 [00:28<00:00, 14.01s/it]"
    ]

    results = [parse_mflux_progress(line) for line in lines]
    assert results == [0, None, 50, None, 100]


# Test pure function: map_mflux_to_overall
def test_map_mflux_to_overall_boundaries():
    """Test progress mapping at boundaries."""
    assert map_mflux_to_overall(0) == 25
    assert map_mflux_to_overall(100) == 100


def test_map_mflux_to_overall_midpoints():
    """Test progress mapping at various points."""
    assert map_mflux_to_overall(50) == 62  # 25 + 50*0.75 = 62.5 -> 62
    assert map_mflux_to_overall(25) == 43  # 25 + 25*0.75 = 43.75 -> 43
    assert map_mflux_to_overall(75) == 81  # 25 + 75*0.75 = 81.25 -> 81


def test_map_mflux_to_overall_formula():
    """Test that mapping formula is correct: 25 + (x * 0.75)."""
    # The formula should map 0-100 to 25-100
    for mflux_pct in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
        overall = map_mflux_to_overall(mflux_pct)
        expected = int(25 + (mflux_pct * 0.75))
        assert overall == expected, f"Failed for {mflux_pct}%: got {overall}, expected {expected}"


def test_map_mflux_to_overall_monotonic():
    """Test that progress mapping is monotonic (always increasing)."""
    previous = 0
    for mflux_pct in range(101):
        current = map_mflux_to_overall(mflux_pct)
        assert current >= previous, f"Progress decreased at {mflux_pct}%"
        previous = current


def test_map_mflux_to_overall_range():
    """Test that all mapped values are in valid range."""
    for mflux_pct in range(101):
        overall = map_mflux_to_overall(mflux_pct)
        assert 25 <= overall <= 100, f"Progress {overall} out of range for input {mflux_pct}"
