#!/usr/bin/env python
"""
Focused debug script for OPA policy evaluation with an existing contract.

This script loads an existing contract JSON file and runs only the OPA policy evaluation
part, skipping the AI agent interactions that generate the contract.
"""

import os
# Disable CUDA devices before importing any transformer libraries.
os.environ["CUDA_VISIBLE_DEVICES"] = ""

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
from sentence_transformers import SentenceTransformer
from transformers import logging as hf_logging

# Global logging configuration (set to INFO for less verbosity)
#hf_logging.set_verbosity_debug()
logging.basicConfig(
    level=logging.DEBUG,  # Changed from DEBUG to INFO for lower verbosity
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.DEBUG)
# Reduce verbosity of other loggers
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("absl").setLevel(logging.WARNING)
logging.getLogger("root").setLevel(logging.DEBUG)
logging.getLogger("httpcore").setLevel(logging.WARNING)

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
            policy_category = "industry_specific/healthcare"
            logger.info(f"Domain detected: {domain}")
            logger.info(f"Using policy_category: {policy_category}")
            
            debug_mode = os.environ.get("OPA_DEBUG", "0") == "1"
            opa_evaluator = OpaEvaluator(
                use_external_server=False,  # Force local evaluator
                server_url=os.environ.get("OPA_SERVER_URL", "http://localhost:8181"),
                debug=debug_mode
            )
            logger.info(f"OPA external server: {opa_evaluator.use_external_server}")
            logger.info(f"OPA server URL: {opa_evaluator.server_url}")
            
            logger.info("Loading OPA policies...")
            opa_evaluator.load_policies()
            
            contract_dict = contract.model_dump()
            
            evaluation_result = {
                "fairness": {
                    "score": 0.9,
                    "gender_bias_detected": False,
                    "racial_bias_detected": False
                },
                "content_safety": {
                    "score": 0.95,
                    "toxicity": {
                        "score": 0.05
                    }
                },
                "risk_management": {
                    "score": 0.92
                }
            }
            
            input_data = {
                "contract": contract_dict,
                "evaluation": evaluation_result
            }
            
            logger.info("Attempting direct OPA evaluation...")
            try:
                policy_path = "healthcare.multi_specialist.diagnostic_safety"
                logger.info(f"Evaluating with policy path: {policy_path}")
                
                input_json_str = json.dumps(input_data, cls=CustomJSONEncoder)
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
            policy_category = "international/eu_ai_act"
            logger.info(f"Domain detected: {domain}")
            logger.info(f"Using policy_category: {policy_category}")

            debug_mode = os.environ.get("OPA_DEBUG", "0") == "1"
            opa_evaluator = OpaEvaluator(
                use_external_server=False,
                server_url=os.environ.get("OPA_SERVER_URL", "http://localhost:8181"),
                debug=debug_mode
            )
            logger.info(f"OPA external server: {opa_evaluator.use_external_server}")
            logger.info(f"OPA server URL: {opa_evaluator.server_url}")
            
            logger.info("Loading OPA policies...")
            opa_evaluator.load_policies()
            
            contract_dict = contract.model_dump()
            
            evaluation_result = {
                "fairness": {
                    "score": 0.85
                },
                "metrics": {
                    "gender_bias_detected": False,
                    "racial_bias_detected": False,
                    "toxicity": {
                        "score": 0.1
                    }
                }
            }
            
            input_data = {
                "contract": contract_dict,
                "evaluation": evaluation_result,
                "metrics": evaluation_result["metrics"]
            }
            
            logger.info("Attempting direct OPA evaluation...")
            try:
                policy_path = "international.eu_ai_act.v1.fairness"
                logger.info(f"Evaluating with policy path: {policy_path}")
                
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
        
        logger.debug("Contract context details:")
        for key, value in contract.context.items():
            if isinstance(value, (dict, list)):
                logger.debug(f"  {key}: {type(value)} with {len(value)} items")
            else:
                logger.debug(f"  {key}: {value}")
        
        try:
            logger.info("Starting contract evaluation with comprehensive API...")
            logger.debug("Calling evaluate_contract_comprehensive with parameters:")
            logger.debug(f"  policy_category: {policy_category}")
            logger.debug(f"  generate_report: True")
            logger.debug(f"  report_format: {report_format}")
            logger.debug(f"  output_dir: {output_dir}")
            
            eval_result = await asyncio.wait_for(
                evaluate_contract_comprehensive(
                    contract=contract,
                    policy_category=policy_category,
                    generate_report=True,
                    report_format=report_format,
                    output_dir=output_dir
                ),
                timeout=120
            )
            
            logger.info("Contract evaluation complete")
            logger.debug(f"Evaluation result keys: {eval_result.keys()}")
            
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
    
    except Exception as e:
        logger.error(f"Error loading contract: {str(e)}")
        logger.error(traceback.format_exc())

def main() -> None:
    """Main function to run the focused OPA policy evaluation."""
    logger.info("Starting debug_policy_evaluation execution...")

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
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", cache_folder=cache_dir)
    logger.info("SentenceTransformer model loaded")

    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
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
    logger.info(f"Using most recent contract file: {latest_contract}")

    try:
        logger.info("Starting asyncio event loop for contract evaluation")
        asyncio.run(evaluate_contract_only(
            contract_path=latest_contract,
            output_dir=str(contract_storage),
            report_format="markdown"
        ))
        logger.info("Contract evaluation completed successfully")
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    print("Initializing debug_policy_evaluation script...", flush=True)
    try:
        main()
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        sys.exit(1)
