"""
Test script for AICertify simplified evaluation functionality

This script tests the simplified evaluator functionality to verify that
it works correctly in isolation from more complex dependencies.
"""

import asyncio
import json
import logging
from pathlib import Path


# Import necessary components
from aicertify.models.contract_models import create_contract, save_contract
from aicertify.evaluators.simple_evaluator import evaluate_contract_simple
from aicertify.opa_core.simple_policy import get_available_policies

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_evaluation():
    """Test the simplified evaluation functionality"""
    # Step 1: Create a simple contract
    print("Creating a test contract...")
    application_name = "TestApplication"
    model_info = {
        "model_name": "TestModel",
        "model_version": "1.0",
        "additional_info": {
            "description": "Test model for evaluation",
            "developer": "AICertify Team",
        },
    }

    interactions = [
        {
            "input_text": "Hello, how are you?",
            "output_text": "I'm doing well, thank you for asking!",
            "metadata": {"test": True},
        },
        {
            "input_text": "What's the weather like today?",
            "output_text": "I don't have access to real-time weather information.",
            "metadata": {"test": True},
        },
    ]

    contract = create_contract(
        application_name=application_name,
        model_info=model_info,
        interactions=interactions,
    )

    # Step 2: Save the contract to a file
    print("Saving contract to file...")
    tests_dir = Path(__file__).parent / "tests"
    tests_dir.mkdir(exist_ok=True)

    contract_path = save_contract(contract, storage_dir=str(tests_dir))
    print(f"Contract saved to {contract_path}")

    # Step 3: Get available policies
    print("\nAvailable policies:")
    policies = get_available_policies()
    for policy in policies:
        print(f"- {policy}")

    # Step 4: Evaluate the contract using the simplified evaluator
    print("\nEvaluating contract with simplified evaluator...")
    for policy in policies:
        print(f"\nEvaluating with policy: {policy}")
        evaluation_results = await evaluate_contract_simple(
            contract_path=contract_path, policy_category=policy
        )

        # Step 5: Print evaluation results
        print("\nEvaluation Results:")

        if "policy_results" in evaluation_results:
            policies_evaluated = evaluation_results["policy_results"][
                "policies_evaluated"
            ]
            print(f"Policy: {evaluation_results['policy_results']['policy_category']}")
            print(
                f"Description: {evaluation_results['policy_results']['policy_description']}"
            )
            print(f"Policies evaluated: {', '.join(policies_evaluated)}")
            print(
                f"Compliance level: {evaluation_results['policy_results']['overall_compliance']}"
            )

            print("\nPolicy Results:")
            for policy_result in evaluation_results["policy_results"]["policy_results"]:
                print(
                    f"- {policy_result['policy_name']}: {policy_result['compliance_level']}"
                )
                print(f"  Description: {policy_result['description']}")
                print(f"  Recommendations: {policy_result['recommendations'][0]}")
        else:
            print("No policy results available in evaluation.")

        # Step 6: Save evaluation results to file
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)

        results_path = results_dir / f"test_evaluation_{policy}.json"
        with open(results_path, "w") as f:
            json.dump(evaluation_results, f, indent=2)

        print(f"Evaluation results saved to: {results_path}")

    print("\nTest completed successfully!")


def main():
    """Run the test"""
    asyncio.run(test_evaluation())


if __name__ == "__main__":
    main()
