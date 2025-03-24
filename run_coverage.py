#!/usr/bin/env python3
"""
Script to run tests with coverage reporting for GCP VM Manager.
This script ensures proper module importing and coverage measurement.
"""

import os
import sys
import subprocess
import coverage

def main():
    """Run tests with coverage."""
    print("Setting up coverage measurement...")
    
    # Set up coverage
    cov = coverage.Coverage(
        source=["gcp_vm_manager"],
        branch=True
    )
    
    # Start coverage
    cov.start()
    
    # Import the module to ensure it's tracked
    import gcp_vm_manager
    
    # Run the tests
    print("\nRunning tests...")
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], 
                           capture_output=False)
    
    # Stop coverage
    cov.stop()
    cov.save()
    
    # Generate reports
    print("\nGenerating coverage reports...")
    cov.report()
    
    # Generate HTML report
    html_dir = "htmlcov"
    cov.html_report(directory=html_dir)
    print(f"HTML coverage report generated in {html_dir}")
    
    # Generate XML report
    xml_file = "coverage.xml"
    cov.xml_report(outfile=xml_file)
    print(f"XML coverage report generated: {xml_file}")
    
    return 0 if result.returncode == 0 else 1

if __name__ == "__main__":
    sys.exit(main()) 