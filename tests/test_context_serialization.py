#!/usr/bin/env python
"""
Test script to verify context serialization in contracts
"""

import os
import json
from pathlib import Path

from aicertify.context_helpers import create_medical_context
from aicertify.models.contract_models import create_contract, save_contract, load_contract
from pydantic import BaseModel

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
    print(f"Original context: {json.dumps(medical_context, indent=2)}")
    print(f"Loaded context: {json.dumps(loaded_contract.context, indent=2)}") 