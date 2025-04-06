"""
Simple example of using AICertify API to evaluate a medical diagnosis contract.

This example demonstrates the most basic usage of the AICertify API.
All outputs (contracts, reports) will be generated in the examples/outputs/api_example directory.
"""

import asyncio
import os
from pathlib import Path

from aicertify.models.contract_models import AiCertifyContract
from aicertify.api import evaluate_contract_object


async def main():
    # Get the directory where this script is located
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))

    # Define output directory relative to the script directory
    output_dir = script_dir / "outputs" / "api_example"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Make sure temp_reports is also in the right place (shared with other examples)
    temp_reports = script_dir / "outputs" / "temp_reports"
    temp_reports.mkdir(parents=True, exist_ok=True)

    print(f"Script directory: {script_dir}")
    print(f"Output directory: {output_dir}")

    # Create a minimal sample contract for Medical Diagnosis
    contract = AiCertifyContract(
        contract_id="med-001",
        application_name="Medical Diagnosis",
        interactions=[
            {
                "input_text": "Patient presents with chest pain and shortness of breath.",
                "output_text": "Preliminary diagnosis pending evaluation.",
                "metadata": {"agent": "Initial"},
            }
        ],
    )

    # Trigger evaluation using the API and generate a report
    result = await evaluate_contract_object(
        contract=contract, policy_category="eu_ai_act", output_dir=str(output_dir)
    )

    # Print the evaluation and report output
    print("Evaluation Result:", result.get("evaluation"))
    print("Policy Results:", result.get("policies"))
    if result.get("report"):
        print("Report:", result.get("report"))
    if result.get("report_path"):
        print("Report saved to:", result.get("report_path"))


if __name__ == "__main__":
    asyncio.run(main())
