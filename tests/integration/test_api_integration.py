"""
Integration tests for API Server Connectivity and Responses

Tests cover:
- Health endpoint validation
- Server version information
- Tools count in health response
- MCP client connection to server
- Server unavailability handling
- API response format validation

Target: 85%+ code coverage for API integration
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import requests
import json

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from hexstrike_mcp import HexStrikeClient


class TestHealthEndpoint:
    """Tests for health endpoint validation"""

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_health_endpoint_returns_valid_json(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that health endpoint returns valid JSON response"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "healthy",
            "version": "6.1.0",
            "tools_count": 100,
            "uptime": 3600
        }
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        health = client.check_health()

        # Assert
        assert isinstance(health, dict)
        assert "status" in health
        assert health["status"] == "healthy"

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_health_endpoint_structure(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that health response has expected structure"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        health_data = {
            "status": "healthy",
            "version": "6.1.0",
            "tools_count": 100,
            "uptime": 3600,
            "cache_stats": {
                "hits": 50,
                "misses": 10
            }
        }
        mock_response.json.return_value = health_data
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        health = client.check_health()

        # Assert
        # Verify expected fields are present
        assert "status" in health
        assert "version" in health
        assert "tools_count" in health

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_health_endpoint_json_serializable(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that health response is JSON serializable"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "healthy",
            "version": "6.1.0",
            "tools_count": 100
        }
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        health = client.check_health()

        # Assert
        # Should be able to serialize to JSON
        try:
            json_str = json.dumps(health)
            assert isinstance(json_str, str)
            assert len(json_str) > 0
        except (TypeError, ValueError) as e:
            pytest.fail(f"Health response not JSON serializable: {e}")


class TestServerVersion:
    """Tests for server version information"""

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_server_version_in_health_response(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that server version is included in health response"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "healthy",
            "version": "6.1.0",
            "tools_count": 100
        }
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        health = client.check_health()

        # Assert
        assert "version" in health
        assert isinstance(health["version"], str)
        assert len(health["version"]) > 0

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_server_version_format(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that server version follows semantic versioning format"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "healthy",
            "version": "6.1.0",
            "tools_count": 100
        }
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        health = client.check_health()

        # Assert
        version = health.get("version", "")
        # Check for semantic versioning pattern (x.y.z)
        parts = version.split(".")
        assert len(parts) >= 2  # At least major.minor

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_server_version_different_versions(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test handling of different server versions"""
        # Arrange
        versions = ["6.0.0", "6.1.0", "6.1.1", "7.0.0-beta"]

        for version in versions:
            mock_session_instance = MagicMock()
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "status": "healthy",
                "version": version,
                "tools_count": 100
            }
            mock_session_instance.get.return_value = mock_response
            mock_session.return_value = mock_session_instance

            client = HexStrikeClient("http://localhost:8888")

            # Act
            health = client.check_health()

            # Assert
            assert health["version"] == version


class TestToolsCount:
    """Tests for tools count in health response"""

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_tools_count_in_health_response(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that tools count is included in health response"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "healthy",
            "version": "6.1.0",
            "tools_count": 100
        }
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        health = client.check_health()

        # Assert
        assert "tools_count" in health
        assert isinstance(health["tools_count"], int)
        assert health["tools_count"] > 0

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_tools_count_positive_value(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that tools count is a positive integer"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "healthy",
            "version": "6.1.0",
            "tools_count": 105
        }
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        health = client.check_health()

        # Assert
        tools_count = health.get("tools_count", 0)
        assert isinstance(tools_count, int)
        assert tools_count >= 0

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_tools_count_realistic_range(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that tools count is in a realistic range"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "healthy",
            "version": "6.1.0",
            "tools_count": 100
        }
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        health = client.check_health()

        # Assert
        tools_count = health.get("tools_count", 0)
        # HexStrike should have at least 50 tools and less than 1000
        assert 50 <= tools_count <= 1000


