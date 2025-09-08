#!/usr/bin/env python3
"""
Test runner script for ISA SuperApp.

This script provides a convenient way to run tests with different configurations
and generate reports.
"""

import sys
import argparse
import subprocess
import json
import time
from pathlib import Path
from typing import List, Optional


def run_command(cmd: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=capture_output, text=True)
    
    if result.returncode != 0 and capture_output:
        print(f"Error output: {result.stderr}")
    
    return result


def run_tests(
    test_path: str = "tests",
    markers: Optional[List[str]] = None,
    coverage: bool = True,
    verbose: bool = False,
    parallel: bool = False,
    generate_report: bool = False
) -> bool:
    """Run tests with specified configuration."""
    
    cmd = ["python", "-m", "pytest"]
    
    # Add test path
    cmd.append(test_path)
    
    # Add markers if specified
    if markers:
        marker_str = " and ".join(markers)
        cmd.extend(["-m", marker_str])
    
    # Add coverage options
    if coverage:
        cmd.extend([
            "--cov=isa_superapp",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml"
        ])
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    
    # Add parallel execution
    if parallel:
        cmd.extend(["-n", "auto"])
    
    # Add report generation
    if generate_report:
        cmd.extend(["--html=report.html", "--self-contained-html"])
    
    # Run tests
    result = run_command(cmd, capture_output=False)
    
    return result.returncode == 0


def run_specific_test(test_file: str, test_function: Optional[str] = None) -> bool:
    """Run a specific test file or function."""
    cmd = ["python", "-m", "pytest", "-v"]
    
    if test_function:
        cmd.append(f"{test_file}::{test_function}")
    else:
        cmd.append(test_file)
    
    result = run_command(cmd, capture_output=False)
    return result.returncode == 0


def run_integration_tests() -> bool:
    """Run integration tests only."""
    return run_tests(markers=["integration"], coverage=False)


def run_unit_tests() -> bool:
    """Run unit tests only."""
    return run_tests(markers=["unit"])


def run_performance_tests() -> bool:
    """Run performance tests."""
    return run_tests(markers=["performance"], coverage=False)


def run_security_tests() -> bool:
    """Run security tests."""
    return run_tests(markers=["security"], coverage=False)


def generate_test_report() -> bool:
    """Generate comprehensive test report."""
    print("Generating comprehensive test report...")
    
    # Run all tests with coverage and HTML report
    success = run_tests(
        coverage=True,
        verbose=True,
        generate_report=True
    )
    
    if success:
        print("Test report generated successfully!")
        print("Reports available at:")
        print("  - HTML Coverage Report: htmlcov/index.html")
        print("  - Test Results: report.html")
        print("  - Coverage XML: coverage.xml")
    else:
        print("Some tests failed. Check the reports for details.")
    
    return success


def check_test_coverage() -> bool:
    """Check test coverage and fail if below threshold."""
    print("Checking test coverage...")
    
    # Run tests with coverage
    success = run_tests(
        coverage=True,
        verbose=False
    )
    
    if not success:
        print("Tests failed. Cannot check coverage.")
        return False
    
    # Parse coverage report
    try:
        with open("coverage.xml", "r") as f:
            coverage_data = f.read()
        
        # Simple check for coverage percentage (you might want to use a proper XML parser)
        if "line-rate=" in coverage_data:
            # Extract coverage percentage (this is a simplified approach)
            import re
            match = re.search(r'line-rate="([0-9.]+)"', coverage_data)
            if match:
                coverage_rate = float(match.group(1))
                coverage_percentage = coverage_rate * 100
                
                print(f"Test coverage: {coverage_percentage:.1f}%")
                
                if coverage_percentage < 80:
                    print("ERROR: Test coverage is below 80%")
                    return False
                else:
                    print("Test coverage meets requirements!")
                    return True
        
        print("Could not parse coverage data")
        return False
        
    except FileNotFoundError:
        print("Coverage report not found")
        return False


def main():
    """Main function to handle command line arguments and run tests."""
    parser = argparse.ArgumentParser(description="ISA SuperApp Test Runner")
    
    parser.add_argument(
        "command",
        choices=[
            "all", "unit", "integration", "performance", "security",
            "specific", "report", "coverage", "help"
        ],
        help="Test command to run"
    )
    
    parser.add_argument(
        "--test-file",
        help="Specific test file to run (for 'specific' command)"
    )
    
    parser.add_argument(
        "--test-function",
        help="Specific test function to run (for 'specific' command)"
    )
    
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Disable coverage reporting"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Handle commands
    if args.command == "help":
        print("Available commands:")
        print("  all          - Run all tests")
        print("  unit         - Run unit tests only")
        print("  integration  - Run integration tests only")
        print("  performance  - Run performance tests")
        print("  security     - Run security tests")
        print("  specific     - Run specific test file/function")
        print("  report       - Generate comprehensive test report")
        print("  coverage     - Check test coverage (must be >= 80%)")
        print("\nExamples:")
        print("  python run_tests.py unit")
        print("  python run_tests.py specific --test-file tests/test_main.py")
        print("  python run_tests.py specific --test-file tests/test_main.py --test-function test_app_initialization")
        print("  python run_tests.py report")
        return True
    
    elif args.command == "all":
        success = run_tests(
            coverage=not args.no_coverage,
            verbose=args.verbose,
            parallel=args.parallel
        )
    
    elif args.command == "unit":
        success = run_unit_tests()
    
    elif args.command == "integration":
        success = run_integration_tests()
    
    elif args.command == "performance":
        success = run_performance_tests()
    
    elif args.command == "security":
        success = run_security_tests()
    
    elif args.command == "specific":
        if not args.test_file:
            print("ERROR: --test-file is required for 'specific' command")
            return False
        
        success = run_specific_test(args.test_file, args.test_function)
    
    elif args.command == "report":
        success = generate_test_report()
    
    elif args.command == "coverage":
        success = check_test_coverage()
    
    else:
        print(f"Unknown command: {args.command}")
        return False
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()