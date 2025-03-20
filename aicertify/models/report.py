"""
Report models for AICertify.

This module contains models for representing evaluation reports,
including metric groups, policy results, and application details.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, model_validator, field_validator
from datetime import datetime, timezone

# Import the MetricValue from evaluation
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
    metrics: List[Dict[str, Any]] = Field(default_factory=list)
    description: Optional[str] = None


class PolicyResult(BaseModel):
    """
    Result of a policy evaluation.
    
    This model represents the outcome of evaluating a policy against an AI system,
    including whether the policy was satisfied and any additional details.
    
    Attributes:
        name: The identifier for the policy
        result: Whether the policy was satisfied (True) or not (False)
        details: Optional dictionary with additional details about the policy evaluation
        metrics: Dictionary of metrics from the policy evaluation
        is_nested: Whether this policy contains nested sub-policies
    """
    name: str
    result: bool
    metrics: Optional[Dict[str, Any]] = None
    details: Optional[Dict[str, Any]] = None
    is_nested: bool = False


class ApplicationDetails(BaseModel):
    """
    Contains details about the application being evaluated.
    """
    name: str
    evaluation_mode: str = "Standard"
    contract_count: int = 0 
    evaluation_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Date and time of evaluation (UTC timezone)"
    )
    model_info: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
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
        summary: Dictionary with summary information
        created_at: Date and time when the report was created
    """
    app_details: ApplicationDetails
    metric_groups: List[MetricGroup] = Field(default_factory=list)
    policy_results: List[PolicyResult] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)

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


def create_metric_group(category: str, metrics: Dict[str, Any]) -> MetricGroup:
    """
    Create a metric group from a category and metrics dictionary.
    
    Args:
        category: The category name for the metric group
        metrics: Dictionary of metrics where keys are metric IDs and values are metric data
        
    Returns:
        A MetricGroup containing the metrics
    """
    # Format the display name from the category
    display_name = " ".join(word.capitalize() for word in category.split("_"))
    
    # Create metric values list as dictionaries
    metric_values = []
    for metric_id, metric_data in metrics.items():
        metric_values.append({
            "name": metric_id,
            "value": metric_data.get("value"),
            "display_name": metric_data.get("name", metric_id),
            "description": metric_data.get("description"),
            "control_passed": metric_data.get("control_passed"),
            "threshold": metric_data.get("threshold"),
            "category": metric_data.get("category", category)
        })
    
    # Create and return the metric group
    return MetricGroup(
        name=category.lower().replace(" ", "_"),
        display_name=display_name,
        metrics=metric_values
    )


def create_evaluation_report(app_details: ApplicationDetails,
                            metric_groups: List[MetricGroup],
                            policy_results: List[PolicyResult],
                            summary: Optional[Dict[str, Any]] = None) -> EvaluationReport:
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