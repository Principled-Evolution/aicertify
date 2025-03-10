import os
import sys
import json
import argparse
from typing import Dict, Any, List, Optional
from pathlib import Path
import datetime

# Add the parent directory to the path so we can import aicertify
sys.path.append(str(Path(__file__).parent.parent))

# Import necessary modules from aicertify
from aicertify.context_helpers import create_medical_context
from aicertify.api import create_contract
from aicertify.models.contract_models import Contract, Interaction
from aicertify.models.report_models import EvaluationReport

# Import our external OPA evaluator
from external_opa_evaluator import ExternalOpaEvaluator

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Medical Diagnosis with External OPA")
    parser.add_argument("--capture-contract", action="store_true", 
                      help="Whether to save the contract to a file")
    parser.add_argument("--report-format", choices=["json", "markdown", "pdf"], default="json",
                      help="Format for the evaluation report")
    return parser.parse_args()

def main():
    """Run the medical diagnosis example with external OPA evaluator."""
    args = parse_args()
    
    # Sample patient case
    patient_case = {
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
    context = create_medical_context(patient_case)
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
    
    interaction = Interaction(
        role="user",
        content="What are the possible diagnoses for this patient? List the top 3 possibilities.",
        timestamp=datetime.datetime.now()
    )
    contract.interactions.append(interaction)
    
    interaction = Interaction(
        role="assistant",
        content="""Based on the symptoms and clinical findings, here are the top 3 possible diagnoses:

1. Community-Acquired Pneumonia (CAP):
   - The fever, cough, and fatigue are classic symptoms
   - Elevated WBC count suggests infection
   - Slightly elevated CRP indicates inflammation
   
2. COVID-19:
   - Presents with fever, cough, and fatigue
   - Can occur despite vaccination status
   - Would need PCR or antigen testing to confirm

3. Acute Bronchitis:
   - Common cause of cough with fever
   - Usually viral in origin
   - May be exacerbated by the patient's history of hypertension

I recommend a chest X-ray to look for infiltrates consistent with pneumonia, COVID testing, and possibly sputum culture if indicated. The patient should be monitored closely given their age and hypertension history.""",
        timestamp=datetime.datetime.now()
    )
    contract.interactions.append(interaction)
    
    # Save the contract if requested
    if args.capture_contract:
        output_dir = Path("outputs") / "medical_diagnosis"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        contract_path = output_dir / f"{contract.contract_id}.json"
        with open(contract_path, "w") as f:
            json.dump(contract.model_dump(), f, indent=2)
        
        print(f"Saved contract to {contract_path}")
    
    # Evaluate the contract using our external OPA evaluator
    print("\nEvaluating contract against policies using external OPA server...")
    evaluator = ExternalOpaEvaluator()
    
    try:
        results = evaluator.evaluate_contract(contract)
        
        # Create evaluation report
        report = EvaluationReport(
            contract_id=contract.contract_id,
            evaluation_time=datetime.datetime.now(),
            results=results,
            summary="Medical diagnosis evaluation using external OPA server"
        )
        
        # Save the report in the requested format
        output_dir = Path("outputs") / "medical_diagnosis"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if args.report_format == "json":
            report_path = output_dir / f"{contract.contract_id}_report.json"
            with open(report_path, "w") as f:
                json.dump(report.model_dump(), f, indent=2)
            print(f"Saved JSON report to {report_path}")
            
        elif args.report_format == "markdown":
            # Simple markdown conversion
            report_path = output_dir / f"{contract.contract_id}_report.md"
            with open(report_path, "w") as f:
                f.write(f"# Evaluation Report for Contract {contract.contract_id}\n\n")
                f.write(f"Evaluation Time: {report.evaluation_time}\n\n")
                f.write(f"Summary: {report.summary}\n\n")
                f.write("## Results\n\n")
                
                for policy_type, result in results.items():
                    f.write(f"### {policy_type.capitalize()}\n\n")
                    f.write("```json\n")
                    f.write(json.dumps(result, indent=2))
                    f.write("\n```\n\n")
            
            print(f"Saved Markdown report to {report_path}")
            
        elif args.report_format == "pdf":
            # PDF generation would typically go here
            # For simplicity, we'll just note that this would be implemented
            print("PDF report generation not implemented in this example")
        
    except Exception as e:
        print(f"Error during evaluation: {str(e)}")

if __name__ == "__main__":
    main() 