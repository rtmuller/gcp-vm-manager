#!/usr/bin/env python3
"""
Unit tests for the GCP VM Manager VM operation functions.
"""

import os
import unittest
from unittest.mock import patch, MagicMock, call

# Import the functions from the main script
import sys
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from gcp_vm_manager import (
    start_vm, stop_vm, reset_vm, view_vm_details, 
    view_vm_logs, run_command_on_vm
)

class TestVMOperations(unittest.TestCase):
    """Test case for VM operation functions."""

    @patch('gcp_vm_manager.run_command')
    @patch('builtins.input')
    def test_start_vm_success(self, mock_input, mock_run_command):
        """Test starting a VM successfully."""
        # Setup mocks
        mock_run_command.return_value = (0, "VM started", "")
        
        # Call function
        start_vm("test-project", "test-vm", "test-zone")
        
        # Verify results
        mock_run_command.assert_called_once_with([
            "gcloud", "compute", "instances", "start", "test-vm",
            "--project", "test-project", "--zone", "test-zone"
        ])
        mock_input.assert_called_once()

    @patch('gcp_vm_manager.run_command')
    @patch('builtins.input')
    def test_start_vm_failure(self, mock_input, mock_run_command):
        """Test starting a VM with an error."""
        # Setup mocks
        mock_run_command.return_value = (1, "", "error message")
        
        # Call function
        start_vm("test-project", "test-vm", "test-zone")
        
        # Verify results
        mock_run_command.assert_called_once_with([
            "gcloud", "compute", "instances", "start", "test-vm",
            "--project", "test-project", "--zone", "test-zone"
        ])
        mock_input.assert_called_once()

    @patch('gcp_vm_manager.run_command')
    @patch('builtins.input')
    def test_stop_vm_success(self, mock_input, mock_run_command):
        """Test stopping a VM successfully."""
        # Setup mocks
        mock_run_command.return_value = (0, "VM stopped", "")
        
        # Call function
        stop_vm("test-project", "test-vm", "test-zone")
        
        # Verify results
        mock_run_command.assert_called_once_with([
            "gcloud", "compute", "instances", "stop", "test-vm",
            "--project", "test-project", "--zone", "test-zone"
        ])
        mock_input.assert_called_once()

    @patch('gcp_vm_manager.run_command')
    @patch('builtins.input')
    def test_stop_vm_failure(self, mock_input, mock_run_command):
        """Test stopping a VM with an error."""
        # Setup mocks
        mock_run_command.return_value = (1, "", "error message")
        
        # Call function
        stop_vm("test-project", "test-vm", "test-zone")
        
        # Verify results
        mock_run_command.assert_called_once_with([
            "gcloud", "compute", "instances", "stop", "test-vm",
            "--project", "test-project", "--zone", "test-zone"
        ])
        mock_input.assert_called_once()

    @patch('gcp_vm_manager.run_command')
    @patch('builtins.input')
    def test_reset_vm_success(self, mock_input, mock_run_command):
        """Test resetting a VM successfully."""
        # Setup mocks
        mock_run_command.return_value = (0, "VM reset", "")
        
        # Call function
        reset_vm("test-project", "test-vm", "test-zone")
        
        # Verify results
        mock_run_command.assert_called_once_with([
            "gcloud", "compute", "instances", "reset", "test-vm",
            "--project", "test-project", "--zone", "test-zone"
        ])
        mock_input.assert_called_once()

    @patch('gcp_vm_manager.run_command')
    @patch('builtins.input')
    def test_reset_vm_failure(self, mock_input, mock_run_command):
        """Test resetting a VM with an error."""
        # Setup mocks
        mock_run_command.return_value = (1, "", "error message")
        
        # Call function
        reset_vm("test-project", "test-vm", "test-zone")
        
        # Verify results
        mock_run_command.assert_called_once_with([
            "gcloud", "compute", "instances", "reset", "test-vm",
            "--project", "test-project", "--zone", "test-zone"
        ])
        mock_input.assert_called_once()

    @patch('gcp_vm_manager.run_command')
    @patch('builtins.input')
    @patch('json.loads')
    @patch('builtins.print')
    def test_view_vm_details_success(self, mock_print, mock_json_loads, mock_input, mock_run_command):
        """Test viewing VM details successfully."""
        # Setup mocks
        mock_run_command.return_value = (0, '{"name": "test-vm"}', "")
        mock_json_loads.return_value = {"name": "test-vm"}
        
        # Call function
        view_vm_details("test-project", "test-vm", "test-zone")
        
        # Verify results
        mock_run_command.assert_called_once_with([
            "gcloud", "compute", "instances", "describe", "test-vm",
            "--project", "test-project", "--zone", "test-zone",
            "--format", "json"
        ])
        mock_json_loads.assert_called_once_with('{"name": "test-vm"}')
        mock_input.assert_called_once()

    @patch('gcp_vm_manager.run_command')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_view_vm_details_failure(self, mock_print, mock_input, mock_run_command):
        """Test viewing VM details with an error."""
        # Setup mocks
        mock_run_command.return_value = (1, "", "error message")
        
        # Call function
        view_vm_details("test-project", "test-vm", "test-zone")
        
        # Verify results
        mock_run_command.assert_called_once_with([
            "gcloud", "compute", "instances", "describe", "test-vm",
            "--project", "test-project", "--zone", "test-zone",
            "--format", "json"
        ])
        mock_input.assert_called_once()

    @patch('gcp_vm_manager.run_command')
    @patch('builtins.input')
    def test_run_command_on_vm_success(self, mock_input, mock_run_command):
        """Test running a command on a VM successfully."""
        # Setup mocks
        mock_input.side_effect = ["test command", None]  # First for command input, second for "Press Enter"
        mock_run_command.return_value = (0, "command output", "")
        
        # Call function
        run_command_on_vm("test-project", "test-vm", "test-zone")
        
        # Verify results
        mock_run_command.assert_called_once_with([
            "gcloud", "compute", "ssh", "test-vm",
            "--project", "test-project", "--zone", "test-zone",
            "--tunnel-through-iap",
            "--command", "test command"
        ])
        self.assertEqual(mock_input.call_count, 2)

    @patch('gcp_vm_manager.run_command')
    @patch('builtins.input')
    def test_run_command_on_vm_failure(self, mock_input, mock_run_command):
        """Test running a command on a VM with an error."""
        # Setup mocks
        mock_input.side_effect = ["test command", None]  # First for command input, second for "Press Enter"
        mock_run_command.return_value = (1, "", "error message")
        
        # Call function
        run_command_on_vm("test-project", "test-vm", "test-zone")
        
        # Verify results
        mock_run_command.assert_called_once_with([
            "gcloud", "compute", "ssh", "test-vm",
            "--project", "test-project", "--zone", "test-zone",
            "--tunnel-through-iap",
            "--command", "test command"
        ])
        self.assertEqual(mock_input.call_count, 2)

    @patch('gcp_vm_manager.run_command')
    @patch('builtins.input')
    def test_run_command_on_vm_empty_command(self, mock_input, mock_run_command):
        """Test running an empty command on a VM."""
        # Setup mocks
        mock_input.side_effect = ["", None]  # First for command input, second for "Press Enter"
        
        # Call function
        run_command_on_vm("test-project", "test-vm", "test-zone")
        
        # Verify results
        mock_run_command.assert_not_called()
        self.assertEqual(mock_input.call_count, 2)


if __name__ == '__main__':
    unittest.main() 