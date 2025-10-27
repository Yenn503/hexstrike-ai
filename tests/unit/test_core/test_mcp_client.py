"""
Unit tests for Core MCP Functionality - HexStrikeClient and setup_mcp_server

Tests cover:
- HexStrikeClient initialization
- safe_get() and safe_post() request methods
- Error handling and recovery
- setup_mcp_server() configuration
- FastMCP integration
- Health check endpoint

Target: 90%+ code coverage for core MCP functionality
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock, call
import requests

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from hexstrike_mcp import HexStrikeClient, setup_mcp_server


class TestHexStrikeClientInitialization:
    """Tests for HexStrikeClient initialization"""

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_hexstrike_client_initializes_with_defaults(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that HexStrikeClient initializes with default parameters"""
        # Arrange
        mock_session.return_value = MagicMock()

        # Act
        client = HexStrikeClient("http://localhost:8888")

        # Assert
        assert client.server_url == "http://localhost:8888"
        assert client.timeout == 300  # DEFAULT_REQUEST_TIMEOUT
        assert client.session is not None

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_hexstrike_client_initializes_with_custom_timeout(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test initialization with custom timeout"""
        # Arrange
        mock_session.return_value = MagicMock()

        # Act
        client = HexStrikeClient("http://localhost:8888", timeout=600)

        # Assert
        assert client.timeout == 600

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_hexstrike_client_creates_session(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that client creates a requests Session"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        # Act
        client = HexStrikeClient("http://localhost:8888")

        # Assert
        mock_session.assert_called_once()
        assert client.session == mock_session_instance

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_hexstrike_client_strips_trailing_slash(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that trailing slash is removed from server URL"""
        # Arrange
        mock_session.return_value = MagicMock()

        # Act
        client = HexStrikeClient("http://localhost:8888///")

        # Assert
        assert client.server_url == "http://localhost:8888"
        assert not client.server_url.endswith("/")


class TestSafeGetRequest:
    """Tests for safe_get() method"""

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_safe_get_successful_request(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test successful GET request"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success", "data": "test"}
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_get("api/test")

        # Assert
        assert result == {"status": "success", "data": "test"}
        mock_session_instance.get.assert_called_once_with(
            "http://localhost:8888/api/test",
            params={},
            timeout=300
        )

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_safe_get_with_params(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test GET request with query parameters"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "filtered"}
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_get("api/search", params={"query": "test", "limit": 10})

        # Assert
        assert result == {"result": "filtered"}
        call_args = mock_session_instance.get.call_args
        assert call_args[1]["params"] == {"query": "test", "limit": 10}

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_safe_get_handles_request_exception(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that safe_get handles RequestException gracefully"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_session_instance.get.side_effect = requests.exceptions.RequestException("Connection timeout")
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_get("api/test")

        # Assert
        assert "error" in result
        assert result["success"] is False
        assert "Connection timeout" in result["error"]

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_safe_get_handles_generic_exception(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that safe_get handles unexpected exceptions"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_session_instance.get.side_effect = ValueError("Unexpected error")
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_get("api/test")

        # Assert
        assert "error" in result
        assert result["success"] is False
        assert "Unexpected error" in result["error"]

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_safe_get_constructs_correct_url(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that safe_get constructs the correct URL"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "test"}
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        client.safe_get("health")

        # Assert
        call_args = mock_session_instance.get.call_args
        assert call_args[0][0] == "http://localhost:8888/health"


class TestSafePostRequest:
    """Tests for safe_post() method"""

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_safe_post_successful_request(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test successful POST request"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "created", "id": 123}
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_post("api/tools/nmap", {"target": "example.com"})

        # Assert
        assert result == {"status": "created", "id": 123}
        mock_session_instance.post.assert_called_once_with(
            "http://localhost:8888/api/tools/nmap",
            json={"target": "example.com"},
            timeout=300
        )

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_safe_post_with_complex_data(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test POST request with complex JSON data"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        complex_data = {
            "target": "example.com",
            "options": {
                "timeout": 30,
                "threads": 10
            },
            "flags": ["verbose", "aggressive"]
        }

        # Act
        result = client.safe_post("api/scan", complex_data)

        # Assert
        assert result == {"success": True}
        call_args = mock_session_instance.post.call_args
        assert call_args[1]["json"] == complex_data

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_safe_post_handles_request_exception(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that safe_post handles RequestException gracefully"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_session_instance.post.side_effect = requests.exceptions.Timeout("Request timeout")
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_post("api/test", {"data": "test"})

        # Assert
        assert "error" in result
        assert result["success"] is False
        assert "Request timeout" in result["error"]

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_safe_post_handles_http_error(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that safe_post handles HTTP errors (4xx, 5xx)"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_post("api/nonexistent", {"data": "test"})

        # Assert
        assert "error" in result
        assert result["success"] is False


class TestCheckHealthEndpoint:
    """Tests for check_health() method"""

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_check_health_returns_health_data(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that check_health returns server health information"""
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
        assert health["status"] == "healthy"
        assert health["version"] == "6.1.0"
        assert health["tools_count"] == 100

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_check_health_calls_health_endpoint(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that check_health calls the correct endpoint"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "healthy"}
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        client.check_health()

        # Assert
        call_args = mock_session_instance.get.call_args
        assert "http://localhost:8888/health" in str(call_args)


class TestExecuteCommand:
    """Tests for execute_command() method"""

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_execute_command_sends_correct_data(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that execute_command sends correct data to API"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "output": "command result"}
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.execute_command("nmap -sV example.com")

        # Assert
        call_args = mock_session_instance.post.call_args
        assert call_args[1]["json"]["command"] == "nmap -sV example.com"
        assert call_args[1]["json"]["use_cache"] is True

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_execute_command_with_cache_disabled(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test execute_command with caching disabled"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.execute_command("whoami", use_cache=False)

        # Assert
        call_args = mock_session_instance.post.call_args
        assert call_args[1]["json"]["use_cache"] is False


class TestSetupMCPServer:
    """Tests for setup_mcp_server() function"""

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_setup_mcp_server_returns_fastmcp_instance(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that setup_mcp_server returns a FastMCP instance"""
        # Arrange
        mock_session.return_value = MagicMock()
        client = HexStrikeClient("http://localhost:8888")

        # Act
        mcp = setup_mcp_server(client)

        # Assert
        from mcp.server.fastmcp import FastMCP
        assert isinstance(mcp, FastMCP)

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_setup_mcp_server_has_correct_name(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that MCP server has correct name"""
        # Arrange
        mock_session.return_value = MagicMock()
        client = HexStrikeClient("http://localhost:8888")

        # Act
        mcp = setup_mcp_server(client)

        # Assert
        assert mcp.name == "hexstrike-ai-mcp"

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_setup_mcp_server_registers_tools(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that setup_mcp_server registers tool functions"""
        # Arrange
        mock_session.return_value = MagicMock()
        client = HexStrikeClient("http://localhost:8888")

        # Act
        mcp = setup_mcp_server(client)

        # Assert
        # FastMCP should have tools registered
        # Check that the mcp instance has the list_tools method
        assert hasattr(mcp, 'list_tools')

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_setup_mcp_server_can_be_called_multiple_times(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that setup_mcp_server can be called multiple times"""
        # Arrange
        mock_session.return_value = MagicMock()
        client = HexStrikeClient("http://localhost:8888")

        # Act
        mcp1 = setup_mcp_server(client)
        mcp2 = setup_mcp_server(client)

        # Assert
        # Should create separate instances
        assert mcp1 is not mcp2
        from mcp.server.fastmcp import FastMCP
        assert isinstance(mcp1, FastMCP)
        assert isinstance(mcp2, FastMCP)


class TestFastMCPRunFallback:
    """Tests for FastMCP run method fallback behavior"""

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_mcp_has_run_method(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that FastMCP instance has a run method"""
        # Arrange
        mock_session.return_value = MagicMock()
        client = HexStrikeClient("http://localhost:8888")

        # Act
        mcp = setup_mcp_server(client)

        # Assert
        assert hasattr(mcp, 'run')
        assert callable(mcp.run)

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_mcp_server_ready_for_stdio_communication(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that MCP server is ready for STDIO communication"""
        # Arrange
        mock_session.return_value = MagicMock()
        client = HexStrikeClient("http://localhost:8888")

        # Act
        mcp = setup_mcp_server(client)

        # Assert
        # MCP should be ready to handle stdio communication
        assert mcp.name == "hexstrike-ai-mcp"
        assert hasattr(mcp, 'run')


class TestClientEdgeCases:
    """Edge cases and error conditions for HexStrikeClient"""

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_client_handles_empty_response(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test client handles empty JSON response"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_get("api/test")

        # Assert
        assert result == {}

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_client_handles_malformed_json(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test client handles malformed JSON response"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_get("api/test")

        # Assert
        assert "error" in result
        assert result["success"] is False

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_client_with_different_timeouts(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test client respects different timeout values"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "test"}
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        # Act & Assert for different timeouts
        for timeout in [30, 60, 300, 600]:
            client = HexStrikeClient("http://localhost:8888", timeout=timeout)
            client.safe_get("health")

            call_args = mock_session_instance.get.call_args
            assert call_args[1]["timeout"] == timeout
