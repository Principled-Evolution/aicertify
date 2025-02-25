#!/usr/bin/env python
"""
Import Diagnostic Script for AICertify

This script helps diagnose Python import path issues by:
1. Printing the Python executable being used
2. Showing the sys.path (where Python looks for imports)
3. Testing imports of key dependencies
4. Checking if packages are installed but not in the path
"""

import os
import sys
import site
import subprocess
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*80}\n{text}\n{'='*80}")

def check_package_installation(package_name):
    """Check if a package is installed using pip"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package_name],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            print(f"✅ {package_name} is installed via pip:")
            for line in result.stdout.splitlines():
                if any(key in line for key in ["Version:", "Location:", "Name:"]):
                    print(f"   {line.strip()}")
            return True
        else:
            print(f"❌ {package_name} is NOT installed via pip")
            return False
    except Exception as e:
        print(f"Error checking {package_name} installation: {e}")
        return False

def find_package_in_path(package_name):
    """Try to find a package in the Python path"""
    found = False
    for path in sys.path:
        package_path = Path(path) / package_name
        init_path = package_path / "__init__.py"
        if package_path.exists() and (init_path.exists() or list(package_path.glob("*.py"))):
            print(f"✅ Found {package_name} at: {package_path}")
            found = True
    
    if not found:
        print(f"❌ Could not find {package_name} in any Python path")
    return found

def test_import(module_name):
    """Test importing a module and print information about it"""
    try:
        module = __import__(module_name)
        print(f"✅ Successfully imported {module_name}")
        print(f"   Module location: {getattr(module, '__file__', 'Unknown')}")
        print(f"   Module version: {getattr(module, '__version__', 'Unknown')}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import {module_name}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error importing {module_name}: {type(e).__name__}: {e}")
        return False

def main():
    """Main diagnostic function"""
    print_header("PYTHON ENVIRONMENT INFORMATION")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    
    # Check environment variables
    print_header("ENVIRONMENT VARIABLES")
    for env_var in ["PYTHONPATH", "VIRTUAL_ENV", "PATH"]:
        print(f"{env_var}: {os.environ.get(env_var, 'Not set')}")
    
    # Print site-packages directories
    print_header("SITE-PACKAGES DIRECTORIES")
    for site_dir in site.getsitepackages():
        print(f"Site package dir: {site_dir}")
    print(f"User site packages: {site.getusersitepackages()}")
    
    # Print sys.path
    print_header("PYTHON SYS.PATH (IMPORT SEARCH LOCATIONS)")
    for i, path in enumerate(sys.path):
        print(f"{i+1}. {path}")
        
    # Check for specific packages
    print_header("PACKAGE INSTALLATION CHECK")
    for package in ["pydantic_ai", "langfair"]:
        check_package_installation(package)
        find_package_in_path(package)
        
    print_header("IMPORT TEST")
    for module in ["pydantic_ai", "langfair"]:
        test_import(module)
        
    # Suggest fixes
    print_header("SUGGESTIONS")
    print("If packages are installed but not importable, try these solutions:")
    print("1. Reinstall the packages: poetry add pydantic_ai langfair --force")
    print("2. Check for name conflicts with your own modules")
    print("3. Try setting PYTHONPATH explicitly: ")
    print("   $env:PYTHONPATH = (Get-Item .venv\\Lib\\site-packages).FullName  # PowerShell")
    print("   export PYTHONPATH=.venv/lib/site-packages  # Bash")
    print("4. Try a direct install with pip (in your virtual env):")
    print("   python -m pip install pydantic_ai langfair")

if __name__ == "__main__":
    main() 