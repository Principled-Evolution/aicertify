#!/usr/bin/env python
"""
Test script to verify the OPA executable path and functionality.
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path
import platform

# Define potential OPA paths
OPA_PATH_WINDOWS = "C:/opa/opa_windows_amd64.exe"
OPA_PATH_WINDOWS_ALT = "C:/opa/opa.exe"
OPA_PATH_WSL = "/mnt/c/opa/opa.exe"
OPA_PATH_WSL_ALT = "/mnt/c/opa/opa_windows_amd64.exe"

def check_path(path):
    """Check if path exists and is executable."""
    if os.path.exists(path):
        print(f"✅ Path exists: {path}")
        if os.access(path, os.X_OK):
            print(f"✅ Path is executable: {path}")
        else:
            print(f"❌ Path exists but is NOT executable: {path}")
            
        # Try to run the executable with --version
        try:
            result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                print(f"✅ Successfully ran executable: {path}")
                print(f"   Version: {result.stdout.strip()}")
            else:
                print(f"❌ Failed to run executable: {path}")
                print(f"   Error: {result.stderr.strip()}")
        except Exception as e:
            print(f"❌ Exception running executable: {path}")
            print(f"   Error: {str(e)}")
    else:
        print(f"❌ Path does NOT exist: {path}")

def check_shutil_which(name):
    """Check if shutil.which can find an executable."""
    result = shutil.which(name)
    if result:
        print(f"✅ shutil.which found: {name} at {result}")
        # Check if it's executable
        try:
            os_result = subprocess.run([result, "--version"], capture_output=True, text=True, timeout=2)
            if os_result.returncode == 0:
                print(f"✅ Successfully ran executable from shutil.which: {result}")
                print(f"   Version: {os_result.stdout.strip()}")
            else:
                print(f"❌ Failed to run executable from shutil.which: {result}")
                print(f"   Error: {os_result.stderr.strip()}")
        except Exception as e:
            print(f"❌ Exception running executable from shutil.which: {result}")
            print(f"   Error: {str(e)}")
    else:
        print(f"❌ shutil.which could NOT find: {name}")

def main():
    """Main function to check OPA paths."""
    print("\n==== SYSTEM INFORMATION ====")
    print(f"Platform: {sys.platform}")
    print(f"Python version: {sys.version}")
    print(f"Platform module details: {platform.platform()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    
    print("\n==== CHECKING ENVIRONMENT ====")
    path_env = os.environ.get('PATH', '')
    print(f"PATH environment variable: {path_env}")
    
    # Check if OPA_PATH environment variable is set
    opa_path_env = os.environ.get('OPA_PATH', '')
    if opa_path_env:
        print(f"✅ OPA_PATH environment variable is set: {opa_path_env}")
    else:
        print("❌ OPA_PATH environment variable is NOT set")
    
    print("\n==== CHECKING KNOWN PATHS ====")
    check_path(OPA_PATH_WINDOWS)
    check_path(OPA_PATH_WINDOWS_ALT)
    check_path(OPA_PATH_WSL)
    check_path(OPA_PATH_WSL_ALT)
    
    # Check if OPA is in PATH
    print("\n==== CHECKING PATH ====")
    check_shutil_which("opa")
    check_shutil_which("opa.exe")
    check_shutil_which("opa_windows_amd64.exe")
    
    print("\n==== CHECKING CURRENT DIRECTORY ====")
    cwd = os.getcwd()
    print(f"Current directory: {cwd}")
    
    # List files in current directory
    print("\nFiles in current directory:")
    for file in os.listdir(cwd):
        if file.startswith("opa"):
            print(f" - {file}")
    
    # List files in /mnt/c/opa
    if os.path.exists("/mnt/c/opa"):
        print("\nFiles in /mnt/c/opa:")
        for file in os.listdir("/mnt/c/opa"):
            print(f" - {file}")
    
    if os.path.exists("C:/opa"):
        print("\nFiles in C:/opa:")
        for file in os.listdir("C:/opa"):
            print(f" - {file}")

if __name__ == "__main__":
    main() 