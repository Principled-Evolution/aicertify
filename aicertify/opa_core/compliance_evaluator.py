import logging
from typing import Dict, Any, Optional

from evaluation_models import AiComplianceInput
from evaluator import OpaEvaluator
from policy_loader import PolicyLoader


def run_opa_on_compliance_input(compliance_input: AiComplianceInput, policy_category: str) -> Optional[Dict[str, Any]]:
    """
    Evaluate all OPA policies in the given category against the provided AiComplianceInput.

    Args:
        compliance_input (AiComplianceInput): The input data containing contract and evaluation results.
        policy_category (str): The category of policies to evaluate (corresponds to a subfolder under the policies directory).

    Returns:
        Optional[Dict[str, Any]]: A dictionary mapping policy file paths to their evaluation results, or None if no policies found.
    """
    data_for_opa: Dict[str, Any] = compliance_input.dict()

    loader = PolicyLoader()
    policy_files = loader.get_policies_by_category(policy_category)
    if policy_files is None:
        logging.error(f"No policies found for category: {policy_category}")
        return None

    opa_evaluator = OpaEvaluator()
    results: Dict[str, Any] = {}
    for policy_file in policy_files:
        logging.info(f"Evaluating policy: {policy_file}")
        eval_result = opa_evaluator.evaluate_policy(policy_file, data_for_opa)
        results[policy_file] = eval_result

    return results 