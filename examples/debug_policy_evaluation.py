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
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from transformers import logging as hf_logging
import colorlog

from aicertify.utils.logging_config import setup_colored_logging

# Set OPA_DEBUG environment variable only if not already set
if "OPA_DEBUG" not in os.environ:
    os.environ["OPA_DEBUG"] = "1"
    print(f"Setting OPA_DEBUG=1 (not previously set in environment)")
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
from aicertify.api import evaluate_contract_comprehensive, evaluate_contract_by_folder
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
            
            logger.info(f"Domain detected: {domain}")
            logger.info(f"Using policy_folder: {policy_folder}")
            logger.info(f"Using policy_category: {policy_category}")
        else:
            # For folder-based evaluation
            policy_folder = "eu_ai_act"
            # For comprehensive evaluation
            policy_category = "international/eu_ai_act"
            
            logger.info(f"Domain detected: {domain}")
            logger.info(f"Using policy_folder: {policy_folder}")
            logger.info(f"Using policy_category: {policy_category}")
        
        logger.debug("Contract context details:")
        for key, value in contract.context.items():
            if isinstance(value, (dict, list)):
                logger.debug(f"  {key}: {type(value)} with {len(value)} items")
            else:
                logger.debug(f"  {key}: {value}")
        
        try:
            logger.info("Starting contract evaluation with folder-based API...")
            logger.debug("Calling evaluate_contract_by_folder with parameters:")
            logger.debug(f"  policy_folder: {policy_folder}")
            logger.debug(f"  generate_report: True")
            logger.debug(f"  report_format: {report_format}")
            logger.debug(f"  output_dir: {output_dir}")
            
            # Pass the existing OpaEvaluator to avoid reloading policies
            # Use the new folder-based evaluation function
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
