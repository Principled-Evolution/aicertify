#!/usr/bin/env python3
"""
Debug script for evaluating contracts against EU AI Act policies.

This script loads an existing contract and evaluates it against the EU AI Act policies
using the folder-based approach. It's designed to help debug and test the EU AI Act
policy integration in the AICertify framework.
"""

import os
import sys
import json
import glob
import asyncio
import logging
import traceback
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# Add the parent directory to the path so we can import from aicertify
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aicertify.api import (
    evaluate_contract_by_folder,
    load_contract,
)


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("debug_policy_evaluation_eu_ai_act.log"),
    ],
)
logger = logging.getLogger("debug_policy_evaluation_eu_ai_act")

# Custom JSON encoder to handle UUID and other non-serializable objects
class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle UUID and other non-serializable objects."""
    
    def default(self, obj):
        """Convert non-serializable objects to strings."""
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

async def debug_evaluation_metrics(evaluation_result: Dict[str, Any]) -> None:
    """
    Debug the evaluation metrics by printing them to the console.
    
    Args:
        evaluation_result: The evaluation result to debug
    """
    logger.info("Debugging evaluation metrics...")
    
    # Check if we have phase1_results
    if "phase1_results" in evaluation_result:
        phase1_results = evaluation_result["phase1_results"]
        logger.info("Phase 1 evaluation results:")
        
        # Check if we have results
        if "results" in phase1_results:
            results = phase1_results["results"]
            logger.info(f"Results keys: {list(results.keys())}")
            
            # Check for fairness results
            if "fairness" in results:
                fairness = results["fairness"]
                logger.info(f"Fairness result: {fairness}")
            
            # Check for toxicity results
            if "toxicity" in results:
                toxicity = results["toxicity"]
                logger.info(f"Toxicity result: {toxicity}")
            
            # Check for accuracy results
            if "accuracy" in results:
                accuracy = results["accuracy"]
                logger.info(f"Accuracy result: {accuracy}")
    
    # Check if we have opa_results
    if "opa_results" in evaluation_result:
        opa_results = evaluation_result["opa_results"]
        logger.info("OPA evaluation results:")
        logger.info(f"OPA result keys: {list(opa_results.keys())}")
        
        # Check if we have result
        if "result" in opa_results:
            result = opa_results["result"]
            logger.info(f"OPA result has {len(result)} items")
            
            # Check the first result
            if len(result) > 0:
                first_result = result[0]
                logger.info(f"First result keys: {list(first_result.keys())}")
                
                # Check if we have expressions
                if "expressions" in first_result:
                    expressions = first_result["expressions"]
                    logger.info(f"Expressions has {len(expressions)} items")
                    
                    # Check the first expression
                    if len(expressions) > 0:
                        first_expr = expressions[0]
                        logger.info(f"First expression keys: {list(first_expr.keys())}")
                        
                        # Check if we have value
                        if "value" in first_expr:
                            value = first_expr["value"]
                            logger.info(f"Value keys: {list(value.keys())}")
                            
                            # Check for version keys (v1, v2, etc.)
                            version_keys = [k for k in value.keys() if k.startswith("v")]
                            logger.info(f"Found version keys: {version_keys}")
                            
                            # Check each version
                            for version_key in version_keys:
                                version_data = value[version_key]
                                logger.info(f"Version {version_key} has {len(version_data)} policies")
                                
                                # Log each policy
                                for policy_name, policy_data in version_data.items():
                                    has_compliance_report = "compliance_report" in policy_data
                                    logger.info(f"Policy {policy_name} has compliance_report: {has_compliance_report}")
                                    
                                    # Log compliance report details
                                    if has_compliance_report:
                                        compliance_report = policy_data["compliance_report"]
                                        logger.info(f"Compliance report keys: {list(compliance_report.keys())}")
                                        
                                        # Log compliance status
                                        if "compliant" in compliance_report:
                                            compliant = compliance_report["compliant"]
                                            logger.info(f"Policy {policy_name} compliant: {compliant}")
                                        
                                        # Log reason
                                        if "reason" in compliance_report:
                                            reason = compliance_report["reason"]
                                            logger.info(f"Policy {policy_name} reason: {reason}")

async def evaluate_contract_only(contract_path: str, output_dir: str, report_format: str = "markdown") -> None:
    """
    Load an existing contract file and run evaluation against EU AI Act policies.
    
    Args:
        contract_path: Path to the existing contract JSON file
        output_dir: Directory to save the evaluation reports
        report_format: Format for the report (markdown or pdf)
    """
    logger.debug(f"Starting contract evaluation from file: {contract_path}")
    logger.debug(f"Output directory: {output_dir}")
    logger.debug(f"Report format: {report_format}")
    
    try:
        # Load the existing contract
        logger.debug(f"Attempting to load contract from: {contract_path}")
        contract = load_contract(contract_path)
        logger.info(f"Contract loaded successfully: {contract.application_name}")
        logger.debug(f"Contract ID: {contract.contract_id}")
        logger.debug(f"Number of interactions: {len(contract.interactions)}")
        
        # For EU AI Act evaluation, we use the 'eu_ai_act' policy folder
        policy_folder = "eu_ai_act"
        logger.info(f"Using policy_folder: {policy_folder}")
        
        # Log contract context details
        logger.debug("Contract context details:")
        for key, value in contract.context.items():
            if isinstance(value, dict) and len(value) > 10:
                logger.debug(f"  {key}: <class '{type(value).__name__}'> with {len(value)} items")
            else:
                logger.debug(f"  {key}: {value}")
        
        # Phase 1 evaluators and OPA policy evaluation
        logger.info("Starting contract evaluation with EU AI Act policies and Phase 1 evaluators...")
        
        # Use the folder-based evaluation function
        eval_result = await asyncio.wait_for(
            evaluate_contract_by_folder(
                contract=contract,
                policy_folder=policy_folder,
                generate_report=True,
                report_format=report_format,
                output_dir=output_dir,
            ),
            timeout=120
        )
        
        logger.info("Contract evaluation complete")
        logger.debug(f"Evaluation result keys: {eval_result.keys()}")
        
        # Debug the evaluation metrics
        await debug_evaluation_metrics(eval_result)
        
        # Add debug statement to check what policies are being extracted
        if "opa_results" in eval_result and "result" in eval_result["opa_results"] and isinstance(eval_result["opa_results"]["result"], list) and len(eval_result["opa_results"]["result"]) > 0:
            first_result = eval_result["opa_results"]["result"][0]
            if "expressions" in first_result and len(first_result["expressions"]) > 0:
                first_expr = first_result["expressions"][0]
                if "value" in first_expr:
                    logger.info("Policies in OPA results:")
                    for version_key, version_data in first_expr["value"].items():
                        if isinstance(version_data, dict):
                            logger.info(f"  Version: {version_key}")
                            for policy_name, policy_data in version_data.items():
                                has_compliance_report = "compliance_report" in policy_data
                                logger.info(f"    Policy: {policy_name} (has compliance report: {has_compliance_report})")
        
        # After evaluating all policies, add this debug code
        logger.info("=== OPA Results Structure ===")
        if "opa_results" in eval_result and "result" in eval_result["opa_results"] and isinstance(eval_result["opa_results"]["result"], list) and len(eval_result["opa_results"]["result"]) > 0:
            first_result = eval_result["opa_results"]["result"][0]
            if "expressions" in first_result and len(first_result["expressions"]) > 0:
                first_expr = first_result["expressions"][0]
                if "value" in first_expr:
                    logger.info(f"OPA results value keys: {list(first_expr['value'].keys())}")
                    
                    # Log all policies in each version
                    for version_key, version_data in first_expr["value"].items():
                        if isinstance(version_data, dict):
                            logger.info(f"  Version: {version_key}, Policies: {list(version_data.keys())}")
                            
                            # Check if policies have compliance_report
                            for policy_name, policy_data in version_data.items():
                                has_compliance_report = "compliance_report" in policy_data
                                logger.info(f"    Policy: {policy_name}, Has compliance_report: {has_compliance_report}")
        
        # Dump the raw evaluation results to a file for inspection
        dump_path = os.path.join(output_dir, "raw_evaluation_results.json")
        with open(dump_path, "w") as f:
            json.dump(eval_result, f, indent=2, cls=CustomJSONEncoder)
        logger.info(f"Dumped raw evaluation results to {dump_path}")
        
        if eval_result.get('report_path'):
            logger.info(f"Evaluation report saved to: {eval_result.get('report_path')}")
        else:
            logger.warning("No report path returned, checking for report content...")
            
            if eval_result.get('report'):
                report_content = eval_result.get('report')
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                fallback_path = os.path.join(output_dir, f"report_{timestamp}.md")
                with open(fallback_path, "w") as f:
                    f.write(report_content)
                logger.info(f"Report content saved to fallback location: {fallback_path}")
            else:
                logger.error("No report content available in evaluation result")

    except asyncio.TimeoutError:
        logger.error("Evaluation timed out after 120 seconds")
    except Exception as e:
        logger.error(f"Error during evaluation: {str(e)}")
        logger.error(traceback.format_exc()) 

def main() -> None:
    """Main function to run the EU AI Act policy evaluation."""
    logger.info("Starting debug_policy_evaluation_eu_ai_act execution...")

    # Load environment variables
    load_dotenv()

    # Set up cache directory for SentenceTransformer (if needed)
    if os.name == "nt":
        cache_dir = os.path.expanduser("~/AppData/Local/aicertify/transformers_cache")
    else:
        cache_dir = os.path.expanduser("~/.cache/aicertify/transformers_cache")
    os.makedirs(cache_dir, exist_ok=True)
    os.environ["TRANSFORMERS_CACHE"] = cache_dir

    logger.info("About to load SentenceTransformer model...")
    SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", cache_folder=cache_dir)
    logger.info("SentenceTransformer model loaded")

    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Create output directory for EU AI Act evaluations
    output_dir = script_dir / "outputs" / "eu_ai_act"
    os.makedirs(output_dir, exist_ok=True)
    
    # Look for contract files in the medical_diagnosis directory (for testing)
    # In a real scenario, you would use contracts specific to your use case
    contract_storage = script_dir / "outputs" / "medical_diagnosis"

    logger.debug(f"Looking for contract files in: {contract_storage}")
    contract_files = glob.glob(str(contract_storage / "contract_*.json"))
    if not contract_files:
        logger.error(f"No contract files found in {contract_storage}")
        sys.exit(1)
    
    logger.debug(f"Found {len(contract_files)} contract files")
    contract_files.sort(key=os.path.getmtime, reverse=True)
    latest_contract = contract_files[0]

    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Script directory: {script_dir}")
    logger.info(f"Contract storage directory: {contract_storage}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Using most recent contract file: {latest_contract}")

    try:
        logger.info("Starting asyncio event loop for contract evaluation")
        asyncio.run(evaluate_contract_only(
            contract_path=latest_contract,
            output_dir=str(output_dir),
            report_format="pdf"
        ))
        logger.info("Contract evaluation completed successfully")
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main() 