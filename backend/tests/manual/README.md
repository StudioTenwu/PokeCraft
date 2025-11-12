# Manual Test Scripts

This directory contains manual test scripts that are used for debugging and manual verification. These scripts are NOT run as part of the automated test suite.

## Scripts

- `test_avatar_progress.py` - Manual test for avatar generation progress streaming
- `test_world_creation.py` - Playwright test for world creation flow
- `test_world_bug.py` - Bug reproduction script for world creation issues
- `test_world_bug_auto.py` - Automated bug reproduction script
- `test_blank_screen.py` - Test to reproduce blank screen bug

## Usage

These scripts are meant to be run directly:

```bash
# Example
python test_avatar_progress.py
```

**Note:** Some scripts require:
- Playwright installed (`pip install playwright && playwright install chromium`)
- Backend and frontend servers running
- Specific test data in the database

These tests are excluded from pytest by being in the `manual/` directory.
