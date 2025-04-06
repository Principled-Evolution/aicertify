"""
AICertify Models Package

This package contains all the data models used by AICertify.
"""

# Base utilities
from aicertify.models.base import ValidationResult, validate_model_data

# Contract models
from aicertify.models.contract import (
    ModelInfo,
    Interaction,
    AiCertifyContract,
    create_contract,
    validate_contract,
    save_contract,
    load_contract,
)

# Evaluation models
from aicertify.models.evaluation import (
    MetricValue,
    AiEvaluationResult,
    AiComplianceInput,
    create_evaluation_result,
    create_compliance_input,
)

# Report models
from aicertify.models.report import (
    MetricGroup,
    PolicyResult,
    ApplicationDetails,
    EvaluationReport,
    create_metric_group,
    create_evaluation_report,
)

# Policy models
from aicertify.models.policy_models import PolicyParameter

# Model card
from aicertify.models.model_card import ModelCard, create_model_card

# LangFair evaluation models
from aicertify.models.langfair_eval import (
    AutoEvalInput,
    ToxicityMetrics,
    StereotypeMetrics,
    CounterfactualMetrics,
    FairnessMetrics,
    AutoEvalResult,
)

__all__ = [
    # Base utilities
    "ValidationResult",
    "validate_model_data",
    # Contract models
    "ModelInfo",
    "Interaction",
    "AiCertifyContract",
    "create_contract",
    "validate_contract",
    "save_contract",
    "load_contract",
    # Evaluation models
    "MetricValue",
    "AiEvaluationResult",
    "AiComplianceInput",
    "create_evaluation_result",
    "create_compliance_input",
    # Report models
    "MetricGroup",
    "PolicyResult",
    "ApplicationDetails",
    "EvaluationReport",
    "create_metric_group",
    "create_evaluation_report",
    # Policy models
    "PolicyParameter",
    # Model card
    "ModelCard",
    "create_model_card",
    # LangFair evaluation models
    "AutoEvalInput",
    "ToxicityMetrics",
    "StereotypeMetrics",
    "CounterfactualMetrics",
    "FairnessMetrics",
    "AutoEvalResult",
]
