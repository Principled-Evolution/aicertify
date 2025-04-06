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
from typing import Any, Dict

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from transformers import logging as hf_logging
import colorlog


# Set OPA_DEBUG environment variable only if not already set
if "OPA_DEBUG" not in os.environ:
    os.environ["OPA_DEBUG"] = "0"  # Use production mode
    print(f"Setting OPA_DEBUG=0 (not previously set in environment)")
else:
    print(f"Using existing OPA_DEBUG={os.environ['OPA_DEBUG']} from environment")

# Get log configuration from environment variables
log_level = os.environ.get("LOG_LEVEL", "INFO")
log_file = os.environ.get("LOG_FILE", None)  # Define log_file variable
log_level_num = getattr(logging, log_level.upper(), logging.INFO)

# Configure colored logging
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
))

# Set up root logger
root_logger = logging.getLogger()
root_logger.setLevel(log_level_num)
for hdlr in root_logger.handlers[:]:
    root_logger.removeHandler(hdlr)
root_logger.addHandler(handler)

# Add file handler if log file is specified
if log_file:
    # Create directory for log file if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
        
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level_num)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    root_logger.addHandler(file_handler)

# Set up logger for this module
logger = logging.getLogger(__name__)

# Set OpenAI logging levels
logging.getLogger("openai").setLevel(logging.INFO)
logging.getLogger("openai._base_client").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Create handlers list
handlers = [logging.StreamHandler()]

# Add file handler if LOG_FILE is specified
if log_file:
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    file_handler = logging.FileHandler(log_file, mode='w')
    handlers.append(file_handler)
    print(f"Logging to file: {log_file}")

# Configure logging with all handlers
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=handlers
)

# Ensure all libraries log at appropriate levels
logging.getLogger("aicertify").setLevel(getattr(logging, log_level))
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("matplotlib").setLevel(logging.WARNING)

# Set HuggingFace logging to less verbose
hf_logging.set_verbosity_error()

logger.info(f"Logging initialized at level {log_level}")

# Add the parent directory to sys.path to import aicertify
sys.path.insert(0, str(Path(__file__).parent.parent))

# Global logging configuration (set to INFO for less verbosity)
#hf_logging.set_verbosity_debug()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger.setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.DEBUG)
# Reduce verbosity of other loggers
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("absl").setLevel(logging.WARNING)
logging.getLogger("root").setLevel(logging.DEBUG)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# Import AICertify modules needed for evaluation
from aicertify.models.contract_models import load_contract
from aicertify.api import evaluate_contract_by_folder
from aicertify.opa_core.evaluator import OpaEvaluator

# Custom JSON encoder to handle UUID and datetime objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

