"""Test mflux progress parsing with real output data.

This test uses actual mflux stdout output captured from running:
    mflux-generate --model schnell --path ~/.AICraft/models/schnell-3bit \
        --prompt "produce cute pikachu" --steps 2

The output shows progress in this format:
    0%|          | 0/2 [00:00<?, ?it/s]
    50%|█████     | 1/2 [00:14<00:14, 14.19s/it]
    100%|██████████| 2/2 [00:27<00:00, 13.88s/it]
"""
import pytest
from avatar_generator import parse_mflux_progress, map_mflux_to_overall


# Real mflux output captured from running with --steps 2
REAL_MFLUX_OUTPUT = """  0%|          | 0/2 [00:00<?, ?it/s] 50%|█████     | 1/2 [00:14<00:14, 14.19s/it]100%|██████████| 2/2 [00:27<00:00, 13.88s/it]100%|██████████| 2/2 [00:27<00:00, 13.93s/it]
"""


class TestMfluxProgressParsing:
    """Test parsing real mflux progress output."""

    def test_parse_real_mflux_0_percent(self):
        """Test parsing 0% progress from real mflux output."""
        line = "  0%|          | 0/2 [00:00<?, ?it/s]"
        result = parse_mflux_progress(line)
        assert result == 0

    def test_parse_real_mflux_50_percent(self):
        """Test parsing 50% progress from real mflux output."""
        line = " 50%|█████     | 1/2 [00:14<00:14, 14.19s/it]"
        result = parse_mflux_progress(line)
        assert result == 50

    def test_parse_real_mflux_100_percent(self):
        """Test parsing 100% progress from real mflux output."""
        line = "100%|██████████| 2/2 [00:27<00:00, 13.88s/it]"
        result = parse_mflux_progress(line)
        assert result == 100

    def test_parse_real_mflux_100_percent_final(self):
        """Test parsing final 100% progress (slightly different timing)."""
        line = "100%|██████████| 2/2 [00:27<00:00, 13.93s/it]"
        result = parse_mflux_progress(line)
        assert result == 100

    def test_parse_empty_line(self):
        """Test parsing empty line returns None."""
        result = parse_mflux_progress("")
        assert result is None

    def test_parse_non_progress_line(self):
        """Test parsing non-progress line returns None."""
        result = parse_mflux_progress("Some random output")
        assert result is None

    def test_full_mflux_output_sequence(self):
        """Test parsing full sequence of real mflux output."""
        lines = REAL_MFLUX_OUTPUT.strip().split()

        # Split by progress bar patterns (look for N%|)
        progress_values = []
        current_line = ""

        for token in lines:
            current_line += token + " "
            if "%|" in current_line:
                pct = parse_mflux_progress(current_line)
                if pct is not None:
                    progress_values.append(pct)
                current_line = ""

        # Should have captured 0%, 50%, 100%, 100%
        assert len(progress_values) == 4
        assert progress_values[0] == 0
        assert progress_values[1] == 50
        assert progress_values[2] == 100
        assert progress_values[3] == 100


class TestMfluxToOverallMapping:
    """Test mapping mflux progress to overall progress (25-100%)."""

    def test_map_0_percent(self):
        """mflux 0% should map to overall 25%."""
        result = map_mflux_to_overall(0)
        assert result == 25

    def test_map_50_percent(self):
        """mflux 50% should map to overall 62%."""
        result = map_mflux_to_overall(50)
        assert result == 62  # 25 + (50 * 0.75) = 62.5 → 62

    def test_map_100_percent(self):
        """mflux 100% should map to overall 100%."""
        result = map_mflux_to_overall(100)
        assert result == 100

    def test_real_sequence_mapping(self):
        """Test mapping real mflux sequence to overall progress."""
        # Real mflux outputs: 0%, 50%, 100%
        mflux_values = [0, 50, 100]
        expected_overall = [25, 62, 100]

        for mflux, expected in zip(mflux_values, expected_overall):
            result = map_mflux_to_overall(mflux)
            assert result == expected, f"mflux {mflux}% should map to {expected}%, got {result}%"


class TestAgentServiceProgressMapping:
    """Test the progress mapping used in agent_service.py."""

    def test_agent_service_formula(self):
        """Test the formula used in agent_service.py line 120.

        Formula: 33 + ((progress - 25) * 67/75)

        This maps:
        - mflux 0% → overall 25% → agent_service shows 33%
        - mflux 50% → overall 62% → agent_service shows ~65%
        - mflux 100% → overall 100% → agent_service shows 100%
        """
        # mflux 0% → overall 25%
        mflux_0 = map_mflux_to_overall(0)
        agent_service_0 = int(33 + ((mflux_0 - 25) * 67 / 75))
        assert agent_service_0 == 33  # Should stay at 33% when starting

        # mflux 50% → overall 62%
        mflux_50 = map_mflux_to_overall(50)
        agent_service_50 = int(33 + ((mflux_50 - 25) * 67 / 75))
        assert 60 <= agent_service_50 <= 70  # Should be around 65-66%

        # mflux 100% → overall 100%
        mflux_100 = map_mflux_to_overall(100)
        agent_service_100 = int(33 + ((mflux_100 - 25) * 67 / 75))
        assert agent_service_100 == 100  # Should reach 100%

    def test_full_progress_flow(self):
        """Test complete progress flow: mflux → overall → agent_service."""
        # Simulate real mflux progress: 0% → 50% → 100%
        real_mflux_values = [0, 50, 100]

        final_percentages = []
        for mflux_pct in real_mflux_values:
            # Step 1: Map mflux to overall (avatar_generator)
            overall_pct = map_mflux_to_overall(mflux_pct)

            # Step 2: Map overall to agent_service display
            agent_service_pct = int(33 + ((overall_pct - 25) * 67 / 75))

            final_percentages.append(agent_service_pct)

        # Verify smooth progression
        assert final_percentages[0] == 33   # Start at 33% (LLM complete + avatar start)
        assert final_percentages[1] >= 60   # Should be ~65% at midpoint
        assert final_percentages[2] == 100  # Should reach 100%

        # Verify no regression
        for i in range(1, len(final_percentages)):
            assert final_percentages[i] >= final_percentages[i-1], \
                f"Progress regressed from {final_percentages[i-1]}% to {final_percentages[i]}%"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
