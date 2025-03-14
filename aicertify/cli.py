#!/usr/bin/env python
"""
AICertify Command Line Interface

This module provides a command-line interface for running AICertify evaluations.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any, Optional
os.environ["CUDA_VISIBLE_DEVICES"] = ""


from aicertify.api import aicertify_app_for_policy

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("aicertify.cli")

# Import AICertify modules
try:
    from aicertify.api import load_contract, evaluate_contract_by_folder
    from aicertify.models.contract import AiCertifyContract
except ImportError as e:
    logger.error(f"Error importing AICertify modules: {e}")
    logger.error("Make sure AICertify is installed and in your PYTHONPATH")
    sys.exit(1)

async def run_evaluation(
    contract_path: str,
    policy_folder: str,
    output_dir: Optional[str] = None,
    report_format: str = "pdf",
    evaluators: Optional[list] = None,
    custom_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Run an evaluation using the specified contract and policy folder.
    
    Args:
        contract_path: Path to the contract JSON file
        policy_folder: Path to the OPA policy folder
        output_dir: Directory to save the report
        report_format: Format of the report (json, markdown, pdf)
        evaluators: Optional list of specific evaluator names to use
        custom_params: Optional custom parameters for OPA policies
        
    Returns:
        Dictionary containing evaluation results and report paths
    """
    logger.info(f"Loading contract from {contract_path}")
    try:
        contract = load_contract(contract_path)
        logger.info(f"Loaded contract for application: {contract.application_name}")
        logger.info(f"Contract has {len(contract.interactions)} interactions")
    except Exception as e:
        logger.error(f"Error loading contract: {e}")
        raise

    # Create output directory if it doesn't exist
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = os.path.join(os.getcwd(), "reports")
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Using default output directory: {output_dir}")

    # Run the evaluation
    logger.info(f"Running evaluation with policy folder: {policy_folder}")
    try:
        results = await aicertify_app_for_policy(
            contract=contract,
            policy_folder=policy_folder,
            output_dir=output_dir,
            report_format=report_format,
            custom_params=custom_params
        )
        
        logger.info("Evaluation completed successfully")
        if "report_path" in results and results["report_path"]:
            logger.info(f"Report generated at: {results['report_path']}")
        
        return results
    except Exception as e:
        logger.error(f"Error during evaluation: {e}")
        raise

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="AICertify Command Line Tool")
    
    # Required arguments
    parser.add_argument(
        "--contract", 
        required=True,
        help="Path to the contract JSON file"
    )
    parser.add_argument(
        "--policy", 
        required=True,
        help="Path or name of the OPA policy folder"
    )
    
    # Optional arguments
    parser.add_argument(
        "--output-dir", 
        help="Directory to save the report (default: ./reports)"
    )
    parser.add_argument(
        "--report-format", 
        choices=["json", "markdown", "pdf"],
        default="pdf",
        help="Format of the report (default: pdf)"
    )
    parser.add_argument(
        "--evaluators", 
        nargs="+",
        help="Specific evaluators to use (space-separated list)"
    )
    parser.add_argument(
        "--params", 
        help="JSON string or path to JSON file with custom parameters for OPA policies"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger("aicertify").setLevel(logging.DEBUG)
    
    # Parse custom parameters
    custom_params = None
    if args.params:
        try:
            # Check if args.params is a file path
            if os.path.isfile(args.params):
                with open(args.params, 'r') as f:
                    custom_params = json.load(f)
            else:
                # Assume it's a JSON string
                custom_params = json.loads(args.params)
        except Exception as e:
            logger.error(f"Error parsing custom parameters: {e}")
            sys.exit(1)
    
    # Run the evaluation
    try:
        results = asyncio.run(run_evaluation(
            contract_path=args.contract,
            policy_folder=args.policy,
            output_dir=args.output_dir,
            report_format=args.report_format,
            evaluators=args.evaluators,
            custom_params=custom_params
        ))
        
        # Print a summary of the results
        print("\nEvaluation Summary:")
        print(f"Contract ID: {results.get('contract_id', 'Unknown')}")
        print(f"Application: {results.get('application_name', 'Unknown')}")
        
        if "report_path" in results and results["report_path"]:
            print(f"Report: {results['report_path']}")
        
        # Check if OPA evaluation was successful
        opa_results = results.get("opa_results", {})
        if "error" in opa_results:
            print(f"OPA Evaluation Error: {opa_results['error']}")
        else:
            print("OPA Evaluation: Successful")
        
        # Exit with success
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 