async def debug_evaluation_metrics(evaluation_result: Dict[str, Any]) -> None:
    """
    Debug function to print out the raw metrics from the evaluation result.
    
    Args:
        evaluation_result: The evaluation result to debug
    """
    logger.info("=== DEBUGGING EVALUATION METRICS ===")
    
    # Log the overall structure
    logger.info(f"Evaluation result keys: {list(evaluation_result.keys())}")
    
    # Check for fairness metrics
    if "fairness_metrics" in evaluation_result:
        logger.info("Found fairness_metrics at root level")
        logger.info(f"fairness_metrics keys: {list(evaluation_result['fairness_metrics'].keys())}")
        logger.info(f"counterfactual_score: {evaluation_result['fairness_metrics'].get('counterfactual_score')}")
        logger.info(f"stereotype_score: {evaluation_result['fairness_metrics'].get('stereotype_score')}")
        logger.info(f"combined_score: {evaluation_result['fairness_metrics'].get('combined_score')}")
        
        # Check for details
        if "details" in evaluation_result["fairness_metrics"]:
            logger.info("Found details in fairness_metrics")
            details = evaluation_result["fairness_metrics"]["details"]
            logger.info(f"details keys: {list(details.keys())}")
            logger.info(f"sentiment_bias: {details.get('sentiment_bias')}")
            logger.info(f"bleu_similarity: {details.get('bleu_similarity')}")
            logger.info(f"rouge_similarity: {details.get('rouge_similarity')}")
    
    # Check for phase1_results
    if "phase1_results" in evaluation_result and "results" in evaluation_result["phase1_results"]:
        logger.info("Found phase1_results")
        results = evaluation_result["phase1_results"]["results"]
        
        if "fairness" in results:
            logger.info("Found fairness in phase1_results")
            fairness = results["fairness"]
            logger.info(f"fairness keys: {list(fairness.keys())}")
            logger.info(f"compliant: {fairness.get('compliant')}")
            logger.info(f"score: {fairness.get('score')}")
            
            if "details" in fairness:
                logger.info("Found details in fairness")
                details = fairness["details"]
                logger.info(f"details keys: {list(details.keys())}")
                logger.info(f"counterfactual_score: {details.get('counterfactual_score')}")
                logger.info(f"stereotype_score: {details.get('stereotype_score')}")
                logger.info(f"combined_score: {details.get('combined_score')}")
    
    # Check for opa_results
    if "opa_results" in evaluation_result:
        logger.info("Found opa_results")
        opa_results = evaluation_result["opa_results"]
        
        if "result" in opa_results and isinstance(opa_results["result"], list) and len(opa_results["result"]) > 0:
            logger.info("Found result list in opa_results")
            first_result = opa_results["result"][0]
            
            if "expressions" in first_result and len(first_result["expressions"]) > 0:
                logger.info("Found expressions in first_result")
                first_expr = first_result["expressions"][0]
                
                if "value" in first_expr and "v1" in first_expr["value"]:
                    logger.info("Found v1 in first_expr.value")
                    v1_data = first_expr["value"]["v1"]
                    logger.info(f"v1_data keys: {list(v1_data.keys())}")
                    
                    # Check for diagnostic_safety
                    if "diagnostic_safety" in v1_data:
                        logger.info("Found diagnostic_safety in v1_data")
                        diagnostic_safety = v1_data["diagnostic_safety"]
                        logger.info(f"diagnostic_safety keys: {list(diagnostic_safety.keys())}")
                        logger.info(f"allow: {diagnostic_safety.get('allow')}")
                        
                        if "compliance_report" in diagnostic_safety:
                            logger.info("Found compliance_report in diagnostic_safety")
                            compliance_report = diagnostic_safety["compliance_report"]
                            logger.info(f"compliance_report keys: {list(compliance_report.keys())}")
                            logger.info(f"overall_result: {compliance_report.get('overall_result')}")
                            logger.info(f"policy: {compliance_report.get('policy')}")

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
        
        # Initialize OPA evaluator once and reuse it for all evaluations
        debug_mode = os.environ.get("OPA_DEBUG", "1") == "1"  # Default to debug mode enabled
        opa_evaluator = OpaEvaluator(
            use_external_server=False,  # Force local evaluator
            server_url=os.environ.get("OPA_SERVER_URL", "http://localhost:8181"),
            debug=debug_mode
        )
        logger.info(f"OPA external server: {opa_evaluator.use_external_server}")
        logger.info(f"OPA server URL: {opa_evaluator.server_url}")
        
        logger.info("Loading OPA policies...")
        opa_evaluator.load_policies()
        
        # Use the correct policy category path based on domain
        if domain == "healthcare":
            # For folder-based evaluation
            policy_folder = "healthcare"
            # For comprehensive evaluation
            policy_category = "industry_specific/healthcare"
            
        elif domain == "finance":
            policy_folder = "bfs"  # Banking, Financial Services
            policy_category = "industry_specific/bfs"
            
        else:
            # Default to global policies
            policy_folder = "global"
            policy_category = "global"
            
        logger.info(f"Domain detected: {domain}")
        logger.info(f"Using policy_folder: {policy_folder}")
        logger.info(f"Using policy_category: {policy_category}")
        
        # Log contract context details
        logger.debug("Contract context details:")
        for key, value in contract.context.items():
            if isinstance(value, dict) and len(value) > 10:
                logger.debug(f"  {key}: <class '{type(value).__name__}'> with {len(value)} items")
            else:
                logger.debug(f"  {key}: {value}")
        
        logger.info("Starting contract evaluation with folder-based API...")
        
        # Evaluate using the folder-based approach
        logger.debug("Calling evaluate_contract_by_folder with parameters:")
        logger.debug(f"  policy_folder: {policy_folder}")
        logger.debug(f"  generate_report: True")
        logger.debug(f"  report_format: {report_format}")
        logger.debug(f"  output_dir: {output_dir}")
        
        # Use the folder-based evaluation function
        eval_result = await asyncio.wait_for(
            evaluate_contract_by_folder(
                contract=contract,
                policy_folder=policy_folder,
                generate_report=True,
                report_format=report_format,
                output_dir=output_dir,
                opa_evaluator=opa_evaluator  # Pass the existing evaluator
            ),
            timeout=120
        )
        
        if False:
            # Now evaluate all child folders and policies within the parent folder
            logger.info(f"Evaluating all child folders and policies within {policy_category}...")
            
            # Get the policy directory
            policy_dir = Path(opa_evaluator.policy_loader.get_policy_dir())
            
            # Build the full path to the policy category
            category_path = policy_dir / policy_category
            
            if category_path.exists() and category_path.is_dir():
                # Find all version folders (v1, v2, etc.)
                version_folders = [d for d in category_path.iterdir() if d.is_dir()]
                
                for version_folder in version_folders:
                    logger.info(f"Processing version folder: {version_folder.name}")
                    
                    # Find all policy folders within this version
                    policy_folders = [d for d in version_folder.iterdir() if d.is_dir()]
                    
                    for policy_folder in policy_folders:
                        policy_name = policy_folder.name
                        logger.info(f"Evaluating policy: {policy_name}")
                        
                        # Create a relative path from the policy directory
                        rel_path = policy_folder.relative_to(policy_dir)
                        package_path = str(rel_path).replace(os.sep, '.')
                        query = f"data.{package_path}"
                       
                        # Serialize input data with custom encoder to handle UUIDs
                        contract_dict = contract.dict()
                        input_json_str = json.dumps({"contract": contract_dict, "evaluation": eval_result.get("phase1_results", {})}, cls=CustomJSONEncoder)
                        input_data_serialized = json.loads(input_json_str)
                        
                        # Evaluate the policy
                        policy_result = opa_evaluator.evaluate_policy(
                            policy_path=str(policy_folder),
                            input_data=input_data_serialized,
                            query=query,
                            mode="debug"  # Use debug mode to get more information
                        )
                        
                        # Check if the policy evaluation failed
                        if "error" in policy_result:
                            logger.warning(f"Policy evaluation failed for {policy_name}: {policy_result.get('error')}")
                            
                            # Create a fallback policy result with error information
                            fallback_result = {
                                "allow": False,
                                "compliance_report": {
                                    "overall_result": False,
                                    "policy": f"{policy_name.replace('_', ' ').title()} Requirements",
                                    "version": "1.0.0",
                                    "status": "Error",
                                    "details": {
                                        "message": f"Error evaluating policy: {policy_result.get('error', 'Unknown error')}"
                                    },
                                    "recommendations": [
                                        f"Check the {policy_name} policy implementation",
                                        "Verify policy syntax and package path",
                                        "Ensure policy input data is correctly formatted"
                                    ]
                                }
                            }
                            
                            # Add the fallback result to the OPA results
                            if "opa_results" in eval_result and "result" in eval_result["opa_results"] and isinstance(eval_result["opa_results"]["result"], list) and len(eval_result["opa_results"]["result"]) > 0:
                                first_result = eval_result["opa_results"]["result"][0]
                                if "expressions" in first_result and len(first_result["expressions"]) > 0:
                                    first_expr = first_result["expressions"][0]
                                    if "value" in first_expr:
                                        # Get the version from the path (e.g., v1)
                                        version_name = version_folder.name
                                        
                                        # Always add to the "v1" key to ensure compatibility with the extraction code
                                        if "v1" not in first_expr["value"]:
                                            first_expr["value"]["v1"] = {}
                                        
                                        # Add the fallback policy value to the v1 data
                                        first_expr["value"]["v1"][policy_name] = fallback_result
                                        logger.info(f"Added fallback {policy_name} policy result to OPA results under v1")
                            
                            # Skip the rest of the processing for this policy
                            continue
                        
                        # Create a compliance_report structure if it doesn't exist
                        if "result" in policy_result and isinstance(policy_result["result"], list) and len(policy_result["result"]) > 0:
                            first_result = policy_result["result"][0]
                            if "expressions" in first_result and len(first_result["expressions"]) > 0:
                                first_expr = first_result["expressions"][0]
                                if "value" in first_expr:
                                    policy_data = first_expr["value"]
                                    
                                    # Check if compliance_report already exists
                                    if not any(key == "compliance_report" for key in policy_data.keys()):
                                        # Extract relevant information for the compliance report
                                        overall_result = policy_data.get("allow", False)
                                        reason = policy_data.get("reason", "")
                                        recommendations = policy_data.get("recommendations", [])
                                        
                                        # Create a compliance_report structure
                                        compliance_report = {
                                            "overall_result": overall_result,
                                            "policy": f"{policy_name.replace('_', ' ').title()} Requirements",
                                            "version": "1.0.0",
                                            "status": "Active",
                                            "details": {
                                                "message": reason or f"Evaluation completed for {policy_name}"
                                            },
                                            "recommendations": recommendations
                                        }
                                        
                                        # Add the compliance_report to the policy data
                                        policy_data["compliance_report"] = compliance_report
                                        logger.info(f"Added compliance_report to {policy_name}")
                        
                        # Add the policy result to the OPA results
                    if "opa_results" in eval_result and "result" in eval_result["opa_results"] and isinstance(eval_result["opa_results"]["result"], list) and len(eval_result["opa_results"]["result"]) > 0:
                        first_result = eval_result["opa_results"]["result"][0]
                        if "expressions" in first_result and len(first_result["expressions"]) > 0:
                            first_expr = first_result["expressions"][0]
                            if "value" in first_expr:
                                # Extract the policy data from the evaluation result
                                if "result" in policy_result and isinstance(policy_result["result"], list) and len(policy_result["result"]) > 0:
                                    policy_first_result = policy_result["result"][0]
                                    if "expressions" in policy_first_result and len(policy_first_result["expressions"]) > 0:
                                        policy_first_expr = policy_first_result["expressions"][0]
                                        if "value" in policy_first_expr:
                                            # Get the version from the path (e.g., v1)
                                            version_name = version_folder.name
                                            
                                            # Always add to the "v1" key to ensure compatibility with the extraction code
                                            if "v1" not in first_expr["value"]:
                                                first_expr["value"]["v1"] = {}
                                            
                                            # Add the policy value to the v1 data
                                            first_expr["value"]["v1"][policy_name] = policy_first_expr["value"]
                                            logger.info(f"Added {policy_name} policy result to OPA results under v1")
            else:
                logger.warning(f"Policy category path does not exist: {category_path}")
        
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
            report_format="pdf"
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
