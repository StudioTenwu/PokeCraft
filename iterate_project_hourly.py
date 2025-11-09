#!/usr/bin/env python3
"""
Script to run iterate_project.py once every hour.
Starts with a 1-hour sleep to allow current execution to finish.
"""

import subprocess
import sys
import time
from datetime import datetime


def log(message):
    """Print timestamped log message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def main():
    """Run iterate_project.py every hour, starting with initial sleep."""
    log("Hourly iteration scheduler started")
    log("Sleeping for 1 hour to allow current execution to finish...")

    # Initial sleep for 1 hour (3600 seconds)

    iteration = 0
    while True:
        iteration += 1
        log(f"Starting iteration #{iteration}")

        try:
            # Run the iterate_project.py script
            result = subprocess.run(
                ["python", "iterate_project.py"],
                check=True,
                capture_output=True,
                text=True,
            )
            log(f"Iteration #{iteration} launched successfully")
            if result.stdout:
                log(f"Output: {result.stdout}")

        except subprocess.CalledProcessError as e:
            log(f"Error running iterate_project.py: {e}")
            if e.stderr:
                log(f"Error output: {e.stderr}")
        except Exception as e:
            log(f"Unexpected error: {e}")

        # Sleep for 1 hour before next iteration
        log(f"Sleeping for 1 hour until next iteration...")
        time.sleep(1800)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\nScheduler stopped by user")
        sys.exit(0)
