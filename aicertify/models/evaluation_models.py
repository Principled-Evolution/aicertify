'''Phase 1: Simplified AICertify Contract Models and Helpers
This module implements a deterministic, easy-to-implement contract based on the AICertify roadmap Phase 1.
'''

from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
import json
import logging

from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    """Model information for the AI system."""
    model_name: str
    model_version: Optional[str] = None
    additional_info: Dict[str, Any] = Field(default_factory=dict)


class Interaction(BaseModel):
    """Represents a single user-AI interaction."""
    interaction_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    input_text: str
    output_text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AiCertifyContract(BaseModel):
    """Pydantic contract model for AI compliance evaluation."""
    contract_id: UUID = Field(default_factory=uuid4)
    application_name: str
    model_info: ModelInfo
    interactions: List[Interaction]
    final_output: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)


def create_contract(
    application_name: str,
    model_info: Dict[str, Any],
    interactions: List[Dict[str, Any]],
    final_output: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> AiCertifyContract:
    """
    Create and return an AiCertifyContract instance.

    Parameters:
        application_name (str): Name of the application.
        model_info (Dict[str, Any]): A dictionary containing model information.
        interactions (List[Dict[str, Any]]): A list of dictionaries with keys 'input_text' and 'output_text'.
        final_output (Optional[str], optional): Final output or summary of the evaluation.
        context (Optional[Dict[str, Any]], optional): Additional context or metadata.

    Returns:
        AiCertifyContract: The constructed contract.
    """
    interactions_objs = [Interaction(**data) for data in interactions]
    contract = AiCertifyContract(
        application_name=application_name,
        model_info=ModelInfo(**model_info),
        interactions=interactions_objs,
        final_output=final_output,
        context=context or {}
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
    logging.info("Contract validated successfully.")
    return True


def aggregate_contracts(contract_files: List[str]) -> Dict[str, Any]:
    """
    Aggregate multiple JSON contract files into a single compliance result.

    For this stub, simply count valid and invalid contracts.

    Parameters:
        contract_files (List[str]): List of file paths to JSON contract files.

    Returns:
        Dict[str, Any]: A dictionary with aggregated contract validation results.
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


# === Added OPA Compliance Models ===

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from aicertify.models.contract_models import AiCertifyContract


class AiEvaluationResult(BaseModel):
    """Captures the final or aggregated results from multiple evaluators,
    e.g. fairness, toxicity, PII scanning, security checks, etc."""
    contract_id: str
    application_name: str
    fairness_metrics: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Consolidated fairness data (toxicity, stereotype, etc.)"
    )
    pii_detected: Optional[bool] = None
    pii_details: Optional[Dict[str, Any]] = None
    security_findings: Optional[Dict[str, Any]] = None
    summary_text: Optional[str] = None
    aggregated_from_contract_count: Optional[int] = None
    evaluation_mode: Optional[str] = None


class AiComplianceInput(BaseModel):
    """The final input to OPA, bundling contract and evaluation results."""
    contract: AiCertifyContract
    evaluation: AiEvaluationResult 