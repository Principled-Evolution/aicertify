"""
ModelCard Pydantic Model for AICertify

This module defines the ModelCard class and helper functions for creating
and using model cards in compliance evaluations, particularly for EU AI Act compliance.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator

class ModelCard(BaseModel):
    """
    Model card for AI model documentation and compliance evaluation.
    
    This structure follows the HuggingFace Model Card format with
    additional fields needed for EU AI Act compliance evaluation.
    
    Fields are organized into categories to make it easy for developers
    to understand what information is needed.
    """
    
    # Basic Information (Required)
    model_name: str = Field(
        ...,
        description="Name of the model"
    )
    model_version: Optional[str] = Field(
        None,
        description="Version of the model (e.g., '1.0', 'v2', etc.)"
    )
    model_type: str = Field(
        ...,
        description="Type of model (e.g., 'text-generation', 'image-classification', etc.)"
    )
    organization: str = Field(
        ...,
        description="Organization that developed or is responsible for the model"
    )
    
    # Intended Use (Required)
    primary_uses: List[str] = Field(
        ...,
        description="List of intended use cases for the model"
    )
    out_of_scope_uses: Optional[List[str]] = Field(
        None,
        description="List of use cases that are out of scope or not recommended"
    )
    
    # Model Details (Required)
    description: str = Field(
        ...,
        description="Detailed description of the model and its capabilities"
    )
    model_architecture: Optional[str] = Field(
        None,
        description="Description of the model architecture"
    )
    input_format: Optional[str] = Field(
        None,
        description="Description of expected input format"
    )
    output_format: Optional[str] = Field(
        None,
        description="Description of expected output format"
    )
    
    # Performance (Optional but Recommended)
    performance_metrics: Optional[Dict[str, Any]] = Field(
        None,
        description="Key performance metrics with values"
    )
    benchmark_results: Optional[Dict[str, Any]] = Field(
        None,
        description="Results on benchmark datasets"
    )
    decision_thresholds: Optional[Dict[str, float]] = Field(
        None,
        description="Thresholds used for making decisions"
    )
    
    # Data (Optional but Recommended)
    training_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Information about the training data"
    )
    evaluation_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Information about the evaluation data"
    )
    
    # Risk & Mitigation (EU AI Act Specific)
    ethical_considerations: Optional[List[str]] = Field(
        None,
        description="Ethical considerations related to model use"
    )
    limitations: Optional[List[str]] = Field(
        None,
        description="Known limitations of the model"
    )
    bias_considerations: Optional[Dict[str, Any]] = Field(
        None,
        description="Identified biases and considerations"
    )
    mitigation_strategies: Optional[List[str]] = Field(
        None,
        description="Strategies implemented to mitigate risks"
    )
    
    # Usage Guidelines (EU AI Act Specific)
    usage_guidelines: Optional[List[str]] = Field(
        None,
        description="Guidelines for proper model usage"
    )
    human_oversight_measures: Optional[List[str]] = Field(
        None,
        description="Measures for human oversight of model outputs"
    )
    
    # EU AI Act Compliance Information
    risk_category: Optional[str] = Field(
        None,
        description="EU AI Act risk category ('minimal', 'limited', 'high', etc.)"
    )
    relevant_articles: Optional[List[str]] = Field(
        None,
        description="Relevant EU AI Act articles for this model"
    )
    
    # Additional Information
    additional_info: Dict[str, Any] = Field(
        default_factory=dict,
        description="Any additional information relevant to the model"
    )
    
    @validator('risk_category')
    def validate_risk_category(cls, v):
        """Validate that risk_category is one of the allowed values."""
        allowed_categories = ['minimal', 'limited', 'high', 'unacceptable', None]
        if v not in allowed_categories:
            raise ValueError(f"risk_category must be one of {allowed_categories}")
        return v
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "model_name": "HealthcareGPT",
                "model_version": "1.0.0",
                "model_type": "text-generation",
                "organization": "Health AI Inc.",
                "primary_uses": ["Medical diagnosis assistance", "Healthcare information"],
                "out_of_scope_uses": ["Direct medical diagnosis without human review"],
                "description": "Large language model fine-tuned for healthcare domain.",
                "model_architecture": "Transformer-based with 1B parameters",
                "input_format": "Natural language text queries",
                "output_format": "Natural language text responses",
                "performance_metrics": {
                    "accuracy": 0.92,
                    "f1_score": 0.89
                },
                "ethical_considerations": [
                    "Data privacy concerns",
                    "Potential biases in medical training data"
                ],
                "limitations": [
                    "Limited knowledge cutoff",
                    "Not a replacement for medical professionals"
                ],
                "mitigation_strategies": [
                    "Human oversight required for all diagnoses",
                    "Clear confidence levels provided with responses"
                ],
                "risk_category": "high",
                "relevant_articles": ["Article 10", "Article 14"]
            }
        }


def create_model_card(
    model_name: str,
    model_type: str,
    organization: str,
    primary_uses: List[str],
    description: str,
    **kwargs
) -> ModelCard:
    """
    Helper function to create a ModelCard with minimum required fields.
    
    Args:
        model_name: Name of the model
        model_type: Type of model
        organization: Organization responsible for the model
        primary_uses: List of intended use cases
        description: Detailed description of the model
        **kwargs: Additional model card fields
        
    Returns:
        ModelCard instance
    """
    required_fields = {
        "model_name": model_name,
        "model_type": model_type,
        "organization": organization,
        "primary_uses": primary_uses,
        "description": description
    }
    
    # Combine required fields with additional kwargs
    model_card_data = {**required_fields, **kwargs}
    
    return ModelCard(**model_card_data)


def model_card_to_dict(model_card: ModelCard) -> Dict[str, Any]:
    """
    Convert a ModelCard to a dictionary suitable for API use.
    
    Args:
        model_card: ModelCard instance
        
    Returns:
        Dictionary representation of the model card
    """
    return model_card.dict(exclude_none=True)


def get_compliance_level(model_card: ModelCard) -> str:
    """
    Calculate the compliance level based on model card completeness.
    
    Args:
        model_card: ModelCard instance
        
    Returns:
        Compliance level ('minimal', 'partial', or 'comprehensive')
    """
    # Convert to dict and count non-None fields
    model_card_dict = model_card.dict(exclude_none=True)
    total_fields = len(ModelCard.__annotations__)
    filled_fields = len(model_card_dict)
    
    completion_ratio = filled_fields / total_fields
    
    if completion_ratio < 0.4:
        return "minimal"
    elif completion_ratio < 0.7:
        return "partial"
    else:
        return "comprehensive" 