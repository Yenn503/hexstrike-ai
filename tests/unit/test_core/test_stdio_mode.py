"""
Unit tests for STDIO Mode Detection in HexStrikeClient

Tests cover:
- TTY detection logic for stdio mode vs interactive mode
- Health check behavior based on mode
- Connection attempt behavior
- Bootstrap performance optimization for MCP hosts

Target: 95%+ code coverage for STDIO mode detection
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from hexstrike_mcp import HexStrikeClient


class TestSTDIOMode:
    """Tests for STDIO mode detection"""

    @patch('sys.stdin')
    @patch('sys.stdout')
    @patch('requests.Session')
    def test_stdio_mode_detected_when_both_non_tty(self, mock_session, mock_stdout, mock_stdin):
        """STDIO mode should be detected when both stdin and stdout are non-TTY"""
        # Arrange
        mock_stdin.isatty.return_value = False
        mock_stdout.isatty.return_value = False

        # Mock session to prevent actual HTTP calls
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        # Act
        client = HexStrikeClient("http://localhost:8888")

        # Assert
        # In stdio mode, no health checks should be attempted
        mock_session_instance.get.assert_not_called()

    @patch('sys.stdin')
    @patch('sys.stdout')
    @patch('requests.Session')
    def test_interactive_mode_when_stdin_is_tty(self, mock_session, mock_stdout, mock_stdin):
        """Interactive mode should be detected when stdin is TTY"""
        # Arrange
        mock_stdin.isatty.return_value = True
        mock_stdout.isatty.return_value = False

        # Mock session and health check response
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': 'healthy',
            'version': '6.1.0'
        }
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        # Act
        client = HexStrikeClient("http://localhost:8888")

        # Assert
        # In interactive mode, health checks should be attempted
        mock_session_instance.get.assert_called()
        assert "/health" in str(mock_session_instance.get.call_args)

    @patch('sys.stdin')
    @patch('sys.stdout')
    @patch('requests.Session')
    def test_interactive_mode_when_stdout_is_tty(self, mock_session, mock_stdout, mock_stdin):
        """Interactive mode should be detected when stdout is TTY"""
        # Arrange
        mock_stdin.isatty.return_value = False
        mock_stdout.isatty.return_value = True

        # Mock session and health check response
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': 'healthy',
            'version': '6.1.0'
        }
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        # Act
        client = HexStrikeClient("http://localhost:8888")

        # Assert
        # In interactive mode, health checks should be attempted
        mock_session_instance.get.assert_called()

    @patch('sys.stdin')
    @patch('sys.stdout')
    @patch('requests.Session')
    def test_health_checks_skipped_in_stdio_mode(self, mock_session, mock_stdout, mock_stdin):
        """Health checks should be completely skipped in STDIO mode"""
        # Arrange
        mock_stdin.isatty.return_value = False
        mock_stdout.isatty.return_value = False

        # Mock session
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        # Act
        client = HexStrikeClient("http://localhost:8888")

        # Assert
        # Verify NO HTTP calls were made
        assert mock_session_instance.get.call_count == 0
        assert mock_session_instance.post.call_count == 0

        # Client should still be initialized properly
        assert client.server_url == "http://localhost:8888"
        assert client.session is not None

    @patch('sys.stdin')
    @patch('sys.stdout')
    @patch('requests.Session')
    @patch('time.sleep')  # Mock sleep to speed up test
    def test_health_checks_run_in_interactive_mode(self, mock_sleep, mock_session, mock_stdout, mock_stdin):
        """Health checks should run with retries in interactive mode"""
        # Arrange
        mock_stdin.isatty.return_value = True
        mock_stdout.isatty.return_value = True

        # Mock session with successful health check
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': 'healthy',
            'version': '6.1.0',
            'tools_count': 100
        }
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        # Act
        client = HexStrikeClient("http://localhost:8888")

        # Assert
        # Health check should be called at least once
        assert mock_session_instance.get.call_count >= 1

        # Verify the health endpoint was called
        call_args = mock_session_instance.get.call_args_list
        assert any("/health" in str(call) for call in call_args)

    @patch('sys.stdin')
    @patch('sys.stdout')
    @patch('requests.Session')
    def test_client_initialization_basic_properties_stdio(self, mock_session, mock_stdout, mock_stdin):
        """Test that client initializes properly in STDIO mode"""
        # Arrange
        mock_stdin.isatty.return_value = False
        mock_stdout.isatty.return_value = False
        mock_session.return_value = MagicMock()

        # Act
        client = HexStrikeClient("http://localhost:8888", timeout=120)

        # Assert
        assert client.server_url == "http://localhost:8888"
        assert client.timeout == 120
        assert client.session is not None

    @patch('sys.stdin')
    @patch('sys.stdout')
    @patch('requests.Session')
    def test_client_initialization_basic_properties_interactive(self, mock_session, mock_stdout, mock_stdin):
        """Test that client initializes properly in interactive mode"""
        # Arrange
        mock_stdin.isatty.return_value = True
        mock_stdout.isatty.return_value = True

        # Mock successful health check
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {'status': 'healthy', 'version': '6.1.0'}
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        # Act
        client = HexStrikeClient("http://localhost:8888", timeout=300)

        # Assert
        assert client.server_url == "http://localhost:8888"
        assert client.timeout == 300
        assert client.session is not None

    @patch('sys.stdin')
    @patch('sys.stdout')
    @patch('requests.Session')
    def test_server_url_trailing_slash_removed(self, mock_session, mock_stdout, mock_stdin):
        """Test that trailing slash is removed from server URL"""
        # Arrange
        mock_stdin.isatty.return_value = False
        mock_stdout.isatty.return_value = False
        mock_session.return_value = MagicMock()

        # Act
        client = HexStrikeClient("http://localhost:8888/")

        # Assert
        assert client.server_url == "http://localhost:8888"
        assert not client.server_url.endswith("/")


class TestConnectionRetries:
    """Tests for connection retry logic in interactive mode"""

    @patch('sys.stdin')
    @patch('sys.stdout')
    @patch('requests.Session')
    @patch('time.sleep')
    def test_retries_on_connection_error(self, mock_sleep, mock_session, mock_stdout, mock_stdin):
        """Test that client retries connection on ConnectionError"""
        # Arrange
        mock_stdin.isatty.return_value = True
        mock_stdout.isatty.return_value = True

        import requests
        mock_session_instance = MagicMock()
        # First two attempts fail, third succeeds
        mock_session_instance.get.side_effect = [
            requests.exceptions.ConnectionError("Connection refused"),
            requests.exceptions.ConnectionError("Connection refused"),
            MagicMock(json=lambda: {'status': 'healthy', 'version': '6.1.0'})
        ]
        mock_session.return_value = mock_session_instance

        # Act
        client = HexStrikeClient("http://localhost:8888")

        # Assert
        # Should have made 3 attempts
        assert mock_session_instance.get.call_count == 3
        # Should have slept between retries
        assert mock_sleep.call_count >= 2

    @patch('sys.stdin')
    @patch('sys.stdout')
    @patch('requests.Session')
    @patch('time.sleep')
    def test_max_retries_exceeded(self, mock_sleep, mock_session, mock_stdout, mock_stdin):
        """Test behavior when max retries are exceeded"""
        # Arrange
        mock_stdin.isatty.return_value = True
        mock_stdout.isatty.return_value = True

        import requests
        mock_session_instance = MagicMock()
        # All attempts fail
        mock_session_instance.get.side_effect = requests.exceptions.ConnectionError("Connection refused")
        mock_session.return_value = mock_session_instance

        # Act
        # Should not raise exception, just log error
        client = HexStrikeClient("http://localhost:8888")

        # Assert
        # Should have attempted MAX_RETRIES times (3 by default)
        assert mock_session_instance.get.call_count == 3
        # Client should still be initialized
        assert client.server_url == "http://localhost:8888"

    @patch('sys.stdin')
    @patch('sys.stdout')
    @patch('requests.Session')
    def test_first_connection_succeeds_no_retries(self, mock_session, mock_stdout, mock_stdin):
        """Test that no retries occur when first connection succeeds"""
        # Arrange
        mock_stdin.isatty.return_value = True
        mock_stdout.isatty.return_value = True

        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {'status': 'healthy', 'version': '6.1.0'}
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        # Act
        client = HexStrikeClient("http://localhost:8888")

        # Assert
        # Should only call once (no retries)
        assert mock_session_instance.get.call_count == 1


class TestBootstrapPerformance:
    """Tests for bootstrap performance optimization"""

    @patch('sys.stdin')
    @patch('sys.stdout')
    @patch('requests.Session')
    def test_stdio_mode_fast_bootstrap(self, mock_session, mock_stdout, mock_stdin):
        """STDIO mode should have fast bootstrap (no HTTP calls)"""
        # Arrange
        mock_stdin.isatty.return_value = False
        mock_stdout.isatty.return_value = False
        mock_session.return_value = MagicMock()

        # Act
        client = HexStrikeClient("http://localhost:8888")

        # Assert
        # Session should be created but no HTTP calls
        session_instance = mock_session.return_value
        assert session_instance.get.call_count == 0

    @patch('sys.stdin')
    @patch('sys.stdout')
    @patch('requests.Session')
    def test_stdio_mode_no_delays(self, mock_session, mock_stdout, mock_stdin):
        """STDIO mode should not have any artificial delays"""
        # Arrange
        mock_stdin.isatty.return_value = False
        mock_stdout.isatty.return_value = False
        mock_session.return_value = MagicMock()

        # Act
        with patch('time.sleep') as mock_sleep:
            client = HexStrikeClient("http://localhost:8888")

            # Assert
            # No sleeps should occur in stdio mode
            assert mock_sleep.call_count == 0


class TestModeDetectionEdgeCases:
    """Edge cases for mode detection"""

    @patch('sys.stdin')
    @patch('sys.stdout')
    @patch('requests.Session')
    def test_both_tty_interactive_mode(self, mock_session, mock_stdout, mock_stdin):
        """Both stdin and stdout as TTY should trigger interactive mode"""
        # Arrange
        mock_stdin.isatty.return_value = True
        mock_stdout.isatty.return_value = True

        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {'status': 'healthy', 'version': '6.1.0'}
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance

        # Act
        client = HexStrikeClient("http://localhost:8888")

        # Assert
        # Should perform health check
        assert mock_session_instance.get.call_count >= 1

    @patch('sys.stdin')
    @patch('sys.stdout')
    @patch('requests.Session')
    def test_isatty_exception_handling(self, mock_session, mock_stdout, mock_stdin):
        """Test that isatty() exceptions bubble up (expected behavior)"""
        # Arrange
        mock_stdin.isatty.side_effect = AttributeError("No isatty")
        mock_stdout.isatty.return_value = False
        mock_session.return_value = MagicMock()

        # Act & Assert
        # The current implementation doesn't catch isatty exceptions,
        # so they will bubble up. This tests that behavior.
        with pytest.raises(AttributeError, match="No isatty"):
            client = HexStrikeClient("http://localhost:8888")

    @patch('sys.stdin')
    @patch('sys.stdout')
    @patch('requests.Session')
    def test_different_server_urls(self, mock_session, mock_stdout, mock_stdin):
        """Test that server URL is properly stored regardless of mode"""
        # Arrange
        mock_stdin.isatty.return_value = False
        mock_stdout.isatty.return_value = False
        mock_session.return_value = MagicMock()

        test_urls = [
            "http://localhost:8888",
            "http://127.0.0.1:8888",
            "https://hexstrike.example.com",
            "http://192.168.1.100:9999"
        ]

        # Act & Assert
        for url in test_urls:
            client = HexStrikeClient(url)
            # Remove trailing slash for comparison
            expected = url.rstrip("/")
            assert client.server_url == expected
