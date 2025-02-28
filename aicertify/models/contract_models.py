'''Phase 1: AICertify Contract Input Models
This module contains the contract input models intended for developers and external systems to use as the interface for providing interaction data to the certifier library.

It includes the core models: ModelInfo, Interaction, and AiCertifyContract, as well as helper methods for creating, validating, and aggregating contracts.
'''

from typing import List, Optional, Dict, Any, ClassVar
from uuid import UUID, uuid4
from datetime import datetime
import json
import logging
from pathlib import Path

from pydantic import BaseModel, Field, model_validator


class ModelInfo(BaseModel):
    """Model information for the AI system."""
    model_name: str
    model_version: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


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
    compliance_context: Optional[Dict[str, Any]] = None
) -> AiCertifyContract:
    """
    Create and return an AiCertifyContract instance.

    Parameters:
        application_name (str): Name of the application.
        model_info (Dict[str, Any]): A dictionary containing model information.
        interactions (List[Dict[str, Any]]): A list of dictionaries with keys 'input_text' and 'output_text'.
        final_output (Optional[str], optional): Final output or summary of the evaluation.
        context (Optional[Dict[str, Any]], optional): Domain-specific context or metadata.
            For healthcare domain, should include:
                - domain: "healthcare"
                - patient_data: Dictionary with demographics and medical history
                - risk_documentation: String with risk assessment and mitigation measures
            For finance domain, should include:
                - domain: "finance"
                - customer_data: Dictionary with demographics and financial profile
                - risk_documentation: String with risk assessment and mitigation measures
        compliance_context (Optional[Dict[str, Any]], optional): Compliance-related context.
            Should include:
                - jurisdictions: List of applicable jurisdictions (e.g., ["us", "eu"])
                - frameworks: List of applicable regulatory frameworks (e.g., ["hipaa", "eu_ai_act"])

    Returns:
        AiCertifyContract: The constructed contract.
    """
    interactions_objs = [Interaction(**data) for data in interactions]
    contract = AiCertifyContract(
        application_name=application_name,
        model_info=ModelInfo(**model_info),
        interactions=interactions_objs,
        final_output=final_output,
        context=context or {},
        compliance_context=compliance_context or {}
    )
    logging.info("Contract created successfully.")
    return contract


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