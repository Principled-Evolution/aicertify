import os
import sys
import json
from typing import Dict, Any, Optional
from pathlib import Path
import datetime
import uuid

# Add the parent directory to the path so we can import aicertify
sys.path.append(str(Path(__file__).parent.parent))

class Contract:
    """Simplified Contract class for testing context serialization."""
    
    def __init__(
        self,
        context: Dict[str, Any],
        model_id: str,
        interaction_type: str,
        contract_id: Optional[str] = None,
        created_at: Optional[datetime.datetime] = None
    ):
        self.context = context
        self.model_id = model_id
        self.interaction_type = interaction_type
        self.contract_id = contract_id or str(uuid.uuid4())
        self.created_at = created_at or datetime.datetime.now()
        self.interactions = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert contract to dictionary."""
        return {
            "contract_id": self.contract_id,
            "context": self.context,
            "model_id": self.model_id,
            "interaction_type": self.interaction_type,
            "created_at": self.created_at.isoformat(),
            "interactions": [i.to_dict() for i in self.interactions] if self.interactions else []
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Contract':
        """Create contract from dictionary."""
        created_at = datetime.datetime.fromisoformat(data["created_at"]) if "created_at" in data else None
        contract = cls(
            context=data.get("context", {}),
            model_id=data.get("model_id", ""),
            interaction_type=data.get("interaction_type", ""),
            contract_id=data.get("contract_id"),
            created_at=created_at
        )
        
        # Add interactions if present
        if "interactions" in data and data["interactions"]:
            for interaction_data in data["interactions"]:
                interaction = Interaction.from_dict(interaction_data)
                contract.interactions.append(interaction)
        
        return contract

class Interaction:
    """Simplified Interaction class for testing."""
    
    def __init__(
        self,
        role: str,
        content: str,
        timestamp: Optional[datetime.datetime] = None
    ):
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert interaction to dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Interaction':
        """Create interaction from dictionary."""
        timestamp = datetime.datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else None
        return cls(
            role=data.get("role", ""),
            content=data.get("content", ""),
            timestamp=timestamp
        )

def create_medical_context(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create medical context from patient data."""
    context = {
        "patient_id": str(uuid.uuid4()),
        "demographics": {
            "age": patient_data.get("age"),
            "gender": patient_data.get("gender"),
        },
        "medical_data": {
            "symptoms": patient_data.get("symptoms", []),
            "medical_history": patient_data.get("medical_history", []),
            "current_medications": patient_data.get("current_medications", []),
            "allergies": patient_data.get("allergies", []),
            "vital_signs": patient_data.get("vital_signs", {}),
            "lab_results": patient_data.get("lab_results", {})
        },
        "consent": {
            "data_processing": True,
            "medical_advice": True,
            "timestamp": datetime.datetime.now().isoformat()
        },
        "analysis_purpose": "medical_diagnosis"
    }
    return context

def create_contract(
    context: Dict[str, Any],
    model_id: str,
    interaction_type: str
) -> Contract:
    """Create a contract with the given context."""
    return Contract(
        context=context,
        model_id=model_id,
        interaction_type=interaction_type
    )

def save_contract(contract: Contract, filepath: str) -> None:
    """Save contract to JSON file."""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Convert contract to dictionary
    contract_dict = contract.to_dict()
    
    # Save to file
    with open(filepath, "w") as f:
        json.dump(contract_dict, f, indent=2)

def load_contract(filepath: str) -> Contract:
    """Load contract from JSON file."""
    with open(filepath, "r") as f:
        contract_dict = json.load(f)
    
    return Contract.from_dict(contract_dict)

def main():
    """Test context serialization and deserialization."""
    # Create test patient data
    patient_data = {
        "name": "John Doe",
        "age": 45,
        "gender": "male",
        "symptoms": ["fever", "cough", "fatigue"],
        "medical_history": ["hypertension"],
        "current_medications": ["lisinopril"],
        "allergies": ["penicillin"],
        "vital_signs": {
            "temperature": 101.2,
            "heart_rate": 88,
            "blood_pressure": "130/85",
            "respiratory_rate": 18,
            "oxygen_saturation": 96
        },
        "lab_results": {
            "white_blood_cell_count": 11200,
            "c_reactive_protein": 15.3,
            "d_dimer": 0.5
        }
    }
    
    # Create medical context
    context = create_medical_context(patient_data)
    print(f"Created medical context with {len(context)} fields")
    
    # Create contract
    contract = create_contract(
        context=context,
        model_id="gpt-4",
        interaction_type="medical_diagnosis"
    )
    print(f"Created contract with ID: {contract.contract_id}")
    
    # Add an example interaction
    interaction = Interaction(
        role="system",
        content="You are an AI medical assistant. Provide a differential diagnosis based on the patient's symptoms.",
        timestamp=datetime.datetime.now()
    )
    contract.interactions.append(interaction)
    
    # Save contract to file
    output_dir = Path(__file__).parent / "outputs" / "test"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = output_dir / f"{contract.contract_id}.json"
    save_contract(contract, filepath)
    print(f"Saved contract to {filepath}")
    
    # Load contract from file
    loaded_contract = load_contract(filepath)
    print(f"Loaded contract with ID: {loaded_contract.contract_id}")
    
    # Compare contexts
    original_context = contract.context
    loaded_context = loaded_contract.context
    
    print("\nComparing contexts:")
    print(f"Original context keys: {list(original_context.keys())}")
    print(f"Loaded context keys: {list(loaded_context.keys())}")
    
    # Deep comparison of contexts
    context_match = True
    for key in original_context:
        if key not in loaded_context:
            print(f"Key missing in loaded context: {key}")
            context_match = False
        elif original_context[key] != loaded_context[key]:
            print(f"Value mismatch for key '{key}':")
            print(f"  Original: {original_context[key]}")
            print(f"  Loaded: {loaded_context[key]}")
            context_match = False
    
    if context_match:
        print("\nSUCCESS: All context keys and values match between original and loaded contracts!")
    else:
        print("\nFAILURE: Context mismatch between original and loaded contracts.")
    
    # Extract the context only and save it separately
    context_filepath = output_dir / "context_only.json"
    with open(context_filepath, "w") as f:
        json.dump(context, f, indent=2)
    print(f"Saved context separately to {context_filepath}")
    
    # Load the context back
    with open(context_filepath, "r") as f:
        loaded_context_only = json.load(f)
    
    # Compare the context data
    context_only_match = context == loaded_context_only
    if context_only_match:
        print("SUCCESS: Context saved and loaded separately matches perfectly!")
    else:
        print("FAILURE: Context mismatch when saved and loaded separately.")

if __name__ == "__main__":
    main() 