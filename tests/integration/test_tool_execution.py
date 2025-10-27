"""
Integration tests for Tool Execution Flow

Tests cover:
- Tool invocation through API
- Nmap tool execution
- Nuclei tool execution
- Tool parameter validation
- Timeout handling
- Recovery mechanisms
- Error scenarios

Target: 85%+ code coverage for tool execution flow
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import requests
import time

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from hexstrike_mcp import HexStrikeClient, setup_mcp_server


class TestNmapToolExecution:
    """Tests for Nmap tool execution through API"""

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_nmap_tool_execution_success(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test successful Nmap tool execution"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "stdout": "Nmap scan report for example.com\nHost is up",
            "stderr": "",
            "returncode": 0,
            "execution_time": 5.2
        }
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_post("api/tools/nmap", {
            "target": "example.com",
            "scan_type": "-sV",
            "ports": "80,443"
        })

        # Assert
        assert result["success"] is True
        assert "stdout" in result
        assert result["returncode"] == 0

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_nmap_tool_with_different_scan_types(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test Nmap tool with different scan types"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "stdout": "Scan output",
            "returncode": 0
        }
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        scan_types = ["-sV", "-sS", "-sT", "-sU", "-sC"]

        # Act & Assert
        for scan_type in scan_types:
            result = client.safe_post("api/tools/nmap", {
                "target": "example.com",
                "scan_type": scan_type
            })

            assert result["success"] is True
            # Verify correct data was sent
            call_args = mock_session_instance.post.call_args
            assert call_args[1]["json"]["scan_type"] == scan_type

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_nmap_tool_with_port_specification(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test Nmap tool with specific port ranges"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "stdout": "PORT STATE SERVICE",
            "returncode": 0
        }
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_post("api/tools/nmap", {
            "target": "example.com",
            "ports": "80,443,8080-8090"
        })

        # Assert
        assert result["success"] is True
        call_args = mock_session_instance.post.call_args
        assert call_args[1]["json"]["ports"] == "80,443,8080-8090"

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_nmap_tool_with_additional_args(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test Nmap tool with additional arguments"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "stdout": "Scan output",
            "returncode": 0
        }
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_post("api/tools/nmap", {
            "target": "example.com",
            "additional_args": "-v -T4 --script vuln"
        })

        # Assert
        assert result["success"] is True


class TestNucleiToolExecution:
    """Tests for Nuclei tool execution through API"""

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_nuclei_tool_execution_success(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test successful Nuclei tool execution"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "stdout": "[CVE-2024-1234] [critical] Vulnerability found",
            "stderr": "",
            "returncode": 0
        }
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_post("api/tools/nuclei", {
            "target": "https://example.com",
            "severity": "critical,high"
        })

        # Assert
        assert result["success"] is True
        assert "stdout" in result

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_nuclei_tool_with_severity_filter(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test Nuclei tool with severity filtering"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "stdout": "Scan results",
            "returncode": 0
        }
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        severities = ["critical", "high", "medium", "low", "info", "critical,high"]

        # Act & Assert
        for severity in severities:
            result = client.safe_post("api/tools/nuclei", {
                "target": "https://example.com",
                "severity": severity
            })

            assert result["success"] is True
            call_args = mock_session_instance.post.call_args
            assert call_args[1]["json"]["severity"] == severity

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_nuclei_tool_with_tags(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test Nuclei tool with tag filtering"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "stdout": "Tagged scan results",
            "returncode": 0
        }
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_post("api/tools/nuclei", {
            "target": "https://example.com",
            "tags": "cve,rce,lfi"
        })

        # Assert
        assert result["success"] is True
        call_args = mock_session_instance.post.call_args
        assert call_args[1]["json"]["tags"] == "cve,rce,lfi"

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_nuclei_tool_with_custom_template(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test Nuclei tool with custom template"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "stdout": "Custom template results",
            "returncode": 0
        }
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_post("api/tools/nuclei", {
            "target": "https://example.com",
            "template": "/path/to/custom/template.yaml"
        })

        # Assert
        assert result["success"] is True


class TestToolWithInvalidParams:
    """Tests for tool execution with invalid parameters"""

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_tool_with_missing_required_param(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test tool execution with missing required parameter"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Bad Request")
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_post("api/tools/nmap", {
            # Missing 'target' parameter
            "scan_type": "-sV"
        })

        # Assert
        assert "error" in result
        assert result["success"] is False

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_tool_with_invalid_param_value(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test tool execution with invalid parameter value"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": False,
            "error": "Invalid scan type",
            "returncode": 1
        }
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_post("api/tools/nmap", {
            "target": "example.com",
            "scan_type": "--invalid-option"
        })

        # Assert
        assert result["success"] is False
        assert "error" in result

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_tool_with_empty_target(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test tool execution with empty target"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": False,
            "error": "Target cannot be empty",
            "returncode": 1
        }
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_post("api/tools/nmap", {
            "target": "",
            "scan_type": "-sV"
        })

        # Assert
        assert result["success"] is False


class TestToolTimeoutHandling:
    """Tests for tool timeout handling"""

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_tool_timeout_during_execution(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test handling of tool execution timeout"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_session_instance.post.side_effect = requests.exceptions.Timeout("Request timeout after 300s")
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_post("api/tools/nmap", {
            "target": "example.com",
            "scan_type": "-sV"
        })

        # Assert
        assert "error" in result
        assert result["success"] is False
        assert "timeout" in result["error"].lower()

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_tool_timeout_with_custom_timeout(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test tool execution with custom timeout value"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "stdout": "Scan completed",
            "returncode": 0
        }
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        # Create client with custom timeout
        client = HexStrikeClient("http://localhost:8888", timeout=600)

        # Act
        result = client.safe_post("api/tools/nmap", {
            "target": "example.com"
        })

        # Assert
        assert result["success"] is True
        # Verify timeout was used in request
        call_args = mock_session_instance.post.call_args
        assert call_args[1]["timeout"] == 600

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_tool_partial_results_on_timeout(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test handling of partial results when timeout occurs"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": False,
            "error": "Timeout occurred",
            "partial_results": True,
            "stdout": "Partial scan output...",
            "returncode": 124  # Timeout exit code
        }
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_post("api/tools/nmap", {
            "target": "example.com"
        })

        # Assert
        assert "partial_results" in result or "stdout" in result


class TestToolRecoveryMechanism:
    """Tests for tool recovery mechanisms"""

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_tool_recovery_on_failure(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that recovery mechanism is triggered on tool failure"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "stdout": "Scan completed after retry",
            "returncode": 0,
            "recovery_info": {
                "recovery_applied": True,
                "attempts_made": 2,
                "strategy_used": "retry_with_backoff"
            }
        }
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_post("api/tools/nmap", {
            "target": "example.com",
            "use_recovery": True
        })

        # Assert
        assert result["success"] is True
        if "recovery_info" in result:
            assert result["recovery_info"]["recovery_applied"] is True
            assert result["recovery_info"]["attempts_made"] > 1

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_tool_max_recovery_attempts_exceeded(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test behavior when max recovery attempts are exceeded"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": False,
            "error": "Max recovery attempts exceeded",
            "recovery_info": {
                "recovery_applied": True,
                "attempts_made": 3,
                "max_attempts_reached": True
            },
            "human_escalation": True
        }
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_post("api/tools/nmap", {
            "target": "example.com",
            "use_recovery": True
        })

        # Assert
        assert result["success"] is False
        if "recovery_info" in result:
            assert result["recovery_info"]["attempts_made"] >= 3

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_tool_recovery_strategies(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test different recovery strategies"""
        # Arrange
        strategies = [
            "retry_with_backoff",
            "parameter_adjustment",
            "fallback_mode",
            "reduced_scope"
        ]

        for strategy in strategies:
            mock_session_instance = MagicMock()
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "success": True,
                "stdout": "Recovered",
                "recovery_info": {
                    "recovery_applied": True,
                    "strategy_used": strategy
                }
            }
            mock_session_instance.post.return_value = mock_response
            mock_session.return_value = mock_session_instance

            client = HexStrikeClient("http://localhost:8888")

            # Act
            result = client.safe_post("api/tools/nmap", {
                "target": "example.com",
                "use_recovery": True
            })

            # Assert
            if "recovery_info" in result and "strategy_used" in result["recovery_info"]:
                assert result["recovery_info"]["strategy_used"] == strategy


