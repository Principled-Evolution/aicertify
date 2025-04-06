"""
Evaluation models for AICertify.

This module contains models for representing evaluation results and metrics.
"""

# Standard library imports
from enum import Enum
from typing import Any, Dict, Optional, Union

# Third-party imports
from pydantic import BaseModel, Field, field_validator

# Project-specific imports
from aicertify.models.contract import AiCertifyContract


class EvaluationMode(str, Enum):
    """Enumeration of valid evaluation modes."""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    HYBRID = "hybrid"


class MetricValue(BaseModel):
    """
    Base model for metric values that can be of different types.
    
    Attributes:
        name: The identifier for the metric
        value: The value of the metric (can be various types)
        display_name: Human readable name for the metric
        metadata: Optional additional information about the metric
    """
    name: str = Field(
        ..., 
        description="Unique identifier for the metric"
    )
    value: Union[str, bool, float, int, Dict[str, Any]] = Field(
        ...,
        description="Value of the metric, which can be a string, boolean, number, or structured data"
    )
    display_name: str = Field(
        ..., 
        description="Human readable name for the metric"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional information about the metric, such as confidence scores or context"
    )


class AiEvaluationResult(BaseModel):
    """
    Captures the final or aggregated results from multiple evaluators.
    
    This model represents the combined results from various evaluators,
    including fairness, toxicity, PII scanning, security checks, etc.
    
    Attributes:
        contract_id: The ID of the contract being evaluated
        application_name: The name of the application being evaluated
        fairness_metrics: Optional consolidated fairness data
        pii_detected: Whether PII was detected in the interactions
        pii_details: Optional details about detected PII
        security_findings: Optional security findings
        summary_text: Optional summary of the evaluation
        aggregated_contract_count: Optional count of contracts aggregated
        evaluation_mode: Optional mode of evaluation (e.g., "automatic", "manual", "hybrid")
    """
    contract_id: str = Field(
        ...,
        description="Unique identifier for the contract being evaluated"
    )
    application_name: str = Field(
        ...,
        description="Name of the application being evaluated"
    )
    fairness_metrics: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Consolidated fairness data (toxicity, stereotype, etc.)"
    )
    pii_detected: Optional[bool] = Field(
        default=None,
        description="Whether personally identifiable information was detected"
    )
    pii_details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Details about detected personally identifiable information"
    )
    security_findings: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Security-related findings from the evaluation"
    )
    summary_text: Optional[str] = Field(
        default=None,
        description="Human-readable summary of the evaluation results"
    )
    aggregated_contract_count: Optional[int] = Field(
        default=None,
        description="Number of contracts from which this evaluation was aggregated"
    )
    evaluation_mode: Optional[str] = Field(
        default=None,
        description="Mode of evaluation (automatic, manual, or hybrid)"
    )
    
    @field_validator('evaluation_mode')
    @classmethod
    def validate_evaluation_mode(cls, v: Optional[str]) -> Optional[str]:
        """Validate that evaluation_mode is one of the allowed values."""
        if v is None:
            return v
        
        try:
            return EvaluationMode(v.lower()).value
        except ValueError:
            valid_modes = [mode.value for mode in EvaluationMode]
            raise ValueError(f"evaluation_mode must be one of {valid_modes}")
    
    @classmethod
    def create(
        cls,
        contract_id: str,
        application_name: str,
        fairness_metrics: Optional[Dict[str, Any]] = None,
        pii_detected: Optional[bool] = None,
        pii_details: Optional[Dict[str, Any]] = None,
        security_findings: Optional[Dict[str, Any]] = None,
        summary_text: Optional[str] = None,
        aggregated_contract_count: Optional[int] = None,
        evaluation_mode: Optional[str] = None
    ) -> "AiEvaluationResult":
        """
        Create an evaluation result with the given parameters.
        
        Args:
            contract_id: The ID of the contract being evaluated
            application_name: The name of the application being evaluated
            fairness_metrics: Optional consolidated fairness data
            pii_detected: Whether PII was detected in the interactions
            pii_details: Optional details about detected PII
            security_findings: Optional security findings
            summary_text: Optional summary of the evaluation
            aggregated_contract_count: Optional count of contracts aggregated
            evaluation_mode: Optional mode of evaluation
            
        Returns:
            AiEvaluationResult: A validated evaluation result instance
        """
        return cls(
            contract_id=contract_id,
            application_name=application_name,
            fairness_metrics=fairness_metrics,
            pii_detected=pii_detected,
            pii_details=pii_details,
            security_findings=security_findings,
            summary_text=summary_text,
            aggregated_contract_count=aggregated_contract_count,
            evaluation_mode=evaluation_mode
        )


