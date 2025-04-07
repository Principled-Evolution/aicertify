#!/usr/bin/env python
"""
Verification script to test the quickstart example after cleanup.
This script attempts to import the necessary modules and verify that they exist.
"""

import importlib
import sys


def check_module(module_name):
    """Check if a module can be imported."""
    try:
        importlib.import_module(module_name)
        print(f"✅ Module '{module_name}' is available")
        return True
    except ImportError as e:
        print(f"❌ Module '{module_name}' is NOT available: {e}")
        return False


def main():
    """Verify that all required modules for the quickstart example are available."""
    print("Verifying required modules for quickstart example...")
    
    # Core modules needed by quickstart.py
    required_modules = [
        "aicertify",
        "aicertify.regulations",
        "aicertify.application",
        "aicertify.api",
        "aicertify.models.contract",
        "aicertify.opa_core.policy_loader",
        "aicertify.opa_core.evaluator",
        "aicertify.report_generation.report_generator",
    ]
    
    # Check each module
    all_available = True
    for module in required_modules:
        if not check_module(module):
            all_available = False
    
    # Print summary
    if all_available:
        print("\n✅ All required modules are available. The quickstart example should work.")
        print("Run it with: python examples/quickstart.py")
        return 0
    else:
        print("\n❌ Some required modules are missing. The quickstart example may not work.")
        print("Please check the errors above and ensure all dependencies are installed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
