#!/usr/bin/env python
"""
Minimal context serialization test that bypasses OPA initialization.
This script directly extracts the relevant context handling components
without importing the full AICertify package.
"""
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timezone
import uuid

# Create output directories
os.makedirs("outputs/test", exist_ok=True)

# Minimal context and contract models
class Contract:
    """Minimal implementation of the Contract model for testing serialization."""
    def __init__(
        self,
        context: Dict[str, Any],
        model_id: str,
        interaction_type: str,
        contract_id: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        self.context = context
        self.model_id = model_id
        self.interaction_type = interaction_type
        self.contract_id = contract_id or str(uuid.uuid4())
        self.created_at = created_at or datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "contract_id": self.contract_id,
            "model_id": self.model_id,
            "interaction_type": self.interaction_type,
            "context": self.context,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Contract':
        """Create Contract from dictionary."""
        context = data.get("context", {})
        created_at = datetime.fromisoformat(data.get("created_at"))
        
        return cls(
            context=context,
            model_id=data.get("model_id"),
            interaction_type=data.get("interaction_type"),
            contract_id=data.get("contract_id"),
            created_at=created_at
        )

# Context creation function
def create_medical_context(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create medical context for testing."""
    context = {
        "domain": "healthcare",
        "patient_id": patient_data.get("patient_id", ""),
        "demographics": {
            "age": patient_data.get("age", 0),
            "gender": patient_data.get("gender", ""),
        },
        "medical_history": patient_data.get("medical_history", ""),
        "symptoms": patient_data.get("symptoms", ""),
        "medications": patient_data.get("medications", ""),
        "allergies": patient_data.get("allergies", ""),
        "vitals": patient_data.get("vitals", {}),
        "risk_factors": [
            {"type": "medical_history", "description": patient_data.get("medical_history", "")},
            {"type": "demographic", "description": f"Age: {patient_data.get('age', 0)}, Gender: {patient_data.get('gender', '')}"}
        ],
        "governance": {
            "healthcare_regulations": ["HIPAA", "HITECH"],
            "patient_consent": True,
            "data_retention_policy": "Standard medical record retention policy applies"
        }
    }
    return context

# Contract creation function
def create_contract(
    context: Dict[str, Any],
    model_id: str,
    interaction_type: str
) -> Contract:
    """Create a test contract."""
    return Contract(
        context=context,
        model_id=model_id,
        interaction_type=interaction_type
    )

# Save contract function
def save_contract(contract: Contract, filepath: str) -> None:
    """Save contract to JSON file."""
    contract_dict = contract.to_dict()
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(contract_dict, f, indent=2)
        
    print(f"Contract saved to {filepath}")

# Load contract function
def load_contract(filepath: str) -> Contract:
    """Load contract from JSON file."""
    with open(filepath, 'r') as f:
        contract_dict = json.load(f)
    
    return Contract.from_dict(contract_dict)

# Test patient data
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

# Test context serialization
print("Creating medical context...")
context = create_medical_context(test_patient)
print(f"Created context: {json.dumps(context, indent=2)}")

# Create and save contract
print("\nCreating and saving contract...")
contract = create_contract(
    context=context,
    model_id="test-model",
    interaction_type="analysis"
)
contract_path = "outputs/test/test_contract.json"
save_contract(contract, contract_path)

# Load contract and verify context
print("\nLoading contract and verifying context...")
loaded_contract = load_contract(contract_path)
loaded_context = loaded_contract.context

# Print both for comparison
print(f"Original context keys: {list(context.keys())}")
print(f"Loaded context keys: {list(loaded_context.keys() if loaded_context else {}.keys())}")

# Compare contexts
if context == loaded_context:
    print("\nSUCCESS: Contexts match exactly!")
else:
    print("\nWARNING: Contexts do not match!")
    
    # Check if loaded_context is empty
    if not loaded_context:
        print("ERROR: Loaded context is empty!")
    else:
        # Find differences
        print("\nDifferences in keys:")
        orig_keys = set(context.keys())
        loaded_keys = set(loaded_context.keys())
        missing_keys = orig_keys - loaded_keys
        extra_keys = loaded_keys - orig_keys
        
        if missing_keys:
            print(f"Keys in original but not in loaded: {missing_keys}")
        if extra_keys:
            print(f"Keys in loaded but not in original: {extra_keys}")
        
        # Check common keys for differences
        common_keys = orig_keys.intersection(loaded_keys)
        print("\nDifferences in common key values:")
        for key in common_keys:
            if context[key] != loaded_context[key]:
                print(f"Key '{key}' has different values:")
                print(f"  Original: {context[key]}")
                print(f"  Loaded: {loaded_context[key]}") 