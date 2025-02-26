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
        AiCertifyContract
    )
    
    # Evaluation functions
    from aicertify.api import (
        evaluate_contract,
        evaluate_contract_object,
        evaluate_conversations,
        generate_report
    )
    
    # Set a flag to indicate successful imports
    AICERTIFY_AVAILABLE = True
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(
        f"AICertify components not fully available. Error: {e}"
    )
    AICERTIFY_AVAILABLE = False
