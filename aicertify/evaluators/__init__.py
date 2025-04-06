"""
AICertify Evaluators Package

This package provides standardized evaluators for different compliance domains.
"""

import threading

from aicertify.evaluators.base_evaluator import BaseEvaluator, EvaluationResult, Report
from aicertify.evaluators.fairness_evaluator import FairnessEvaluator
from aicertify.evaluators.content_safety_evaluator import ContentSafetyEvaluator
from aicertify.evaluators.risk_management_evaluator import RiskManagementEvaluator
from aicertify.evaluators.compliance_evaluator import (
    ComplianceEvaluator,
    EvaluatorConfig,
)
from aicertify.evaluators.accuracy_evaluator import AccuracyEvaluator
from aicertify.evaluators.biometric_categorization_evaluator import (
    BiometricCategorizationEvaluator,
)

# Import prohibited practices evaluators
from aicertify.evaluators.prohibited_practices import (
    ManipulationEvaluator,
    VulnerabilityExploitationEvaluator,
    SocialScoringEvaluator,
    EmotionRecognitionEvaluator,
)

# Import documentation evaluators
from aicertify.evaluators.documentation import ModelCardEvaluator

# Import the API
from aicertify.evaluators.api import AICertifyEvaluator

# Flag to track if initialization has been performed
_package_initialized = False
_init_lock = threading.RLock()


# Initialize the evaluator registry when the package is imported
# This ensures all available evaluators are registered
def _initialize_registry():
    """Initialize the evaluator registry on package import."""
    import logging
    import threading

    global _package_initialized

    # Use a lock to ensure thread safety
    with _init_lock:
        # Skip if already initialized
        if _package_initialized:
            return

        try:
            # Import here to avoid circular imports
            from .evaluator_registry import initialize_evaluator_registry

            initialize_evaluator_registry()
            _package_initialized = True
            logging.debug("Evaluator registry initialized from package import")
        except Exception as e:
            logging.exception(f"Error initializing evaluator registry: {e}")


# Perform initialization immediately when package is imported
# Don't delay until exit - we need this initialized before API calls
_initialize_registry()

__all__ = [
    "BaseEvaluator",
    "EvaluationResult",
    "Report",
    "FairnessEvaluator",
    "ContentSafetyEvaluator",
    "RiskManagementEvaluator",
    "ComplianceEvaluator",
    "EvaluatorConfig",
    "AICertifyEvaluator",
    "AccuracyEvaluator",
    "BiometricCategorizationEvaluator",
    # Prohibited practices evaluators
    "ManipulationEvaluator",
    "VulnerabilityExploitationEvaluator",
    "SocialScoringEvaluator",
    "EmotionRecognitionEvaluator",
    # Documentation evaluators
    "ModelCardEvaluator",
]
