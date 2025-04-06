"""
Contract models for AICertify.

This module contains models for representing AI contracts, including ModelInfo,
Interaction, and AiCertifyContract, as well as helper functions for creating,
validating, and managing contracts.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timezone
import json
import logging
from pathlib import Path

from pydantic import BaseModel, Field, model_validator

# Import from centralized models
from aicertify.models.model_card import ModelCard
from aicertify.models.base import validate_model_data

logger = logging.getLogger(__name__)

# Domain-specific requirements mapping
DOMAIN_REQUIREMENTS = {
    "healthcare": ["risk_documentation", "patient_data"],
    "finance": ["risk_documentation", "customer_data"]
}


class ModelInfo(BaseModel):
    """
    Model information for the AI system.
    
    This model contains information about the AI model being evaluated,
    including its name, version, and optional model card.
    
    Attributes:
        model_name: The name of the AI model
        model_version: Optional version identifier for the model
        metadata: Additional metadata about the model
        model_card: Optional detailed model card with comprehensive information
    """
    model_name: str
    model_version: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    model_card: Optional[ModelCard] = None


class Interaction(BaseModel):
    """
    Represents a single user-AI interaction.
    
    This model captures a single interaction between a user and an AI system,
    including the input, output, and metadata about the interaction.
    
    Attributes:
        interaction_id: Unique identifier for the interaction
        timestamp: When the interaction occurred (UTC)
        input_text: The user's input to the AI system
        output_text: The AI system's response
        metadata: Additional metadata about the interaction
    """
    interaction_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of the interaction (UTC timezone)"
    )
    input_text: str
    output_text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AiCertifyContract(BaseModel):
    """
    Pydantic contract model for AI compliance evaluation.
    
    This model serves as the interface for external systems to provide
    interaction data to the certifier library for evaluation.
    
    Attributes:
        contract_id: Unique identifier for the contract
        application_name: Name of the application being evaluated
        model_info: Information about the AI model
        interactions: List of user-AI interactions
        final_output: Optional final output or summary
        context: Additional context information
        compliance_context: Compliance-specific context information
    """
    contract_id: UUID = Field(default_factory=uuid4)
    application_name: str
    model_info: ModelInfo
    interactions: List[Interaction]
    final_output: Optional[str] = None
    
    # Enhanced context fields
    context: Dict[str, Any] = Field(default_factory=dict)
    compliance_context: Dict[str, Any] = Field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
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
    
    def __getitem__(self, key: str) -> Any:
        """
        Support dictionary-style access to contract attributes and context.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The value associated with the key
            
        Raises:
            KeyError: If the key is not found
        """
        if hasattr(self, key):
            return getattr(self, key)
        
        # Check in context and compliance_context
        if key in self.context:
            return self.context[key]
        if key in self.compliance_context:
            return self.compliance_context[key]
            
        raise KeyError(f"Key '{key}' not found in contract")
    
    @model_validator(mode='after')
    def validate_domain_specific(self) -> "AiCertifyContract":
        """
        Validate domain-specific requirements if domain is provided.
        
        Returns:
            The validated contract instance
            
        Raises:
            ValueError: If domain-specific requirements are not met
        """
        context = self.context
        domain = context.get("domain")
        
        if domain in DOMAIN_REQUIREMENTS:
            for required_key in DOMAIN_REQUIREMENTS[domain]:
                if required_key not in context:
                    raise ValueError(f"{domain.capitalize()} contracts must include {required_key}")
        
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
        AiCertifyContract: A validated contract instance
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


def validate_contract(contract: AiCertifyContract) -> bool:
    """
    Validate the AiCertifyContract by ensuring mandatory fields are populated.

    Args:
        contract: The contract to validate

    Returns:
        bool: True if validation passes, False otherwise
    """
    if not contract.application_name:
        logger.error("Validation failed: Application name is empty.")
        return False
    if not contract.interactions:
        logger.error("Validation failed: No interactions provided.")
        return False
    
    # Check for domain-specific requirements
    domain = contract.context.get("domain")
    if domain in DOMAIN_REQUIREMENTS:
        for required_key in DOMAIN_REQUIREMENTS[domain]:
            if required_key not in contract.context:
                logger.error(f"Validation failed: {domain.capitalize()} contract missing {required_key}.")
                return False
    
    logger.info("Contract validated successfully.")
    return True


def save_contract(contract: AiCertifyContract, file_path: str) -> bool:
    """
    Save a contract to a JSON file.

    Args:
        contract: The contract to save
        file_path: Path where the contract should be saved

    Returns:
        bool: True if the contract was saved successfully, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Convert contract to JSON and save
        with open(file_path, 'w') as f:
            json.dump(contract.model_dump(), f, default=str, indent=2)
        
        logger.info(f"Contract saved to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save contract: {str(e)}")
        return False


def load_contract(file_path: str) -> Optional[AiCertifyContract]:
    """
    Load a contract from a JSON file.

    Args:
        file_path: Path to the contract JSON file

    Returns:
        Optional[AiCertifyContract]: The loaded contract, or None if loading failed
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Validate the loaded data
        validation_result = validate_model_data(data, AiCertifyContract)
        if not validation_result.is_valid:
            logger.error(f"Invalid contract data: {validation_result.error_message}")
            return None
            
        logger.info(f"Contract loaded from {file_path}")
        return validation_result.model_instance
    except Exception as e:
        logger.error(f"Failed to load contract: {str(e)}")
        return None


# Explicitly define the public API
__all__ = [
    'ModelInfo',
    'Interaction',
    'AiCertifyContract',
    'create_contract',
    'validate_contract',
    'save_contract',
    'load_contract'
] 