#!/usr/bin/env python
"""
Focused debug script for OPA policy evaluation with an existing contract.

This script loads an existing contract JSON file and runs only the OPA policy evaluation
part, skipping the AI agent interactions that generate the contract.
"""

import os
import sys
import logging
import asyncio
import traceback
from pathlib import Path
import glob
import json
from uuid import UUID
from datetime import datetime

from dotenv import load_dotenv

# Configure logging with a detailed format
logging.basicConfig(
    level=logging.INFO,  # Changed to INFO for less verbose output
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Keep our script's logger at DEBUG level

# Reduce verbosity of other loggers
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("absl").setLevel(logging.WARNING)
logging.getLogger("root").setLevel(logging.INFO)

# Import AICertify modules needed for evaluation
from aicertify.models.contract_models import load_contract
from aicertify.api import evaluate_contract_comprehensive
from aicertify.opa_core.evaluator import OpaEvaluator

# Custom JSON encoder to handle UUID and datetime objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

async def evaluate_contract_only(contract_path: str, output_dir: str, report_format: str = "markdown") -> None:
    """
    Load an existing contract file and run only the OPA policy evaluation.
    
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
        
        # Get domain from context to choose appropriate policy category
        domain = contract.context.get("domain", "").lower()
        
        # Use the correct policy category path based on domain
        if domain == "healthcare":
            # For healthcare, use the industry_specific/healthcare path
            policy_category = "industry_specific/healthcare"
            logger.info(f"Domain detected: {domain}")
            logger.info(f"Using policy_category: {policy_category}")
            
            # Create an OPA evaluator instance for direct testing
            opa_evaluator = OpaEvaluator(
                use_external_server=os.environ.get("OPA_USE_EXTERNAL_SERVER", "false").lower() == "true",
                server_url=os.environ.get("OPA_SERVER_URL", "http://localhost:8181")
            )
            
            # Log OPA configuration
            logger.info(f"OPA external server: {opa_evaluator.use_external_server}")
            logger.info(f"OPA server URL: {opa_evaluator.server_url}")
            
            # Load policies
            logger.info("Loading OPA policies...")
            opa_evaluator.load_policies()
            
            # Convert contract to dictionary for evaluation
            contract_dict = contract.model_dump()
            
            # Create a more comprehensive evaluation result structure
            evaluation_result = {
                "fairness": {
                    "score": 0.9,  # Example score
                    "gender_bias_detected": False,
                    "racial_bias_detected": False
                },
                "content_safety": {
                    "score": 0.95,  # Example score
                    "toxicity": {
                        "score": 0.05  # Low toxicity is good
                    }
                },
                "risk_management": {
                    "score": 0.92  # Example score
                }
            }
            
            # Prepare input data for OPA
            input_data = {
                "contract": contract_dict,
                "evaluation": evaluation_result
            }
            
            # Try direct OPA evaluation first
            logger.info("Attempting direct OPA evaluation...")
            try:
                # Evaluate using the healthcare multi_specialist policy
                policy_path = "healthcare.multi_specialist.diagnostic_safety"
                logger.info(f"Evaluating with policy path: {policy_path}")
                
                # Convert input_data to JSON string with custom encoder to handle UUID objects
                input_json_str = json.dumps(input_data, cls=CustomJSONEncoder)
                # Convert back to dict for the evaluator
                input_data_serialized = json.loads(input_json_str)
                
                opa_results = opa_evaluator.evaluate_policies_by_category(
                    category="industry_specific",
                    subcategory="healthcare",
                    input_data=input_data_serialized,
                    version="v1"
                )
                
                logger.info(f"Direct OPA evaluation results: {json.dumps(opa_results, indent=2)}")
            except Exception as e:
                logger.error(f"Direct OPA evaluation failed: {str(e)}")
                logger.error(traceback.format_exc())
        else:
            # For other domains, use international/eu_ai_act
            policy_category = "international/eu_ai_act"
            logger.info(f"Domain detected: {domain}")
            logger.info(f"Using policy_category: {policy_category}")

            # Create an OPA evaluator instance for direct testing
            opa_evaluator = OpaEvaluator(
                use_external_server=os.environ.get("OPA_USE_EXTERNAL_SERVER", "false").lower() == "true",
                server_url=os.environ.get("OPA_SERVER_URL", "http://localhost:8181")
            )
            
            # Log OPA configuration
            logger.info(f"OPA external server: {opa_evaluator.use_external_server}")
            logger.info(f"OPA server URL: {opa_evaluator.server_url}")
            
            # Load policies
            logger.info("Loading OPA policies...")
            opa_evaluator.load_policies()
            
            # Convert contract to dictionary for evaluation
            contract_dict = contract.model_dump()
            
            # Create a fairness-focused evaluation result structure
            evaluation_result = {
                "fairness": {
                    "score": 0.85  # Example score
                },
                "metrics": {
                    "gender_bias_detected": False,
                    "racial_bias_detected": False,
                    "toxicity": {
                        "score": 0.1  # Low toxicity
                    }
                }
            }
            
            # Prepare input data for OPA
            input_data = {
                "contract": contract_dict,
                "evaluation": evaluation_result,
                "metrics": evaluation_result["metrics"]
            }
            
            # Try direct OPA evaluation first
            logger.info("Attempting direct OPA evaluation...")
            try:
                # Evaluate using the EU AI Act fairness policy
                policy_path = "international.eu_ai_act.v1.fairness"
                logger.info(f"Evaluating with policy path: {policy_path}")
                
                # Serialize input data with custom encoder to handle UUIDs
                input_json_str = json.dumps(input_data, cls=CustomJSONEncoder)
                input_data_serialized = json.loads(input_json_str)
                
                opa_results = opa_evaluator.evaluate_policies_by_category(
                    category="international",
                    subcategory="eu_ai_act",
                    input_data=input_data_serialized,
                    version="v1"
                )
                
                logger.info(f"Direct OPA evaluation results: {json.dumps(opa_results, indent=2)}")
            except Exception as e:
                logger.error(f"Direct OPA evaluation failed: {str(e)}")
                logger.error(traceback.format_exc())
        
        # Log context details for debugging
        logger.debug("Contract context details:")
        for key, value in contract.context.items():
            if isinstance(value, (dict, list)):
                logger.debug(f"  {key}: {type(value)} with {len(value)} items")
            else:
                logger.debug(f"  {key}: {value}")
        
        # Evaluate the contract using OPA policies
        try:
            logger.info("Starting contract evaluation with comprehensive API...")
            logger.debug("Calling evaluate_contract_comprehensive with parameters:")
            logger.debug(f"  policy_category: {policy_category}")
            logger.debug(f"  generate_report: True")
            logger.debug(f"  report_format: {report_format}")
            logger.debug(f"  output_dir: {output_dir}")
            
            # Set a longer timeout for async operations
            eval_result = await asyncio.wait_for(
                evaluate_contract_comprehensive(
                    contract=contract,
                    policy_category=policy_category,  # Note: singular parameter name
                    generate_report=True,
                    report_format=report_format,
                    output_dir=output_dir
                ),
                timeout=120  # 2 minutes timeout
            )
            
            # Log evaluation results
            logger.info("Contract evaluation complete")
            logger.debug(f"Evaluation result keys: {eval_result.keys()}")
            
            if eval_result.get('report_path'):
                logger.info(f"Evaluation report saved to: {eval_result.get('report_path')}")
            else:
                logger.warning("No report path returned, checking for report content...")
                
                # Check if report content is available directly
                if eval_result.get('report'):
                    report_content = eval_result.get('report')
                    # Save report content to a file
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
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    except Exception as e:
        logger.error(f"Error loading contract: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")


def main() -> None:
    """Main function to run the focused OPA policy evaluation."""
    logger.debug("Starting debug_policy_evaluation script")
    
    # Define the contract storage directory (same as in the original script)
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    contract_storage = script_dir / "outputs" / "medical_diagnosis"
    
    logger.debug(f"Looking for contract files in: {contract_storage}")
    
    # Find the most recent contract JSON file
    contract_files = glob.glob(str(contract_storage / "contract_*.json"))
    if not contract_files:
        logger.error(f"No contract files found in {contract_storage}")
        sys.exit(1)
    
    logger.debug(f"Found {len(contract_files)} contract files")
    
    # Sort by modification time (most recent first)
    contract_files.sort(key=os.path.getmtime, reverse=True)
    latest_contract = contract_files[0]
    
    # Print useful diagnostic information
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Script directory: {script_dir}")
    logger.info(f"Contract storage directory: {contract_storage}")
    logger.info(f"Using most recent contract file: {latest_contract}")
    
    # Print modules available
    logger.debug("Imported modules:")
    logger.debug(f"  aicertify.models.contract_models.load_contract: {load_contract}")
    logger.debug(f"  aicertify.api.evaluate_contract_comprehensive: {evaluate_contract_comprehensive}")
    
    try:
        # Call the async function with event loop
        logger.info("Starting asyncio event loop for contract evaluation")
        asyncio.run(evaluate_contract_only(
            contract_path=latest_contract,
            output_dir=str(contract_storage),
            report_format="markdown"
        ))
        logger.info("Contract evaluation completed successfully")
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    try:
        # Load environment variables
        load_dotenv()
        
        # Verify OPA environment variables
        opa_path = os.environ.get("OPA_PATH")
        opa_server_url = os.environ.get("OPA_SERVER_URL")
        opa_use_external = os.environ.get("OPA_USE_EXTERNAL_SERVER")
        
        logger.info(f"OPA_PATH: {opa_path}")
        logger.info(f"OPA_SERVER_URL: {opa_server_url}")
        logger.info(f"OPA_USE_EXTERNAL_SERVER: {opa_use_external}")
        
        main()
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1) 