"""
AICertify Models Package

This package contains all the data models used by AICertify.
"""

# Import and re-export the contract models for easier access
from aicertify.models.contract_models import (
    ModelInfo,
    Interaction,
    AiCertifyContract,
    create_contract,
    validate_contract,
    save_contract,
    load_contract
)

# Import and re-export the evaluation models
from aicertify.models.evaluation_models import (
    AiEvaluationResult,
    AiComplianceInput
)

__all__ = [
    # Contract models
    'ModelInfo',
    'Interaction',
    'AiCertifyContract',
    'create_contract',
    'validate_contract',
    'save_contract',
    'load_contract',
    
    # Evaluation models
    'AiEvaluationResult',
    'AiComplianceInput'
]
