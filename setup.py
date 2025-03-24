#!/usr/bin/env python3
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gcp-vm-manager",
    version="1.1.0",
    author="Rafael Muller",
    author_email="your.email@example.com",
    description="A powerful command-line utility for managing GCP Virtual Machines and Cloud Run instances",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gcp-vm-manager",
    py_modules=["gcp_vm_manager"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    install_requires=[
        "colorama>=0.4.4",
        "rich>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "gcp-vm-manager=gcp_vm_manager:main",
        ],
    },
) 