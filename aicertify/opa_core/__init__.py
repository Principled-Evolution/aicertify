"""
OPA Core - Open Policy Agent integration for AICertify.

This package provides tools for working with OPA policies and evaluating
inputs against those policies.
"""

# Import main components
from aicertify.opa_core.evaluator import OpaEvaluator
from aicertify.opa_core.policy_loader import PolicyLoader

# Import extraction utilities
from aicertify.opa_core.extraction import (
    extract_policy_results,
    extract_all_policy_results,
    extract_policy_data,
    validate_opa_results,
)

# Define package exports
__all__ = [
    'OpaEvaluator',
    'PolicyLoader',
    'extract_policy_results',
    'extract_all_policy_results',
    'extract_policy_data',
    'validate_opa_results',
]
