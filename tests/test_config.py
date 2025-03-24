#!/usr/bin/env python3
"""
Unit tests for the GCP VM Manager configuration functions.
"""

import os
import json
import unittest
from unittest.mock import patch, mock_open

# Import the functions from the main script
import sys
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from gcp_vm_manager import load_config, save_config, get_project_list

class TestConfigFunctions(unittest.TestCase):
    """Test case for configuration functions."""

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"projects": {"test-project": {"vms": []}}}')
    def test_load_config_existing_file(self, mock_file, mock_exists):
        """Test loading configuration from an existing file."""
        mock_exists.return_value = True
        config = load_config()
        mock_exists.assert_called_once_with("config.json")
        mock_file.assert_called_once_with("config.json", 'r')
        self.assertEqual(config, {"projects": {"test-project": {"vms": []}}})

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_config_new_file(self, mock_file, mock_exists):
        """Test loading configuration when the file doesn't exist."""
        mock_exists.return_value = False
        config = load_config()
        mock_exists.assert_called_once_with("config.json")
        mock_file.assert_called_once_with("config.json", 'w')
        self.assertEqual(config, {"projects": {}})

    @patch('builtins.open', new_callable=mock_open)
    def test_save_config(self, mock_file):
        """Test saving configuration to a file."""
        config = {"projects": {"test-project": {"vms": []}}}
        save_config(config)
        mock_file.assert_called_once_with("config.json", 'w')
        # Check if write was called at least once (not strict on exactly once)
        self.assertTrue(mock_file().write.called)
        # Check if the written content is valid JSON by joining all write calls
        write_args = [args[0] for args, _ in mock_file().write.call_args_list]
        written_content = ''.join(write_args)
        self.assertTrue(json.loads(written_content))

    @patch('gcp_vm_manager.load_config')
    def test_get_project_list(self, mock_load_config):
        """Test getting the list of projects from the configuration."""
        mock_load_config.return_value = {"projects": {"test-project1": {}, "test-project2": {}}}
        projects = get_project_list()
        mock_load_config.assert_called_once()
        self.assertEqual(projects, ["test-project1", "test-project2"])

    @patch('gcp_vm_manager.load_config')
    def test_get_project_list_empty(self, mock_load_config):
        """Test getting the list of projects when the configuration is empty."""
        mock_load_config.return_value = {"projects": {}}
        projects = get_project_list()
        mock_load_config.assert_called_once()
        self.assertEqual(projects, [])


if __name__ == '__main__':
    unittest.main() 