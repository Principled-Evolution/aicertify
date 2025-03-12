"""
Report models for AICertify.

This module contains models for representing evaluation reports,
including metric groups, policy results, and application details.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, model_validator, field_validator
from datetime import datetime, timezone

# Import from centralized models
from aicertify.models.evaluation import MetricValue


class MetricGroup(BaseModel):
    """
    Group of related metrics.
    
    This model represents a collection of related metrics with a common name and display name.
    
    Attributes:
        name: The identifier for the metric group
        display_name: Human-readable name for the metric group
        metrics: List of metrics in the group
        description: Optional description of the metric group
    """
    name: str
    display_name: str
    metrics: List[MetricValue]
    description: Optional[str] = None
    
    @model_validator(mode='after')
    def validate_metrics_not_empty(self):
        """Validate that the metrics list is not empty."""
        if not self.metrics:
            raise ValueError(f"Metric group '{self.name}' must contain at least one metric")
        return self


class PolicyResult(BaseModel):
    """
    Result of a policy evaluation.
    
    This model represents the outcome of evaluating a policy against an AI system,
    including whether the policy was satisfied and any additional details.
    
    Attributes:
        name: The identifier for the policy
        result: Whether the policy was satisfied (True) or not (False)
        details: Optional dictionary with additional details about the policy evaluation
    """
    name: str
    result: bool
    details: Optional[Dict[str, Any]] = None


class ApplicationDetails(BaseModel):
    """
    Basic details about the application being evaluated.
    
    This model contains information about the AI application that was evaluated,
    including its name, evaluation mode, and the number of contracts evaluated.
    
    Attributes:
        name: The name of the application
        evaluation_mode: The mode of evaluation (e.g., "Automatic", "Manual")
        contract_count: The number of contracts evaluated (must be non-negative)
        evaluation_date: The date and time of the evaluation (UTC timezone)
    """
    name: str
    evaluation_mode: str
    contract_count: int = Field(ge=0, description="Number of contracts evaluated (must be non-negative)")
    evaluation_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Date and time of evaluation (UTC timezone)"
    )
    
    @field_validator('evaluation_date')
    @classmethod
    def ensure_timezone_aware(cls, v: datetime) -> datetime:
        """Ensure the evaluation date is timezone aware, converting to UTC if needed."""
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v


class EvaluationReport(BaseModel):
    """
    Main report model containing all evaluation data.
    
    This model represents a complete evaluation report for an AI system,
    including application details, metric groups, and policy results.
    
    Attributes:
        app_details: Details about the application being evaluated
        metric_groups: List of metric groups with their metrics
        policy_results: List of policy evaluation results
        summary: Optional summary of the evaluation
    """
    app_details: ApplicationDetails
    metric_groups: List[MetricGroup]
    policy_results: List[PolicyResult]
    summary: Optional[str] = None
    
    @model_validator(mode='after')
    def validate_report_structure(self):
        """Validate the overall structure of the report."""
        if not self.metric_groups:
            raise ValueError("Report must contain at least one metric group")
        if not self.policy_results:
            raise ValueError("Report must contain at least one policy result")
        return self

    class Config:
        json_schema_extra = {
            "example": {
                "app_details": {
                    "name": "TestApp",
                    "evaluation_mode": "Automatic",
                    "contract_count": 5,
                    "evaluation_date": "2024-03-20T10:00:00Z"
                },
                "metric_groups": [
                    {
                        "name": "fairness",
                        "display_name": "Fairness Metrics",
                        "metrics": [
                            {
                                "name": "ftu_satisfied",
                                "display_name": "FTU Satisfied",
                                "value": True
                            },
                            {
                                "name": "race_words_count",
                                "display_name": "Race Words Count",
                                "value": 0
                            }
                        ]
                    }
                ],
                "policy_results": [
                    {
                        "name": "eu_ai_act",
                        "result": True,
                        "details": {"specific_rule": "passed"}
                    }
                ],
                "summary": "All evaluation criteria met"
            }
        }


def create_metric_group(name: str, display_name: str, metrics: List[MetricValue], 
                        description: Optional[str] = None) -> MetricGroup:
    """
    Create a metric group with the given parameters.
    
    Args:
        name: The identifier for the metric group
        display_name: Human-readable name for the metric group
        metrics: List of metrics in the group
        description: Optional description of the metric group
        
    Returns:
        MetricGroup: A validated metric group instance
        
    Raises:
        ValueError: If metrics is empty or validation fails
    """
    return MetricGroup(
        name=name,
        display_name=display_name,
        metrics=metrics,
        description=description
    )


def create_evaluation_report(app_details: ApplicationDetails,
                            metric_groups: List[MetricGroup],
                            policy_results: List[PolicyResult],
                            summary: Optional[str] = None) -> EvaluationReport:
    """
    Create an evaluation report with the given parameters.
    
    Args:
        app_details: Details about the application being evaluated
        metric_groups: List of metric groups with their metrics
        policy_results: List of policy evaluation results
        summary: Optional summary of the evaluation
        
    Returns:
        EvaluationReport: A validated evaluation report instance
        
    Raises:
        ValueError: If validation fails (e.g., empty metric_groups or policy_results)
    """
    return EvaluationReport(
        app_details=app_details,
        metric_groups=metric_groups,
        policy_results=policy_results,
        summary=summary
    ) 