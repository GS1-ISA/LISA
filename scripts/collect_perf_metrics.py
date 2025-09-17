#!/usr/bin/env python3
"""
Performance metrics collection script for ISA_D application.
Collects memory usage, CPU utilization, and response times during test execution.
"""

import time
import psutil
import subprocess
import json
from pathlib import Path
from typing import Dict, List
import os

def get_system_metrics() -> Dict:
    """Get current system memory and CPU metrics."""
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=1)

    return {
        "memory_percent": memory.percent,
        "memory_used_mb": memory.used / 1024 / 1024,
        "memory_available_mb": memory.available / 1024 / 1024,
        "cpu_percent": cpu_percent,
        "timestamp": time.time()
    }

def run_tests_with_monitoring(test_command: str, duration: int = 60) -> Dict:
    """Run tests while monitoring system resources."""
    metrics_over_time = []
    start_time = time.time()

    # Start the test process
    process = subprocess.Popen(test_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Monitor for the specified duration
    while time.time() - start_time < duration and process.poll() is None:
        metrics = get_system_metrics()
        metrics_over_time.append(metrics)
        time.sleep(1)

    # Get final metrics
    if process.poll() is None:
        process.terminate()
        process.wait()

    stdout, stderr = process.communicate()

    return {
        "command": test_command,
        "return_code": process.returncode,
        "duration": time.time() - start_time,
        "metrics": metrics_over_time,
        "stdout": stdout.decode('utf-8', errors='ignore')[:1000],  # First 1000 chars
        "stderr": stderr.decode('utf-8', errors='ignore')[:1000]   # First 1000 chars
    }

def main():
    """Main function to collect performance metrics."""
    results = {}

    # Test commands for different components
    test_commands = {
        "api_server": "pytest tests/test_api_server.py::TestHealthEndpoints::test_root_endpoint tests/test_api_server.py::TestHealthEndpoints::test_metrics_endpoint -v",
        "agents": "pytest tests/test_agents.py::TestAgentResponse::test_agent_response_creation -v",
        "vector_store": "pytest tests/test_vector_store.py::TestVectorDocument::test_vector_document_creation -v"
    }

    for component, command in test_commands.items():
        print(f"Running performance test for {component}...")
        results[component] = run_tests_with_monitoring(command, duration=30)

    # Calculate summary statistics
    summary = {}
    for component, data in results.items():
        if data["metrics"]:
            memory_usage = [m["memory_percent"] for m in data["metrics"]]
            cpu_usage = [m["cpu_percent"] for m in data["metrics"]]

            summary[component] = {
                "avg_memory_percent": sum(memory_usage) / len(memory_usage),
                "max_memory_percent": max(memory_usage),
                "avg_cpu_percent": sum(cpu_usage) / len(cpu_usage),
                "max_cpu_percent": max(cpu_usage),
                "duration": data["duration"],
                "return_code": data["return_code"]
            }

    results["summary"] = summary

    # Save results
    output_file = Path("docs/performance/baseline_metrics.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Performance metrics saved to {output_file}")

    # Print summary
    print("\n=== PERFORMANCE BASELINE SUMMARY ===")
    for component, stats in summary.items():
        print(f"\n{component.upper()}:")
        print(".1f")
        print(".1f")
        print(".1f")
        print(".1f")
        print(".2f")

if __name__ == "__main__":
    main()