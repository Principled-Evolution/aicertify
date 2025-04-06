"""
OPA Results Schema Models

These Pydantic models represent the exact structure of OPA evaluation results
to ensure reliable extraction of metrics and policy results.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Any, Optional, Union
from datetime import datetime


class MetricValue(BaseModel):
    """Individual metric value from an OPA policy evaluation."""

    control_passed: bool = Field(
        ..., description="Whether this control passed validation"
    )
    name: str = Field(..., description="Display name of the metric")
    value: Any = Field(..., description="Value of the metric (can be any type)")


class Location(BaseModel):
    """Location information in OPA evaluation results."""

    row: int
    col: int


class ReportOutput(BaseModel):
    """The core policy report output structure."""

    metrics: Dict[str, MetricValue] = Field(
        ..., description="Map of metric IDs to metric values"
    )
    policy: str = Field(..., description="Display name of the policy")
    result: bool = Field(..., description="Overall result of the policy evaluation")
    timestamp: Union[int, str] = Field(..., description="Timestamp of evaluation")


class Expression(BaseModel):
    """Expression evaluation details from OPA."""

    value: ReportOutput = Field(..., description="The actual report output data")
    text: str = Field(..., description="OPA query text that returned this result")
    location: Optional[Location] = Field(
        None, description="Source location information"
    )

    @validator("text")
    def validate_report_output_text(cls, v):
        """Ensure the text field contains 'report_output'."""
        if "report_output" not in v:
            raise ValueError("Expression text must contain 'report_output'")
        return v


class ExpressionResult(BaseModel):
    """Container for expressions."""

    expressions: List[Expression]


class PolicyResult(BaseModel):
    """Result for a specific policy."""

    result: List[ExpressionResult]


class PolicyEvaluation(BaseModel):
    """Individual policy evaluation result."""

    policy: str = Field(..., description="Policy identifier including full path")
    result: PolicyResult


class AggregatedResults(BaseModel):
    """Top-level container for aggregated policy results."""

    policy: str = Field("Aggregated Individual Results")
    results: List[PolicyEvaluation]
    timestamp: Optional[str] = None


class OpaEvaluationResults(BaseModel):
    """Complete OPA evaluation results structure."""

    result: AggregatedResults


class ExtractedPolicyResult(BaseModel):
    """Simplified extracted policy result for report generation."""

    policy_id: str = Field(..., description="Original policy identifier (full path)")
    policy_name: str = Field(..., description="Display name of the policy")
    result: bool = Field(..., description="Overall policy evaluation result")
    metrics: Dict[str, MetricValue] = Field(
        ..., description="All metrics from this policy"
    )
    timestamp: Optional[Union[int, str, datetime]] = None

    class Config:
        """Pydantic model configuration."""

        validate_assignment = True