class AiComplianceInput(BaseModel):
    """
    The final input to OPA, bundling contract and evaluation results.
    
    This model combines a contract and its evaluation results into a single
    object that can be passed to the OPA policy engine for compliance evaluation.
    
    Attributes:
        contract: The contract being evaluated
        evaluation: The evaluation results for the contract
    """
    contract: AiCertifyContract = Field(
        ...,
        description="The contract containing interactions to evaluate"
    )
    evaluation: AiEvaluationResult = Field(
        ...,
        description="The evaluation results for the contract"
    )
    
    @classmethod
    def create(
        cls,
        contract: AiCertifyContract,
        evaluation: AiEvaluationResult
    ) -> "AiComplianceInput":
        """
        Create a compliance input with the given parameters.
        
        Args:
            contract: The contract being evaluated
            evaluation: The evaluation results for the contract
            
        Returns:
            AiComplianceInput: A validated compliance input instance
        """
        return cls(
            contract=contract,
            evaluation=evaluation
        )


# For backward compatibility
def create_evaluation_result(
    contract_id: str,
    application_name: str,
    fairness_metrics: Optional[Dict[str, Any]] = None,
    pii_detected: Optional[bool] = None,
    pii_details: Optional[Dict[str, Any]] = None,
    security_findings: Optional[Dict[str, Any]] = None,
    summary_text: Optional[str] = None,
    aggregated_from_contract_count: Optional[int] = None,
    evaluation_mode: Optional[str] = None
) -> AiEvaluationResult:
    """
    Create an evaluation result with the given parameters.
    
    This function is maintained for backward compatibility.
    Consider using AiEvaluationResult.create() for new code.
    
    Args:
        contract_id: The ID of the contract being evaluated
        application_name: The name of the application being evaluated
        fairness_metrics: Optional consolidated fairness data
        pii_detected: Whether PII was detected in the interactions
        pii_details: Optional details about detected PII
        security_findings: Optional security findings
        summary_text: Optional summary of the evaluation
        aggregated_from_contract_count: Optional count of contracts aggregated
        evaluation_mode: Optional mode of evaluation
        
    Returns:
        AiEvaluationResult: A validated evaluation result instance
    """
    return AiEvaluationResult.create(
        contract_id=contract_id,
        application_name=application_name,
        fairness_metrics=fairness_metrics,
        pii_detected=pii_detected,
        pii_details=pii_details,
        security_findings=security_findings,
        summary_text=summary_text,
        aggregated_contract_count=aggregated_from_contract_count,
        evaluation_mode=evaluation_mode
    )


def create_compliance_input(
    contract: AiCertifyContract,
    evaluation: AiEvaluationResult
) -> AiComplianceInput:
    """
    Create a compliance input with the given parameters.
    
    This function is maintained for backward compatibility.
    Consider using AiComplianceInput.create() for new code.
    
    Args:
        contract: The contract being evaluated
        evaluation: The evaluation results for the contract
        
    Returns:
        AiComplianceInput: A validated compliance input instance
    """
    return AiComplianceInput.create(
        contract=contract,
        evaluation=evaluation
    )


# Explicitly define the public API
__all__ = [
    'MetricValue',
    'AiEvaluationResult',
    'AiComplianceInput',
    'EvaluationMode',
    'create_evaluation_result',
    'create_compliance_input'
] 