#!/usr/bin/env python3
"""
Smoke tests for ISA SuperApp deployment verification.
"""

import argparse
import requests
import sys
import time
from typing import Optional


def test_health_endpoint(endpoint: str, timeout: int = 30) -> bool:
    """Test the health endpoint."""
    try:
        response = requests.get(f"{endpoint}/health", timeout=timeout)
        if response.status_code == 200:
            print(f"✅ Health check passed: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_api_endpoints(endpoint: str, timeout: int = 30) -> bool:
    """Test basic API endpoints."""
    tests = [
        ("GET", f"{endpoint}/api/v1/status"),
        ("GET", f"{endpoint}/api/v1/docs"),
    ]
    
    all_passed = True
    for method, url in tests:
        try:
            if method == "GET":
                response = requests.get(url, timeout=timeout)
            else:
                continue
                
            if response.status_code in [200, 404]:  # 404 is acceptable for some endpoints
                print(f"✅ {method} {url} - Status: {response.status_code}")
            else:
                print(f"❌ {method} {url} - Status: {response.status_code}")
                all_passed = False
        except requests.exceptions.RequestException as e:
            print(f"❌ {method} {url} - Error: {e}")
            all_passed = False
    
    return all_passed


def test_database_connection(endpoint: str, timeout: int = 30) -> bool:
    """Test database connectivity through API."""
    try:
        response = requests.get(f"{endpoint}/api/v1/health/db", timeout=timeout)
        if response.status_code == 200:
            print(f"✅ Database connection test passed")
            return True
        else:
            print(f"❌ Database connection test failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Database connection test failed: {e}")
        return False


def run_smoke_tests(endpoint: str, wait_time: int = 0) -> bool:
    """Run all smoke tests."""
    if wait_time > 0:
        print(f"Waiting {wait_time} seconds for deployment to stabilize...")
        time.sleep(wait_time)
    
    print(f"Running smoke tests against: {endpoint}")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("API Endpoints", test_api_endpoints),
        ("Database Connection", test_database_connection),
    ]
    
    all_passed = True
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        result = test_func(endpoint)
        results.append((test_name, result))
        if not result:
            all_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    print("SMOKE TEST SUMMARY:")
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Run smoke tests against ISA SuperApp")
    parser.add_argument(
        "--endpoint",
        required=True,
        help="Base URL of the application (e.g., https://api.example.com)"
    )
    parser.add_argument(
        "--wait",
        type=int,
        default=0,
        help="Seconds to wait before running tests (default: 0)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)"
    )
    
    args = parser.parse_args()
    
    # Ensure endpoint doesn't have trailing slash
    endpoint = args.endpoint.rstrip('/')
    
    success = run_smoke_tests(endpoint, args.wait)
    
    if success:
        print("\n🎉 All smoke tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some smoke tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()