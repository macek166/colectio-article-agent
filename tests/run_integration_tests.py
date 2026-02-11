"""
Integration test runner script.

Runs all integration tests and generates a comprehensive report.
"""

import sys
import subprocess
from pathlib import Path


def run_integration_tests():
    """Run all integration tests."""
    print("=" * 80)
    print("Running Integration Tests for TCG Content Generator")
    print("=" * 80)
    print()
    
    # Get the tests directory
    tests_dir = Path(__file__).parent
    integration_dir = tests_dir / "integration"
    
    # Test files to run
    test_files = [
        "test_end_to_end_flow.py",
        "test_neon_integration.py",
        "test_context7_integration.py"
    ]
    
    print("Test Coverage:")
    print("- Complete workflow from UI to database")
    print("- Kiro Power integration")
    print("- Context7 MCP integration")
    print("- Error recovery with retry logic (max 3 attempts)")
    print("- Checkpoint and resume functionality")
    print("- Default distribution (5 Pokémon, 3 Hockey, 2 Soccer)")
    print("- Custom distributions")
    print("- Sequential processing (one topic at a time)")
    print("- DOCUMENTATION.md and PROBLEMS.md updates")
    print("- Category-specific source consultation")
    print("- Topic deduplication against Neon database")
    print("- JSON serialization of topics")
    print()
    print("=" * 80)
    print()
    
    all_passed = True
    results = {}
    
    for test_file in test_files:
        test_path = integration_dir / test_file
        
        if not test_path.exists():
            print(f"⚠️  Test file not found: {test_file}")
            results[test_file] = "NOT FOUND"
            all_passed = False
            continue
        
        print(f"Running {test_file}...")
        print("-" * 80)
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_path), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                cwd=tests_dir.parent
            )
            
            print(result.stdout)
            
            if result.returncode == 0:
                print(f"✅ {test_file} PASSED")
                results[test_file] = "PASSED"
            else:
                print(f"❌ {test_file} FAILED")
                print(result.stderr)
                results[test_file] = "FAILED"
                all_passed = False
        
        except Exception as e:
            print(f"❌ Error running {test_file}: {e}")
            results[test_file] = f"ERROR: {e}"
            all_passed = False
        
        print()
    
    # Print summary
    print("=" * 80)
    print("Integration Test Summary")
    print("=" * 80)
    
    for test_file, status in results.items():
        status_symbol = "✅" if status == "PASSED" else "❌"
        print(f"{status_symbol} {test_file}: {status}")
    
    print()
    
    if all_passed:
        print("🎉 All integration tests PASSED!")
        return 0
    else:
        print("⚠️  Some integration tests FAILED. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_integration_tests())
