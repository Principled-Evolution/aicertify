"""
Simple Evaluator for AICertify

This module provides a simplified evaluator implementation that doesn't
depend on external libraries or complex dependencies. It's designed as
a fallback when full evaluation capabilities aren't available.
"""

import logging
from typing import Dict, Any

from aicertify.models.contract_models import AiCertifyContract, load_contract
from aicertify.models.evaluation_models import AiEvaluationResult
from aicertify.opa_core.simple_policy import evaluate_policy_simple

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class SimpleEvaluator:
    """
    A simplified evaluator that provides basic evaluation capabilities
    without depending on external libraries or complex dependencies.

    This evaluator is designed to:
    1. Provide basic evaluation results for AICertify contracts
    2. Serve as a fallback when full evaluation isn't possible
    3. Support the staged implementation approach
    """

    def __init__(self):
        """Initialize the simple evaluator"""
        logger.info("Initializing SimpleEvaluator")

    async def evaluate_contract(
        self, contract: AiCertifyContract, policy_category: str = "eu_ai_act"
    ) -> Dict[str, Any]:
        """
        Evaluate a contract using simplified evaluation logic.

        Args:
            contract: The AiCertifyContract to evaluate
            policy_category: The policy category to evaluate against

        Returns:
            Dictionary containing evaluation results
        """
        logger.info(f"Evaluating contract {contract.contract_id} using SimpleEvaluator")

        # Basic evaluation - just counting interactions
        evaluation_result = {
            "contract_id": str(contract.contract_id),
            "application_name": contract.application_name,
            "interaction_count": len(contract.interactions),
            "policy_category": policy_category,
            "simplified_evaluation": True,
            "summary": f"Evaluated {len(contract.interactions)} interactions using SimpleEvaluator",
        }

        # Create a structured evaluation result
        result = AiEvaluationResult(
            contract_id=str(contract.contract_id),
            application_name=contract.application_name,
            summary_text=f"SimpleEvaluator analyzed {len(contract.interactions)} interactions",
            evaluation_mode="simplified",
        )

        # Evaluate against policies
        policy_results = evaluate_policy_simple(
            evaluation_result=evaluation_result, policy_category=policy_category
        )

        return {
            "evaluation_result": evaluation_result,
            "structured_result": result.dict() if result else None,
            "policy_results": policy_results,
        }


async def evaluate_contract_simple(
    contract_path: str,
    policy_category: str = "eu_ai_act",
) -> Dict[str, Any]:
    """
    Evaluate a contract file using the SimpleEvaluator.

    This function provides a convenient entry point for evaluating
    contracts without complex dependencies.

    Args:
        contract_path: Path to the contract JSON file
        policy_category: Policy category to evaluate against

    Returns:
        Dictionary containing evaluation results
    """
    try:
        # Load the contract
        contract = load_contract(contract_path)

        # Create and use the simple evaluator
        evaluator = SimpleEvaluator()
        results = await evaluator.evaluate_contract(
            contract=contract, policy_category=policy_category
        )

        return results
    except Exception as e:
        logger.error(f"Error evaluating contract from {contract_path}: {e}")
        return {"error": str(e), "contract_path": contract_path, "status": "failed"}
