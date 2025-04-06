"""
Test OPA Results Schema Validation

This module verifies that our Pydantic schema correctly validates real OPA evaluation results.
"""

import json
import os
import pytest
from pathlib import Path

from aicertify.models.opa_results import OpaEvaluationResults
from aicertify.opa_core.extraction import extract_policy_results_with_schema


def find_opa_results_files():
    """Find all OPA results JSON files in the debug_output directory."""
    debug_dir = Path(os.getcwd()) / "debug_output"
    if not debug_dir.exists():
        return []

    return list(debug_dir.glob("opa_results_*.json"))


@pytest.mark.parametrize("result_file", find_opa_results_files())
def test_opa_results_schema_validation(result_file):
    """Test that real OPA results conform to our schema."""
    with open(result_file, "r") as f:
        opa_results = json.load(f)

    # Validate the results against our schema
    validated = OpaEvaluationResults.model_validate(opa_results)

    # Verify that all policy evaluations have the expected structure
    assert hasattr(validated, "result")
    assert hasattr(validated.result, "results")
    assert len(validated.result.results) > 0

    for policy_eval in validated.result.results:
        assert hasattr(policy_eval, "policy")
        assert hasattr(policy_eval, "result")
        assert hasattr(policy_eval.result, "result")

        # Verify that expressions can be accessed
        expressions = policy_eval.result.result[0].expressions
        assert len(expressions) > 0

        # Verify that at least one expression has the report_output format
        report_output_found = False
        for expr in expressions:
            if "report_output" in expr.text:
                report_output_found = True

                # Verify that the report output has the expected structure
                assert hasattr(expr.value, "metrics")
                assert hasattr(expr.value, "policy")
                assert hasattr(expr.value, "result")
                assert hasattr(expr.value, "timestamp")

                # Verify that metrics have the expected structure
                assert len(expr.value.metrics) > 0
                for metric_key, metric in expr.value.metrics.items():
                    assert hasattr(metric, "control_passed")
                    assert hasattr(metric, "name")
                    assert hasattr(metric, "value")

        assert (
            report_output_found
        ), f"No report_output expression found for policy {policy_eval.policy}"


def test_extract_policy_results():
    """Test that our extraction function works correctly with real data."""
    # Find the most recent OPA results file
    result_files = find_opa_results_files()
    if not result_files:
        pytest.skip("No OPA results files found for testing")

    # Sort by modified time to get the most recent
    result_file = sorted(result_files, key=lambda p: p.stat().st_mtime)[-1]

    with open(result_file, "r") as f:
        opa_results = json.load(f)

    # Extract policy results
    extracted = extract_policy_results_with_schema(opa_results)

    # Verify that extraction worked
    assert len(extracted) > 0

    # Verify that each extracted policy has the expected structure
    for policy in extracted:
        assert hasattr(policy, "policy_id")
        assert hasattr(policy, "policy_name")
        assert hasattr(policy, "result")
        assert hasattr(policy, "metrics")
        assert hasattr(policy, "timestamp")

        # Verify that metrics were correctly extracted
        assert len(policy.metrics) > 0
        for metric_key, metric in policy.metrics.items():
            assert hasattr(metric, "control_passed")
            assert hasattr(metric, "name")
            assert hasattr(metric, "value")
