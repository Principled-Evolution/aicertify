"""
AICertify Contract Input Models (Legacy)

This module is maintained for backward compatibility.
Please use aicertify.models.contract for new code.
"""

import warnings

# Emit a deprecation warning when this module is imported
warnings.warn(
    "The 'contract_models.py' module is deprecated and will be removed in a future release. "
    "Please use 'aicertify.models.contract' for new code.",
    DeprecationWarning, 
    stacklevel=2
)

# Re-export models from the centralized location
from aicertify.models.contract import (
    ModelInfo,
    Interaction,
    AiCertifyContract,
    create_contract,
    validate_contract,
    save_contract,
    load_contract
)

from typing import List, Optional, Dict, Any, ClassVar
from uuid import UUID, uuid4
from datetime import datetime
import json
import logging
from pathlib import Path

from pydantic import BaseModel, Field, model_validator

# Import the ModelCard class
from aicertify.models.model_card import ModelCard, create_model_card

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


class ModelInfo(BaseModel):
    """Model information for the AI system."""
    model_name: str
    model_version: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    model_card: Optional[ModelCard] = None  # Added ModelCard support


class Interaction(BaseModel):
    """Represents a single user-AI interaction."""
    interaction_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    input_text: str
    output_text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AiCertifyContract(BaseModel):
    """Pydantic contract model for AI compliance evaluation, serving as the interface for external systems."""
    contract_id: UUID = Field(default_factory=uuid4)
    application_name: str
    model_info: ModelInfo
    interactions: List[Interaction]
    final_output: Optional[str] = None
    
    # Enhanced context fields for Phase 1
    context: Dict[str, Any] = Field(default_factory=dict)
    compliance_context: Dict[str, Any] = Field(default_factory=dict)
    
    def get(self, key, default=None):
        """
        Get a value from the contract by key, similar to dictionary access.
        
        Args:
            key: The key to retrieve
            default: Default value to return if key is not found
            
        Returns:
            The value associated with the key or default if not found
        """
        if hasattr(self, key):
            return getattr(self, key)
        
        # Check in context and compliance_context
        if key in self.context:
            return self.context[key]
        if key in self.compliance_context:
            return self.compliance_context[key]
            
        return default
    
    @model_validator(mode='after')
    def validate_domain_specific(self):
        """Validate domain-specific requirements if domain is provided."""
        context = self.context
        domain = context.get("domain")
        
        if domain == "healthcare":
            # Validate healthcare-specific requirements
            if "risk_documentation" not in context:
                raise ValueError("Healthcare contracts must include risk documentation")
            if "patient_data" not in context:
                raise ValueError("Healthcare contracts must include patient data")
        
        elif domain == "finance":
            # Validate finance-specific requirements
            if "risk_documentation" not in context:
                raise ValueError("Financial contracts must include risk documentation")
            if "customer_data" not in context:
                raise ValueError("Financial contracts must include customer data")
        
        return self


def create_contract(
    application_name: str,
    model_info: Dict[str, Any],
    interactions: List[Dict[str, Any]],
    final_output: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    compliance_context: Optional[Dict[str, Any]] = None,
    model_card: Optional[ModelCard] = None
) -> AiCertifyContract:
    """
    Create and return an AiCertifyContract instance.

    Args:
        application_name: Name of the application
        model_info: Dictionary containing model information
        interactions: List of interaction dictionaries
        final_output: Optional final output text
        context: Optional context information
        compliance_context: Optional compliance context information
        model_card: Optional ModelCard instance for detailed model documentation

    Returns:
        An AiCertifyContract instance
    """
    # Handle model_card integration with model_info
    if model_card is not None:
        # If model_card is provided, ensure model_info has the key information
        model_info['model_name'] = model_info.get('model_name', model_card.model_name)
        model_info['model_version'] = model_info.get('model_version', model_card.model_version)
        
        # Create ModelInfo with model_card
        model_info_obj = ModelInfo(
            model_name=model_info['model_name'],
            model_version=model_info.get('model_version'),
            metadata=model_info.get('metadata', {}),
            model_card=model_card
        )
    else:
        # Create ModelInfo without model_card
        model_info_obj = ModelInfo(**model_info)

    # Create Interaction objects
    interaction_objects = []
    for interaction in interactions:
        if isinstance(interaction, Interaction):
            interaction_objects.append(interaction)
        else:
            interaction_objects.append(Interaction(**interaction))

    # Create contract
    return AiCertifyContract(
        application_name=application_name,
        model_info=model_info_obj,
        interactions=interaction_objects,
        final_output=final_output,
        context=context or {},
        compliance_context=compliance_context or {}
    )


