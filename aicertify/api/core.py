"""
AICertify API Core Module

This module provides core functionality for the AICertify API, including
contract loading, validation, and utility functions.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Import models
from aicertify.models.contract_models import AiCertifyContract

def load_contract(contract_path: str) -> AiCertifyContract:
    """
    Load an AiCertifyContract from a JSON file.
    
    Args:
        contract_path: Path to the contract JSON file
        
    Returns:
        AiCertifyContract object
    """
    try:
        with open(contract_path, "r") as f:
            contract_data = json.load(f)
        return AiCertifyContract.parse_obj(contract_data)
    except Exception as e:
        logger.error(f"Error loading contract from {contract_path}: {e}")
        raise

# Custom JSON encoder to handle UUID serialization
class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles UUID objects."""
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def _ensure_valid_evaluation_structure(evaluation_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure the evaluation result has a valid structure for policy evaluation.
    
    Args:
        evaluation_result: The evaluation result to validate and fix
        
    Returns:
        A validated and fixed evaluation result
    """
    if evaluation_result is None:
        evaluation_result = {}
    
    # Ensure metrics exists
    if "metrics" not in evaluation_result:
        evaluation_result["metrics"] = {}
    
    # Ensure toxicity metrics exist
    if "toxicity" not in evaluation_result["metrics"]:
        evaluation_result["metrics"]["toxicity"] = {}
    
    # Ensure toxicity values are valid
    toxicity = evaluation_result["metrics"]["toxicity"]
    if not isinstance(toxicity.get("toxic_fraction"), (int, float)):
        toxicity["toxic_fraction"] = 0.0
    if not isinstance(toxicity.get("max_toxicity"), (int, float)):
        toxicity["max_toxicity"] = 0.0
    if not isinstance(toxicity.get("toxicity_probability"), (int, float)):
        toxicity["toxicity_probability"] = 0.0
    
    # Ensure summary exists
    if "summary" not in evaluation_result:
        evaluation_result["summary"] = {}
    
    # Ensure toxicity_values exists in summary
    if "toxicity_values" not in evaluation_result["summary"]:
        evaluation_result["summary"]["toxicity_values"] = {
            "toxic_fraction": toxicity.get("toxic_fraction", 0.0),
            "max_toxicity": toxicity.get("max_toxicity", 0.0),
            "toxicity_probability": toxicity.get("toxicity_probability", 0.0)
        }
    
    # Ensure stereotype_values exists in summary
    if "stereotype_values" not in evaluation_result["summary"]:
        evaluation_result["summary"]["stereotype_values"] = {
            "gender_bias_detected": False,
            "racial_bias_detected": False
        }
    
    # Create the evaluation structure expected by OPA policies
    if "evaluation" not in evaluation_result:
        evaluation_result["evaluation"] = {
            "toxicity_score": toxicity.get("max_toxicity", 0.0),
            "toxic_fraction": toxicity.get("toxic_fraction", 0.0),
            "toxicity_probability": toxicity.get("toxicity_probability", 0.0),
            "gender_bias_detected": evaluation_result["summary"].get("stereotype_values", {}).get("gender_bias_detected", False),
            "racial_bias_detected": evaluation_result["summary"].get("stereotype_values", {}).get("racial_bias_detected", False)
        }
    
    return evaluation_result
