"""
Report models for AICertify (Legacy).

This module is maintained for backward compatibility.
Please use aicertify.models.report for new code.
"""

import warnings

# Issue a deprecation warning
warnings.warn(
    "The module aicertify.report_generation.report_models is deprecated. "
    "Please use aicertify.models.report and aicertify.models.evaluation instead.",
    DeprecationWarning,
    stacklevel=2
)

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