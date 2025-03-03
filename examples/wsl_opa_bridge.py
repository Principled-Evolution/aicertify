#!/usr/bin/env python
"""
This script provides a bridge to run OPA in WSL environment.
It creates a wrapper script that correctly invokes the Windows OPA executable
from within WSL.
"""
import os
import sys
import json
from pathlib import Path
import subprocess
import shutil

# Constants
OPA_WINDOWS_PATH = "/mnt/c/opa/opa.exe"
WRAPPER_SCRIPT_PATH = os.path.join(os.getcwd(), "opa_wsl_wrapper.sh")

def create_wrapper_script():
    """Create a wrapper script that can be used to invoke the Windows OPA executable."""
    script_content = f"""#!/bin/bash
# This is a wrapper script to call the Windows OPA executable from WSL
# It translates paths and arguments as needed

# Check if arguments are provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 [opa arguments]"
    exit 1
fi

# Convert the first argument (usually a filepath) from WSL path to Windows path if it exists
if [ -f "$1" ]; then
    # Convert to Windows path if it's a file
    WINPATH=$(wslpath -w "$1")
    shift
    # Run OPA with the Windows path
    {OPA_WINDOWS_PATH} "$WINPATH" "$@"
else
    # Just pass all arguments directly
    {OPA_WINDOWS_PATH} "$@"
fi
"""
    
    with open(WRAPPER_SCRIPT_PATH, "w") as f:
        f.write(script_content)
    
    # Make the script executable
    os.chmod(WRAPPER_SCRIPT_PATH, 0o755)
    print(f"Created wrapper script at {WRAPPER_SCRIPT_PATH}")
    
    # Add the script to PATH
    os.environ["PATH"] = os.getcwd() + ":" + os.environ.get("PATH", "")
    print(f"Added wrapper script directory to PATH")
    
    return WRAPPER_SCRIPT_PATH

def verify_wrapper():
    """Verify that the wrapper script works."""
    try:
        result = subprocess.run([WRAPPER_SCRIPT_PATH, "version"], 
                               capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Wrapper script works! Output: \n{result.stdout.strip()}")
            return True
        else:
            print(f"❌ Wrapper script failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception running wrapper script: {str(e)}")
        return False

def set_opa_path_env():
    """Set the OPA_PATH environment variable to the wrapper script."""
    os.environ["OPA_PATH"] = WRAPPER_SCRIPT_PATH
    print(f"✅ Set OPA_PATH environment variable to: {WRAPPER_SCRIPT_PATH}")

def main():
    """Main function to set up the WSL-OPA bridge."""
    print("\n==== SETTING UP WSL-OPA BRIDGE ====")
    
    # Check if OPA exists
    if not os.path.exists(OPA_WINDOWS_PATH):
        print(f"❌ OPA executable not found at {OPA_WINDOWS_PATH}")
        return False
    
    print(f"✅ Found OPA executable at {OPA_WINDOWS_PATH}")
    
    # Create wrapper script
    wrapper_path = create_wrapper_script()
    
    # Verify the wrapper works
    if not verify_wrapper():
        print("❌ Wrapper verification failed")
        return False
    
    # Set OPA_PATH environment variable
    set_opa_path_env()
    
    print("\n==== WSL-OPA BRIDGE SETUP COMPLETE ====")
    print("You can now run scripts that depend on OPA.")
    print(f"The OPA_PATH environment variable is set to: {os.environ.get('OPA_PATH')}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 