class TestMCPClientConnection:
    """Tests for MCP client connection to server"""

    @patch('sys.stdin.isatty', return_value=True)
    @patch('sys.stdout.isatty', return_value=True)
    @patch('requests.Session')
    def test_mcp_client_connects_to_server(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that MCP client successfully connects to server"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "healthy",
            "version": "6.1.0",
            "tools_count": 100
        }
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        # Act
        client = HexStrikeClient("http://localhost:8888")

        # Assert
        # Connection should be established
        assert client.server_url == "http://localhost:8888"
        assert client.session is not None
        # Health check should have been called in interactive mode
        assert mock_session_instance.get.call_count >= 1

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_mcp_client_handles_connection_in_stdio_mode(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that MCP client handles connection in STDIO mode"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        # Act
        client = HexStrikeClient("http://localhost:8888")

        # Assert
        # Client should initialize without health checks in stdio mode
        assert client.server_url == "http://localhost:8888"
        assert client.session is not None
        # No health check should be made in stdio mode
        assert mock_session_instance.get.call_count == 0

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_mcp_client_uses_session_for_requests(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that MCP client uses Session for all requests"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "test"}
        mock_session_instance.get.return_value = mock_response
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        client.safe_get("health")
        client.safe_post("api/test", {"data": "test"})

        # Assert
        # Session methods should be used
        assert mock_session_instance.get.called
        assert mock_session_instance.post.called


class TestServerUnavailability:
    """Tests for handling server unavailability"""

    @patch('sys.stdin.isatty', return_value=True)
    @patch('sys.stdout.isatty', return_value=True)
    @patch('requests.Session')
    @patch('time.sleep')
    def test_mcp_handles_server_unavailable(self, mock_sleep, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that MCP client handles server unavailability gracefully"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_session_instance.get.side_effect = requests.exceptions.ConnectionError("Connection refused")
        mock_session.return_value = mock_session_instance

        # Act
        # Should not raise exception, just log warnings
        client = HexStrikeClient("http://localhost:8888")

        # Assert
        # Client should still be initialized
        assert client.server_url == "http://localhost:8888"
        assert client.session is not None
        # Should have attempted MAX_RETRIES times
        assert mock_session_instance.get.call_count == 3  # MAX_RETRIES

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_api_request_fails_when_server_down(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that API requests return error when server is down"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_session_instance.get.side_effect = requests.exceptions.ConnectionError("Connection refused")
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_get("health")

        # Assert
        assert "error" in result
        assert result["success"] is False
        assert "Connection refused" in result["error"]

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_timeout_handling(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that client handles request timeouts"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_session_instance.get.side_effect = requests.exceptions.Timeout("Request timeout")
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_get("api/long-running-task")

        # Assert
        assert "error" in result
        assert result["success"] is False
        assert "timeout" in result["error"].lower()

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_http_error_handling(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that client handles HTTP errors (4xx, 5xx)"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Internal Server Error")
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_get("api/broken")

        # Assert
        assert "error" in result
        assert result["success"] is False


class TestAPIResponseFormat:
    """Tests for API response format validation"""

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_successful_response_format(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that successful API responses have expected format"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "data": {"result": "test"},
            "message": "Operation completed"
        }
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_get("api/test")

        # Assert
        assert isinstance(result, dict)
        assert result["success"] is True

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_error_response_format(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that error responses have expected format"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_session_instance.get.side_effect = requests.exceptions.RequestException("Error occurred")
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_get("api/test")

        # Assert
        assert isinstance(result, dict)
        assert "error" in result
        assert "success" in result
        assert result["success"] is False

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_response_contains_required_fields(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that API responses contain required fields"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "healthy",
            "version": "6.1.0",
            "tools_count": 100,
            "uptime": 3600,
            "timestamp": "2024-01-01T12:00:00Z"
        }
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.check_health()

        # Assert
        # Core fields should be present
        assert "status" in result
        assert "version" in result
        assert "tools_count" in result


class TestAPIEndpoints:
    """Tests for various API endpoints"""

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_health_endpoint_accessibility(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that health endpoint is accessible"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "healthy"}
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_get("health")

        # Assert
        assert isinstance(result, dict)
        assert "status" in result

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_api_command_endpoint(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that API command endpoint accepts requests"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "output": "command result"}
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.execute_command("test command")

        # Assert
        assert isinstance(result, dict)
        assert "success" in result or "error" in result

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_tool_endpoint_structure(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that tool endpoints follow expected structure"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "stdout": "tool output",
            "stderr": "",
            "returncode": 0
        }
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_post("api/tools/nmap", {"target": "example.com"})

        # Assert
        assert isinstance(result, dict)
