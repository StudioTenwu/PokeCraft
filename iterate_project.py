#!/usr/bin/env python3
"""
Script to launch autonomous project improvement workflow.
Initiates 4 rounds of TDD-driven development with verification.
"""

import subprocess
import sys

IMPROVEMENT_PROMPT = """Continue perfecting the current project, commit what you have to a git repository. go through 4 rounds of brainstorm design + TDD, from testing to implementation, and then launch a verificiation agent to verify the implementation. When you run out of ideas, look at the file AICraft.md, and make the vision better than it is right now."""


def main():
    """Launch Claude Code with the improvement prompt."""
    try:
        # Launch claude with the prompt
        subprocess.run(
            ["claude", "--dangerously-skip-permissions", "-c", IMPROVEMENT_PROMPT],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error launching Claude: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(
            "Error: 'claude' command not found. Is Claude Code installed?",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
