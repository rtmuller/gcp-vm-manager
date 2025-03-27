#!/usr/bin/env python3
"""
Unit tests for GCP VM Manager
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the Python path so we can import gcp_vm_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gcp_vm_manager import configure_port_forwarding

class TestPortForwarding(unittest.TestCase):
    """Test cases for port forwarding functionality"""

    def setUp(self):
        """Set up test environment"""
        self.project = "test-project"
        self.vm_name = "test-vm"
        self.zone = "us-central1-a"
        self.remote_port = "8080"
        self.local_port = "8080"

    @patch('builtins.input')
    @patch('subprocess.run')
    def test_successful_port_forwarding(self, mock_subprocess, mock_input):
        """Test successful port forwarding setup"""
        # Mock user inputs including the final "Press Enter to continue" prompt
        mock_input.side_effect = [self.remote_port, self.local_port, ""]
        
        # Mock subprocess.run to simulate successful execution
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        # Call the function
        configure_port_forwarding(self.project, self.vm_name, self.zone)
        
        # Verify subprocess.run was called with correct arguments
        expected_cmd = [
            "gcloud", "compute", "start-iap-tunnel",
            self.vm_name, self.remote_port,
            "--local-host-port", f"localhost:{self.local_port}",
            "--project", self.project,
            "--zone", self.zone
        ]
        mock_subprocess.assert_called_once_with(expected_cmd)

    @patch('builtins.input')
    @patch('subprocess.run')
    def test_invalid_remote_port(self, mock_subprocess, mock_input):
        """Test handling of invalid remote port input"""
        # Mock user inputs - first invalid, then valid, and the final prompt
        mock_input.side_effect = ["invalid", "0", "-1", "70000", self.remote_port, self.local_port, ""]
        
        # Mock subprocess.run to simulate successful execution
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        # Call the function
        configure_port_forwarding(self.project, self.vm_name, self.zone)
        
        # Verify subprocess.run was called with correct arguments
        expected_cmd = [
            "gcloud", "compute", "start-iap-tunnel",
            self.vm_name, self.remote_port,
            "--local-host-port", f"localhost:{self.local_port}",
            "--project", self.project,
            "--zone", self.zone
        ]
        mock_subprocess.assert_called_once_with(expected_cmd)

    @patch('builtins.input')
    @patch('subprocess.run')
    def test_invalid_local_port(self, mock_subprocess, mock_input):
        """Test handling of invalid local port input"""
        # Mock user inputs - first valid remote port, then invalid local ports, then valid, and the final prompt
        mock_input.side_effect = [self.remote_port, "invalid", "0", "-1", "70000", self.local_port, ""]
        
        # Mock subprocess.run to simulate successful execution
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        # Call the function
        configure_port_forwarding(self.project, self.vm_name, self.zone)
        
        # Verify subprocess.run was called with correct arguments
        expected_cmd = [
            "gcloud", "compute", "start-iap-tunnel",
            self.vm_name, self.remote_port,
            "--local-host-port", f"localhost:{self.local_port}",
            "--project", self.project,
            "--zone", self.zone
        ]
        mock_subprocess.assert_called_once_with(expected_cmd)

    @patch('builtins.input')
    @patch('subprocess.run')
    def test_subprocess_error(self, mock_subprocess, mock_input):
        """Test handling of subprocess error"""
        # Mock user inputs including the final prompt
        mock_input.side_effect = [self.remote_port, self.local_port, ""]
        
        # Mock subprocess.run to simulate error
        mock_subprocess.side_effect = Exception("Test error")
        
        # Call the function
        configure_port_forwarding(self.project, self.vm_name, self.zone)
        
        # Verify subprocess.run was called with correct arguments
        expected_cmd = [
            "gcloud", "compute", "start-iap-tunnel",
            self.vm_name, self.remote_port,
            "--local-host-port", f"localhost:{self.local_port}",
            "--project", self.project,
            "--zone", self.zone
        ]
        mock_subprocess.assert_called_once_with(expected_cmd)

    @patch('builtins.input')
    @patch('subprocess.run')
    def test_keyboard_interrupt(self, mock_subprocess, mock_input):
        """Test handling of keyboard interrupt"""
        # Mock user inputs including the final prompt
        mock_input.side_effect = [self.remote_port, self.local_port, ""]
        
        # Mock subprocess.run to simulate keyboard interrupt
        mock_subprocess.side_effect = KeyboardInterrupt()
        
        # Call the function
        configure_port_forwarding(self.project, self.vm_name, self.zone)
        
        # Verify subprocess.run was called with correct arguments
        expected_cmd = [
            "gcloud", "compute", "start-iap-tunnel",
            self.vm_name, self.remote_port,
            "--local-host-port", f"localhost:{self.local_port}",
            "--project", self.project,
            "--zone", self.zone
        ]
        mock_subprocess.assert_called_once_with(expected_cmd)

if __name__ == '__main__':
    unittest.main() 