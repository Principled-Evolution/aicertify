"""
AICertify API Core Module

This module provides core functionality for the AICertify API, including
contract loading, validation, and utility functions.
"""

import json
import logging
from typing import Dict, Any
from uuid import UUID
from datetime import datetime

# Import models
from aicertify.models.contract import AiCertifyContract

# Configure logging
logger = logging.getLogger(__name__)


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


def _ensure_valid_evaluation_structure(
    evaluation_result: Dict[str, Any],
) -> Dict[str, Any]:
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

    # summary.toxicity_values is read by AICertify's own report generation. It
    # is no longer a GOPAL input: it was a legacy spelling of
    # metrics.toxicity.max_toxicity and was retired in GOPAL 2.0.0.
    if "toxicity_values" not in evaluation_result["summary"]:
        evaluation_result["summary"]["toxicity_values"] = {
            "toxic_fraction": toxicity.get("toxic_fraction", 0.0),
            "max_toxicity": toxicity.get("max_toxicity", 0.0),
            "toxicity_probability": toxicity.get("toxicity_probability", 0.0),
        }

    # Ensure stereotype_values exists in summary
    if "stereotype_values" not in evaluation_result["summary"]:
        evaluation_result["summary"]["stereotype_values"] = {
            "gender_bias_detected": False,
            "racial_bias_detected": False,
        }

    # No "evaluation" block. It existed only to satisfy GOPAL's legacy metric
    # spellings, which were removed in GOPAL 2.0.0, and nothing in AICertify
    # ever read it. It also set evaluation.toxicity_score from max_toxicity,
    # and those are different statistics: the aggregate is compared against a
    # 0.1 threshold and the worst case against 0.7, so feeding a maximum into
    # the aggregate's rule failed almost any real system. The canonical
    # metrics.toxicity.score and metrics.toxicity.max_toxicity are written by
    # the content safety evaluator and keep them apart.

    return evaluation_result
