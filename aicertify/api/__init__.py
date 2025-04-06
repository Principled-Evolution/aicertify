"""
AICertify API

A simple entry point for developers to integrate AICertify evaluation into their applications.
This module provides functions to evaluate AI interactions for compliance with various policies.
"""

import logging


# Re-export public API from specialized modules
from aicertify.api.core import (
    load_contract,
    CustomJSONEncoder
)

from aicertify.api.evaluators import (
    evaluate_contract,
    evaluate_contract_object,
    evaluate_contract_with_phase1_evaluators,
    evaluate_contract_comprehensive,
    evaluate_conversations
)

from aicertify.api.reports import (
    generate_report,
    generate_reports
)

from aicertify.api.policy import (
    evaluate_by_policy,
    aicertify_app_for_policy
)

# Configure logging
logger = logging.getLogger(__name__)
# Define the public API
__all__ = [
    'load_contract',
    'evaluate_contract',
    'evaluate_contract_object',
    'evaluate_contract_with_phase1_evaluators',
    'evaluate_contract_comprehensive',
    'evaluate_conversations',
    'generate_report',
    'generate_reports',
    'evaluate_by_policy',
    'aicertify_app_for_policy',
    'CustomJSONEncoder'
]
