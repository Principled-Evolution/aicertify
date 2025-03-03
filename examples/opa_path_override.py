#!/usr/bin/env python
"""
Test script that explicitly sets OPA_PATH environment variable and tests context serialization
"""

import os
import json
import sys
from pathlib import Path

# Set OPA path environment variable
os.environ["OPA_PATH"] = "/mnt/c/opa/opa.exe"

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Monkey patch the OPA verification function to always return our path
import aicertify.opa_core.evaluator as evaluator

# Save the original function
original_verify_opa = evaluator.OpaEvaluator._verify_opa_installation

# Override with a function that always returns our path
def patched_verify_opa(self):
    print(f"Using OPA at: {os.environ['OPA_PATH']}")
    return os.environ["OPA_PATH"]

# Apply the monkey patch
evaluator.OpaEvaluator._verify_opa_installation = patched_verify_opa

# Now import what we need
from aicertify.context_helpers import create_medical_context
from aicertify.models.contract_models import create_contract, save_contract, load_contract

# Define a simple test case
test_case = """**Patient Case Report**
    **Patient Information:**
    - Name: Test Patient
    - DoB: 01/01/1990
    - Sex: F
    - Weight: 150 lbs
    - Chief Complaint: Headache
"""

specialists = ["Neurologist", "General Practitioner"]

# Create the medical context
print("Creating medical context...")
medical_context = create_medical_context(test_case, specialists)
print(f"Context created: {json.dumps(medical_context, indent=2)}")

# Create a simple model info
model_info = {
    "name": "test-model",
    "version": "1.0",
    "provider": "test-provider"
}

# Create a simple interaction
interactions = [
    {
        "id": "test-interaction",
        "timestamp": "2023-01-01T00:00:00Z",
        "input": "What's the diagnosis?",
        "output": "Based on the symptoms, it could be a tension headache.",
        "metadata": {}
    }
]

# Create the contract
print("\nCreating contract...")
contract = create_contract(
    application_name="test-app",
    model_info=model_info,
    interactions=interactions,
    context=medical_context
)

# Save the contract
output_dir = Path("outputs/test")
output_dir.mkdir(parents=True, exist_ok=True)
contract_path = output_dir / "test_contract.json"

print(f"\nSaving contract to {contract_path}...")
save_contract(contract, contract_path)

# Load the contract back
print("\nLoading contract...")
loaded_contract = load_contract(contract_path)

# Check if context is preserved
print("\nChecking context in loaded contract...")
if loaded_contract.context:
    print(f"Context found in loaded contract: {json.dumps(loaded_contract.context, indent=2)}")
else:
    print("ERROR: Context is empty in loaded contract!")

# Compare original and loaded contexts
print("\nComparing original and loaded contexts...")
if loaded_contract.context == medical_context:
    print("SUCCESS: Contexts match!")
else:
    print("ERROR: Contexts don't match!")
    print(f"Original context: {type(medical_context)}")
    print(f"Loaded context: {type(loaded_contract.context)}")
    
    # Print differences in keys
    print("\nComparing context keys:")
    orig_keys = set(medical_context.keys())
    loaded_keys = set(loaded_contract.context.keys())
    
    if orig_keys == loaded_keys:
        print("Context keys match!")
    else:
        print(f"Original keys: {orig_keys}")
        print(f"Loaded keys: {loaded_keys}")
        print(f"Keys only in original: {orig_keys - loaded_keys}")
        print(f"Keys only in loaded: {loaded_keys - orig_keys}")
    
    # Compare content values
    print("\nComparing values for shared keys:")
    for key in orig_keys.intersection(loaded_keys):
        if medical_context[key] == loaded_contract.context[key]:
            print(f"Key '{key}': MATCH")
        else:
            print(f"Key '{key}': DIFFER")
            print(f"  Original: {medical_context[key]}")
            print(f"  Loaded: {loaded_contract.context[key]}") 