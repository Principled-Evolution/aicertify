#!/usr/bin/env python
"""
AICertify CLI Wrapper

This is a simple wrapper script to run the AICertify CLI tool.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the CLI
from aicertify.cli import main

if __name__ == "__main__":
    main() 