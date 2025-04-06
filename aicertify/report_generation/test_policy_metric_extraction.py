"""
Test module for policy metric extraction integration.

This module provides test functions to verify the integration between
the evaluator registry and the flexible extraction system.
"""

import logging
from typing import Dict, Any, Optional
from pprint import pformat

from aicertify.evaluators.evaluator_registry import (
    get_default_registry,
    initialize_evaluator_registry,
)
from aicertify.report_generation.policy_metric_extraction import (
    initialize_metric_extraction,
    extract_policy_required_metrics,
    _generate_extraction_paths,
)

logger = logging.getLogger(__name__)


def test_registry_initialization() -> Dict[str, Any]:
    """
    Test the evaluator registry initialization.

    Returns:
        Dictionary with test results
    """
    try:
        # Initialize the registry
        initialize_evaluator_registry()

        # Get registry information
        registry = get_default_registry()
        metrics = registry.get_all_metrics()
        evaluators = registry.get_all_evaluators()

        return {
            "success": True,
            "metrics_count": len(metrics),
            "evaluators_count": len(evaluators),
            "metrics": sorted(list(metrics)),
            "evaluator_classes": [e.__name__ for e in evaluators],
        }
    except Exception as e:
        logger.exception("Error testing registry initialization")
        return {"success": False, "error": str(e)}


def test_extraction_path_generation() -> Dict[str, Any]:
    """
    Test the generation of extraction paths for metrics.

    Returns:
        Dictionary with test results
    """
    try:
        test_metrics = [
            "fairness.score",
            "toxicity.severity",
            "accuracy",
            "evaluator.sub.metric",
        ]

        results = {}
        for metric in test_metrics:
            paths = _generate_extraction_paths(metric)
            results[metric] = paths

        return {"success": True, "path_generation_results": results}
    except Exception as e:
        logger.exception("Error testing extraction path generation")
        return {"success": False, "error": str(e)}


def test_custom_extraction_logic(
    sample_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Test the custom extraction logic for OPA results.

    Args:
        sample_result: Optional sample evaluation result to use for testing

    Returns:
        Dictionary with test results
    """
    if sample_result is None:
        sample_result = {
            "opa_results": {
                "allow": True,
                "violations": [
                    {"rule": "rule1", "description": "Violation 1"},
                    {"rule": "rule2", "description": "Violation 2"},
                ],
                "compliance_score": 0.85,
            },
            "policy_violations": [
                {"policy": "fairness", "description": "Fairness violation"},
                {"policy": "fairness", "description": "Another fairness violation"},
                {"policy": "privacy", "description": "Privacy violation"},
            ],
        }

    try:
        # Extract metrics from sample result
        metrics = extract_policy_required_metrics(sample_result)

        return {
            "success": True,
            "extracted_metrics_count": len(metrics),
            "extracted_metrics": [
                {"name": m.name, "display_name": m.display_name, "value": m.value}
                for m in metrics
            ],
        }
    except Exception as e:
        logger.exception("Error testing custom extraction logic")
        return {"success": False, "error": str(e)}


def test_full_integration() -> Dict[str, Any]:
    """
    Test the full integration between registry and extraction.

    Returns:
        Dictionary with test results
    """
    try:
        # Step 1: Initialize the evaluator registry
        registry_result = test_registry_initialization()
        if not registry_result["success"]:
            return registry_result

        # Step 2: Initialize the metric extraction
        initialize_metric_extraction()

        # Step 3: Test extraction path generation
        paths_result = test_extraction_path_generation()
        if not paths_result["success"]:
            return paths_result

        # Step 4: Test custom extraction logic
        extraction_result = test_custom_extraction_logic()
        if not extraction_result["success"]:
            return extraction_result

        return {
            "success": True,
            "registry_test": registry_result,
            "paths_test": paths_result,
            "extraction_test": extraction_result,
            "message": "Full integration test successful",
        }
    except Exception as e:
        logger.exception("Error in full integration test")
        return {"success": False, "error": str(e)}


def run_all_tests() -> None:
    """
    Run all tests and print the results.
    """
    logging.basicConfig(level=logging.INFO)

    print("\n====== Testing Policy Metric Extraction Integration ======\n")

    print("\n----- Testing Registry Initialization -----\n")
    registry_result = test_registry_initialization()
    print(pformat(registry_result))

    print("\n----- Testing Extraction Path Generation -----\n")
    paths_result = test_extraction_path_generation()
    print(pformat(paths_result))

    print("\n----- Testing Custom Extraction Logic -----\n")
    extraction_result = test_custom_extraction_logic()
    print(pformat(extraction_result))

    print("\n----- Testing Full Integration -----\n")
    full_result = test_full_integration()
    print(pformat(full_result))

    print("\n====== Test Complete ======\n")


if __name__ == "__main__":
    run_all_tests()
