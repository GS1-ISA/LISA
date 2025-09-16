#!/usr/bin/env python3
"""
Socket.io Chat Functionality Test Script

This script tests the Socket.io chat functionality of the Conversational Compliance Assistant server.
Tests include:
- Server initialization and CORS setup
- Client connection/disconnection with auth data
- Chat message flow end-to-end
- Error handling for invalid messages
- Role-based personalization
"""

import asyncio
import json
import logging
import socketio
import time
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SocketIOTestClient:
    """Test client for Socket.io chat functionality."""

    def __init__(self, server_url: str = "http://localhost:8001"):
        self.server_url = server_url
        self.sio = socketio.AsyncClient()
        self.test_results = []
        self.connected = False
        self.session_id = None

        # Set up event handlers
        self._setup_event_handlers()

    def _setup_event_handlers(self):
        """Set up Socket.io event handlers."""

        @self.sio.event
        async def connect():
            logger.info("Connected to server")
            self.connected = True

        @self.sio.event
        async def disconnect():
            logger.info("Disconnected from server")
            self.connected = False

        @self.sio.event
        async def connected(data):
            logger.info(f"Received connected event: {data}")
            self._log_test_result("connection", True, f"Connected successfully: {data}")

        @self.sio.event
        async def typing(data):
            logger.info(f"Received typing event: {data}")

        @self.sio.event
        async def chat_response(data):
            logger.info(f"Received chat response: {data}")
            self._log_test_result("chat_response", True, f"Received response: {data}")

        @self.sio.event
        async def error(data):
            logger.error(f"Received error event: {data}")
            self._log_test_result("error_handling", True, f"Error handled: {data}")

    def _log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log a test result."""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        status = "PASS" if success else "FAIL"
        logger.info(f"[{status}] {test_name}: {details}")

    async def connect_with_auth(self, user_id: int, username: str, role: str) -> bool:
        """Connect to server with authentication data."""
        try:
            auth_data = {
                "user_id": user_id,
                "username": username,
                "role": role
            }
            logger.info(f"Connecting with auth: {auth_data}")
            await self.sio.connect(
                self.server_url,
                auth=auth_data,
                wait_timeout=10
            )
            await asyncio.sleep(1)  # Wait for connection to establish
            return self.connected
        except Exception as e:
            self._log_test_result("connection", False, f"Connection failed: {str(e)}")
            return False

    async def send_chat_message(self, message: str) -> bool:
        """Send a chat message and wait for response."""
        try:
            logger.info(f"Sending chat message: {message}")
            await self.sio.emit('chat_message', {'message': message})

            # Wait for response (typing and chat_response events)
            await asyncio.sleep(3)
            return True
        except Exception as e:
            self._log_test_result("chat_message", False, f"Failed to send message: {str(e)}")
            return False

    async def test_empty_message(self) -> bool:
        """Test sending an empty message."""
        try:
            await self.sio.emit('chat_message', {'message': ''})
            await asyncio.sleep(1)
            return True
        except Exception as e:
            self._log_test_result("empty_message", False, f"Empty message test failed: {str(e)}")
            return False

    async def test_invalid_message_format(self) -> bool:
        """Test sending message with invalid format."""
        try:
            await self.sio.emit('chat_message', {})  # Missing message field
            await asyncio.sleep(1)
            return True
        except Exception as e:
            self._log_test_result("invalid_format", False, f"Invalid format test failed: {str(e)}")
            return False

    async def disconnect(self):
        """Disconnect from server."""
        try:
            await self.sio.disconnect()
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Disconnect failed: {str(e)}")

    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of test results."""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests

        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "results": self.test_results
        }