def create_contract_with_model_card(
    application_name: str,
    model_card: ModelCard,
    interactions: List[Dict[str, Any]],
    final_output: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    compliance_context: Optional[Dict[str, Any]] = None
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
        'model_name': model_card.model_name,
        'model_version': model_card.model_version,
        'metadata': {
            'model_type': model_card.model_type,
            'organization': model_card.organization
        }
    }
    
    # If context doesn't exist, initialize it
    if context is None:
        context = {}
    
    # Add model card information to context
    if 'eu_ai_act' not in context:
        context['eu_ai_act'] = {}
    
    # Include risk_category in context if available
    if model_card.risk_category:
        context['eu_ai_act']['risk_category'] = model_card.risk_category
    
    # Include relevant_articles in context if available
    if model_card.relevant_articles:
        context['eu_ai_act']['relevant_articles'] = model_card.relevant_articles
    
    return create_contract(
        application_name=application_name,
        model_info=model_info,
        interactions=interactions,
        final_output=final_output,
        context=context,
        compliance_context=compliance_context,
        model_card=model_card
    )


def validate_contract(contract: AiCertifyContract) -> bool:
    """
    Validate the AiCertifyContract by ensuring mandatory fields are populated.

    Parameters:
        contract (AiCertifyContract): The contract to validate.

    Returns:
        bool: True if validation passes, False otherwise.
    """
    if not contract.application_name:
        logging.error("Validation failed: Application name is empty.")
        return False
    if not contract.interactions:
        logging.error("Validation failed: No interactions provided.")
        return False
    
    # Check for domain-specific requirements
    if "domain" in contract.context:
        domain = contract.context["domain"]
        if domain == "healthcare":
            if "risk_documentation" not in contract.context:
                logging.error("Validation failed: Healthcare contract missing risk documentation.")
                return False
            if "patient_data" not in contract.context:
                logging.error("Validation failed: Healthcare contract missing patient data.")
                return False
        elif domain == "finance":
            if "risk_documentation" not in contract.context:
                logging.error("Validation failed: Financial contract missing risk documentation.")
                return False
            if "customer_data" not in contract.context:
                logging.error("Validation failed: Financial contract missing customer data.")
                return False
    
    logging.info("Contract validated successfully.")
    return True


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
        "contracts": []
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


def save_contract(contract: AiCertifyContract, storage_dir: str = 'contracts') -> str:
    """
    Save the contract to a JSON file in the specified storage directory.

    Parameters:
        contract (AiCertifyContract): The contract to save.
        storage_dir (str, optional): Directory in which to save the contract file. Defaults to 'contracts'.

    Returns:
        str: The file path where the contract was saved.
    """
    # Ensure the storage directory exists
    storage_path = Path(storage_dir)
    storage_path.mkdir(parents=True, exist_ok=True)

    timestamp_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"contract_{timestamp_str}.json"
    file_path = storage_path / filename

    with open(file_path, 'w') as f:
        json.dump(contract.model_dump(), f, default=str, indent=2)

    return str(file_path)


def load_contract(contract_path: str) -> AiCertifyContract:
    """
    Load an AiCertifyContract from a JSON file.
    
    Parameters:
        contract_path (str): Path to the contract JSON file
        
    Returns:
        AiCertifyContract: The loaded contract object
    """
    try:
        with open(contract_path, "r") as f:
            contract_data = json.load(f)
        # Use model_validate for newer Pydantic versions
        try:
            return AiCertifyContract.model_validate(contract_data)
        except AttributeError:
            # Fallback for older Pydantic versions
            return AiCertifyContract.parse_obj(contract_data)
    except Exception as e:
        logging.error(f"Error loading contract from {contract_path}: {e}")
        raise 