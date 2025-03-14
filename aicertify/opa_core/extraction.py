"""
OPA result extraction utilities.

This module provides utility functions for extracting data from OPA evaluation results
using the FlexibleExtractor class.
"""

from typing import Dict, Any, List, Optional
import logging

from aicertify.models.report import PolicyResult
from aicertify.opa_core.flexible_extractor import FlexibleExtractor

# Configure logger
logger = logging.getLogger(__name__)

# Global singleton instance of the extractor
_extractor = None

def get_extractor() -> FlexibleExtractor:
    """
    Get the singleton FlexibleExtractor instance.
    
    Returns:
        FlexibleExtractor: The singleton extractor instance
    """
    global _extractor
    if _extractor is None:
        _extractor = FlexibleExtractor()
    return _extractor

def extract_policy_results(opa_results: Dict[str, Any], policy_name: str) -> Optional[PolicyResult]:
    """
    Extract results for a specific policy from OPA evaluation results.
    
    Args:
        opa_results: The OPA evaluation results
        policy_name: Name of the policy to extract results for
        
    Returns:
        PolicyResult for the specified policy, or None if an error occurs
    """
    try:
        extractor = get_extractor()
        return extractor.extract_policy_results(opa_results, policy_name)
    except Exception as e:
        logger.error(f"Error extracting policy results for {policy_name}: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return None

def extract_all_policy_results(opa_results: Dict[str, Any]) -> List[PolicyResult]:
    """
    Extract results for all policies found in the OPA evaluation results.
    
    Args:
        opa_results: The OPA evaluation results
        
    Returns:
        List of PolicyResult objects, one for each policy found
    """
    try:
        extractor = get_extractor()
        return extractor.extract_all_policy_results(opa_results)
    except Exception as e:
        logger.error(f"Error extracting all policy results: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return []

def extract_policy_data(opa_results: Dict[str, Any], policy_name: str) -> Optional[Dict[str, Any]]:
    """
    Extract raw policy data for a specific policy from OPA evaluation results.
    
    Args:
        opa_results: The OPA evaluation results
        policy_name: Name of the policy to extract data for
        
    Returns:
        Raw policy data as a dictionary, or None if not found or an error occurs
    """
    try:
        extractor = get_extractor()
        return extractor.extract_policy_data(opa_results, policy_name)
    except Exception as e:
        logger.error(f"Error extracting policy data for {policy_name}: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return None

def validate_opa_results(opa_results: Dict[str, Any]) -> bool:
    """
    Validate that OPA results have the expected structure.
    
    Args:
        opa_results: The OPA evaluation results to validate
        
    Returns:
        True if the results have a valid structure, False otherwise
    """
    if not opa_results or not isinstance(opa_results, dict):
        logger.warning("Invalid OPA results: results are None or not a dictionary")
        return False
        
    if "result" not in opa_results:
        logger.warning("Invalid OPA results: missing 'result' key")
        return False
        
    result_list = opa_results["result"]
    if not isinstance(result_list, list) or not result_list:
        logger.warning("Invalid OPA results: 'result' is not a non-empty list")
        return False
        
    first_result = result_list[0]
    if not isinstance(first_result, dict):
        logger.warning("Invalid OPA results: first result is not a dictionary")
        return False
        
    if "expressions" not in first_result or not first_result["expressions"]:
        logger.warning("Invalid OPA results: missing or empty 'expressions' key")
        return False
        
    first_expr = first_result["expressions"][0]
    if not isinstance(first_expr, dict):
        logger.warning("Invalid OPA results: first expression is not a dictionary")
        return False
        
    if "value" not in first_expr:
        logger.warning("Invalid OPA results: missing 'value' key")
        return False
        
    value = first_expr["value"]
    if not isinstance(value, dict):
        logger.warning("Invalid OPA results: 'value' is not a dictionary")
        return False
        
    # Check for at least one version key (v1, v2, etc.)
    version_keys = [k for k in value.keys() if k.startswith("v")]
    if not version_keys:
        logger.warning("Invalid OPA results: no version keys found")
        return False
        
    # Results have valid structure
    return True 