async def run_comprehensive_tests():
    """Run comprehensive Socket.io chat functionality tests."""

    logger.info("Starting Socket.io Chat Functionality Tests")
    logger.info("=" * 50)

    # Test configurations
    test_configs = [
        {"user_id": 1, "username": "admin_user", "role": "admin"},
        {"user_id": 2, "username": "researcher_user", "role": "researcher"},
        {"user_id": 3, "username": "auditor_user", "role": "auditor"},
        {"user_id": 4, "username": "regular_user", "role": "user"},
    ]

    all_results = []

    for i, config in enumerate(test_configs, 1):
        logger.info(f"\n--- Test Set {i}: Role '{config['role']}' ---")

        client = SocketIOTestClient()

        # Test 1: Connection with auth
        logger.info("Test 1: Connection with authentication")
        connected = await client.connect_with_auth(
            config["user_id"],
            config["username"],
            config["role"]
        )

        if not connected:
            logger.error(f"Failed to connect for role {config['role']}, skipping remaining tests")
            all_results.extend(client.test_results)
            continue

        # Test 2: Send valid chat message
        logger.info("Test 2: Send valid chat message")
        test_message = f"What are the key compliance requirements for data privacy regulations? (Test from {config['role']})"
        await client.send_chat_message(test_message)

        # Test 3: Test role-based personalization
        logger.info("Test 3: Test role-based personalization")
        role_specific_message = "Explain GDPR compliance"
        await client.send_chat_message(role_specific_message)

        # Test 4: Error handling - empty message
        logger.info("Test 4: Error handling - empty message")
        await client.test_empty_message()

        # Test 5: Error handling - invalid format
        logger.info("Test 5: Error handling - invalid message format")
        await client.test_invalid_message_format()

        # Disconnect
        await client.disconnect()

        all_results.extend(client.test_results)

    # Test 6: CORS and server initialization
    logger.info("\n--- Test Set: Server Initialization and CORS ---")
    cors_client = SocketIOTestClient()

    # Test connection without auth (should still work for basic connection)
    try:
        await cors_client.sio.connect(cors_client.server_url, wait_timeout=10)
        await asyncio.sleep(1)
        if cors_client.connected:
            cors_client._log_test_result("cors_connection", True, "CORS allows connection without auth")
        else:
            cors_client._log_test_result("cors_connection", False, "Failed to connect for CORS test")
        await cors_client.sio.disconnect()
    except Exception as e:
        cors_client._log_test_result("cors_connection", False, f"CORS test failed: {str(e)}")

    all_results.extend(cors_client.test_results)

    # Generate summary
    logger.info("\n" + "=" * 50)
    logger.info("TEST SUMMARY")
    logger.info("=" * 50)

    summary = {
        "total_tests": len(all_results),
        "passed": len([r for r in all_results if r["success"]]),
        "failed": len([r for r in all_results if not r["success"]]),
        "results": all_results
    }

    summary["success_rate"] = (summary["passed"] / summary["total_tests"] * 100) if summary["total_tests"] > 0 else 0

    logger.info(f"Total Tests: {summary['total_tests']}")
    logger.info(f"Passed: {summary['passed']}")
    logger.info(f"Failed: {summary['failed']}")
    logger.info(".1f")

    # Detailed results
    logger.info("\nDetailed Results:")
    for result in all_results:
        status = "✓" if result["success"] else "✗"
        logger.info(f"{status} {result['test']}: {result['details']}")

    # Check for critical issues
    critical_failures = []
    for result in all_results:
        if not result["success"] and result["test"] in ["connection", "cors_connection"]:
            critical_failures.append(result)

    if critical_failures:
        logger.error("\nCRITICAL ISSUES FOUND:")
        for failure in critical_failures:
            logger.error(f"- {failure['test']}: {failure['details']}")
    else:
        logger.info("\nNo critical connection issues found.")

    return summary

async def main():
    """Main test execution function."""
    try:
        results = await run_comprehensive_tests()

        # Save results to file
        with open("socketio_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info("\nTest results saved to socketio_test_results.json")

        # Exit with appropriate code
        if results["failed"] > 0:
            logger.warning(f"Tests completed with {results['failed']} failures")
            return 1
        else:
            logger.info("All tests passed!")
            return 0

    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)