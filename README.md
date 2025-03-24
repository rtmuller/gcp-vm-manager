# GCP VM Manager

[![Python Tests](https://github.com/yourusername/gcp-vm-manager/actions/workflows/python-tests.yml/badge.svg)](https://github.com/yourusername/gcp-vm-manager/actions/workflows/python-tests.yml)
[![codecov](https://codecov.io/gh/yourusername/gcp-vm-manager/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/gcp-vm-manager)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A powerful command-line utility for managing Google Cloud Platform (GCP) Virtual Machines and Cloud Run instances. This tool provides an interactive interface for common GCP operations, making it easier to manage your cloud resources.

## Features

- Interactive menu with real-time VM status
- Quick SSH access to VMs
- Common VM operations (start, stop, reset)
- View VM details and logs
- Transfer files to/from VMs
- Run commands on VMs remotely
- Project-wide operations
- SSH access to Cloud Run instances
- Rich terminal interface with color support
- Debug mode for troubleshooting
- Project management (add, remove, list projects)

## Prerequisites

- Python 3.8 or higher
- Google Cloud SDK installed and configured
- Appropriate GCP permissions

## Installation

### From PyPI (Recommended)

```bash
pip install gcp-vm-manager
```

### From Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gcp-vm-manager.git
cd gcp-vm-manager
```

2. Install the package:
```bash
pip install -e .
```

3. Set up your configuration:
```bash
cp config.json.template config.json
```

## Usage

Run the tool:

```bash
# If installed from PyPI
gcp-vm-manager

# If installed from source
python gcp-vm-manager.py
```

### Command Line Options

- `--version`: Show version information
- `--debug`: Enable debug mode for additional logging
- `--no-color`: Disable colored output
- `--config`: Specify path to custom config file (e.g., `--config /path/to/my-config.json`)

## Configuration

The script uses your GCP configuration from the Google Cloud SDK. Make sure you have:

1. Authenticated with GCP:
```bash
gcloud auth login
```

2. Set up your project:
```bash
gcloud config set project YOUR_PROJECT_ID
```

### Project Management

The tool uses a `config.json` file to store your project configurations. You can manage your projects through the interactive menu:

1. Select "Manage Projects" from the main menu
2. Choose from the following options:
   - List configured projects
   - Add new project
   - Remove project

The configuration file is automatically created when you first run the tool. You can also manually edit the `config.json` file to add or remove projects.

### Private Data Protection

This tool is designed to protect your private information:

1. The `config.json` file is not tracked in git (it's in `.gitignore`)
2. A template file (`config.json.template`) is provided as a reference
3. All project names and VM information are fetched dynamically from GCP
4. No sensitive information is stored in the code

## Testing

The project includes comprehensive unit tests and test coverage reporting.

### Running Tests

To run all tests:

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run tests
python -m unittest discover -s tests
```

### Coverage Reports

To generate coverage reports:

```bash
# Run tests with coverage
python run_coverage.py
```

This will:
1. Run all unit tests
2. Generate a console coverage report showing the percentage of code covered
3. Create an HTML coverage report in the `htmlcov` directory
4. Generate an XML coverage report for CI tools

### Test Structure

- `tests/test_config.py`: Tests for configuration functions
- `tests/test_commands.py`: Tests for command execution functions
- `tests/test_vm_operations.py`: Tests for VM operations

## Features in Detail

### VM Management
- List all VMs in a project
- View VM status and details
- Start/Stop/Reset VMs
- SSH into VMs
- Upload/Download files
- Run remote commands

### Cloud Run Management
- List Cloud Run services
- View service details and logs
- SSH into Cloud Run instances
- Debug Cloud Run services

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

When contributing, please:
1. Add tests for any new features
2. Ensure all tests pass
3. Make sure code coverage remains high

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Security

For information about reporting security vulnerabilities and supported versions, please see [SECURITY.md](SECURITY.md).

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed list of changes in each release.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Rafael

## Acknowledgments

- Google Cloud Platform
- Rich library for terminal formatting
- Colorama for cross-platform color support 