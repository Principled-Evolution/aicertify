"""
Report models for AICertify (Legacy).

This module is maintained for backward compatibility.
Please use aicertify.models.report for new code.
"""

import warnings
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# Re-export models from the centralized location
from aicertify.models.report import (
    MetricGroup,
    PolicyResult,
    ApplicationDetails,
    EvaluationReport,
    create_metric_group,
    create_evaluation_report
)

# Re-export MetricValue from the centralized location
from aicertify.models.evaluation import MetricValue
# Issue a deprecation warning
warnings.warn(
    "The module aicertify.report_generation.report_models is deprecated. "
    "Please use aicertify.models.report and aicertify.models.evaluation instead.",
    DeprecationWarning,
    stacklevel=2
)

# Define the public API
__all__ = [
    'MetricValue',
    'MetricGroup',
    'PolicyResult',
    'ApplicationDetails',
    'EvaluationReport',
    'create_metric_group',
    'create_evaluation_report'
]

class MetricResult(BaseModel):
    """Individual metric result"""
    name: str
    value: Any
    control_passed: bool
    
    class Config:
        arbitrary_types_allowed = True

class ControlSummary(BaseModel):
    """Summary of control evaluation results"""
    total_controls: int = 0
    passed_controls: int = 0
    failed_controls: int = 0
    
    @property
    def pass_rate(self) -> float:
        """Calculate the pass rate as a percentage"""
        if self.total_controls == 0:
            return 0.0
        return (self.passed_controls / self.total_controls) * 100

class PolicyReport(BaseModel):
    """Individual policy report from OPA evaluation"""
    policy: str
    result: bool
    metrics: Dict[str, MetricResult]
    timestamp: int
    package_path: Optional[str] = None  # Added to track nested policy location
    file_path: Optional[str] = None     # Added to track policy file location

class NestedPolicyReport(BaseModel):
    """Container for nested policy reports with metadata"""
    category: str
    subcategory: str
    version: str
    evaluation_time: datetime
    total_policies: int
    successful_evaluations: int
    failed_evaluations: int
    policy_reports: List[PolicyReport]
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as a percentage"""
        if self.total_policies == 0:
            return 0.0
        if self.successful_evaluations == 0:
            return 0.0
        return (self.successful_evaluations / self.total_policies) * 100

class AggregatedReport(BaseModel):
    """Aggregated report combining multiple policy results"""
    app_name: str
    evaluation_date: datetime = Field(default_factory=datetime.now)
    regulations: List[str]
    control_summary: ControlSummary
    policy_reports: List[PolicyReport]
    nested_reports: List[NestedPolicyReport] = Field(default_factory=list)  # Added for nested policy results
    recommendations: List[str] = Field(default_factory=list)
    
    def calculate_control_summary(self) -> None:
        """Calculate control summary from all policy reports including nested ones"""
        total = 0
        passed = 0
        
        # Process regular policy reports
        for policy in self.policy_reports:
            for metric in policy.metrics.values():
                total += 1
                if metric.control_passed:
                    passed += 1
        
        # Process nested policy reports
        for nested_report in self.nested_reports:
            for policy in nested_report.policy_reports:
                for metric in policy.metrics.values():
                    total += 1
                    if metric.control_passed:
                        passed += 1
        
        self.control_summary = ControlSummary(
            total_controls=total,
            passed_controls=passed,
            failed_controls=total - passed
        ) 