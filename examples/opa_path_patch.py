#!/usr/bin/env python
"""
This script patches the OPA path verification before importing AICertify modules
to ensure that the OPA executable is correctly located in the WSL environment.
"""
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Union
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG, 
                  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.debug("Script started")

# Set the OPA_PATH environment variable explicitly
OPA_PATH = "/mnt/c/opa/opa.exe"
os.environ["OPA_PATH"] = OPA_PATH
logger.debug(f"Set OPA_PATH environment variable to: {OPA_PATH}")

# Check if the OPA executable exists
if os.path.exists(OPA_PATH):
    logger.debug(f"OPA executable found at: {OPA_PATH}")
else:
    logger.error(f"OPA executable NOT found at: {OPA_PATH}")

# Create a patch for the OPA evaluator before importing it
import importlib.util
import types

logger.debug("Preparing to patch OPA evaluator")

# Define a patched version of _verify_opa_installation
def _patched_verify_opa_installation(self) -> str:
    """Patched method that always returns the specified OPA path."""
    logger.debug(f"Using patched OPA path: {OPA_PATH}")
    return OPA_PATH

try:
    # Load the evaluator module and patch it
    logger.debug("Finding aicertify.opa_core.evaluator module")
    spec = importlib.util.find_spec("aicertify.opa_core.evaluator")
    
    if spec is None:
        logger.error("Could not find aicertify.opa_core.evaluator module")
        sys.exit(1)
        
    logger.debug("Loading evaluator module")
    evaluator_module = importlib.util.module_from_spec(spec)
    
    logger.debug("Executing evaluator module")
    spec.loader.exec_module(evaluator_module)
    
    # Patch the OpaEvaluator._verify_opa_installation method
    logger.debug("Patching OpaEvaluator._verify_opa_installation method")
    evaluator_module.OpaEvaluator._verify_opa_installation = _patched_verify_opa_installation
    
    # Update the sys.modules cache
    logger.debug("Updating sys.modules cache")
    sys.modules["aicertify.opa_core.evaluator"] = evaluator_module
    
    logger.debug("OPA evaluator successfully patched")
except Exception as e:
    logger.error(f"Error patching OPA evaluator: {e}")
    raise

# Now we can safely import from AICertify
logger.debug("Importing AICertify modules")
try:
    from aicertify.context_helpers import create_medical_context
    from aicertify.models.contract_models import create_contract
    from aicertify.api import save_contract, load_contract
    logger.debug("Successfully imported AICertify modules")
except Exception as e:
    logger.error(f"Error importing AICertify modules: {e}")
    raise

# Define a test patient for context creation
test_patient = {
    "patient_id": "P12345",
    "name": "John Doe",
    "age": 45,
    "gender": "Male",
    "symptoms": "Chest pain, shortness of breath",
    "medical_history": "Hypertension, Type 2 Diabetes",
    "medications": "Lisinopril, Metformin",
    "allergies": "Penicillin",
    "vitals": {
        "blood_pressure": "140/90",
        "heart_rate": 85,
        "temperature": 98.6,
        "respiratory_rate": 16
    }
}

# Create a output directory if it doesn't exist
logger.debug("Creating output directory")
os.makedirs("outputs/test", exist_ok=True)

# Create medical context
logger.debug("Creating medical context")
context = create_medical_context(test_patient)
logger.debug(f"Created context with keys: {list(context.keys())}")
print(f"Created context: {json.dumps(context, indent=2)}")

# Create and save contract
logger.debug("Creating contract")
contract = create_contract(
    context=context,
    model_id="test-model",
    interaction_type="analysis"
)
logger.debug("Contract created successfully")

contract_path = "outputs/test/test_contract.json"
logger.debug(f"Saving contract to {contract_path}")
save_contract(contract, contract_path)
logger.debug("Contract saved successfully")
print(f"Saved contract to {contract_path}")

# Load contract and verify context
logger.debug("Loading contract")
loaded_contract = load_contract(contract_path)
logger.debug("Contract loaded successfully")
loaded_context = loaded_contract.context
logger.debug(f"Loaded context: {loaded_context}")

# Print both for comparison
print(f"Original context keys: {list(context.keys())}")
print(f"Loaded context keys: {list(loaded_context.keys() if loaded_context else {}.keys())}")

# Compare contexts
if context == loaded_context:
    logger.debug("Context comparison: MATCH")
    print("\nSUCCESS: Contexts match exactly!")
else:
    logger.warning("Context comparison: MISMATCH")
    print("\nWARNING: Contexts do not match!")
    
    # Check if loaded_context is empty
    if not loaded_context:
        logger.error("Loaded context is empty")
        print("ERROR: Loaded context is empty!")
    else:
        # Find differences
        logger.debug("Analyzing context differences")
        print("\nDifferences in keys:")
        orig_keys = set(context.keys())
        loaded_keys = set(loaded_context.keys())
        missing_keys = orig_keys - loaded_keys
        extra_keys = loaded_keys - orig_keys
        
        if missing_keys:
            logger.warning(f"Missing keys: {missing_keys}")
            print(f"Keys in original but not in loaded: {missing_keys}")
        if extra_keys:
            logger.warning(f"Extra keys: {extra_keys}")
            print(f"Keys in loaded but not in original: {extra_keys}")
        
        # Check common keys for differences
        common_keys = orig_keys.intersection(loaded_keys)
        logger.debug(f"Checking {len(common_keys)} common keys for value differences")
        print("\nDifferences in common key values:")
        for key in common_keys:
            if context[key] != loaded_context[key]:
                logger.warning(f"Value mismatch for key: {key}")
                print(f"Key '{key}' has different values:")
                print(f"  Original: {context[key]}")
                print(f"  Loaded: {loaded_context[key]}") 