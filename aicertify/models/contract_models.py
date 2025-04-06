"""
AICertify Contract Input Models (Legacy)

This module is maintained for backward compatibility.
Please use aicertify.models.contract for new code.
"""

import warnings

from aicertify.models.contract import (
    ModelInfo,
    Interaction,
    AiCertifyContract,
    create_contract,
    validate_contract,
    save_contract,
    load_contract,
)

from typing import List, Optional, Dict, Any
import json
import logging

# Import the ModelCard class
from aicertify.models.model_card import ModelCard

# Emit a deprecation warning when this module is imported
warnings.warn(
    "The 'contract_models.py' module is deprecated and will be removed in a future release. "
    "Please use 'aicertify.models.contract' for new code.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export models from the centralized location

# Define the public API for this module
__all__ = [
    "ModelInfo",
    "Interaction",
    "AiCertifyContract",
    "create_contract",
    "validate_contract",
    "save_contract",
    "load_contract",
]


def create_contract_with_model_card(
    application_name: str,
    model_card: ModelCard,
    interactions: List[Dict[str, Any]],
    final_output: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    compliance_context: Optional[Dict[str, Any]] = None,
) -> AiCertifyContract:
    """
    Create a contract with a detailed model card.

    This is a specialized version of create_contract that puts model_card front and center,
    making it easier for developers to provide detailed model information for EU AI Act compliance.

    Args:
        application_name: Name of the application
        model_card: ModelCard instance with detailed model information
        interactions: List of interaction dictionaries
        final_output: Optional final output text
        context: Optional context information
        compliance_context: Optional compliance context information

    Returns:
        An AiCertifyContract instance
    """
    # Create minimal model_info from model_card
    model_info = {
        "model_name": model_card.model_name,
        "model_version": model_card.model_version,
        "metadata": {
            "model_type": model_card.model_type,
            "organization": model_card.organization,
        },
    }

    # If context doesn't exist, initialize it
    if context is None:
        context = {}

    # Add model card information to context
    if "eu_ai_act" not in context:
        context["eu_ai_act"] = {}

    # Include risk_category in context if available
    if model_card.risk_category:
        context["eu_ai_act"]["risk_category"] = model_card.risk_category

    # Include relevant_articles in context if available
    if model_card.relevant_articles:
        context["eu_ai_act"]["relevant_articles"] = model_card.relevant_articles

    return create_contract(
        application_name=application_name,
        model_info=model_info,
        interactions=interactions,
        final_output=final_output,
        context=context,
        compliance_context=compliance_context,
        model_card=model_card,
    )


def aggregate_contracts(contract_files: List[str]) -> Dict[str, Any]:
    """
    Aggregate multiple JSON contract files into a single compliance result.

    For this stub, it simply counts valid and invalid contracts.

    Parameters:
        contract_files (List[str]): List of file paths to JSON contract files.

    Returns:
        Dict[str, Any]: Aggregated contract validation results.
    """
    valid_count = 0
    invalid_count = 0
    aggregated = {
        "total": len(contract_files),
        "valid": 0,
        "invalid": 0,
        "contracts": [],
    }
    for cf in contract_files:
        try:
            with open(cf, "r") as f:
                data = json.load(f)
            contract = AiCertifyContract.parse_obj(data)
            if validate_contract(contract):
                valid_count += 1
            else:
                invalid_count += 1
            aggregated["contracts"].append(contract.dict())
        except Exception as exc:
            logging.error(f"Failed to load contract from {cf}: {exc}")
            invalid_count += 1
    aggregated["valid"] = valid_count
    aggregated["invalid"] = invalid_count
    return aggregated
