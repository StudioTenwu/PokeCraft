"""Run all E2E tests and generate a summary report."""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


def check_servers_running() -> bool:
    """Check if backend and frontend servers are running."""
    import urllib.request
    import urllib.error

    def is_server_responding(url: str) -> bool:
        try:
            response = urllib.request.urlopen(url, timeout=2)
            return True
        except urllib.error.HTTPError as e:
            # Server is running if we get HTTP errors (like 405 Method Not Allowed)
            return True
        except (urllib.error.URLError, ConnectionRefusedError):
            return False

    backend_running = is_server_responding('http://localhost:8000/docs')
    frontend_running = is_server_responding('http://localhost:3000')

    if not backend_running:
        print("❌ Backend not running on port 8000")
        print("   Start with: cd backend && uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000")

    if not frontend_running:
        print("❌ Frontend not running on port 3000")
        print("   Start with: cd frontend && npm run dev")

    return backend_running and frontend_running


def run_test(test_file: str) -> dict:
    """
    Run a single test file and return results.

    Args:
        test_file: Name of test file to run

    Returns:
        dict with 'success', 'output', 'duration' keys
    """
    start_time = datetime.now()

    test_path = Path(__file__).parent / test_file
    result = subprocess.run(
        [sys.executable, str(test_path)],
        capture_output=True,
        text=True
    )

    duration = (datetime.now() - start_time).total_seconds()

    return {
        'success': result.returncode == 0,
        'output': result.stdout + result.stderr,
        'duration': duration
    }


def print_summary(results: dict):
    """Print test results summary."""
    print("\n" + "="*80)
    print("E2E TEST SUITE SUMMARY")
    print("="*80)

    total = len(results)
    passed = sum(1 for r in results.values() if r['success'])
    failed = total - passed

    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"\nSuccess Rate: {(passed/total)*100:.1f}%")

    print("\n" + "-"*80)
    print("Individual Test Results:")
    print("-"*80)

    for test_name, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        duration = f"{result['duration']:.2f}s"
        print(f"{status} | {test_name:<40} | {duration:>8}")

    if failed > 0:
        print("\n" + "-"*80)
        print("Failed Test Details:")
        print("-"*80)
        for test_name, result in results.items():
            if not result['success']:
                print(f"\n{test_name}:")
                # Print last 20 lines of output
                output_lines = result['output'].split('\n')
                for line in output_lines[-20:]:
                    print(f"  {line}")


def main():
    """Run all E2E tests."""
    print("\n" + "="*80)
    print("AICRAFT E2E TEST SUITE")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check servers are running
    print("\n[Pre-flight Check] Verifying servers are running...")
    if not check_servers_running():
        print("\n❌ Please start both backend and frontend servers before running tests.")
        return 1

    print("✅ Both servers are running\n")

    # Define test suite
    tests = [
        'test_pokemon_creation.py',
        'test_world_creation.py',
        'test_tool_creation.py',
        'test_agent_deployment.py'
    ]

    # Run all tests
    results = {}

    for i, test in enumerate(tests, 1):
        print(f"\n{'='*80}")
        print(f"[{i}/{len(tests)}] Running: {test}")
        print("="*80)

        result = run_test(test)
        results[test] = result

        if result['success']:
            print(f"✅ {test} completed in {result['duration']:.2f}s")
        else:
            print(f"❌ {test} FAILED after {result['duration']:.2f}s")

    # Print summary
    print_summary(results)

    # Return exit code
    all_passed = all(r['success'] for r in results.values())
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
