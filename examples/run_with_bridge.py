#!/usr/bin/env python
"""
This script runs another script with the OPA bridge set up.
It first sets up the WSL-OPA bridge, then runs the specified script.
"""
import os
import sys
import subprocess
from pathlib import Path

# Import the bridge setup
from wsl_opa_bridge import main as setup_bridge

def run_script(script_path):
    """Run a script with the OPA bridge."""
    print(f"\n==== RUNNING SCRIPT WITH OPA BRIDGE: {script_path} ====")
    
    try:
        # Run the script with the current environment (which has OPA_PATH set)
        result = subprocess.run(
            ["poetry", "run", "python", script_path],
            env=os.environ,
            check=True
        )
        print(f"\n==== SCRIPT COMPLETED WITH EXIT CODE: {result.returncode} ====")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n==== SCRIPT FAILED WITH EXIT CODE: {e.returncode} ====")
        return False
    except Exception as e:
        print(f"\n==== SCRIPT FAILED WITH ERROR: {str(e)} ====")
        return False

def main():
    """Main function."""
    # Set up the WSL-OPA bridge
    if not setup_bridge():
        print("Failed to set up the WSL-OPA bridge")
        return False
    
    # Check if a script path is provided
    if len(sys.argv) < 2:
        print("Usage: python run_with_bridge.py <script_path>")
        return False
    
    script_path = sys.argv[1]
    if not os.path.exists(script_path):
        print(f"Script not found: {script_path}")
        return False
    
    # Run the script
    return run_script(script_path)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 