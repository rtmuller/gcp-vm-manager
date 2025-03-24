#!/usr/bin/env python3
"""
Unit tests for the GCP VM Manager command execution functions.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

# Import the functions from the main script
import sys
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from gcp_vm_manager import run_command, get_vm_status, get_all_vm_statuses

class TestCommandFunctions(unittest.TestCase):
    """Test case for command execution functions."""

    @patch('subprocess.run')
    def test_run_command_success(self, mock_run):
        """Test running a command that succeeds."""
        # Setup mock
        process_mock = MagicMock()
        process_mock.returncode = 0
        process_mock.stdout = "test output"
        process_mock.stderr = ""
        mock_run.return_value = process_mock

        # Call function
        code, stdout, stderr = run_command(["test", "command"])

        # Verify results
        mock_run.assert_called_once_with(
            ["test", "command"],
            capture_output=True,
            text=True,
            check=False
        )
        self.assertEqual(code, 0)
        self.assertEqual(stdout, "test output")
        self.assertEqual(stderr, "")

    @patch('subprocess.run')
    def test_run_command_failure(self, mock_run):
        """Test running a command that fails."""
        # Setup mock
        process_mock = MagicMock()
        process_mock.returncode = 1
        process_mock.stdout = ""
        process_mock.stderr = "error message"
        mock_run.return_value = process_mock

        # Call function
        code, stdout, stderr = run_command(["test", "command"])

        # Verify results
        mock_run.assert_called_once_with(
            ["test", "command"],
            capture_output=True,
            text=True,
            check=False
        )
        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "error message")

    @patch('subprocess.run')
    def test_run_command_exception(self, mock_run):
        """Test running a command that raises an exception."""
        # Setup mock
        mock_run.side_effect = Exception("Test exception")

        # Call function
        code, stdout, stderr = run_command(["test", "command"])

        # Verify results
        mock_run.assert_called_once_with(
            ["test", "command"],
            capture_output=True,
            text=True,
            check=False
        )
        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "Test exception")

    @patch('gcp_vm_manager.run_command')
    def test_get_vm_status_running(self, mock_run_command):
        """Test getting the status of a running VM."""
        # Setup mock
        mock_run_command.return_value = (0, '{"status": "RUNNING"}', "")

        # Call function
        status = get_vm_status("test-project", "test-vm", "test-zone")

        # Verify results
        self.assertEqual(status, "RUNNING")
        mock_run_command.assert_called_once()

    @patch('gcp_vm_manager.run_command')
    def test_get_vm_status_error(self, mock_run_command):
        """Test getting the status of a VM when the command fails."""
        # Setup mock
        mock_run_command.return_value = (1, "", "error message")

        # Call function
        status = get_vm_status("test-project", "test-vm", "test-zone")

        # Verify results
        self.assertEqual(status, "ERROR")
        mock_run_command.assert_called_once()

    @patch('gcp_vm_manager.run_command')
    def test_get_vm_status_invalid_json(self, mock_run_command):
        """Test getting the status of a VM when the response is not valid JSON."""
        # Setup mock
        mock_run_command.return_value = (0, "not json", "")

        # Call function
        status = get_vm_status("test-project", "test-vm", "test-zone")

        # Verify results
        self.assertEqual(status, "UNKNOWN")
        mock_run_command.assert_called_once()

    @patch('gcp_vm_manager.run_command')
    def test_get_all_vm_statuses_success(self, mock_run_command):
        """Test getting the statuses of all VMs in a project."""
        # Setup mock
        mock_run_command.return_value = (
            0,
            '[{"name": "vm1", "status": "RUNNING"}, {"name": "vm2", "status": "TERMINATED"}]',
            ""
        )

        # Call function
        statuses = get_all_vm_statuses("test-project")

        # Verify results
        self.assertEqual(statuses, {"vm1": "RUNNING", "vm2": "TERMINATED"})
        mock_run_command.assert_called_once()

    @patch('gcp_vm_manager.run_command')
    def test_get_all_vm_statuses_error(self, mock_run_command):
        """Test getting VM statuses when the command fails."""
        # Setup mock
        mock_run_command.return_value = (1, "", "error message")

        # Call function
        statuses = get_all_vm_statuses("test-project")

        # Verify results
        self.assertEqual(statuses, {})
        mock_run_command.assert_called_once()

    @patch('gcp_vm_manager.run_command')
    def test_get_all_vm_statuses_invalid_json(self, mock_run_command):
        """Test getting VM statuses when the response is not valid JSON."""
        # Setup mock
        mock_run_command.return_value = (0, "not json", "")

        # Call function
        statuses = get_all_vm_statuses("test-project")

        # Verify results
        self.assertEqual(statuses, {})
        mock_run_command.assert_called_once()


if __name__ == '__main__':
    unittest.main() 