"""
Simplified AICertify Contract Models and Helpers (Legacy)

This module is maintained for backward compatibility.
Please use aicertify.models.contract and aicertify.models.evaluation for new code.
"""

import warnings

# Intentionally re-export models from the centralized location for backward compatibility
from aicertify.models.contract import (
    ModelInfo,
    Interaction,
    AiCertifyContract,
    create_contract,
    validate_contract,
)

from aicertify.models.evaluation import (
    AiEvaluationResult,
    AiComplianceInput,
    create_evaluation_result,
    create_compliance_input,
)


# Emit a deprecation warning when this module is imported
warnings.warn(
    "The 'evaluation_models.py' module is deprecated and will be removed in a future release. "
    "Please use 'aicertify.models.contract' and 'aicertify.models.evaluation' for new code.",
    DeprecationWarning,
    stacklevel=2,
)

# Define the public API for this module
__all__ = [
    "ModelInfo",
    "Interaction",
    "AiCertifyContract",
    "create_contract",
    "validate_contract",
    "AiEvaluationResult",
    "AiComplianceInput",
    "create_evaluation_result",
    "create_compliance_input",
]
