#!/usr/bin/env python
"""
Script to capture evaluation and OPA results from a real run for debugging.
"""

import json
import logging
import os
import sys
import traceback
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("data_capture")

# Create a directory for captured data
capture_dir = "temp_reports/captured_data"
os.makedirs(capture_dir, exist_ok=True)

# Monkey patch the create_evaluation_report function to capture data
from aicertify.report_generation.data_extraction import create_evaluation_report as original_create_evaluation_report

def create_evaluation_report_with_capture(evaluation_result, opa_results=None):
    """Wrapper around create_evaluation_report that captures input data."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Capture evaluation result
    eval_result_path = os.path.join(capture_dir, f"evaluation_result_{timestamp}.json")
    try:
        with open(eval_result_path, "w") as f:
            json.dump(evaluation_result, f, indent=2, default=str)
        logger.info(f"Captured evaluation result to {eval_result_path}")
    except Exception as e:
        logger.error(f"Error capturing evaluation result: {str(e)}")
    
    # Capture OPA results if available
    if opa_results:
        opa_results_path = os.path.join(capture_dir, f"opa_results_{timestamp}.json")
        try:
            with open(opa_results_path, "w") as f:
                json.dump(opa_results, f, indent=2, default=str)
            logger.info(f"Captured OPA results to {opa_results_path}")
        except Exception as e:
            logger.error(f"Error capturing OPA results: {str(e)}")
    
    # Call the original function
    try:
        result = original_create_evaluation_report(evaluation_result, opa_results)
        return result
    except Exception as e:
        error_path = os.path.join(capture_dir, f"error_{timestamp}.txt")
        with open(error_path, "w") as f:
            f.write(f"Error in create_evaluation_report: {str(e)}\n\n")
            f.write(traceback.format_exc())
        logger.error(f"Error in create_evaluation_report: {str(e)}")
        logger.error(f"Error details saved to {error_path}")
        raise

# Replace the original function with our capturing version
import aicertify.report_generation.data_extraction
aicertify.report_generation.data_extraction.create_evaluation_report = create_evaluation_report_with_capture

# Also capture data from evaluate_contract_by_folder
from aicertify.api import evaluate_contract_by_folder as original_evaluate_contract_by_folder

def evaluate_contract_by_folder_with_capture(contract, policy_folder, evaluators=None, 
                                            evaluator_config=None, generate_report=False, 
                                            report_format="markdown", output_dir=None, 
                                            opa_evaluator=None):
    """Wrapper around evaluate_contract_by_folder that captures input and output data."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Capture contract
    contract_path = os.path.join(capture_dir, f"contract_{timestamp}.json")
    try:
        with open(contract_path, "w") as f:
            json.dump(contract.dict(), f, indent=2, default=str)
        logger.info(f"Captured contract to {contract_path}")
    except Exception as e:
        logger.error(f"Error capturing contract: {str(e)}")
    
    # Call the original function
    try:
        result = original_evaluate_contract_by_folder(
            contract, policy_folder, evaluators, evaluator_config, 
            generate_report, report_format, output_dir, opa_evaluator
        )
        
        # Capture result
        result_path = os.path.join(capture_dir, f"evaluate_result_{timestamp}.json")
        try:
            with open(result_path, "w") as f:
                json.dump(result, f, indent=2, default=str)
            logger.info(f"Captured evaluation result to {result_path}")
        except Exception as e:
            logger.error(f"Error capturing evaluation result: {str(e)}")
        
        return result
    except Exception as e:
        error_path = os.path.join(capture_dir, f"evaluate_error_{timestamp}.txt")
        with open(error_path, "w") as f:
            f.write(f"Error in evaluate_contract_by_folder: {str(e)}\n\n")
            f.write(traceback.format_exc())
        logger.error(f"Error in evaluate_contract_by_folder: {str(e)}")
        logger.error(f"Error details saved to {error_path}")
        raise

# Replace the original function with our capturing version
import aicertify.api
aicertify.api.evaluate_contract_by_folder = evaluate_contract_by_folder_with_capture

logger.info("Installed data capture hooks. Run debug_policy_evaluation.py to capture data.")
logger.info(f"Data will be saved to {os.path.abspath(capture_dir)}")

if __name__ == "__main__":
    print(f"Data capture hooks installed. Data will be saved to {os.path.abspath(capture_dir)}")
    print("Run debug_policy_evaluation.py to capture data during execution.") 