import os
import sys
import json
from typing import Dict, Any
from pathlib import Path

# Add the parent directory to the path so we can import aicertify
sys.path.append(str(Path(__file__).parent.parent))

# Import necessary modules from aicertify
from aicertify.models.contract_models import Contract
from aicertify.opa_core.policy_loader import PolicyLoader

# Import our OPA client
from opa_client import OpaClient


class ExternalOpaEvaluator:
    """Evaluator that connects to an external OPA server to execute policy evaluations."""

    def __init__(self, opa_url: str = "http://localhost:8182"):
        """Initialize the External OPA Evaluator.

        Args:
            opa_url: URL of the OPA server
        """
        self.client = OpaClient(opa_url)
        self.policy_loader = PolicyLoader()
        self.policies_loaded = False

    def load_policies(self) -> None:
        """Load all policies from the standard AICertify policy locations."""
        if self.policies_loaded:
            return

        # Get all policies from the policy loader
        base_dir = Path(__file__).parent.parent / "aicertify" / "opa_policies"
        policies = self.policy_loader.load_policies(str(base_dir))

        # Load each policy into the OPA server
        for policy in policies:
            policy_name = os.path.basename(policy.path)
            if policy_name.endswith(".rego"):
                policy_name = policy_name[:-5]  # Remove .rego extension

            self.client.load_policy(policy_name, policy.content)

        self.policies_loaded = True
        print(f"Loaded {len(policies)} policies into the OPA server")

    def evaluate_contract(self, contract: Contract) -> Dict[str, Any]:
        """Evaluate a contract against loaded policies.

        Args:
            contract: The contract to evaluate

        Returns:
            Dict: Evaluation results
        """
        # Ensure policies are loaded
        self.load_policies()

        # Convert contract to dictionary for evaluation
        contract_dict = contract.model_dump()

        # Evaluate the contract against all policy types
        results = {}
        policy_types = [
            "fairness",
            "security",
            "compliance",
            "regulatory",
            "operational",
        ]

        for policy_type in policy_types:
            try:
                # Evaluate each policy type
                policy_path = f"{policy_type}/evaluate"
                result = self.client.evaluate_policy(policy_path, contract_dict)
                results[policy_type] = result.get("result", {})
            except Exception as e:
                print(f"Error evaluating {policy_type} policies: {str(e)}")
                results[policy_type] = {"error": str(e)}

        return results


# Test context and contract serialization with the external OPA evaluator
if __name__ == "__main__":
    # Import functions for context and contract creation
    from aicertify.context_helpers import create_medical_context
    from aicertify.api import create_contract

    # Create a test context
    patient_data = {
        "name": "John Doe",
        "age": 45,
        "gender": "male",
        "symptoms": ["fever", "cough", "fatigue"],
        "medical_history": ["hypertension"],
    }

    # Create medical context
    context = create_medical_context(patient_data)

    # Create contract with context
    contract = create_contract(
        context=context, model_id="gpt-4", interaction_type="medical_diagnosis"
    )

    # Save the contract to a JSON file
    output_dir = Path(__file__).parent / "outputs" / "test"
    output_dir.mkdir(parents=True, exist_ok=True)

    contract_path = output_dir / "test_contract.json"
    with open(contract_path, "w") as f:
        json.dump(contract.model_dump(), f, indent=2)

    print(f"Saved contract to {contract_path}")

    # Load the contract back to verify serialization
    with open(contract_path, "r") as f:
        loaded_contract_data = json.load(f)

    # Recreate the contract from the loaded data
    from aicertify.models.contract_models import Contract as ContractModel

    loaded_contract = ContractModel.model_validate(loaded_contract_data)

    # Verify that the context was preserved
    original_context = contract.context
    loaded_context = loaded_contract.context

    print("\nComparing contexts:")
    print(f"Original context keys: {list(original_context.keys())}")
    print(f"Loaded context keys: {list(loaded_context.keys())}")

    # Compare all keys and values
    all_keys_match = True
    for key in original_context:
        if key not in loaded_context:
            print(f"Key '{key}' missing in loaded context")
            all_keys_match = False
        elif original_context[key] != loaded_context[key]:
            print(f"Value mismatch for key '{key}':")
            print(f"  Original: {original_context[key]}")
            print(f"  Loaded: {loaded_context[key]}")
            all_keys_match = False

    if all_keys_match:
        print("All context keys and values match!")

    # Initialize the external OPA evaluator
    evaluator = ExternalOpaEvaluator()

    # Try to evaluate the contract (this may fail if OPA server is not running)
    try:
        print("\nEvaluating contract against policies...")
        results = evaluator.evaluate_contract(loaded_contract)
        print("Evaluation results:")
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f"Error during evaluation: {str(e)}")