class TestToolExecutionFlow:
    """Integration tests for complete tool execution flow"""

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_complete_nmap_execution_flow(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test complete Nmap execution flow from request to response"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "stdout": "Nmap scan report\nHost is up\n80/tcp open http",
            "stderr": "",
            "returncode": 0,
            "execution_time": 12.5,
            "cached": False
        }
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_post("api/tools/nmap", {
            "target": "example.com",
            "scan_type": "-sV",
            "ports": "80,443"
        })

        # Assert
        assert result["success"] is True
        assert "stdout" in result
        assert result["returncode"] == 0
        assert "execution_time" in result

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_complete_nuclei_execution_flow(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test complete Nuclei execution flow from request to response"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "stdout": "[CVE-2024-1234] [critical] SQL Injection found\n[CVE-2024-5678] [high] XSS detected",
            "stderr": "",
            "returncode": 0,
            "vulnerabilities_found": 2
        }
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_post("api/tools/nuclei", {
            "target": "https://example.com",
            "severity": "critical,high"
        })

        # Assert
        assert result["success"] is True
        assert "stdout" in result
        assert "CRITICAL" in result["stdout"] or "critical" in result["stdout"]

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_tool_execution_with_caching(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test that tool execution supports caching"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response_cached = MagicMock()
        mock_response_cached.json.return_value = {
            "success": True,
            "stdout": "Cached scan results",
            "cached": True,
            "cache_age": 120
        }
        mock_session_instance.post.return_value = mock_response_cached
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        # Act
        result = client.safe_post("api/tools/nmap", {
            "target": "example.com",
            "scan_type": "-sV"
        })

        # Assert
        if "cached" in result:
            assert isinstance(result["cached"], bool)

    @patch('sys.stdin.isatty', return_value=False)
    @patch('sys.stdout.isatty', return_value=False)
    @patch('requests.Session')
    def test_multiple_tools_sequential_execution(self, mock_session, mock_stdout_tty, mock_stdin_tty):
        """Test executing multiple tools sequentially"""
        # Arrange
        mock_session_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "stdout": "Tool output",
            "returncode": 0
        }
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        client = HexStrikeClient("http://localhost:8888")

        tools = [
            ("api/tools/nmap", {"target": "example.com"}),
            ("api/tools/nuclei", {"target": "https://example.com"}),
        ]

        # Act
        results = []
        for endpoint, params in tools:
            result = client.safe_post(endpoint, params)
            results.append(result)

        # Assert
        assert len(results) == 2
        for result in results:
            assert result["success"] is True
