#!/usr/bin/env python3
"""
Script to run all tests and generate coverage reports for GCP VM Manager.
"""

import os
import sys
import unittest
import coverage
import importlib.util

def main():
    """Run all tests and generate coverage reports."""
    # Ensure the module is imported before testing
    module_path = os.path.join(os.path.dirname(__file__), 'gcp_vm_manager.py')
    
    # Dynamically import the module to ensure coverage tracks it
    spec = importlib.util.spec_from_file_location("gcp_vm_manager", module_path)
    gcp_vm_manager = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gcp_vm_manager)
    
    # Start coverage measurement
    cov = coverage.Coverage(
        source=["gcp_vm_manager.py"],
        omit=["*/__pycache__/*", "*/test_*.py", "run_tests.py"],
        branch=True
    )
    cov.start()

    # Discover and run tests
    loader = unittest.TestLoader()
    tests_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(tests_dir)

    print("Running tests...")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Stop coverage measurement
    cov.stop()
    cov.save()

    # Generate reports
    print("\nGenerating coverage reports...")
    try:
        cov.report()
        
        # Generate HTML report
        html_dir = os.path.join(os.path.dirname(__file__), 'htmlcov')
        cov.html_report(directory=html_dir)
        print(f"HTML coverage report generated in {html_dir}")
        
        # Generate XML report for CI tools
        xml_file = os.path.join(os.path.dirname(__file__), 'coverage.xml')
        cov.xml_report(outfile=xml_file)
        print(f"XML coverage report generated: {xml_file}")
    except Exception as e:
        print(f"Error generating coverage reports: {str(e)}")

    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(main()) 