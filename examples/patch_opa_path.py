#!/usr/bin/env python
"""
This script patches the OPA path verification function in AICertify
before it's called during import.
"""
import os
import sys
import builtins
import subprocess

# Set the OPA path
OPA_PATH = "/mnt/c/opa/opa.exe"
os.environ["OPA_PATH"] = OPA_PATH

# Store the original import function
original_import = builtins.__import__

# Define our patched import function
def patched_import(name, globals=None, locals=None, fromlist=(), level=0):
    """
    Patched import function that intercepts the import of OpaEvaluator
    and patches its _verify_opa_installation method.
    """
    # Call the original import
    module = original_import(name, globals, locals, fromlist, level)
    
    # Check if we're importing the OPA evaluator
    if name == "aicertify.opa_core.evaluator" or (name == "evaluator" and fromlist and "OpaEvaluator" in fromlist):
        if hasattr(module, "OpaEvaluator"):
            # Define a patched method
            def patched_verify_opa_installation(self):
                print(f"Using patched OPA path: {OPA_PATH}")
                return OPA_PATH
            
            # Apply the patch to the method
            module.OpaEvaluator._verify_opa_installation = patched_verify_opa_installation
            print(f"Successfully patched OpaEvaluator._verify_opa_installation")
    
    return module

# Replace the import function
builtins.__import__ = patched_import

# Make sure the script arguments are passed correctly
if len(sys.argv) < 2:
    print("Usage: python patch_opa_path.py <script_name> [arguments...]")
    sys.exit(1)

script_path = sys.argv[1]
script_args = sys.argv[2:]

if not os.path.exists(script_path):
    print(f"Error: Script not found - {script_path}")
    sys.exit(1)

# Run the script as a subprocess with the patched environment
try:
    cmd = ["poetry", "run", "python", script_path] + script_args
    print(f"Running command: {' '.join(cmd)}")
    
    # Pass our current environment with the OPA_PATH set
    result = subprocess.run(cmd, env=os.environ)
    sys.exit(result.returncode)
except Exception as e:
    print(f"Error running script: {e}")
    sys.exit(1) 