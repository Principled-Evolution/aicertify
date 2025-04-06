"""
AICertify package.

This package provides tools for certifying AI applications against different
compliance frameworks.
"""

# Version information
__version__ = "0.1.0"

# Direct imports for developer convenience
try:
    # Contract creation and management
    from aicertify.models.contract_models import (
        create_contract,
        save_contract,
        load_contract,
        AiCertifyContract,
    )

    # Evaluation functions
    from aicertify.api import (
        evaluate_contract,
        evaluate_contract_object,
        evaluate_conversations,
        evaluate_contract_with_phase1_evaluators,
        evaluate_contract_comprehensive,
        generate_report,
    )

    # Phase 1 Evaluators
    from aicertify.evaluators import (
        BaseEvaluator,
        EvaluationResult,
        Report,
        FairnessEvaluator,
        ContentSafetyEvaluator,
        RiskManagementEvaluator,
        ComplianceEvaluator,
        EvaluatorConfig,
    )

    # Set a flag to indicate successful imports
    AICERTIFY_AVAILABLE = True
except ImportError as e:
    import logging

    logging.getLogger(__name__).warning(
        f"AICertify components not fully available. Error: {e}"
    )
    AICERTIFY_AVAILABLE = False
